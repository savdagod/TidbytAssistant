import logging
import os
import yaml
import re
import asyncio
import aiofiles
import aiohttp
import time
from .addon import get_addon_manager
from .const import (
    DOMAIN,
    CONF_DEVICE,
    CONF_TOKEN,
    CONF_ID,
    CONF_PORT,
    CONF_HOST,
    CONF_NAME,
    CONF_EXTERNALADDON,
    CONF_API_URL,
    CONF_TRONBYT,
    ATTR_CONTENT,
    ATTR_CONTENT_ID,
    ATTR_DEVICENANME,
    ATTR_CONT_TYPE,
    ATTR_CUSTOM_CONT,
    ATTR_TEXT_TYPE,
    ATTR_FONT,
    ATTR_COLOR,
    ATTR_TITLE_CONTENT,
    ATTR_TITLE_COLOR,
    ATTR_TITLE_FONT,
    ATTR_ARGS,
    ATTR_PUBLISH_TYPE,
    ATTR_LANG,
    ADDON_MIN_VERSION,
    DEFAULT_API_URL
)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
from homeassistant.config_entries import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.components.hassio import AddonManager, AddonState
from homeassistant.helpers.discovery import load_platform

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = "9000"
DEFAULT_HOST = "localhost"
DEFAULT_EXTERNAL_ADDON = False
DEFAULT_TITLE = ""
DEFAULT_TITLE_COLOR = ""
DEFAULT_TITLE_FONT = ""
DEFAULT_ARGS = ""
DEFAULT_CONTENT_ID = ""
DEFAULT_LANG = "en"

TIDBYT_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME): cv.string,
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_API_URL): cv.string,
        vol.Optional(CONF_TRONBYT): cv.boolean,
    }
)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE): vol.All(cv.ensure_list, [TIDBYT_SCHEMA]),
                vol.Optional(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT): cv.string,
                vol.Optional(CONF_EXTERNALADDON): cv.boolean,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

async def getdevicename(endpoint, deviceid, token) -> str:
    url = f"{endpoint}/v0/devices/{deviceid}"
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=header) as response:
            data = await response.json()
    return data.get("displayName")

@callback
def _get_addon_manager(hass: HomeAssistant) -> AddonManager:
    addon_manager: AddonManager = get_addon_manager(hass)
    if addon_manager.task_in_progress():
        raise ConfigEntryNotReady
    return addon_manager

