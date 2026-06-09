# Mofei MQTT Bridge

Home Assistant 自定义集成，用于把墨菲中控相关命令映射为可调用实体，并通过 MQTT 下发控制消息。

## 功能

- 通过配置的 MAC 自动拼接 `/ACS/<mac>/up` 与 `/ACS/<mac>/down` 主题
- 提供按钮实体，映射场景、影音、空调、灯光、KTV 等控制命令
- 支持场景名称持久化和前端卡片同步
- 提供 `mofei_mqtt_bridge.send_message` 服务

## 安装

### HACS（推荐）

1. 在 HACS 中搜索 `Mofei MQTT Bridge`
2. 安装后重启 Home Assistant

### 手动安装

将 `custom_components/mofei_mqtt_bridge` 复制到 Home Assistant 的 `custom_components` 目录下。

## 配置

安装后在 Home Assistant 中添加集成：

- MAC
- 名称
- QoS
- 是否 retain

## 搭配 UI

推荐与 `mofei_remote_hacs_ui` 卡片一起使用。
