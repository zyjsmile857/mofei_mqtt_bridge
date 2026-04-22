"""Button platform for the Mofei MQTT Bridge integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MofeiConfigEntry
from .commands import DOWNLINK_COMMANDS, CommandDefinition
from .entity import MofeiBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MofeiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up downlink buttons."""
    async_add_entities(
        MofeiCommandButton(entry, command) for command in DOWNLINK_COMMANDS
    )


class MofeiCommandButton(MofeiBaseEntity, ButtonEntity):
    """A button entity that publishes a fixed MQTT payload."""

    def __init__(self, entry: MofeiConfigEntry, command: CommandDefinition) -> None:
        """Initialize the button."""
        super().__init__(entry)
        self._command = command
        self._attr_name = command.name
        self._attr_icon = command.icon
        self._attr_unique_id = f"{entry.entry_id}_{command.key}"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the mapped command for easier debugging."""
        return {
            "payload": self._command.payload,
            "configured_mac": self.runtime_data.mac,
            "discovered_topic_mac": self.runtime_data.discovered_topic_mac or "",
            "topic_down": self.runtime_data.topic_down,
        }

    async def async_press(self) -> None:
        """Publish the command payload."""
        await self.runtime_data.async_publish(self._command.payload)
