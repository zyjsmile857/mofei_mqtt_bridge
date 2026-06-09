"""Constants for the Mofei MQTT Bridge integration."""

DOMAIN = "mofei_mqtt_bridge"

SERVICE_SEND_MESSAGE = "send_message"
WS_TYPE_GET_SCENE_LABELS = "mofei_mqtt_bridge/get_scene_labels"
WS_TYPE_SET_SCENE_LABEL = "mofei_mqtt_bridge/set_scene_label"
STORAGE_KEY_SCENE_LABELS = "mofei_mqtt_bridge_scene_labels"
STORAGE_VERSION = 1

CONF_MAC = "mac"
CONF_NAME = "name"
CONF_QOS = "qos"
CONF_RETAIN = "retain"

DEFAULT_NAME = "Mofei MQTT Bridge"
DEFAULT_QOS = 0
DEFAULT_RETAIN = False

PLATFORMS = ["sensor", "text", "button"]
