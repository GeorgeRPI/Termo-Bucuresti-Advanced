"""Diagnostics support for Termo Bucuresti."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from typing import Any
import json

from .const import DOMAIN

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = {
        "config_entry": {
            "title": config_entry.title,
            "data": dict(config_entry.data),
            "options": dict(config_entry.options),
            "unique_id": config_entry.unique_id,
            "entry_id": config_entry.entry_id,
        },
        "integration_data": {},
        "entities": [],
        "system_info": {
            "homeassistant_version": str(hass.config.version),
            "integration_version": "2.0.0"
        }
    }
    
    # Get integration data if available
    if DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]:
        integration_data = hass.data[DOMAIN][config_entry.entry_id]
        data["integration_data"] = integration_data
    
    # Get entities information
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    termo_entities = [
        entity for entity in entity_registry.entities.values()
        if entity.config_entry_id == config_entry.entry_id
    ]
    
    for entity in termo_entities:
        state = hass.states.get(entity.entity_id)
        entity_data = {
            "entity_id": entity.entity_id,
            "name": entity.name,
            "unique_id": entity.unique_id,
            "disabled": entity.disabled,
            "platform": entity.platform,
        }
        
        if state:
            entity_data.update({
                "state": state.state,
                "attributes": dict(state.attributes),
                "last_updated": state.last_updated.isoformat(),
                "last_changed": state.last_changed.isoformat(),
            })
        
        data["entities"].append(entity_data)
    
    return data

async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    return {
        "config_entry": config_entry.entry_id,
        "device": {
            "identifiers": list(device.identifiers),
            "name": device.name,
            "model": device.model,
            "manufacturer": device.manufacturer,
            "sw_version": device.sw_version,
        }
    }
