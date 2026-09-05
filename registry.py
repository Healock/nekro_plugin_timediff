from . import plugin
from .commands import update_last_seen_command
from .lifecycle import cleanup_plugin, inject_time_diff_prompt
from .tracking import track_user_message


plugin.mount_on_user_message()(track_user_message)

__all__ = [
    "cleanup_plugin",
    "inject_time_diff_prompt",
    "track_user_message",
    "update_last_seen_command",
]
