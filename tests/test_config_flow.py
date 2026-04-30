from unittest.mock import MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import AbortFlow
from pytest_homeassistant_custom_component.common import MockConfigEntry

from erie_watertreatment.config_flow import (
    ConfigFlow,
    InvalidData,
    _login_and_select_first_active_device,
)
from erie_watertreatment.const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_ID,
    CONF_EMAIL,
    DOMAIN,
)


# ---------------------------------------------------------------------------
# Tests for the synchronous helper (no HA machinery required)
# ---------------------------------------------------------------------------

def test_login_selects_device_and_returns_id(mock_erie_api):
    device_id = _login_and_select_first_active_device(mock_erie_api)
    assert device_id == "device_123"
    mock_erie_api.login.assert_called_once()
    mock_erie_api.select_first_active_device.assert_called_once()


def test_login_raises_invalid_data_when_device_is_none():
    api = MagicMock()
    api.device = None
    with pytest.raises(InvalidData):
        _login_and_select_first_active_device(api)


def test_login_raises_invalid_data_when_auth_is_none():
    api = MagicMock()
    api.auth = None
    with pytest.raises(InvalidData):
        _login_and_select_first_active_device(api)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_flow(hass):
    flow = ConfigFlow()
    flow.hass = hass
    flow.handler = DOMAIN
    flow.context = {"source": config_entries.SOURCE_USER}
    flow._flow_id = "test_flow"
    return flow


# ---------------------------------------------------------------------------
# Tests for async config flow steps
# ---------------------------------------------------------------------------

async def test_step_user_no_input_shows_form(hass):
    flow = await _make_flow(hass)
    result = await flow.async_step_user(user_input=None)
    assert result["type"] == "form"
    assert result["step_id"] == "user"


async def test_step_user_valid_credentials_creates_entry(hass, mock_erie_api):
    with patch("erie_watertreatment.config_flow.ErieConnect", return_value=mock_erie_api):
        flow = await _make_flow(hass)
        result = await flow.async_step_user(
            user_input={"email": "test@example.com", "password": "secret"}
        )

    assert result["type"] == "create_entry"
    assert result["data"][CONF_EMAIL] == "test@example.com"
    assert result["data"][CONF_DEVICE_ID] == "device_123"
    assert result["data"][CONF_ACCESS_TOKEN] == "token"


async def test_step_user_missing_device_shows_error(hass):
    api = MagicMock()
    api.device = None

    with patch("erie_watertreatment.config_flow.ErieConnect", return_value=api):
        flow = await _make_flow(hass)
        result = await flow.async_step_user(
            user_input={"email": "test@example.com", "password": "bad"}
        )

    assert result["type"] == "form"
    assert result["errors"]["base"] == "missing_data"


async def test_step_user_duplicate_device_aborted(hass, mock_erie_api):
    existing = MockConfigEntry(domain=DOMAIN, unique_id="device_123")
    existing.add_to_hass(hass)

    with patch("erie_watertreatment.config_flow.ErieConnect", return_value=mock_erie_api):
        flow = await _make_flow(hass)
        with pytest.raises(AbortFlow) as exc_info:
            await flow.async_step_user(
                user_input={"email": "test@example.com", "password": "secret"}
            )

    assert exc_info.value.reason == "already_configured"
