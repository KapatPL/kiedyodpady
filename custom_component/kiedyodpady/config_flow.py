import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_LOCALITY_ID,
    CONF_STREET_ID,
    CONF_NUMBER,
    CONF_PROPERTY_TYPE,
    CONF_BUILDING_TYPE,
    CONF_ORIGIN,
    DEFAULT_ORIGIN,
    DEFAULT_PROPERTY_TYPE,
    DEFAULT_BUILDING_TYPE,
)

API_BASE = "https://api.kiedyodpady.pl"


class KiedyOdpadyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data = {}
        self._streets = []

    def _headers(self):
        origin = self._data[CONF_ORIGIN].rstrip("/")
        return {
            "Accept": "application/json",
            "Origin": origin,
            "Referer": f"{origin}/",
            "User-Agent": "Mozilla/5.0 HomeAssistant kiedyodpady custom integration",
        }

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            try:
                await self._fetch_streets()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_street()

        schema = vol.Schema({
            vol.Required(CONF_ORIGIN, default=DEFAULT_ORIGIN): str,
            vol.Required(CONF_LOCALITY_ID, default="0920404"): str,
            vol.Required(CONF_PROPERTY_TYPE, default=DEFAULT_PROPERTY_TYPE): str,
            vol.Required(CONF_BUILDING_TYPE, default=DEFAULT_BUILDING_TYPE): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_street(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_number()

        options = [
            {
                "value": street["id"],
                "label": street.get("extendedName") or street.get("name") or street["id"],
            }
            for street in self._streets
        ]

        schema = vol.Schema({
            vol.Required(CONF_STREET_ID): selector({
                "select": {
                    "options": options,
                    "mode": "dropdown",
                    "sort": True,
                }
            })
        })

        return self.async_show_form(
            step_id="street",
            data_schema=schema,
            errors={},
        )

    async def async_step_number(self, user_input=None):
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            await self.async_set_unique_id(
                f"{self._data[CONF_LOCALITY_ID]}-{self._data[CONF_STREET_ID]}-{self._data[CONF_NUMBER]}"
            )
            self._abort_if_unique_id_configured()

            street_name = self._get_selected_street_name()
            return self.async_create_entry(
                title=f"{street_name} {self._data[CONF_NUMBER]}",
                data=self._data,
            )

        try:
            numbers = await self._fetch_numbers()
        except Exception:
            errors["base"] = "cannot_connect"
            numbers = []

        options = [
            {
                "value": str(number),
                "label": str(number),
            }
            for number in numbers
        ]

        schema = vol.Schema({
            vol.Required(CONF_NUMBER): selector({
                "select": {
                    "options": options,
                    "mode": "dropdown",
                    "sort": False,
                }
            })
        })

        return self.async_show_form(
            step_id="number",
            data_schema=schema,
            errors=errors,
        )

    async def _fetch_streets(self):
        session = async_get_clientsession(self.hass)
        locality_id = self._data[CONF_LOCALITY_ID]

        url = f"{API_BASE}/public/territory/localities/{locality_id}/streets"

        async with session.get(url, headers=self._headers()) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Streets API error: {resp.status}")

            self._streets = await resp.json()

    async def _fetch_numbers(self):
        session = async_get_clientsession(self.hass)
        locality_id = self._data[CONF_LOCALITY_ID]
        street_id = self._data[CONF_STREET_ID]

        url = f"{API_BASE}/public/territory/localities/{locality_id}/addresses/{street_id}"

        async with session.get(url, headers=self._headers()) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Addresses API error: {resp.status}")

            return await resp.json()

    def _get_selected_street_name(self):
        street_id = self._data.get(CONF_STREET_ID)

        for street in self._streets:
            if street.get("id") == street_id:
                return street.get("extendedName") or street.get("name") or street_id

        return street_id