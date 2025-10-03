"""Config flow for Codnida Camera integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

class CodnidaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Codnida Camera."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_USERNAME): str,
                        vol.Required(CONF_PASSWORD): str,
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                        vol.Optional(CONF_NAME): str,
                    }
                ),
            )

        # Test connection and device here before creating entry
        # TODO: Add device test/validation

        return self.async_create_entry(
            title=user_input.get(CONF_NAME, user_input[CONF_HOST]),
            data=user_input,
        )