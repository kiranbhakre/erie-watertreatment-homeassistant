from unittest.mock import MagicMock

import pytest

from erie_watertreatment.sensor import (
    ErieStatusSensor,
    ErieVolumeIncreaseSensor,
    ErieWarning,
    ErieWaterConsumptionSensor,
    ErieWaterFlowRateSensor,
)


_BASE_DATA = {
    "last_regeneration": "2024-01-01T10:00:00",
    "nr_regenerations": "42",
    "last_maintenance": "2023-06-01",
    "total_volume": "5000",
    "warnings": [],
}


def _coordinator(data=None):
    c = MagicMock()
    c.data = dict(_BASE_DATA) if data is None else data
    return c


# ---------------------------------------------------------------------------
# ErieWaterConsumptionSensor (Energy Dashboard)
# ---------------------------------------------------------------------------

def test_water_consumption_native_value():
    sensor = ErieWaterConsumptionSensor(_coordinator(), "device_123")
    assert sensor.native_value == 5000


def test_water_consumption_none_when_no_data():
    c = MagicMock()
    c.data = None
    assert ErieWaterConsumptionSensor(c, "device_123").native_value is None


def test_water_consumption_unique_id():
    sensor = ErieWaterConsumptionSensor(_coordinator(), "device_123")
    assert sensor.unique_id == "device_123_water_consumption"


def test_water_consumption_device_class():
    sensor = ErieWaterConsumptionSensor(_coordinator(), "device_123")
    assert sensor.device_class == "water"


def test_water_consumption_state_class():
    sensor = ErieWaterConsumptionSensor(_coordinator(), "device_123")
    assert sensor.state_class == "total_increasing"


def test_water_consumption_unit():
    sensor = ErieWaterConsumptionSensor(_coordinator(), "device_123")
    assert sensor.native_unit_of_measurement == "L"


# ---------------------------------------------------------------------------
# ErieWaterFlowRateSensor (normal sensor, L/h)
# ---------------------------------------------------------------------------

def _flow_rate_sensor(new_total, old_total_state):
    coordinator = _coordinator({"total_volume": str(new_total)})
    mock_hass = MagicMock()
    if old_total_state is not None:
        old = MagicMock()
        old.state = str(old_total_state)
        mock_hass.states.get.return_value = old
    else:
        mock_hass.states.get.return_value = None
    return ErieWaterFlowRateSensor(mock_hass, coordinator, "device_123")


def test_flow_rate_calculates_litres_per_hour():
    # delta=10 L over 120 s → 10 * (3600/120) = 300 L/h
    assert _flow_rate_sensor(5010, 5000).native_value == 300.0


def test_flow_rate_zero_on_first_run():
    assert _flow_rate_sensor(5000, None).native_value == 0


def test_flow_rate_zero_when_no_coordinator_data():
    c = MagicMock()
    c.data = None
    sensor = ErieWaterFlowRateSensor(MagicMock(), c, "device_123")
    assert sensor.native_value == 0


def test_flow_rate_never_negative():
    # old > new should not produce negative rate
    assert _flow_rate_sensor(5000, 5010).native_value == 0


def test_flow_rate_unique_id():
    assert _flow_rate_sensor(0, 0).unique_id == "device_123_water_flow_rate"


def test_flow_rate_unit():
    assert _flow_rate_sensor(0, 0).native_unit_of_measurement == "L/h"


def test_flow_rate_state_class():
    assert _flow_rate_sensor(0, 0).state_class == "measurement"


# ---------------------------------------------------------------------------
# ErieStatusSensor
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("info_type,expected", [
    ("last_regeneration", "2024-01-01T10:00:00"),
    ("nr_regenerations", "42"),
    ("last_maintenance", "2023-06-01"),
    ("total_volume", "5000"),
])
def test_status_sensor_state(info_type, expected):
    assert ErieStatusSensor(_coordinator(), info_type, "").state == expected


def test_status_sensor_none_when_no_data():
    c = MagicMock()
    c.data = None
    assert ErieStatusSensor(c, "last_regeneration", "").state is None


def test_status_sensor_volume_unit():
    assert ErieStatusSensor(_coordinator(), "total_volume", "L").unit_of_measurement == "L"


def test_status_sensor_empty_unit():
    assert ErieStatusSensor(_coordinator(), "nr_regenerations", "").unit_of_measurement == ""


# ---------------------------------------------------------------------------
# ErieVolumeIncreaseSensor
# ---------------------------------------------------------------------------

def _flow_sensor(current_volume, old_state_value):
    coordinator = _coordinator({"total_volume": str(current_volume)})
    mock_hass = MagicMock()
    if old_state_value is not None:
        old = MagicMock()
        old.state = str(old_state_value)
        mock_hass.states.get.return_value = old
    else:
        mock_hass.states.get.return_value = None
    return ErieVolumeIncreaseSensor(mock_hass, coordinator, "total_volume", "flow", "L")


def test_flow_sensor_calculates_delta():
    assert _flow_sensor(6000, 5000).state == 1000


def test_flow_sensor_returns_zero_on_first_run():
    assert _flow_sensor(5000, None).state == 0


def test_flow_sensor_returns_zero_when_no_coordinator_data():
    c = MagicMock()
    c.data = None
    sensor = ErieVolumeIncreaseSensor(MagicMock(), c, "total_volume", "flow", "L")
    assert sensor.state == 0


def test_flow_sensor_state_class():
    # delta sensor fluctuates — measurement is the correct state class
    assert _flow_sensor(1000, 0).state_class == "measurement"


def test_flow_sensor_unit():
    assert _flow_sensor(1000, 0).unit_of_measurement == "L"


# ---------------------------------------------------------------------------
# ErieWarning
# ---------------------------------------------------------------------------

def test_warnings_sensor_formats_multiple_warnings():
    data = {**_BASE_DATA, "warnings": [{"description": "Low Salt"}, {"description": "Filter"}]}
    assert ErieWarning(_coordinator(data)).state == "⚠️ Low Salt\n⚠️ Filter\n"


def test_warnings_sensor_none_when_empty():
    data = {**_BASE_DATA, "warnings": []}
    assert ErieWarning(_coordinator(data)).state is None


def test_warnings_sensor_none_when_no_data():
    c = MagicMock()
    c.data = None
    assert ErieWarning(c).state is None
