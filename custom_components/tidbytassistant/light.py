import logging
import requests
import math
import time
from typing import Any
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNAVAILABLE

BRIGHTNESS_SCALE = (1, 100)

from .const import DOMAIN, CONF_DEVICE, CONF_NAME, CONF_TOKEN, CONF_ID

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None:
    if discovery_info is None:
        return

    conf = hass.data[DOMAIN]
    for tidbyt in conf[CONF_DEVICE]:
        add_entities([TidbytLight(tidbyt)])

class TidbytLight(LightEntity):
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, tidbyt):
        self._name = tidbyt["name"]
        self._deviceid = tidbyt["deviceid"]
        self._token = tidbyt["token"]
        self._is_on = True
        self._url = f"https://api.tidbyt.com/v0/devices/{self._deviceid}"

        self._header = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = requests.get(self._url, headers=self._header)    
        status = f"{response.status_code}"
        if status != "200":
            self._brightness = None
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
        else:
            data = response.json()
            self._brightness = round((data.get("brightness", 0)*.01) * 255)

    @property
    def name(self):
        append = self._deviceid.split('-')
        return f"{self._name} {append[3].capitalize()} Brightness"

    @property
    def unique_id(self):
        return f"tidbytlight-{self._deviceid}"

    @property
    def brightness(self):
        return self._brightness

    @property
    def icon(self):
        return "mdi:television-ambient-light" 

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._is_on
    
    def turn_on(self, **kwargs: any) -> None:
        """Instruct the light to turn on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = round((kwargs[ATTR_BRIGHTNESS] / 255) * 100)
        else:        
            brightness = self._brightness

        payload = {
            "brightness": int(brightness)
        }
        response = requests.patch(self._url, headers=self._header, json=payload)
        
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
        else:
            self._brightness = brightness

    def turn_off(self, **kwargs: any) -> None:
        """do nothing"""
        
    def update(self) -> None:
        """Fetch new state data for this light."""
        response = requests.get(self._url, headers=self._header)
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
        else:
            data = response.json()
            self._is_on = data.get("brightness", 0) >= 1
            self._brightness = round((data.get("brightness", 0)*.01) * 255)

    def poll_device(self):
        while True:
            self.update()
            time.sleep(30)