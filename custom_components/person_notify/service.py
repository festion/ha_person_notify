"""Services for the Person-Based Notification System integration."""
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from .const import (
    DOMAIN,
    CONF_PERSON,
    CONF_SEVERITY,
    CONF_TITLE,
    CONF_MESSAGE,
    SERVICE_NOTIFY_PERSON,
    SEVERITIES,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PERSON): cv.string,
        vol.Required(CONF_SEVERITY): vol.In(SEVERITIES),
        vol.Required(CONF_TITLE): cv.string,
        vol.Required(CONF_MESSAGE): cv.string,
    }
)

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the Person-Based Notification System integration."""
    
    async def handle_notify_person(call: ServiceCall) -> None:
        """Handle the notify_person service call."""
        person = call.data[CONF_PERSON]
        severity = call.data[CONF_SEVERITY]
        title = call.data[CONF_TITLE]
        message = call.data[CONF_MESSAGE]
        
        # In a full implementation, this would get user preferences and route notifications
        _LOGGER.info(
            "Notification for %s: [%s] %s - %s", 
            person.title(), 
            severity.upper(), 
            title, 
            message
        )
        
        # TODO: Implement the full routing logic based on user preferences
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_NOTIFY_PERSON,
        handle_notify_person,
        schema=SERVICE_SCHEMA,
    )