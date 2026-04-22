"""The Mofei MQTT Bridge integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import re
from typing import Any, Callable

from homeassistant.components import mqtt
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol
from homeassistant.util import dt as dt_util

from .const import (
    CONF_MAC,
    CONF_NAME,
    CONF_QOS,
    CONF_RETAIN,
    DOMAIN,
    PLATFORMS,
    SERVICE_SEND_MESSAGE,
    STORAGE_KEY_SCENE_LABELS,
    STORAGE_VERSION,
    WS_TYPE_GET_SCENE_LABELS,
    WS_TYPE_SET_SCENE_LABEL,
)

DATA_ENTRIES = "entries"
DATA_SCENE_LABEL_STORE = "scene_label_store"

LOGGER = logging.getLogger(__name__)


def normalize_payload(payload: str) -> str:
    """Normalize payload format by removing spaces and uppercasing hex commands."""
    return payload.replace(" ", "").upper()


def normalize_mac_token(value: str) -> str:
    """Normalize a MAC-like token for loose topic matching."""
    return re.sub(r"[^0-9A-Fa-f]", "", value or "").upper()


def format_downlink_payload(payload: str) -> str:
    """Wrap a command in the fixed MQTT JSON envelope."""
    return json.dumps(
        {
            "messageId": "12",
            "action": "scene",
            "data": {
                "channel": 1,
                "cmd": normalize_payload(payload),
            },
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


class SceneLabelStore:
    """Persisted scene label storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = Store[dict[str, dict[str, str]]](hass, STORAGE_VERSION, STORAGE_KEY_SCENE_LABELS)
        self._data: dict[str, dict[str, str]] = {}

    async def async_load(self) -> None:
        """Load persisted scene labels."""
        self._data = await self._store.async_load() or {}

    def get_labels(self, mac: str) -> dict[str, str]:
        """Return labels for one device mac."""
        return dict(self._data.get(mac, {}))

    async def async_set_label(self, mac: str, command: str, label: str) -> dict[str, str]:
        """Set or clear one label and persist it."""
        labels = dict(self._data.get(mac, {}))
        next_label = label.strip()

        if next_label:
            labels[command] = next_label
        else:
            labels.pop(command, None)

        if labels:
            self._data[mac] = labels
        else:
            self._data.pop(mac, None)

        await self._store.async_save(self._data)
        LOGGER.debug(
            "Saved scene label to store: mac=%s command=%s label=%s labels=%s",
            mac,
            command,
            next_label,
            labels,
        )
        return dict(labels)


@dataclass
class MofeiRuntimeData:
    """Runtime data for a single config entry."""

    hass: HomeAssistant
    mac: str
    qos: int
    retain: bool
    last_payload: str = ""
    last_topic: str = ""
    last_received_at: datetime | None = None
    discovered_topic_mac: str | None = None
    _listeners: list[Callable[[], None]] = field(default_factory=list)
    _unsub_mqtt: Callable[[], None] | None = None

    @property
    def topic_up(self) -> str:
        """Return the topic used to receive messages."""
        return f"/ACS/{self._resolved_topic_mac}/up"

    @property
    def topic_down(self) -> str:
        """Return the topic used to send messages."""
        return f"/ACS/{self._resolved_topic_mac}/down"

    @property
    def discovery_topic(self) -> str:
        """Return the wildcard topic used to discover the active device topic."""
        return "/ACS/#"

    @property
    def _resolved_topic_mac(self) -> str:
        """Return the discovered topic MAC when available."""
        return self.discovered_topic_mac or self.mac

    @callback
    def register_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a listener for state changes."""
        self._listeners.append(listener)

        @callback
        def _remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove

    @callback
    def _notify_listeners(self) -> None:
        """Notify entities that new data is available."""
        for listener in tuple(self._listeners):
            listener()

    def _matches_device_topic(self, topic_mac: str) -> bool:
        """Return whether a topic MAC belongs to this configured bridge."""
        if self.discovered_topic_mac is not None:
            return topic_mac == self.discovered_topic_mac

        return normalize_mac_token(topic_mac) == normalize_mac_token(self.mac)

    @callback
    def _handle_message(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle a new MQTT message."""
        topic = getattr(msg, "topic", "") or ""
        topic = topic.lstrip("/")
        parts = topic.split("/")
        if len(parts) < 3 or parts[0] != "ACS":
            return

        topic_mac = parts[1]
        direction = parts[-1].lower()
        if direction == "down" or not self._matches_device_topic(topic_mac):
            return

        topic_changed = self.discovered_topic_mac != topic_mac
        if topic_changed:
            self.discovered_topic_mac = topic_mac
            LOGGER.debug(
                "Discovered MQTT topic MAC for configured mac=%s: %s",
                self.mac,
                topic_mac,
            )

        self.last_topic = topic
        self.last_payload = msg.payload
        self.last_received_at = dt_util.utcnow()
        self._notify_listeners()

    async def async_start(self) -> None:
        """Start the MQTT subscription and auto-discover the active topic MAC."""
        self._unsub_mqtt = await mqtt.async_subscribe(
            self.hass,
            self.discovery_topic,
            self._handle_message,
            qos=self.qos,
            encoding="utf-8",
        )
        LOGGER.debug(
            "Subscribed to %s for configured mac=%s; waiting for device traffic or heartbeat.",
            self.discovery_topic,
            self.mac,
        )

    async def async_stop(self) -> None:
        """Stop the MQTT subscription."""
        if self._unsub_mqtt is not None:
            self._unsub_mqtt()
            self._unsub_mqtt = None

    async def async_publish(self, payload: str) -> None:
        """Publish a payload to the configured downlink topic."""
        payload = format_downlink_payload(payload)
        await self.hass.services.async_call(
            mqtt.DOMAIN,
            mqtt.SERVICE_PUBLISH,
            {
                mqtt.ATTR_TOPIC: self.topic_down,
                mqtt.ATTR_PAYLOAD: payload,
                mqtt.ATTR_QOS: self.qos,
                mqtt.ATTR_RETAIN: self.retain,
            },
            blocking=True,
        )


