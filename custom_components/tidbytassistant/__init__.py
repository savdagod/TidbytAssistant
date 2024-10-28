import logging
import os
import requests
import yaml
import re
from typing import Dict
from .const import (
    DOMAIN, 
    CONF_DEVICE, 
    CONF_TOKEN, 
    CONF_ID, 
    CONF_PORT, 
    CONF_HOST, 
    CONF_NAME, 
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
    ATTR_BRIGHTNESS,
    ATTR_AUTODIM,
    ATTR_LANG
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.discovery import load_platform

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = "9000"
DEFAULT_HOST = "localhost"
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
    }
)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE): vol.All(cv.ensure_list, [TIDBYT_SCHEMA]),
                vol.Optional(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT): cv.string,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

def getdevicename(deviceid, token) -> str:
    url = f"https://api.tidbyt.com/v0/devices/{deviceid}"
    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=header)
    data = response.json()
    return data.get("displayName")

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST,DEFAULT_HOST)
    port = conf.get(CONF_PORT,DEFAULT_PORT)
    url = f"http://{host}:{port}"

    try:
        response = requests.get(f"{url}/apps")
    except:
        _LOGGER.error("Could not connect to the add-on. Make sure it is installed or running and try again.")
        return False
    
    config_dir = hass.config.path()
    yaml_path = os.path.join(config_dir, "custom_components", "tidbytassistant", "services.yaml")
    with open(yaml_path) as file:
        config = yaml.safe_load(file)
    
    devicelist = []
    for item in conf[CONF_DEVICE]:
        if CONF_NAME in item:
            devicelist.append(item[CONF_NAME])
        else:
            retrievedname = getdevicename(item[CONF_ID],item[CONF_TOKEN])
            devicelist.append(retrievedname)
            item[CONF_NAME] = retrievedname

    device_name_options = [{"label": name, "value": name} for name in devicelist]

    config['push']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['delete']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['text']['fields']['devicename']['selector']['select']['options'] = device_name_options

    response = requests.get(f"{url}/apps")
    status = f"{response.status_code}"
    if status != "200":
        error = f"{response.text}"
        _LOGGER.error(f"{error}")
    
    data = response.json()
    content_options = [{"label": item["label"], "value": item["value"]} for item in data]

    config['push']['fields']['content']['selector']['select']['options'] = content_options

    with open(yaml_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    def validateid(input):
        """Check if the string contains only A-Z, a-z, and 0-9."""
        pattern = r'^[A-Za-z0-9]+$'
        return bool(re.match(pattern, input))

    def getinstalledapps(deviceid, token):
        url = f"https://api.tidbyt.com/v0/devices/{deviceid}/installations"
        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=header)
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
            raise HomeAssistantError(f"{error}")
            
        appids = []
        data = response.json()
        for item in data['installations']:
            if item["appID"] == "":
                appids.append(item["id"])
        return appids

    def command(webhook_url, payload):
        response = requests.post(webhook_url, json=payload)

        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
            raise HomeAssistantError(f"{error}")

    def pixlet_push(call: ServiceCall) -> None:
        webhook_url = f"{url}/push"
        contentid = call.data.get(ATTR_CONTENT_ID,DEFAULT_CONTENT_ID)
        contenttype = call.data.get(ATTR_CONT_TYPE)
        publishtype = call.data.get(ATTR_PUBLISH_TYPE)
        args = call.data.get(ATTR_ARGS,DEFAULT_ARGS)
        arguments = {}
        if args != "":
            a = args.split(";")
            for p in a:
                key, value = p.split("=")
                arguments[key] = value

        match contenttype:
            case "builtin":
                content = call.data.get(ATTR_CONTENT)
                arguments["lang"] = call.data.get(ATTR_LANG,DEFAULT_LANG)
            case "custom":
                content = call.data.get(ATTR_CUSTOM_CONT)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {
                        "content": content,
                        "contentid": contentid,
                        "contenttype": contenttype,
                        "publishtype": publishtype,
                        "token": token,
                        "deviceid": deviceid,
                        "starargs": arguments,
                    }
                    command(webhook_url, todo)

    def pixlet_text(call: ServiceCall) -> None:
        webhook_url = f"{url}/push"
        contenttype = "builtin"
        contentid = call.data.get(ATTR_CONTENT_ID,DEFAULT_CONTENT_ID)
        publishtype = call.data.get(ATTR_PUBLISH_TYPE)
        texttype = call.data.get(ATTR_TEXT_TYPE)
        content = f"text-{texttype}"
        devicename = call.data.get(ATTR_DEVICENANME)

        arguments = {}
        arguments["content"] = call.data.get(ATTR_CONTENT)
        arguments["font"] = call.data.get(ATTR_FONT)
        arguments["color"] = call.data.get(ATTR_COLOR)
        arguments["title"] = call.data.get(ATTR_TITLE_CONTENT,DEFAULT_TITLE)
        arguments["titlecolor"] = call.data.get(ATTR_TITLE_COLOR,DEFAULT_TITLE_COLOR)
        arguments["titlefont"] = call.data.get(ATTR_TITLE_FONT,DEFAULT_TITLE_FONT)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {
                        "content": content,
                        "contentid": contentid,
                        "contenttype": contenttype,
                        "publishtype": publishtype,
                        "texttype": texttype, 
                        "token": token, 
                        "deviceid": deviceid,
                        "starargs": arguments
                    }
                    command(webhook_url, todo)

    def pixlet_delete(call: ServiceCall) -> None:
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
                    
                    validids = getinstalledapps(deviceid, token)
                    if contentid not in validids:
                        _LOGGER.error(f"The Content ID you entered is not an installed app on {device}. Currently installed apps are: {validids}")
                        raise HomeAssistantError(f"The Contend ID you entered is not an installed app on {device}. Currently installed apps are: {validids}")
                    
                    url = f"https://api.tidbyt.com/v0/devices/{deviceid}/installations/{contentid}"
                    header = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }
                    response = requests.delete(url, headers=header)

                    status = f"{response.status_code}"
                    if status != "200":
                        error = f"{response.text}"
                        _LOGGER.error(f"{error}")
                        raise HomeAssistantError(f"{error}")

    hass.services.register(DOMAIN, "push", pixlet_push)
    hass.services.register(DOMAIN, "text", pixlet_text)
    hass.services.register(DOMAIN, "delete", pixlet_delete)

    hass.data[DOMAIN] = conf
    load_platform(hass, 'light', DOMAIN, {}, config)
    load_platform(hass, 'switch', DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successful.
    return True

    

