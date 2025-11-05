"""Termo Bucuresti Advanced Integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Termo Bucuresti component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Termo Bucuresti from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store configuration
    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "options": entry.options
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup services
    await _setup_services(hass)
    
    # Add update listener
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    
    _LOGGER.info(
        "Termo Bucuresti Advanced configurat cu succes pentru strada: %s",
        entry.data.get("strada", "Necunoscută")
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    await _unload_services(hass)
    
    return unload_ok

async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def _setup_services(hass: HomeAssistant):
    """Set up services for Termo Bucuresti."""
    
    async def async_handle_refresh_data(call):
        """Handle refresh data service call."""
        _LOGGER.info("Reîmprospătare manuală a datelor solicitată")
        
        # Trigger update for all Termo Bucuresti entities
        for entry_id in hass.data[DOMAIN]:
            # This would trigger entity updates
            pass
            
    async def async_handle_get_report(call):
        """Handle get report service call."""
        from datetime import datetime, timedelta
        
        period = call.data.get("period", "7days")
        _LOGGER.info("Generare raport pentru perioada: %s", period)
        
        # Calculate period
        if period == "1day":
            days = 1
        elif period == "7days":
            days = 7
        else:  # 30days
            days = 30
            
        report_data = {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_interruptions": 0,
                "services_affected": [],
                "average_duration": "N/A"
            }
        }
        
        # In a real implementation, this would collect data from all entities
        hass.bus.async_fire("termo_bucuresti_report_generated", report_data)
        
    async def async_handle_export_data(call):
        """Handle export data service call."""
        export_format = call.data.get("format", "json")
        _LOGGER.info("Export date în format: %s", export_format)
        
        # Export logic would go here
        
    # Register services
    hass.services.async_register(DOMAIN, "refresh_data", async_handle_refresh_data)
    hass.services.async_register(DOMAIN, "get_report", async_handle_get_report)
    hass.services.async_register(DOMAIN, "export_data", async_handle_export_data)

async def _unload_services(hass: HomeAssistant):
    """Unload services for Termo Bucuresti."""
    hass.services.async_remove(DOMAIN, "refresh_data")
    hass.services.async_remove(DOMAIN, "get_report")
    hass.services.async_remove(DOMAIN, "export_data")
