"""Support for Codnida IP Cameras."""
from __future__ import annotations

import logging
import asyncio
from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_platform

from .const import (
    DOMAIN,
    SERVICE_PTZ,
    SERVICE_PRESET,
    ATTR_PRESET,
    ATTR_MOVEMENT,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Codnida Camera based on a config entry."""
    camera = CodnidaCamera(
        entry.data[CONF_NAME] if CONF_NAME in entry.data else None,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    async_add_entities([camera])

    # Register services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_PTZ,
        {
            vol.Required(ATTR_MOVEMENT): vol.In(["up", "down", "left", "right"]),
        },
        "async_ptz_control"
    )

    platform.async_register_entity_service(
        SERVICE_PRESET,
        {
            vol.Required(ATTR_PRESET): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
        },
        "async_set_preset"
    )

class CodnidaCamera(Camera):
    """An implementation of a Codnida IP camera."""

    def __init__(
        self,
        name,
        host,
        port,
        username,
        password,
    ):
        """Initialize a Codnida camera."""
        super().__init__()

        self._attr_name = name
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._attr_supported_features = (
            CameraEntityFeature.STREAM | CameraEntityFeature.ON_OFF
        )

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        # TODO: Implement image capture
        pass

    async def async_stream_source(self) -> str | None:
        """Return the source of the stream."""
        # TODO: Return RTSP stream URL
        return f"rtsp://{self._username}:{self._password}@{self._host}:{self._port}/stream1"

    async def async_ptz_control(self, movement: str) -> None:
        """Move camera."""
        # TODO: Implement PTZ control
        _LOGGER.debug("PTZ control: %s", movement)

    async def async_set_preset(self, preset: int) -> None:
        """Set preset position."""
        # TODO: Implement preset control
        _LOGGER.debug("Setting preset: %s", preset)