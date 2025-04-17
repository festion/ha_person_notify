"""The Person-Based Notification System integration."""
import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN, 
    CONF_PERSON,
    CONF_SEVERITY,
    CONF_TITLE,
    CONF_MESSAGE,
    SERVICE_NOTIFY_PERSON,
    SEVERITIES,
)
from .service import async_setup_services

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Person-Based Notification System component."""
    hass.data.setdefault(DOMAIN, {})
    
    # Register services
    await async_setup_services(hass)
    
    return True