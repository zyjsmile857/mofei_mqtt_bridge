"""Sensor platform for the Mofei MQTT Bridge integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MofeiConfigEntry
from .entity import MofeiBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MofeiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the receive sensor."""
    async_add_entities([MofeiReceiveSensor(entry)])


class MofeiReceiveSensor(MofeiBaseEntity, SensorEntity):
    """Entity that exposes the latest received payload."""

    _attr_name = "Receive"
    _attr_icon = "mdi:message-arrow-left-outline"

    def __init__(self, entry: MofeiConfigEntry) -> None:
        """Initialize the receive sensor."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_receive"

    @property
    def native_value(self) -> str:
        """Return the latest received payload."""
        return self.runtime_data.last_payload

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return diagnostic details about the subscription."""
        attrs: dict[str, str] = {
            "configured_mac": self.runtime_data.mac,
            "discovered_topic_mac": self.runtime_data.discovered_topic_mac or "",
            "discovery_topic": self.runtime_data.discovery_topic,
            "topic_up": self.runtime_data.topic_up,
            "topic_down": self.runtime_data.topic_down,
        }
        if self.runtime_data.last_topic:
            attrs["last_topic"] = self.runtime_data.last_topic
        if self.runtime_data.last_received_at is not None:
            attrs["last_received_at"] = self.runtime_data.last_received_at.isoformat()
        return attrs
