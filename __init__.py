from typing import Dict

from pydantic import Field

from nekro_agent.api.plugin import ConfigBase, NekroPlugin


plugin = NekroPlugin(
    name="Agent 时间感知与跨会话联动",
    module_name="nekro_plugin_timediff",
    description="提供温和的时间差感知，保留近期活跃事实并以轻量背景呈现时间间隔。",
    version="1.0.2",
    author="Healock",
    url="https://github.com/Healock/nekro_plugin_timediff",
    support_adapter=["onebot_v11"],
)


@plugin.mount_config()
class TimeDiffConfig(ConfigBase):
    notice_threshold_minutes: int = Field(default=30, title="【感知】最小触发阈值（分钟）")
    blame_threshold_hours: int = Field(default=4, title="【显著】长时段阈值（小时）")
    jealousy_window_minutes: int = Field(
        default=60,
        title="【短期】活跃判定窗口（分钟）",
        description="日常对话中，用户最近一段时间内活跃过时，仅作为近期活跃差异背景。",
    )
    abandon_days_threshold: int = Field(default=3, title="【失联】长期失联阈值（天）")
    abandon_active_window_minutes: int = Field(
        default=1440,
        title="【长期】回归判定窗口（分钟）",
        description="长期失联后，仅提示回归前一段时间内的活跃事实。",
    )
    debug_log: bool = Field(default=True, title="开启调试日志")


STORE_SCOPE = "timediff_global_scope"
STORE_KEY_NAME = "interaction_data_v2"
runtime_diff_cache: Dict[str, str] = {}

config = plugin.get_config(TimeDiffConfig)

# 注册回调、命令和清理逻辑。导入放在配置实例之后，避免循环导入。
from . import registry as _registry  # noqa: E402,F401
from .lifecycle import cleanup_plugin, inject_time_diff_prompt
from .prompt import generate_complex_prompt
from .tracking import track_user_message

track_and_analyze = track_user_message


__all__ = [
    "TimeDiffConfig",
    "cleanup_plugin",
    "config",
    "generate_complex_prompt",
    "inject_time_diff_prompt",
    "plugin",
    "track_and_analyze",
    "track_user_message",
]
