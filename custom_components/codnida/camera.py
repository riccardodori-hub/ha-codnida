"""Support for Codnida IP Cameras."""
from __future__ import annotations
import logging
import aiohttp
from typing import Any
from asyncio import TimeoutError

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import PlatformNotReady

from .const import DOMAIN, SERVICE_PTZ, SERVICE_PRESET

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10
SUPPORTED_PTZ_COMMANDS = ["up", "down", "left", "right"]

class CodnidaCamera(Camera):
    """Codnida camera class."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        hass: HomeAssistant | None = None,
    ) -> None:
        """Initialize Codnida camera."""
        super().__init__()
        self.hass = hass
        self._attr_unique_id = f"codnida_{host}_{port}"
        self._name = name
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._available = True
        self._attr_supported_features = (
            CameraEntityFeature.STREAM | 
            CameraEntityFeature.ON_OFF
        )
        self._session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(username, password),
            timeout=aiohttp.ClientTimeout(total=10)
        )

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to hass."""
        await self._test_connection()

    async def async_will_remove_from_hass(self) -> None:
        """Close session when entity is being removed."""
        if self._session:
            await self._session.close()

    async def _test_connection(self) -> None:
        """Test if we can communicate with the camera."""
        try:
            await self._send_command("/cgi-bin/status")
            self._available = True
        except (TimeoutError, aiohttp.ClientError) as err:
            self._available = False
            raise PlatformNotReady(f"Cannot connect to {self._host}: {err}")

    async def async_stream_source(self) -> str:
        """Return the RTSP stream source."""
        return f"rtsp://{self._username}:{self._password}@{self._host}:{self._port}/11"

    async def _move_camera(self, direction: str) -> None:
        """Move camera in specified direction."""
        if direction not in SUPPORTED_PTZ_COMMANDS:
            _LOGGER.error("Unsupported PTZ command: %s", direction)
            return
        
        command = f"/cgi-bin/ptz?action={direction}"
        await self._send_command(command)

    async def _set_preset(self, preset: int) -> None:
        """Set camera preset position."""
        if not 1 <= preset <= 16:
            _LOGGER.error("Invalid preset number. Must be between 1 and 16")
            return
            
        command = f"/cgi-bin/preset?action=set&preset={preset}"
        await self._send_command(command)

    async def _send_command(self, command: str) -> None:
        """Send command to camera."""
        if not self._available:
            _LOGGER.error("Camera is not available")
            return

        url = f"http://{self._host}:{self._port}{command}"
        
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    self._available = False
                    _LOGGER.error(
                        "Camera command failed: %s (status=%d)",
                        command,
                        response.status
                    )
                    return
                
                response_text = await response.text()
                _LOGGER.debug("Command response: %s -> %s", command, response_text)
                
        except (TimeoutError, aiohttp.ClientError) as err:
            self._available = False
            _LOGGER.error("Failed to send command %s: %s", command, err)

    async def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        try:
            command = "/cgi-bin/snapshot"
            url = f"http://{self._host}:{self._port}{command}"
            
            async with self._session.get(url) as response:
                if response.status != 200:
                    _LOGGER.error("Failed to get snapshot, status: %s", response.status)
                    return None
                    
                return await response.read()
                
        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Failed to get snapshot: %s", err)
            return None

    async def async_ptz_control(self, direction: str) -> None:
        """Control PTZ movement."""
        await self._move_camera(direction)

    async def async_set_preset(self, preset: int) -> None:
        """Set preset position."""
        await self._set_preset(preset)

    async def async_turn_on(self) -> None:
        """Turn on camera."""
        await self._send_command("/cgi-bin/power?action=on")

    async def async_turn_off(self) -> None:
        """Turn off camera."""
        await self._send_command("/cgi-bin/power?action=off")

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def name(self) -> str:
        """Return the camera name."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._attr_unique_id

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