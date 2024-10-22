import logging
import requests
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_DEVICE, CONF_NAME, CONF_TOKEN, CONF_ID

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass: HomeAssistant, config: ConfigType, add_entities: AddEntitiesCallback, discovery_info: DiscoveryInfoType | None = None) -> None:
    if discovery_info is None:
        return

    conf = hass.data[DOMAIN]
    for tidbyt in conf[CONF_DEVICE]:
        add_entities([TidbytSwitch(tidbyt)])

class TidbytSwitch(SwitchEntity):
    def __init__(self, tidbyt):
        self._name = tidbyt["name"]
        self._deviceid = tidbyt["deviceid"]
        self._token = tidbyt["token"]
        
        append = self._deviceid.split('-')
        self._entity_id = f"switch.{self._name.replace(" ","_")}_{append[3]}"
        
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
            self._is_on = data.get("autoDim")    

    @property
    def name(self):
        append = self._deviceid.split('-')
        return f"{self._name} {append[3].capitalize()} AutoDim"

    @property
    def unique_id(self):
        return f"tidbytautodim{self._deviceid}"

    @property
    def icon(self):
        return "mdi:brightness-auto" 

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    def turn_on(self, **kwargs: Any) -> None:
        payload = {
            "autoDim": True
        }
        response = requests.patch(self._url, headers=self._header, json=payload)
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")

    def turn_off(self, **kwargs: Any) -> None:
        payload = {
            "autoDim": False
        }
        response = requests.patch(self._url, headers=self._header, json=payload)
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")

    def update(self) -> None:
        response = requests.get(self._url, headers=self._header)
        
        data = response.json()
        status = f"{response.status_code}"
        if status != "200":
            error = f"{response.text}"
            _LOGGER.error(f"{error}")
        else:
            self._is_on = data.get("autoDim")

    def poll_device(self):
        while True:
            self.update()
            time.sleep(30)