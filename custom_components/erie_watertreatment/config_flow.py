"""Config flow for Erie Water Treatment IQ26 integration.

Presents a simple email + password form.  On submit it calls the ErieConnect
API (blocking I/O, run in executor), authenticates the user, selects the
first active device on the account, and stores the resulting auth tokens in
the config entry data so the integration never needs to prompt for credentials
again at runtime.
"""
import logging
from collections import OrderedDict
from typing import Dict

import voluptuous as vol

from homeassistant import config_entries, exceptions

from erie_connect.client import ErieConnect

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_ID,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_EMAIL,
    CONF_EXPIRY,
    CONF_PASSWORD,
    CONF_UID,
    DOMAIN,
    OPTION_EMAIL,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Erie Water Treatment IQ26."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step — show form, then validate credentials."""
        _LOGGER.debug(f"{DOMAIN}: async_step_user: {user_input}")

        errors = {}

        if user_input is None:
            # First load — show the blank form
            return await self._show_setup_form(user_input, None)

        email = user_input["email"]
        password = user_input["password"]

        _LOGGER.debug(f"{DOMAIN}: creating ErieConnect for {email}")
        self.api = ErieConnect(email, password)

        try:
            # Login and device selection are blocking — run in executor thread
            device_id = await self.hass.async_add_executor_job(
                _login_and_select_first_active_device, self.api
            )
        except InvalidData:
            errors["base"] = "missing_data"

        if errors:
            _LOGGER.warning(f"{DOMAIN}: config flow errors: {errors}")
            return await self._show_setup_form(user_input, errors)

        # Prevent duplicate config entries for the same physical device
        await self.async_set_unique_id(device_id, raise_on_progress=False)
        self._abort_if_unique_id_configured()

        # Store all auth tokens so async_setup_entry can reconstruct the API client
        config_data = {
            CONF_EMAIL:        email,
            CONF_PASSWORD:     password,
            CONF_ACCESS_TOKEN: self.api.auth.access_token,
            CONF_CLIENT_ID:    self.api.auth.client,
            CONF_UID:          self.api.auth.uid,
            CONF_EXPIRY:       self.api.auth.expiry,
            CONF_DEVICE_ID:    self.api.device.id,
            CONF_DEVICE_NAME:  self.api.device.name,
        }

        return self.async_create_entry(title=self.api.device.name or DOMAIN, data=config_data)

    async def _show_setup_form(self, user_input=None, errors=None):
        """Render the email + password form."""
        if not user_input:
            user_input = {}

        schema: Dict[str, type] = OrderedDict()
        schema["email"] = str
        schema["password"] = str

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(schema),
            errors=errors or {},
        )


def _login_and_select_first_active_device(api):
    """Authenticate with Erie Connect and select the first active device.

    This function performs blocking network I/O and must be called via
    hass.async_add_executor_job().  Raises InvalidData if login succeeds
    but no active device is returned.
    """
    _LOGGER.debug(f"{DOMAIN}: erie_connect.login()")
    api.login()

    _LOGGER.debug(f"{DOMAIN}: erie_connect.select_first_active_device()")
    api.select_first_active_device()

    if api.device is None or api.auth is None:
        raise InvalidData("Login succeeded but no active device was found.")

    return api.device.id


class InvalidData(exceptions.HomeAssistantError):
    """Raised when login succeeds but the API returns no usable device."""
