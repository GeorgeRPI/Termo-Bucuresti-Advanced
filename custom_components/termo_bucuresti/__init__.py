"""Termo Bucuresti Integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "termo_bucuresti"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    from homeassistant.config_entries import ConfigEntryNotReady
    
    try:
        await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)
        return True
    except Exception as e:
        raise ConfigEntryNotReady from e