MofeiConfigEntry = ConfigEntry[MofeiRuntimeData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from YAML."""
    hass.data.setdefault(DOMAIN, {DATA_ENTRIES: {}})
    scene_label_store = SceneLabelStore(hass)
    await scene_label_store.async_load()
    hass.data[DOMAIN][DATA_SCENE_LABEL_STORE] = scene_label_store

    async def async_handle_send_message(service_call) -> None:
        """Send a message through a configured bridge."""
        mac = service_call.data[CONF_MAC]
        payload = service_call.data["payload"]

        for runtime_data in hass.data[DOMAIN][DATA_ENTRIES].values():
            if runtime_data.mac == mac:
                await runtime_data.async_publish(payload)
                return

        raise vol.Invalid(f"No {DOMAIN} entry found for mac {mac}")

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_MESSAGE,
        async_handle_send_message,
        schema=vol.Schema(
            {
                vol.Required(CONF_MAC): cv.string,
                vol.Required("payload"): cv.string,
            }
        ),
    )

    @websocket_api.websocket_command(
        {
            vol.Required("type"): WS_TYPE_GET_SCENE_LABELS,
            vol.Required(CONF_MAC): cv.string,
        }
    )
    @callback
    def websocket_get_scene_labels(
        hass: HomeAssistant,
        connection: websocket_api.ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        """Return scene labels for a device."""
        store: SceneLabelStore = hass.data[DOMAIN][DATA_SCENE_LABEL_STORE]
        LOGGER.debug("Websocket get_scene_labels: mac=%s", msg[CONF_MAC])
        connection.send_result(msg["id"], {"labels": store.get_labels(msg[CONF_MAC])})

    @websocket_api.websocket_command(
        {
            vol.Required("type"): WS_TYPE_SET_SCENE_LABEL,
            vol.Required(CONF_MAC): cv.string,
            vol.Required("command"): cv.string,
            vol.Optional("label", default=""): cv.string,
        }
    )
    @websocket_api.async_response
    async def websocket_set_scene_label(
        hass: HomeAssistant,
        connection: websocket_api.ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        """Persist one scene label for a device."""
        store: SceneLabelStore = hass.data[DOMAIN][DATA_SCENE_LABEL_STORE]
        LOGGER.debug(
            "Websocket set_scene_label: mac=%s command=%s label=%s",
            msg[CONF_MAC],
            msg["command"],
            msg["label"],
        )
        labels = await store.async_set_label(msg[CONF_MAC], msg["command"], msg["label"])
        connection.send_result(msg["id"], {"labels": labels})

    websocket_api.async_register_command(hass, websocket_get_scene_labels)
    websocket_api.async_register_command(hass, websocket_set_scene_label)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: MofeiConfigEntry) -> bool:
    """Set up Mofei MQTT Bridge from a config entry."""
    runtime_data = MofeiRuntimeData(
        hass=hass,
        mac=entry.data[CONF_MAC],
        qos=entry.options.get(CONF_QOS, entry.data.get(CONF_QOS, 0)),
        retain=entry.options.get(CONF_RETAIN, entry.data.get(CONF_RETAIN, False)),
    )
    await runtime_data.async_start()
    hass.data[DOMAIN][DATA_ENTRIES][entry.entry_id] = runtime_data
    entry.runtime_data = runtime_data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MofeiConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.async_stop()
        hass.data[DOMAIN][DATA_ENTRIES].pop(entry.entry_id, None)
    return unload_ok
