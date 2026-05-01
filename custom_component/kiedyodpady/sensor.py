from __future__ import annotations

from datetime import date, datetime, timedelta
import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_LOCALITY_ID,
    CONF_STREET_ID,
    CONF_NUMBER,
    CONF_PROPERTY_TYPE,
    CONF_BUILDING_TYPE,
    CONF_ORIGIN,
    WASTE_TYPES,
)

_LOGGER = logging.getLogger(__name__)

API_URL = "https://api.kiedyodpady.pl/public/schedules/find"
SCAN_INTERVAL = timedelta(hours=12)

WASTE_ICONS = {
    "Bio": "mdi:leaf",
    "Zielone": "mdi:tree-outline",
    "Zmieszane": "mdi:trash-can",
    "Metale i tworzywa sztuczne": "mdi:recycle",
    "Papier": "mdi:file-document-outline",
    "Szkło": "mdi:bottle-wine-outline",
}


def get_next_event(coordinator):
    if not coordinator.data:
        return None
    return coordinator.data[0]


def get_icon_for_types(types: list[str]) -> str:
    if not types:
        return "mdi:trash-can-outline"

    if len(types) == 1:
        return WASTE_ICONS.get(types[0], "mdi:trash-can-outline")

    return "mdi:recycle"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        KiedyOdpadyNextDateSensor(coordinator, entry),
        KiedyOdpadyDisplayDateSensor(coordinator, entry),
        KiedyOdpadyTypesSensor(coordinator, entry),
        KiedyOdpadyDaysUntilSensor(coordinator, entry),
    ])


class KiedyOdpadyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, session, config: dict):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.session = session
        self.config = config

    async def _async_update_data(self):
        today = date.today()
        to_date = today + timedelta(days=60)
        origin = self.config[CONF_ORIGIN].rstrip("/")

        payload = {
            "from": today.isoformat(),
            "to": to_date.isoformat(),
            "queries": [
                {
                    "localityId": self.config[CONF_LOCALITY_ID],
                    "streetId": self.config[CONF_STREET_ID],
                    "number": self.config[CONF_NUMBER],
                    "buildingType": self.config[CONF_BUILDING_TYPE],
                    "propertyType": self.config[CONF_PROPERTY_TYPE],
                }
            ],
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": origin,
            "Referer": f"{origin}/",
            "User-Agent": "Mozilla/5.0 HomeAssistant kiedyodpady custom integration",
        }

        async with self.session.post(API_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"KiedyOdpady API error {resp.status}: {text}")

            data = await resp.json()

        events_by_date: dict[str, list[str]] = {}

        for occurrence in data.get("occurrences", []):
            event_date = occurrence.get("when", "")[:10]
            waste_type_id = occurrence.get("what")
            waste_name = WASTE_TYPES.get(waste_type_id, waste_type_id)

            if event_date and waste_name:
                events_by_date.setdefault(event_date, []).append(waste_name)

        return [
            {
                "date": event_date,
                "types": sorted(set(types)),
            }
            for event_date, types in sorted(events_by_date.items())
        ]


class KiedyOdpadyNextDateSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Następny odbiór odpadów"
    _attr_icon = "mdi:calendar-clock"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: KiedyOdpadyCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_next_waste_collection_date"

    @property
    def native_value(self):
        event = get_next_event(self.coordinator)
        if not event:
            return None

        event_date = datetime.fromisoformat(event["date"])
        return event_date.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

    @property
    def extra_state_attributes(self):
        event = get_next_event(self.coordinator)
        if not event:
            return {}

        next_date = datetime.fromisoformat(event["date"]).date()

        return {
            "next_date": event["date"],
            "days_until": (next_date - date.today()).days,
            "next_types": event["types"],
            "next_types_text": ", ".join(event["types"]),
            "next_types_icons": [
                {
                    "name": waste_type,
                    "icon": WASTE_ICONS.get(waste_type, "mdi:trash-can-outline"),
                }
                for waste_type in event["types"]
            ],
            "schedule": self.coordinator.data,
        }


class KiedyOdpadyDisplayDateSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Data odbioru odpadów"
    _attr_icon = "mdi:calendar"

    def __init__(self, coordinator: KiedyOdpadyCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_waste_collection_display_date"

    @property
    def native_value(self):
        event = get_next_event(self.coordinator)
        if not event:
            return None

        return datetime.fromisoformat(event["date"]).strftime("%d.%m.%Y")


class KiedyOdpadyTypesSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Co odbierają odpady"

    def __init__(self, coordinator: KiedyOdpadyCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_waste_collection_types"

    @property
    def native_value(self):
        event = get_next_event(self.coordinator)
        if not event:
            return None

        return ", ".join(event["types"])

    @property
    def icon(self):
        event = get_next_event(self.coordinator)
        if not event:
            return "mdi:trash-can-outline"

        return get_icon_for_types(event["types"])

    @property
    def extra_state_attributes(self):
        event = get_next_event(self.coordinator)
        if not event:
            return {}

        return {
            "items": event["types"],
            "items_icons": [
                {
                    "name": waste_type,
                    "icon": WASTE_ICONS.get(waste_type, "mdi:trash-can-outline"),
                }
                for waste_type in event["types"]
            ],
        }


class KiedyOdpadyDaysUntilSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Dni do odbioru odpadów"
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator: KiedyOdpadyCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_waste_collection_days_until"

    @property
    def native_value(self):
        event = get_next_event(self.coordinator)
        if not event:
            return None

        next_date = datetime.fromisoformat(event["date"]).date()
        return (next_date - date.today()).days