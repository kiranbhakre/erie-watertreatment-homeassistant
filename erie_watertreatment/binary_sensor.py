"""Erie Water Treatment binary sensors."""
import logging

from homeassistant.helpers.entity import Entity

from . import get_coordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug(f"{DOMAIN}: binary_sensor: async_setup_entry: {entry}")
    coordinator = await get_coordinator(hass)
    async_add_entities([ErieLowSaltBinarySensor(coordinator)])


class ErieLowSaltBinarySensor(Entity):
    """True when any active warning mentions low salt."""

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.info_type = "low_salt"

    @property
    def name(self):
        return f"{DOMAIN}.{self.info_type}"

    @property
    def device_class(self):
        return "problem"

    @property
    def state(self):
        status = self.coordinator.data
        if status is None or not status["warnings"]:
            return False
        return any("Salt" in w["description"] for w in status["warnings"])
