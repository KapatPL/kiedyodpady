import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_LOCALITY_ID,
    CONF_STREET_ID,
    CONF_NUMBER,
    CONF_PROPERTY_TYPE,
    CONF_BUILDING_TYPE,
    CONF_ORIGIN,
)


class KiedyOdpadyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_LOCALITY_ID]}-{user_input[CONF_STREET_ID]}-{user_input[CONF_NUMBER]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Kiedy Odpady {user_input[CONF_NUMBER]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_LOCALITY_ID): str,
            vol.Required(CONF_STREET_ID): str,
            vol.Required(CONF_NUMBER): str,
            vol.Required(CONF_PROPERTY_TYPE): str,
            vol.Required(CONF_BUILDING_TYPE): str,
            vol.Required(CONF_ORIGIN): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )