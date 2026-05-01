from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_LOCALITY_NAME,
    CONF_ORIGIN,
    CONF_STREET_ID,
    CONF_STREET_NAME,
    CONF_NUMBER,
)


def get_next_event(coordinator, entry: ConfigEntry, include_collected: bool = False):
    if not coordinator.data:
        return None

    collected_date = entry.options.get("collected_date")

    for event in coordinator.data:
        if include_collected or event["date"] != collected_date:
            return event

    return None


class KiedyOdpadyEntity(CoordinatorEntity):
    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self):
        address = self.entry.data.get(CONF_NUMBER) or ""
        street_id = self.entry.data.get(CONF_STREET_ID)
        street_name = self.entry.data.get(CONF_STREET_NAME)
        locality_name = self.entry.data.get(CONF_LOCALITY_NAME)

        if street_name:
            device_name = f"Kiedy Odpady {street_name} {address}".strip()
        else:
            device_name = f"Kiedy Odpady {self.entry.title}".strip()

        return {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": device_name,
            "manufacturer": "kiedyodpady.pl",
            "model": locality_name or "Harmonogram odbioru odpadów",
            "configuration_url": self.entry.data.get(CONF_ORIGIN),
            "suggested_area": "Odpady",
            "sw_version": "0.1.0",
            "serial_number": f"{street_id}-{address}",
        }
