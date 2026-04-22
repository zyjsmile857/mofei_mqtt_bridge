"""Config flow for the Mofei MQTT Bridge integration."""

from __future__ import annotations

import asyncio
import contextlib

from homeassistant.components import mqtt
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_MAC,
    CONF_NAME,
    CONF_QOS,
    CONF_RETAIN,
    DEFAULT_NAME,
    DEFAULT_QOS,
    DEFAULT_RETAIN,
    DOMAIN,
)


async def async_discover_mac_from_mqtt(hass, timeout: float = 2.0) -> str:
    """Try to discover a device MAC from /ACS/# traffic."""
    loop = asyncio.get_running_loop()
    future: asyncio.Future[str] = loop.create_future()

    @callback
    def handle_message(msg: mqtt.ReceiveMessage) -> None:
        topic = getattr(msg, "topic", "") or ""
        topic = topic.lstrip("/")
        parts = topic.split("/")
        if len(parts) < 3 or parts[0] != "ACS":
            return

        topic_mac = parts[1].strip()
        if topic_mac and not future.done():
            future.set_result(topic_mac)

    unsub = await mqtt.async_subscribe(
        hass,
        "/ACS/#",
        handle_message,
        qos=0,
        encoding="utf-8",
    )

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except TimeoutError:
        return ""
    finally:
        with contextlib.suppress(Exception):
            unsub()


class MofeiMqttBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mofei MQTT Bridge."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mac = user_input[CONF_MAC].strip()
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or mac,
                data={
                    CONF_MAC: mac,
                    CONF_NAME: user_input.get(CONF_NAME) or DEFAULT_NAME,
                    CONF_QOS: user_input[CONF_QOS],
                    CONF_RETAIN: user_input[CONF_RETAIN],
                },
            )

        discovered_mac = await async_discover_mac_from_mqtt(self.hass)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC, default=discovered_mac): str,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_QOS, default=DEFAULT_QOS): vol.In([0, 1, 2]),
                    vol.Optional(CONF_RETAIN, default=DEFAULT_RETAIN): bool,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return MofeiMqttBridgeOptionsFlow(config_entry)


class MofeiMqttBridgeOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle the integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_QOS,
                        default=self.config_entry.options.get(
                            CONF_QOS,
                            self.config_entry.data.get(CONF_QOS, DEFAULT_QOS),
                        ),
                    ): vol.In([0, 1, 2]),
                    vol.Optional(
                        CONF_RETAIN,
                        default=self.config_entry.options.get(
                            CONF_RETAIN,
                            self.config_entry.data.get(CONF_RETAIN, DEFAULT_RETAIN),
                        ),
                    ): bool,
                }
            ),
        )
