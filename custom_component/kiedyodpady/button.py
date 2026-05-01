from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def get_next_event(coordinator):
    if not coordinator.data:
        return None
    return coordinator.data[0]


class KiedyOdpadyCollectedButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = False
    _attr_name = "Śmieci odebrane"
    _attr_icon = "mdi:check-circle-outline"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_waste_collection_collected_button"

    async def async_press(self):
        event = get_next_event(self.coordinator)
        if not event:
            return

        new_options = dict(self.entry.options)
        new_options["collected_date"] = event["date"]

        self.hass.config_entries.async_update_entry(
            self.entry,
            options=new_options,
        )

        self.coordinator.async_update_listeners()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KiedyOdpadyCollectedButton(coordinator, entry)])
