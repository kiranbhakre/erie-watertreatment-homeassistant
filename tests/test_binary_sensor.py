from unittest.mock import MagicMock

from erie_watertreatment.binary_sensor import ErieLowSaltBinarySensor


def _sensor(warnings):
    c = MagicMock()
    c.data = {"warnings": warnings}
    return ErieLowSaltBinarySensor(c)


def test_low_salt_true_when_salt_in_description():
    assert _sensor([{"description": "Low Salt Level"}]).state is True


def test_low_salt_false_when_no_salt_in_description():
    assert _sensor([{"description": "Filter Replacement Needed"}]).state is False


def test_low_salt_false_when_no_warnings():
    assert _sensor([]).state is False


def test_low_salt_false_when_data_is_none():
    c = MagicMock()
    c.data = None
    assert ErieLowSaltBinarySensor(c).state is False


def test_device_class_is_problem():
    assert _sensor([]).device_class == "problem"
