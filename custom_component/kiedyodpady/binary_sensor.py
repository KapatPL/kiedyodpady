from __future__ import annotations

from datetime import datetime

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def get_next_event(coordinator):
    if not coordinator.data:
        return None
    return coordinator.data[0]


class KiedyOdpadySoonBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Odbiór odpadów wkrótce"
    _attr_icon = "mdi:trash-can-clock"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_waste_collection_soon"

    @property
    def is_on(self):
        event = get_next_event(self.coordinator)
        if not event:
            return False

        event_date = event["date"]
        days_until = (datetime.fromisoformat(event_date).date() - datetime.now().date()).days
        collected_date = self.entry.options.get("collected_date")

        return 0 <= days_until <= 2 and collected_date != event_date

    @property
    def extra_state_attributes(self):
        event = get_next_event(self.coordinator)
        if not event:
            return {}

        return {
            "next_date": event["date"],
            "next_types": event["types"],
            "next_types_text": ", ".join(event["types"]),
            "collected_date": self.entry.options.get("collected_date"),
        }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KiedyOdpadySoonBinarySensor(coordinator, entry)])