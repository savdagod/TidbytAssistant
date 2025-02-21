import logging
import requests
import aiohttp
import asyncio
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_DEVICE, CONF_NAME, CONF_TOKEN, CONF_ID, CONF_API_URL, DEFAULT_API_URL

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None:
    if discovery_info is None:
        return

    conf = hass.data[DOMAIN]
    for tidbyt in conf[CONF_DEVICE]:
        add_entities([TidbytSwitch(tidbyt)])

class TidbytSwitch(SwitchEntity):
    def __init__(self, tidbyt):
        self._name = tidbyt[CONF_NAME]
        self._deviceid = tidbyt[CONF_ID]
        self._token = tidbyt[CONF_TOKEN]
        
        append = self._deviceid.split('-')
        if len(append) > 3:
            self._entity_id = f"switch.{self._name.replace(" ","_")}_{append[3]}"
        else:
            self._entity_id = f"switch.{self._name.replace(" ","_")}"
        
        self._url = f"{tidbyt.get(CONF_API_URL, DEFAULT_API_URL)}/v0/devices/{self._deviceid}"
        self._header = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._brightness = None
        self._is_on = None 

    @property
    def name(self):
        id_components = self._deviceid.split('-')
        if len(id_components) > 3:
            return f"{self._name} {id_components[3].capitalize()} AutoDim"
        return f"{self._name} AutoDim"

    @property
    def unique_id(self):
        return f"tidbytautodim{self._deviceid}"

    @property
    def icon(self):
        return "mdi:brightness-auto" 

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        payload = {
            "autoDim": True
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(self._url, headers=self._header, json=payload) as response:
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")

    async def async_turn_off(self, **kwargs: Any) -> None:
        payload = {
            "autoDim": False
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(self._url, headers=self._header, json=payload) as response:
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")

    async def async_update(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url, headers=self._header) as response:       
                data = await response.json()
                status = f"{response.status}"
                if status != "200":
                    error = await response.text()
                    _LOGGER.error(f"{error}")
                else:
                    self._is_on = data.get("autoDim")

    async def async_poll_device(self):
        while True:
            self.update()
            time.sleep(30)