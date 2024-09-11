import logging
import requests
from typing import Dict
from .const import DOMAIN, CONF_DEVICE, CONF_TOKEN, CONF_ID, CONF_PORT, CONF_NAME, ATTR_CONTENT, ATTR_DEVICENANME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.exceptions import HomeAssistantError
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = "9000"

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
                vol.Optional(CONF_PORT): cv.string,
            }
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    conf = config[DOMAIN]
    port = conf.get(CONF_PORT,DEFAULT_PORT)
    
    def pixlet_push(call: ServiceCall) -> None:
        """Handle the service action call."""
        url = f"http://localhost:{port}/hooks/tidbyt-display"
        content = call.data.get(ATTR_CONTENT)
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
            todo = {"content": content, "token": token, "deviceid": deviceid}
            response = requests.post(url, json=todo)

    hass.services.register(DOMAIN, "Push", pixlet_push)

    # Return boolean to indicate that initialization was successful.
    return True
