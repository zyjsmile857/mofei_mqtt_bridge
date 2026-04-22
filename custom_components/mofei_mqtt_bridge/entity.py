"""Shared entity support for Mofei MQTT Bridge."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from . import MofeiConfigEntry
from .const import CONF_NAME, DOMAIN


class MofeiBaseEntity(Entity):
    """Base entity for the integration."""

    _attr_has_entity_name = True

    def __init__(self, entry: MofeiConfigEntry) -> None:
        """Initialize the base entity."""
        self.entry = entry
        self.runtime_data = entry.runtime_data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Mofei",
            model="MQTT Bridge",
            name=entry.data.get(CONF_NAME, entry.title),
        )

    async def async_added_to_hass(self) -> None:
        """Register update callbacks."""
        self.async_on_remove(
            self.runtime_data.register_listener(self._handle_runtime_update)
        )

    def _handle_runtime_update(self) -> None:
        """Write state when the runtime data updates."""
        self.async_write_ha_state()
