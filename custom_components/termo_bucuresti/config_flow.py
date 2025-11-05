"""Config flow for Termo Bucuresti."""
from homeassistant import config_entries
import voluptuous as vol

class ConfigFlow(config_entries.ConfigFlow, domain="termo_bucuresti"):
    """Config flow."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}
        
        if user_input is not None:
            await self.async_set_unique_id(
                f"termo_{user_input['strada'].lower().replace(' ', '_')}"
            )
            self._abort_if_unique_id_configured()
            
            return self.async_create_entry(
                title=f"Termo - {user_input['strada']}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("strada"): str,
        })
        
        return self.async_show_form(
            step_id="user", 
            data_schema=schema, 
            errors=errors
        )