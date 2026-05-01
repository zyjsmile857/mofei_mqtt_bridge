# Mofei MQTT Bridge

![Mofei MQTT Bridge](brands/mofei_mqtt_bridge/icon.png)

Mofei MQTT Bridge is a Home Assistant custom integration for mapping Mofei central-control commands to Home Assistant entities and MQTT messages.

## Features

- Builds MQTT topics from the configured MAC address, including `/ACS/<mac>/up` and `/ACS/<mac>/down`.
- Provides button entities for scene, media, facility, lighting, and KTV control commands.
- Stores scene names so they can stay synchronized with the Lovelace card.
- Provides the `mofei_mqtt_bridge.send_message` service for direct command publishing.

## Installation

### HACS

1. Open HACS.
2. Add this repository as a custom repository.
3. Select `Integration` as the category.
4. Install `Mofei MQTT Bridge`.
5. Restart Home Assistant.
6. Add the integration from **Settings > Devices & services**.

### Manual

Copy `custom_components/mofei_mqtt_bridge` into the `custom_components` directory in your Home Assistant configuration folder, then restart Home Assistant.

## Configuration

After installation, add the integration in Home Assistant and configure:

- MAC address
- Display name
- MQTT QoS
- MQTT retain setting

## Services

### `mofei_mqtt_bridge.send_message`

Publishes a control message to the configured MQTT topic.

Example:

```yaml
service: mofei_mqtt_bridge.send_message
data:
  mac: "001122334455"
  payload: "FE04D000"
```

## Recommended Card

This integration is designed to work with [Mofei Remote Card](https://github.com/zyjsmile857/mofei-remote-card).
