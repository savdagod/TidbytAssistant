import logging
import requests
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
    
    def pixlet_push(call: ServiceCall) -> None:
        """Handle the service action call."""
        
        webhook_url = f"{url}/tidbyt-push"
        contenttype = call.data.get(ATTR_CONT_TYPE)
        arguments = call.data.get(ATTR_ARGS)
        match contenttype:
            case "builtin":
                content = call.data.get(ATTR_CONTENT)
            case "custom":
                content = call.data.get(ATTR_CUSTOM_CONT)

        devicename = call.data.get(ATTR_DEVICENANME)
        data = config[DOMAIN]
        devicefound = False
        for item in data[CONF_DEVICE]:
            if item[CONF_NAME] == devicename:
                token = item[CONF_TOKEN]
                deviceid = item[CONF_ID]
                devicefound = True
                break
        if devicefound is False:
            valid_names = ""
            for item in data[CONF_DEVICE]:
                vname = item[CONF_NAME]
                valid_names += vname + ", "
            valid_names = valid_names[:-2]
            raise HomeAssistantError(f"Device name {devicename} was not found. Valid device names are: {valid_names}")
        else:  
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
        arguments = call.data.get(ATTR_ARGS)
        publishtype = call.data.get(ATTR_PUBLISH_TYPE)
        devicename = call.data.get(ATTR_DEVICENANME)
        data = config[DOMAIN]
        devicefound = False
        for item in data[CONF_DEVICE]:
            if item[CONF_NAME] == devicename:
                token = item[CONF_TOKEN]
                deviceid = item[CONF_ID]
                devicefound = True
                break
        if devicefound is False:
            valid_names = ""
            for item in data[CONF_DEVICE]:
                vname = item[CONF_NAME]
                valid_names += vname + ", "
            valid_names = valid_names[:-2]
            raise HomeAssistantError(f"Device name {devicename} was not found. Valid device names are: {valid_names}")
        else:  
            todo = {"content": content, "contentid": contentid, "token": token, "deviceid": deviceid, "publishtype": publishtype, "starargs": arguments}
            try:
                response = requests.post(webhook_url, json=todo)
            except:
                raise HomeAssistantError(f"Could not communicate with the add-on. Is it installed?")

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

        data = config[DOMAIN]
        devicefound = False
        for item in data[CONF_DEVICE]:
            if item[CONF_NAME] == devicename:
                token = item[CONF_TOKEN]
                deviceid = item[CONF_ID]
                devicefound = True
                break
        if devicefound is False:
            valid_names = ""
            for item in data[CONF_DEVICE]:
                vname = item[CONF_NAME]
                valid_names += vname + ", "
            valid_names = valid_names[:-2]
            raise HomeAssistantError(f"Device name {devicename} was not found. Valid device names are: {valid_names}")
        else:
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
        data = config[DOMAIN]
        devicefound = False
        for item in data[CONF_DEVICE]:
            if item[CONF_NAME] == devicename:
                token = item[CONF_TOKEN]
                deviceid = item[CONF_ID]
                devicefound = True
                break
        if devicefound is False:
            valid_names = ""
            for item in data[CONF_DEVICE]:
                vname = item[CONF_NAME]
                valid_names += vname + ", "
            valid_names = valid_names[:-2]
            raise HomeAssistantError(f"Device name {devicename} was not found. Valid device names are: {valid_names}")
        else:  
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