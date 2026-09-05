from nekro_agent.api import core
from nekro_agent.api.schemas import AgentCtx

from . import plugin, runtime_diff_cache


def _remove_command_matcher() -> None:
    try:
        from nonebot.matcher import matchers
        from .commands import update_last_seen_matcher
    except (ImportError, AttributeError):
        return

    for priority, registered in list(matchers.items()):
        if isinstance(registered, set):
            registered.discard(update_last_seen_matcher)
            if not registered:
                matchers.pop(priority, None)
        elif isinstance(registered, list):
            remaining = [item for item in registered if item is not update_last_seen_matcher]
            if remaining:
                matchers[priority] = remaining
            else:
                matchers.pop(priority, None)
        elif isinstance(registered, tuple):
            remaining = tuple(item for item in registered if item is not update_last_seen_matcher)
            if remaining:
                matchers[priority] = remaining
            else:
                matchers.pop(priority, None)


@plugin.mount_prompt_inject_method(name="time_diff_context", description="注入时间差感知上下文")
async def inject_time_diff_prompt(_ctx: AgentCtx) -> str:
    prompt = runtime_diff_cache.pop(_ctx.chat_key, "")
    if prompt:
        core.logger.debug("[时间感知] 上下文注入成功")
    return prompt


@plugin.mount_cleanup_method()
async def cleanup_plugin() -> None:
    runtime_diff_cache.clear()
    _remove_command_matcher()
    core.logger.success("[时间感知] 清理完成")
