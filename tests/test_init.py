"""Tests for the Codnida Camera integration."""
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.codnida.const import DOMAIN, DEFAULT_PORT
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME


@pytest.mark.asyncio
async def test_setup_with_config_entry(hass):
    """Test setting up the Codnida Camera integration through config entry."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.1.100",
            CONF_USERNAME: "admin",
            CONF_PASSWORD: "password",
            CONF_PORT: DEFAULT_PORT,
            CONF_NAME: "Test Camera",
        },
    )

    config_entry.add_to_hass(hass)

    with patch("custom_components.codnida.camera.CodnidaCamera"):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert DOMAIN in hass.data