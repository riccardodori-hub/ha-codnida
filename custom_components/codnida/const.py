"""Constants for the Codnida Camera integration."""

DOMAIN = "codnida"

# Config flow
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_PORT = "port"

# Defaults
DEFAULT_PORT = 8080
DEFAULT_NAME = "Codnida Camera"

# Platform
PLATFORMS = ["camera"]

# Services
SERVICE_PTZ = "ptz"
SERVICE_PRESET = "preset"

# Attributes
ATTR_PRESET = "preset"
ATTR_MOVEMENT = "movement"