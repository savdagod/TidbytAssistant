import logging
import os
import requests
import yaml
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
    ATTR_PUBLISH_TYPE
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = "9000"
DEFAULT_HOST = "localhost"
DEFAULT_TITLE = ""
DEFAULT_TITLE_COLOR = ""
DEFAULT_TITLE_FONT = ""
DEFAULT_ARGS = ""

TIDBYT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string, 
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

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST,DEFAULT_HOST)
    port = conf.get(CONF_PORT,DEFAULT_PORT)
    url = f"http://{host}:{port}/hooks"
    
    config_dir = hass.config.path()
    yaml_path = os.path.join(config_dir, "custom_components", "tidbytassistant", "services.yaml")
    with open(yaml_path) as file:
        config = yaml.safe_load(file)
    
    devicelist = []
    for item in conf[CONF_DEVICE]:
        devicelist.append(item[CONF_NAME])
    device_name_options = [{"label": name, "value": name} for name in devicelist]

    config['push']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['publish']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['delete']['fields']['devicename']['selector']['select']['options'] = device_name_options
    config['text']['fields']['devicename']['selector']['select']['options'] = device_name_options
    
    with open(yaml_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)

    def pixlet_push(call: ServiceCall) -> None:
        """Handle the service action call."""
        
        webhook_url = f"{url}/tidbyt-push"
        contenttype = call.data.get(ATTR_CONT_TYPE)
        arguments = call.data.get(ATTR_ARGS,DEFAULT_ARGS)
        match contenttype:
            case "builtin":
                content = call.data.get(ATTR_CONTENT)
            case "custom":
                content = call.data.get(ATTR_CUSTOM_CONT)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {"content": content, "token": token, "deviceid": deviceid, "contenttype": contenttype, "starargs": arguments}
                    try:
                        response = requests.post(webhook_url, json=todo)
                    except:
                        raise HomeAssistantError(f"Could not communicate with the add-on. Is it installed?")

                    status = f"{response.status_code}"
                    if status == "500":
                        error = f"{response.text}"
                        _LOGGER.error(f"{error}")
                        raise HomeAssistantError(f"An error occurred. Check the logs for more details.")
    
    def pixlet_publish(call: ServiceCall) -> None:
        """Handle the service action call."""
        
        webhook_url = f"{url}/tidbyt-publish"
        content = call.data.get(ATTR_CONTENT)
        contentid = call.data.get(ATTR_CONTENT_ID)
        arguments = call.data.get(ATTR_ARGS,DEFAULT_ARGS)
        publishtype = call.data.get(ATTR_PUBLISH_TYPE)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {"content": content, "contentid": contentid, "token": token, "deviceid": deviceid, "publishtype": publishtype, "starargs": arguments}
                    try:
                        response = requests.post(webhook_url, json=todo)
                    except:
                        raise HomeAssistantError(f"Could not communicate with the add-on. Is it installed?")
                        break

                    status = f"{response.status_code}"
                    if status == "500":
                        error = f"{response.text}"
                        _LOGGER.error(f"{error}")
                        raise HomeAssistantError(f"An error occurred. Check the logs for more details.")
    
    def pixlet_text(call: ServiceCall) -> None:
        """Handle the service action call."""
        
        webhook_url = f"{url}/tidbyt-text"
        content = call.data.get(ATTR_CONTENT)
        texttype = call.data.get(ATTR_TEXT_TYPE)
        devicename = call.data.get(ATTR_DEVICENANME)
        font = call.data.get(ATTR_FONT)
        color = call.data.get(ATTR_COLOR)
        title = call.data.get(ATTR_TITLE_CONTENT,DEFAULT_TITLE)
        titlecolor = call.data.get(ATTR_TITLE_COLOR,DEFAULT_TITLE_COLOR)
        titlefont = call.data.get(ATTR_TITLE_FONT,DEFAULT_TITLE_FONT)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {"content": content, "texttype": texttype, "font": font, "color": color, "title": title, "titlecolor": titlecolor, "titlefont": titlefont, "token": token, "deviceid": deviceid}
                    try:
                        response = requests.post(webhook_url, json=todo)
                    except:
                        raise HomeAssistantError(f"Could not communicate with the add-on. Is it installed?")

                    status = f"{response.status_code}"
                    if status == "500":
                        error = f"{response.text}"
                        _LOGGER.error(f"{error}")
                        raise HomeAssistantError(f"An error occurred. Check the logs for more details.")

    def pixlet_delete(call: ServiceCall) -> None:
        """Handle the service action call."""

        webhook_url = f"{url}/tidbyt-delete"
        contentid = call.data.get(ATTR_CONTENT_ID)
        devicename = call.data.get(ATTR_DEVICENANME)

        devicename = call.data.get(ATTR_DEVICENANME)
        for device in devicename:
            for item in conf[CONF_DEVICE]:
                if item[CONF_NAME] == device:
                    token = item[CONF_TOKEN]
                    deviceid = item[CONF_ID]
                    todo = {"contentid": contentid, "token": token, "deviceid": deviceid}
                    try:
                        response = requests.post(webhook_url, json=todo)
                    except:
                        raise HomeAssistantError(f"Could not communicate with the add-on. Is it installed?")

                    status = f"{response.status_code}"
                    if status == "500":
                        error = f"{response.text}"
                        _LOGGER.error(f"{error}")
                        raise HomeAssistantError(f"An error occurred. Check the logs for more details.")

    hass.services.register(DOMAIN, "Push", pixlet_push)
    hass.services.register(DOMAIN, "Publish", pixlet_publish)
    hass.services.register(DOMAIN, "Text", pixlet_text)
    hass.services.register(DOMAIN, "Delete", pixlet_delete)

    # Return boolean to indicate that initialization was successful.
    return True