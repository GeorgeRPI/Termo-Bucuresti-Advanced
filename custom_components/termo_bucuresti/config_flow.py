"""Config flow for Termo Bucuresti."""
from homeassistant import config_entries
import voluptuous as vol
from .const import (
    DOMAIN, CONF_STRADA, CONF_PUNCT_TERMIC, CONF_SECTOR, 
    CONF_UPDATE_INTERVAL, PUNCTE_TERMICE, SECTORI, DEFAULT_UPDATE_INTERVAL
)

class TermoBucurestiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Termo Bucuresti."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"Termo - {user_input[CONF_STRADA]}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required(CONF_STRADA): str,
            vol.Required(CONF_PUNCT_TERMIC, default="toate"): vol.In(PUNCTE_TERMICE),
            vol.Required(CONF_SECTOR, default="toate"): vol.In(SECTORI),
            vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=120)
            ),
        })

        return self.async_show_form(step_id="user", data_schema=schema)
