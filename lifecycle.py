from nekro_agent.api import core
from nekro_agent.api.schemas import AgentCtx

from . import plugin, runtime_diff_cache
from .matcher_cleanup import destroy_matcher


def _remove_command_matcher() -> None:
    try:
        from .commands import update_last_seen_matcher
    except (ImportError, AttributeError):
        return

    destroy_matcher(update_last_seen_matcher)


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
