"""Erie Water Treatment binary sensors."""
import logging

from homeassistant.helpers.entity import Entity

from . import get_coordinator
from .const import CONF_DEVICE_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug(f"{DOMAIN}: binary_sensor: async_setup_entry: {entry}")
    coordinator = await get_coordinator(hass)
    device_id = entry.data[CONF_DEVICE_ID]
    async_add_entities([
        ErieLowSaltBinarySensor(coordinator),
        # Parameterised warning sensors (one per warning category)
        ErieWarningBinarySensor(coordinator, device_id, "filter",  "filter_warning"),
        ErieWarningBinarySensor(coordinator, device_id, "service", "service_warning"),
        ErieWarningBinarySensor(coordinator, device_id, "error",   "error_warning"),
        # True when any warning is active
        ErieAnyWarningBinarySensor(coordinator, device_id),
        # Holiday mode
        ErieHolidayModeBinarySensor(coordinator, device_id),
    ])


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


# ---------------------------------------------------------------------------
# Parameterised warning binary sensor — one instance per warning category
# ---------------------------------------------------------------------------

class ErieWarningBinarySensor(Entity):
    """True when any active warning description contains the given keyword (case-insensitive)."""

    def __init__(self, coordinator, device_id, keyword: str, sensor_name: str):
        self.coordinator = coordinator
        self._device_id = device_id
        self._keyword = keyword.lower()
        self._sensor_name = sensor_name

    @property
    def unique_id(self):
        return f"{self._device_id}_{self._sensor_name}"

    @property
    def name(self):
        return f"{DOMAIN}.{self._sensor_name}"

    @property
    def device_class(self):
        return "problem"

    @property
    def state(self):
        data = self.coordinator.data
        if data is None or not data["warnings"]:
            return False
        return any(
            self._keyword in w["description"].lower()
            for w in data["warnings"]
        )


class ErieAnyWarningBinarySensor(Entity):
    """True when the warnings list is non-empty (any active warning)."""

    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id

    @property
    def unique_id(self):
        return f"{self._device_id}_any_warning"

    @property
    def name(self):
        return f"{DOMAIN}.any_warning"

    @property
    def device_class(self):
        return "problem"

    @property
    def state(self):
        data = self.coordinator.data
        if data is None:
            return False
        return bool(data["warnings"])


class ErieHolidayModeBinarySensor(Entity):
    """True when the softener is in holiday (bypass) mode."""

    def __init__(self, coordinator, device_id):
        self.coordinator = coordinator
        self._device_id = device_id

    @property
    def unique_id(self):
        return f"{self._device_id}_holiday_mode"

    @property
    def name(self):
        return f"{DOMAIN}.holiday_mode"

    @property
    def device_class(self):
        return "running"

    @property
    def state(self):
        data = self.coordinator.data
        if data is None:
            return False
        return bool(data.get("holiday_mode", False))
