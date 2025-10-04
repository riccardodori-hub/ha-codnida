"""Tests for the Codnida Camera integration."""
import logging
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path
import os
from datetime import datetime
import aiohttp
import tempfile

# Add custom_components to Python path
sys.path.append(str(Path(__file__).parent.parent))

from homeassistant.core import HomeAssistant
from homeassistant.components.camera import CameraEntityFeature
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)

from custom_components.codnida.camera import CodnidaCamera
from custom_components.codnida.const import DOMAIN, SERVICE_PTZ, SERVICE_PRESET

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

@pytest.fixture
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
async def hass(event_loop, config_dir):
    """Fixture to provide a test instance of Home Assistant."""
    hass = HomeAssistant(config_dir)
    await hass.async_start()
    yield hass
    await hass.async_stop()

@pytest.fixture
async def camera(hass):
    """Create a test camera instance."""
    camera = CodnidaCamera(
        hass=hass,
        name="Test Camera",
        host="192.168.1.100",
        port=80,
        username="admin",
        password="password"
    )
    async with aiohttp.ClientSession() as session:
        camera._session = session
        yield camera
        await session.close()

@pytest.mark.asyncio
async def test_camera_initialization(camera):
    """Test camera initialization."""
    assert camera.name == "Test Camera"
    assert camera.unique_id == "codnida_192.168.1.100_80"
    assert camera.available is True

@pytest.mark.asyncio
async def test_camera_stream_source(camera):
    """Test camera stream source URL."""
    stream_source = await camera.async_stream_source()
    assert stream_source == "rtsp://admin:password@192.168.1.100:80/11"

@pytest.mark.asyncio
async def test_camera_move_command(camera):
    """Test camera movement commands."""
    with patch.object(camera, '_send_command') as mock_command:
        await camera._move_camera("up")
        mock_command.assert_called_with("/cgi-bin/ptz?action=up")

@pytest.mark.asyncio
async def test_invalid_movement_command(camera):
    """Test invalid movement command."""
    with patch.object(camera, '_send_command') as mock_command:
        await camera._move_camera("invalid")
        mock_command.assert_not_called()

@pytest.mark.asyncio
async def test_camera_snapshot_error(camera):
    """Test camera snapshot with error response."""
    async with aiohttp.ClientSession() as session:
        camera._session = session
        with patch.object(session, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            image = await camera.camera_image()
            assert image is None

@pytest.mark.asyncio
async def test_camera_connection_error(camera):
    """Test camera behavior when connection fails."""
    with patch.object(camera, '_send_command', side_effect=aiohttp.ClientError):
        await camera._test_connection()
        assert camera.available is False

@pytest.mark.asyncio
async def test_camera_preset_limits(camera):
    """Test camera preset position limits."""
    with patch.object(camera, '_send_command') as mock_command:
        await camera._set_preset(0)  # Invalid preset
        mock_command.assert_not_called()
        
        await camera._set_preset(17)  # Invalid preset
        mock_command.assert_not_called()
        
        await camera._set_preset(1)  # Valid preset
        mock_command.assert_called_once_with("/cgi-bin/preset?action=set&preset=1")

@pytest.mark.asyncio
async def test_camera_snapshot_success(camera):
    """Test successful camera snapshot."""
    fake_image = b"fake_image_data"
    async with aiohttp.ClientSession() as session:
        camera._session = session
        with patch.object(session, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.read = AsyncMock(return_value=fake_image)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            image = await camera.camera_image()
            assert image == fake_image

@pytest.mark.asyncio
async def test_camera_turn_on_off_commands(camera):
    """Test camera power control commands."""
    with patch.object(camera, '_send_command') as mock_command:
        await camera.async_turn_on()
        mock_command.assert_called_with("/cgi-bin/power?action=on")
        
        await camera.async_turn_off()
        mock_command.assert_called_with("/cgi-bin/power?action=off")

@pytest.mark.asyncio
async def test_camera_send_command_network_error(camera):
    """Test camera command sending with network error."""
    with patch.object(camera._session, 'get', side_effect=aiohttp.ClientError):
        await camera._send_command("/test")
        assert not camera.available

@pytest.mark.asyncio
async def test_camera_send_command_timeout(camera):
    """Test camera command sending with timeout."""
    with patch.object(camera._session, 'get', side_effect=TimeoutError):
        await camera._send_command("/test")
        assert not camera.available

@pytest.mark.asyncio
async def test_camera_send_command_invalid_response(camera):
    """Test camera command with invalid response status."""
    async with aiohttp.ClientSession() as session:
        camera._session = session
        with patch.object(session, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 500
            mock_get.return_value.__aenter__.return_value = mock_response
            
            await camera._send_command("/test")
            assert not camera.available

@pytest.mark.asyncio
async def test_camera_cleanup(camera):
    """Test camera cleanup on removal."""
    with patch.object(camera._session, 'close') as mock_close:
        await camera.async_will_remove_from_hass()
        mock_close.assert_called_once()

@pytest.mark.asyncio
async def test_camera_supported_features(camera):
    """Test camera supported features."""
    expected_features = (
        CameraEntityFeature.STREAM | 
        CameraEntityFeature.ON_OFF
    )
    assert camera.supported_features == expected_features

@pytest.mark.asyncio
async def test_camera_ptz_all_directions(camera):
    """Test PTZ movement in all supported directions."""
    for direction in ["up", "down", "left", "right"]:
        with patch.object(camera, '_send_command') as mock_command:
            await camera._move_camera(direction)
            mock_command.assert_called_once_with(f"/cgi-bin/ptz?action={direction}")

@pytest.mark.asyncio
async def test_camera_connection_retry(camera):
    """Test camera connection retry behavior."""
    # First attempt fails
    with patch.object(camera, '_send_command', side_effect=aiohttp.ClientError):
        try:
            await camera._test_connection()
        except Exception:
            pass
        assert not camera.available
    
    # Second attempt succeeds
    with patch.object(camera, '_send_command') as mock_command:
        await camera._test_connection()
        mock_command.assert_called_once_with("/cgi-bin/status")
        assert camera.available