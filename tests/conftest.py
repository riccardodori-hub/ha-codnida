"""Test fixtures for Codnida integration."""
import os
import tempfile
from unittest.mock import patch
import pytest

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(monkeypatch):
    """Enable custom integrations in Home Assistant."""
    monkeypatch.setenv("PYTEST_ENABLE_CUSTOM_INTEGRATIONS", "1")

@pytest.fixture
def hass_storage():
    """Fixture to provide a test storage directory."""
    with tempfile.TemporaryDirectory() as storage_dir:
        yield storage_dir

@pytest.fixture
async def hass(hass_storage):
    """Fixture to provide a test instance of Home Assistant."""
    from homeassistant.core import HomeAssistant

    hass = HomeAssistant(hass_storage)
    await hass.async_start()
    yield hass
    await hass.async_stop()