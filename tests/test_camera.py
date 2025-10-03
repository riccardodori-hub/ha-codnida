"""Tests for the Codnida Camera platform."""
from unittest.mock import patch
import pytest

from homeassistant.components.camera import CameraEntityFeature
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME

from custom_components.codnida.camera import CodnidaCamera


@pytest.fixture
def camera():
    """Camera fixture."""
    return CodnidaCamera(
        name="Test Camera",
        host="192.168.1.100",
        port=80,
        username="admin",
        password="password",
    )

async def test_camera_stream_source(camera):
    """Test camera stream source."""
    stream_source = await camera.async_stream_source()
    assert stream_source == "rtsp://admin:password@192.168.1.100:80/stream1"

def test_camera_supported_features(camera):
    """Test camera supported features."""
    assert camera.supported_features == (
        CameraEntityFeature.STREAM | CameraEntityFeature.ON_OFF
    )

@pytest.mark.asyncio
async def test_camera_ptz_control(camera):
    """Test camera PTZ control."""
    with patch("logging.Logger.debug") as mock_debug:
        await camera.async_ptz_control("up")
        mock_debug.assert_called_once_with("PTZ control: up")

@pytest.mark.asyncio
async def test_camera_set_preset(camera):
    """Test camera preset control."""
    with patch("logging.Logger.debug") as mock_debug:
        await camera.async_set_preset(1)
        mock_debug.assert_called_once_with("Setting preset: 1")