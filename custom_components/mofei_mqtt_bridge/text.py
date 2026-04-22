"""Text platform for the Mofei MQTT Bridge integration."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MofeiConfigEntry
from . import normalize_payload
from .entity import MofeiBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MofeiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the send text entity."""
    async_add_entities([MofeiSendText(entry)])


class MofeiSendText(MofeiBaseEntity, TextEntity):
    """Text entity used to publish MQTT messages."""

    _attr_name = "Send"
    _attr_icon = "mdi:message-arrow-right-outline"
    _attr_native_max = 1024
    _attr_mode = TextMode.TEXT

    def __init__(self, entry: MofeiConfigEntry) -> None:
        """Initialize the send text entity."""
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_send"
        self._current_value = ""

    @property
    def native_value(self) -> str:
        """Return the current text value."""
        return self._current_value

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return publish details."""
        return {
            "configured_mac": self.runtime_data.mac,
            "discovered_topic_mac": self.runtime_data.discovered_topic_mac or "",
            "discovery_topic": self.runtime_data.discovery_topic,
            "topic_down": self.runtime_data.topic_down,
            "topic_up": self.runtime_data.topic_up,
        }

    async def async_set_value(self, value: str) -> None:
        """Publish the new value to MQTT."""
        self._current_value = normalize_payload(value)
        await self.runtime_data.async_publish(value)
        self.async_write_ha_state()
