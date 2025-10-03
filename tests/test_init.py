"""Tests for Codnida Camera integration."""
from unittest.mock import patch

from homeassistant.setup import async_setup_component

from custom_components.codnida.const import DOMAIN


async def test_setup(hass):
    """Test setup of the integration."""
    with patch('custom_components.codnida.setup', return_value=True):
        assert await async_setup_component(hass, DOMAIN, {
            DOMAIN: {
                "host": "192.168.1.100",
                "username": "admin",
                "password": "password"
            }
        })
        await hass.async_block_till_done()