def is_min_version(version1: str, version2: str) -> bool:
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))
    
    max_length = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_length - len(v1_parts)))
    v2_parts.extend([0] * (max_length - len(v2_parts)))
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return True
        elif v1 < v2:
            return False

    return True

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST,DEFAULT_HOST)
    port = conf.get(CONF_PORT,DEFAULT_PORT)
    external_addon = conf.get(CONF_EXTERNALADDON,DEFAULT_EXTERNAL_ADDON)
    url = f"http://{host}:{port}"

    has_tidbyt = False
    devicelist = []
    for device in conf[CONF_DEVICE]:
        if not device.get(CONF_TRONBYT, False):
            has_tidbyt = True
            break
        if CONF_NAME in device:
            devicelist.append(device[CONF_NAME])
        else:
            retrievedname = await getdevicename(
                device.get(CONF_API_URL, DEFAULT_API_URL),
                device[CONF_ID],
                device[CONF_TOKEN]
            )
            devicelist.append(retrievedname)
            device[CONF_NAME] = retrievedname

    # Check if the add-on is installed and running if at least one device is not a Tronbyt
    if has_tidbyt:
        if not external_addon:
            addon_manager = _get_addon_manager(hass)
            addon_info = await addon_manager.async_get_addon_info()
            addon_state = addon_info.state
            addon_current_ver = addon_info.version
            if addon_state == AddonState.NOT_INSTALLED:
                _LOGGER.error("The add-on is not installed. Make sure it is installed and try again.")
                return False
            if not is_min_version(addon_current_ver, ADDON_MIN_VERSION):
                _LOGGER.error(f"The minimum required add-on version is {ADDON_MIN_VERSION} but the currently installed version is {addon_current_ver}. Please update the add-on to the latest version.")
                return False
        else:
            timeout = time.time() + 60
            while True:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{url}/apps") as response:
                            status = f"{response.status}"
                            if status == "200":
                                break
                except aiohttp.ClientError:
                    pass
                if time.time() > timeout:
                    _LOGGER.error("Connection to add-on timed out after 60 seconds. Make sure it is installed or running and try again.")
                    return False
                await asyncio.sleep(5)

    config_dir = hass.config.path()
    yaml_path = os.path.join(config_dir, "custom_components", "tidbytassistant", "services.yaml")
    async with aiofiles.open(yaml_path) as file:
        content = await file.read()
        config = yaml.safe_load(content)

    device_name_options = [{"label": name, "value": name} for name in devicelist]

    config['push']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['delete']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['text']['fields']['devicename']['selector']['select']['options'] = device_name_options

    if has_tidbyt:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}/apps") as response:
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")

                data = await response.json()
        content_options = [{"label": item["label"], "value": item["value"]} for item in data]

        config['push']['fields']['content']['selector']['select']['options'] = content_options

    async with aiofiles.open(yaml_path, 'w') as file:
        await file.write(yaml.dump(config, default_flow_style=False, sort_keys=False))

    async def validateid(input):
        """Check if the string contains only A-Z, a-z, and 0-9."""
        pattern = r'^[A-Za-z0-9]+$'
        return bool(re.match(pattern, input))

    async def getinstalledapps(endpoint, deviceid, token):
        url = f"{endpoint}/v0/devices/{deviceid}/installations"
        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as response:
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")
                    raise HomeAssistantError(f"{error}")
                appids = []
                data = await response.json()
                for item in data['installations']:
                    if item["appID"] == "":
                        appids.append(item["id"])
                return appids

    async def command(webhook_url, payload, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, headers=headers) as response:
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")
                    raise HomeAssistantError(f"{error}")

    async def handle_push_or_text(call: ServiceCall, is_text: bool) -> None:
        webhook_url = f"{url}/push"
        contentid = call.data.get(ATTR_CONTENT_ID, DEFAULT_CONTENT_ID)
        publishtype = call.data.get(ATTR_PUBLISH_TYPE)
        devicename = call.data.get(ATTR_DEVICENANME)

        arguments = {}
        if is_text:
            contenttype = "builtin"
            texttype = call.data.get(ATTR_TEXT_TYPE)
            content = f"text-{texttype}"
            arguments["content"] = call.data.get(ATTR_CONTENT)
            arguments["font"] = call.data.get(ATTR_FONT)
            arguments["color"] = call.data.get(ATTR_COLOR)
            arguments["title"] = call.data.get(ATTR_TITLE_CONTENT, DEFAULT_TITLE)
            arguments["titlecolor"] = call.data.get(ATTR_TITLE_COLOR, DEFAULT_TITLE_COLOR)
            arguments["titlefont"] = call.data.get(ATTR_TITLE_FONT, DEFAULT_TITLE_FONT)
        else:
            contenttype = call.data.get(ATTR_CONT_TYPE)
            args = call.data.get(ATTR_ARGS, DEFAULT_ARGS)
            if args != "":
                a = args.split(";")
                for p in a:
                    key, value = p.split("=")
                    arguments[key] = value

            match contenttype:
                case "builtin":
                    content = call.data.get(ATTR_CONTENT)
                    arguments["lang"] = call.data.get(ATTR_LANG, DEFAULT_LANG)
                case "custom":
                    content = call.data.get(ATTR_CUSTOM_CONT)

        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    is_tronbyt = item.get(CONF_TRONBYT, False)
                    if is_tronbyt:
                        api_url = f"{item[CONF_API_URL]}/v0/devices/{deviceid}/push_app"
                        header = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                        }
                        body = {
                            "config": arguments,
                            "app_id": content,
                            "installationID": contentid,
                        }
                        await command(api_url, body, headers=header)
                    else:
                        todo = {
                            "content": content,
                            "contentid": contentid,
                            "contenttype": contenttype,
                            "publishtype": publishtype,
                            "token": token,
                            "deviceid": deviceid,
                            "starargs": arguments,
                        }
                        if is_text:
                            todo["texttype"] = texttype
                        if CONF_API_URL in item:
                            todo["base_url"] = item[CONF_API_URL]
                        await command(webhook_url, todo)

    async def pixlet_push(call: ServiceCall) -> None:
        await handle_push_or_text(call, is_text=False)

    async def pixlet_text(call: ServiceCall) -> None:
        await handle_push_or_text(call, is_text=True)

    async def pixlet_delete(call: ServiceCall) -> None:
        contentid = call.data.get(ATTR_CONTENT_ID)
        if not validateid(contentid):
            _LOGGER.error("Content ID must contain characters A-Z, a-z or 0-9")
            raise HomeAssistantError("Content ID must contain characters A-Z, a-z or 0-9")
        
        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    base_url = item.get(CONF_API_URL, DEFAULT_API_URL)

                    validids = await getinstalledapps(base_url, deviceid, token)
                    if contentid not in validids:
                        _LOGGER.error(f"The Content ID you entered is not an installed app on {device}. Currently installed apps are: {validids}")
                        raise HomeAssistantError(f"The Content ID you entered is not an installed app on {device}. Currently installed apps are: {validids}")
                    
                    url = f"{base_url}/v0/devices/{deviceid}/installations/{contentid}"
                    header = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                    async with aiohttp.ClientSession() as session:
                        async with session.delete(url, headers=header) as response:
                            status = f"{response.status}"
                            if status != "200":
                                error = await response.text()
                                _LOGGER.error(f"{error}")
                                raise HomeAssistantError(f"{error}")

    hass.services.async_register(DOMAIN, "push", pixlet_push)
    hass.services.async_register(DOMAIN, "text", pixlet_text)
    hass.services.async_register(DOMAIN, "delete", pixlet_delete)

    hass.data[DOMAIN] = conf
    load_platform(hass, 'light', DOMAIN, {}, config)
    load_platform(hass, 'switch', DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successful.
    return True
