from unittest.mock import MagicMock

import pytest

try:
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    _HA_FRAMEWORK = True
except ImportError:
    _HA_FRAMEWORK = False

from custom_components.erie_watertreatment.const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_EMAIL,
    CONF_EXPIRY,
    CONF_PASSWORD,
    CONF_UID,
    DOMAIN,
)


@pytest.fixture
def mock_erie_api():
    api = MagicMock()
    api.auth.access_token = "token"
    api.auth.client = "client_id"
    api.auth.uid = "uid123"
    api.auth.expiry = "2099-01-01"
    api.device.id = "device_123"
    api.device.name = "My Softener"
    api.info.return_value.content = {
        "last_regeneration": "2024-01-01",
        "nr_regenerations": "42",
        "last_maintenance": "2023-06-01",
        "total_volume": "5000 L",
    }
    api.dashboard.return_value.content = {
        "warnings": [{"description": "Low Salt Level"}]
    }
    return api


@pytest.fixture
def mock_config_entry():
    if not _HA_FRAMEWORK:
        pytest.skip("pytest-homeassistant-custom-component not installed")
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_EMAIL: "test@example.com",
            CONF_PASSWORD: "secret",
            CONF_ACCESS_TOKEN: "token",
            CONF_CLIENT_ID: "client_id",
            CONF_UID: "uid123",
            CONF_EXPIRY: "2099-01-01",
            CONF_DEVICE_ID: "device_123",
            CONF_DEVICE_NAME: "My Softener",
        },
    )
