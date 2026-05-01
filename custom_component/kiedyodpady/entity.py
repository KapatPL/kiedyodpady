from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_ORIGIN, CONF_STREET_ID, CONF_NUMBER


class KiedyOdpadyEntity(CoordinatorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        address = self.entry.data.get(CONF_NUMBER)
        street_id = self.entry.data.get(CONF_STREET_ID)

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"Kiedy Odpady {address}",
            "manufacturer": "kiedyodpady.pl",
            "model": "Harmonogram odbioru odpadów",
            "configuration_url": self.entry.data.get(CONF_ORIGIN),
            "suggested_area": "Odpady",
            "sw_version": "0.1.0",
            "serial_number": f"{street_id}-{address}",
        }