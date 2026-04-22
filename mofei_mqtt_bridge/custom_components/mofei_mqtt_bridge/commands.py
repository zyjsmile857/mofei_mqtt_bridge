"""Static downlink command definitions for Mofei MQTT Bridge."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommandDefinition:
    """Describe a single button-driven MQTT downlink command."""

    key: str
    name: str
    payload: str
    icon: str = "mdi:gesture-tap-button"


def _build_light_channel_commands() -> list[CommandDefinition]:
    """Build on/off commands for light channels 9-14."""
    commands: list[CommandDefinition] = []
    for channel_number in range(9, 15):
        index = channel_number - 1
        channel_hex = f"{index:02X}"
        commands.append(
            CommandDefinition(
                key=f"light_channel_{channel_number}_on",
                name=f"灯光 通道{channel_number}开",
                payload=f"FE05D1{channel_hex}01",
                icon="mdi:lightbulb-on-outline",
            )
        )
        commands.append(
            CommandDefinition(
                key=f"light_channel_{channel_number}_off",
                name=f"灯光 通道{channel_number}关",
                payload=f"FE05D1{channel_hex}00",
                icon="mdi:lightbulb-off-outline",
            )
        )
    return commands


def _build_ac_temperature_commands() -> list[CommandDefinition]:
    """Build temperature commands for 18-30 degrees."""
    commands: list[CommandDefinition] = []
    for temperature in range(18, 31):
        icon = "mdi:thermometer"
        if temperature <= 20:
            icon = "mdi:thermometer-low"
        elif temperature >= 28:
            icon = "mdi:thermometer-high"

        commands.append(
            CommandDefinition(
                key=f"ac_temp_{temperature}",
                name=f"空调 {temperature}度",
                payload=f"FE07C001{temperature:02X}0004",
                icon=icon,
            )
        )
    return commands


DOWNLINK_COMMANDS: list[CommandDefinition] = [
    CommandDefinition("scene_cinema", "场景 影院模式", "FE04D000", "mdi:movie-open"),
    CommandDefinition("scene_ktv", "场景 KTV模式", "FE04D001", "mdi:microphone"),
    CommandDefinition("scene_game", "场景 游戏模式", "FE04D002", "mdi:controller-classic-outline"),
    CommandDefinition("scene_tv", "场景 电视模式", "FE04D003", "mdi:television"),
    CommandDefinition("scene_guest", "场景 会客模式", "FE04D004", "mdi:account-group-outline"),
    CommandDefinition("scene_leave", "场景 离开模式", "FE04D00D", "mdi:logout"),
    CommandDefinition("mood_dynamic", "氛围 动感", "FE04D0A0", "mdi:music-note"),
    CommandDefinition("mood_soft", "氛围 柔和", "FE04D0A1", "mdi:weather-sunset"),
    CommandDefinition("mood_bright", "氛围 明亮", "FE04D0A2", "mdi:white-balance-sunny"),
    CommandDefinition("mood_lyric", "氛围 抒情", "FE04D0A3", "mdi:heart-outline"),
    CommandDefinition("curtain_open", "窗帘 窗帘开", "FE05CF0101", "mdi:curtains"),
    CommandDefinition("curtain_close", "窗帘 窗帘关", "FE05CF0100", "mdi:curtains-closed"),
    CommandDefinition("curtain_stop", "窗帘 窗帘停", "FE05CF0102", "mdi:pause-circle-outline"),
    CommandDefinition("sheer_open", "窗帘 窗纱开", "FE05CF0201", "mdi:blinds-open"),
    CommandDefinition("sheer_close", "窗帘 窗纱关", "FE05CF0200", "mdi:blinds"),
    CommandDefinition("sheer_stop", "窗帘 窗纱停", "FE05CF0202", "mdi:pause-circle-outline"),
    CommandDefinition("curtain_all_open", "窗帘 全部开", "FE05CF0001", "mdi:curtains"),
    CommandDefinition("curtain_all_close", "窗帘 全部关", "FE05CF0000", "mdi:curtains-closed"),
    CommandDefinition("curtain_all_stop", "窗帘 全部停", "FE05CF0002", "mdi:pause-circle-outline"),
    CommandDefinition("ac_power_toggle", "空调 开关", "FE07C001160001", "mdi:power"),
    CommandDefinition("ac_mode_heat", "空调 制热", "FE07C001160002", "mdi:fire"),
    CommandDefinition("ac_mode_cool", "空调 制冷", "FE07C001160102", "mdi:snowflake"),
    CommandDefinition("ac_mode_fan", "空调 送风", "FE07C001160202", "mdi:fan"),
    CommandDefinition("ac_fan_low", "空调 低风", "FE07C001160003", "mdi:fan-speed-1"),
    CommandDefinition("ac_fan_medium", "空调 中风", "FE07C002160003", "mdi:fan-speed-2"),
    CommandDefinition("ac_fan_high", "空调 高风", "FE07C003160003", "mdi:fan-speed-3"),
    CommandDefinition("ac_fan_auto", "空调 自动风", "FE07C004160003", "mdi:fan-auto"),
    CommandDefinition("amp_open", "功放 功放开", "FE05C00101", "mdi:speaker"),
    CommandDefinition("amp_close", "功放 功放关", "FE05C00100", "mdi:speaker-off"),
    CommandDefinition("projector_open", "投影 投影开", "FE05C10101", "mdi:projector"),
    CommandDefinition("projector_close", "投影 投影关", "FE05C10100", "mdi:projector-off"),
    CommandDefinition("hdmi_1", "HDMI HDMI1", "FE05C20101", "mdi:video-input-hdmi"),
    CommandDefinition("hdmi_2", "HDMI HDMI2", "FE05C20102", "mdi:video-input-hdmi"),
    CommandDefinition("hdmi_3", "HDMI HDMI3", "FE05C20103", "mdi:video-input-hdmi"),
    CommandDefinition("hdmi_4", "HDMI HDMI4", "FE05C20104", "mdi:video-input-hdmi"),
    CommandDefinition("ktv_next_song", "KTV 切歌", "FE04B069", "mdi:skip-next"),
    CommandDefinition("ktv_original_vocal", "KTV 原伴唱", "FE04B070", "mdi:account-voice"),
    CommandDefinition("ktv_mute", "KTV 静音", "FE04B071", "mdi:volume-off"),
    CommandDefinition("ktv_music_up", "KTV 音乐大", "FE04B049", "mdi:volume-plus"),
    CommandDefinition("ktv_music_down", "KTV 音乐小", "FE04B041", "mdi:volume-minus"),
    CommandDefinition("ktv_replay", "KTV 重唱", "FE04B06C", "mdi:repeat"),
    CommandDefinition("ktv_play_pause", "KTV 播放暂停", "FE04B062", "mdi:play-pause"),
    CommandDefinition("ktv_cheer", "KTV 喝彩", "FE04B054", "mdi:party-popper"),
    CommandDefinition("ktv_boo", "KTV 倒彩", "FE04B05B", "mdi:thumb-down-outline"),
    CommandDefinition("ktv_mic_up", "KTV 麦克风大", "FE04B03F", "mdi:microphone-plus"),
    CommandDefinition("ktv_mic_down", "KTV 麦克风小", "FE04B037", "mdi:microphone-minus"),
    CommandDefinition("ktv_amp_up", "KTV 功放音量大", "FE04B038", "mdi:volume-plus"),
    CommandDefinition("ktv_amp_down", "KTV 功放音量小", "FE04B039", "mdi:volume-minus"),
    CommandDefinition("ktv_pitch_up", "KTV 音调升", "FE04B040", "mdi:arrow-up-bold"),
    CommandDefinition("ktv_pitch_down", "KTV 音调降", "FE04B050", "mdi:arrow-down-bold"),
    CommandDefinition("ktv_balance", "KTV 平衡调", "FE04B047", "mdi:scale-balance"),
    CommandDefinition("ktv_prank", "KTV 整蛊", "FE04B01C", "mdi:emoticon-excited-outline"),
    CommandDefinition("ktv_singer", "KTV 唱将", "FE04B032", "mdi:microphone-variant"),
    CommandDefinition("ktv_harmony", "KTV 和声", "FE04B021", "mdi:music-clef-treble"),
    CommandDefinition("ktv_funny", "KTV 搞怪", "FE04B023", "mdi:emoticon-outline"),
    CommandDefinition("media_power_off", "媒体 关机", "FE04C700", "mdi:power"),
    CommandDefinition("media_power_on", "媒体 开机", "FE04C701", "mdi:power-on"),
    CommandDefinition("media_volume_up", "媒体 音量加", "FE04C702", "mdi:volume-plus"),
    CommandDefinition("media_volume_down", "媒体 音量减", "FE04C703", "mdi:volume-minus"),
    CommandDefinition("media_mute", "媒体 静音", "FE04C704", "mdi:volume-off"),
    CommandDefinition("media_menu", "媒体 菜单", "FE04C705", "mdi:menu"),
    CommandDefinition("media_clear", "媒体 清除", "FE04C706", "mdi:backspace-outline"),
    CommandDefinition("media_home", "媒体 主页", "FE04C707", "mdi:home"),
    CommandDefinition("media_previous_page", "媒体 上一页", "FE04C708", "mdi:page-previous"),
    CommandDefinition("media_next_page", "媒体 下一页", "FE04C709", "mdi:page-next"),
    CommandDefinition("media_up", "媒体 方向上", "FE04C70A", "mdi:chevron-up"),
    CommandDefinition("media_down", "媒体 方向下", "FE04C70B", "mdi:chevron-down"),
    CommandDefinition("media_left", "媒体 方向左", "FE04C70C", "mdi:chevron-left"),
    CommandDefinition("media_right", "媒体 方向右", "FE04C70D", "mdi:chevron-right"),
    CommandDefinition("media_select", "媒体 选择", "FE04C70E", "mdi:checkbox-marked-circle-outline"),
    CommandDefinition("media_back", "媒体 返回", "FE04C70F", "mdi:keyboard-return"),
    CommandDefinition("media_play", "媒体 播放", "FE04C724", "mdi:play"),
    CommandDefinition("media_pause", "媒体 暂停", "FE04C725", "mdi:pause"),
    CommandDefinition("media_fast_forward", "媒体 快进", "FE04C712", "mdi:fast-forward"),
    CommandDefinition("media_rewind", "媒体 快退", "FE04C713", "mdi:rewind"),
    CommandDefinition("media_audio_track", "媒体 音轨", "FE04C714", "mdi:audio-track"),
    CommandDefinition("media_subtitle", "媒体 字幕", "FE04C715", "mdi:subtitles-outline"),
    CommandDefinition("media_repeat", "媒体 循环", "FE04C716", "mdi:repeat"),
    CommandDefinition("media_3d", "媒体 3D", "FE04C717", "mdi:video-3d"),
    CommandDefinition("media_shutdown", "媒体 关闭电源", "FE04C718", "mdi:power-standby"),
    CommandDefinition("media_output", "媒体 输出", "FE04C719", "mdi:export-variant"),
    CommandDefinition("media_digit_1", "媒体 数字1", "FE04C71A", "mdi:numeric-1-circle-outline"),
    CommandDefinition("media_digit_2", "媒体 数字2", "FE04C71B", "mdi:numeric-2-circle-outline"),
    CommandDefinition("media_digit_3", "媒体 数字3", "FE04C71C", "mdi:numeric-3-circle-outline"),
    CommandDefinition("media_digit_4", "媒体 数字4", "FE04C71D", "mdi:numeric-4-circle-outline"),
    CommandDefinition("media_digit_5", "媒体 数字5", "FE04C71E", "mdi:numeric-5-circle-outline"),
    CommandDefinition("media_digit_6", "媒体 数字6", "FE04C71F", "mdi:numeric-6-circle-outline"),
    CommandDefinition("media_digit_7", "媒体 数字7", "FE04C720", "mdi:numeric-7-circle-outline"),
    CommandDefinition("media_digit_8", "媒体 数字8", "FE04C721", "mdi:numeric-8-circle-outline"),
    CommandDefinition("media_digit_9", "媒体 数字9", "FE04C722", "mdi:numeric-9-circle-outline"),
    CommandDefinition("media_digit_10", "媒体 数字10", "FE04C723", "mdi:numeric-10-circle-outline"),
]

DOWNLINK_COMMANDS.extend(_build_light_channel_commands())
DOWNLINK_COMMANDS.extend(_build_ac_temperature_commands())

