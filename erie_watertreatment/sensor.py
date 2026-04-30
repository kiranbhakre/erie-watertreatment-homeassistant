"""Erie Water Treatment sensors."""
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfVolume
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import get_coordinator
from .const import (
    CONF_DEVICE_ID,
    COORDINATOR_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug(f"{DOMAIN}: sensor: async_setup_entry: {entry}")

    coordinator = await get_coordinator(hass)
    device_id = entry.data[CONF_DEVICE_ID]

    entities = [
        ErieWaterConsumptionSensor(coordinator, device_id),
        ErieWaterFlowRateSensor(hass, coordinator, device_id),
        ErieVolumeIncreaseSensor(hass, coordinator, "total_volume", "flow", "L"),
        ErieStatusSensor(coordinator, "last_regeneration", ""),
        ErieStatusSensor(coordinator, "nr_regenerations", ""),
        ErieStatusSensor(coordinator, "last_maintenance", ""),
        ErieStatusSensor(coordinator, "total_volume", "L"),
        ErieWarning(coordinator),
    ]
    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Energy Dashboard sensor — cumulative total (device_class=water)
# ---------------------------------------------------------------------------

class ErieWaterConsumptionSensor(SensorEntity):
    """Cumulative water consumption — compatible with HA Energy Dashboard."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS

    def __init__(self, coordinator, device_id):
        super().__init__()
        self.coordinator = coordinator
        self._device_id = device_id

    @property
    def unique_id(self):
        return f"{self._device_id}_water_consumption"

    @property
    def name(self):
        return "Erie Water Consumption"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return int(self.coordinator.data["total_volume"])

    async def async_update(self):
        await self.coordinator.async_request_refresh()


# ---------------------------------------------------------------------------
# Flow-rate sensor — instantaneous L/h (normal dashboard card)
# ---------------------------------------------------------------------------

class ErieWaterFlowRateSensor(SensorEntity):
    """Instantaneous water usage rate in L/h."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "L/h"
    _POLL_SECONDS = int(COORDINATOR_UPDATE_INTERVAL.total_seconds())

    def __init__(self, hass, coordinator, device_id):
        super().__init__()
        self.hass = hass
        self.coordinator = coordinator
        self._device_id = device_id

    @property
    def unique_id(self):
        return f"{self._device_id}_water_flow_rate"

    @property
    def name(self):
        return "Erie Water Flow Rate"

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return 0
        new_total = int(self.coordinator.data["total_volume"])
        old_state = self.hass.states.get(f"sensor.{DOMAIN}_total_volume")
        if old_state is None or old_state.state in ("unknown", "unavailable"):
            return 0
        try:
            old_total = int(old_state.state)
        except (ValueError, TypeError):
            return 0
        delta = max(0, new_total - old_total)
        return round(delta * (3600 / self._POLL_SECONDS), 1)

    async def async_update(self):
        await self.coordinator.async_request_refresh()


# ---------------------------------------------------------------------------
# Legacy sensors (plain Entity — kept for backward compatibility)
# ---------------------------------------------------------------------------

class ErieVolumeIncreaseSensor(Entity):
    """Delta volume sensor — difference since last poll."""

    def __init__(self, hass, coordinator, info_type, sensor_name, unit):
        self.hass = hass
        self.coordinator = coordinator
        self.info_type = info_type
        self.sensor_name = sensor_name
        self.unit = unit

    @property
    def name(self):
        return f"{DOMAIN}.{self.sensor_name}"

    @property
    def state(self):
        sensor_entity_id = f"sensor.{DOMAIN}_{self.info_type}"
        old_state = self.hass.states.get(sensor_entity_id)
        _LOGGER.debug(f"{sensor_entity_id}: data={self.coordinator.data} old={old_state}")
        if self.coordinator.data and self.info_type in self.coordinator.data and old_state:
            old_value = self._to_int(old_state.state)
            new_value = self._to_int(self.coordinator.data[self.info_type])
            return new_value - old_value
        return 0

    @property
    def unit_of_measurement(self):
        return self.unit

    @property
    def state_class(self):
        # Delta value — fluctuates up and down, so MEASUREMENT is correct
        return "measurement"

    def _to_int(self, value):
        if value is not None:
            return int(str(value).split()[0])
        return 0

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class ErieWarning(Entity):
    """Active warnings as a formatted string."""

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.info_type = "warnings"

    @property
    def name(self):
        return f"{DOMAIN}.{self.info_type}"

    @property
    def state(self):
        _LOGGER.debug(f"{DOMAIN}: sensor: state: {self.coordinator.data}")
        if self.coordinator.data is None:
            return None
        warning_string = "".join(
            f"⚠️ {w['description']}\n"
            for w in self.coordinator.data[self.info_type]
        )
        return warning_string or None


class ErieStatusSensor(Entity):
    """Read-only status value from the coordinator."""

    def __init__(self, coordinator, info_type, unit):
        self.coordinator = coordinator
        self.info_type = info_type
        self.unit = unit

    @property
    def name(self):
        return f"{DOMAIN}.{self.info_type}"

    @property
    def state(self):
        _LOGGER.debug(f"{DOMAIN}: sensor: state: {self.coordinator.data}")
        if self.coordinator.data is not None:
            return self.coordinator.data[self.info_type]
        return None

    @property
    def unit_of_measurement(self):
        return self.unit
