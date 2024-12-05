from __future__ import annotations
import logging
from homeassistant.components.hassio import AddonManager
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.singleton import singleton

from .const import ADDON_SLUG, DOMAIN

DATA_ADDON_MANAGER = f"{DOMAIN}_addon_manager"
_LOGGER = logging.getLogger(__name__)

@singleton(DATA_ADDON_MANAGER)
@callback
def get_addon_manager(hass: HomeAssistant) -> AddonManager:
    """Get the add-on manager."""
    return AddonManager(hass, _LOGGER, "TidbytAssistant", ADDON_SLUG)