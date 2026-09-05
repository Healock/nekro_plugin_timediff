import time

from nekro_agent.api import core
from nekro_agent.api.message import ChatMessage
from nekro_agent.api.schemas import AgentCtx

from . import STORE_KEY_NAME, STORE_SCOPE, config, plugin, runtime_diff_cache
from .analysis import analyze_gap
from .prompt import render_time_prompt
from .storage import load_state, save_state


async def track_user_message(_ctx: AgentCtx, message: ChatMessage) -> None:
    try:
        user_id = message.sender_id
        if not user_id:
            return

        current_ts = time.time()
        state = await load_state(plugin.store, STORE_SCOPE, STORE_KEY_NAME, user_id)
        if state is None or state.last_interaction_ts == 0:
            if config.debug_log:
                core.logger.info(f"[时间感知] 新用户：{user_id}")
            await save_state(plugin.store, STORE_SCOPE, STORE_KEY_NAME, user_id, current_ts, current_ts)
            return

        if message.is_tome:
            analysis = analyze_gap(state.last_interaction_ts, state.last_active_ts, current_ts, config)
            if analysis.interaction_minutes >= config.notice_threshold_minutes:
                runtime_diff_cache[_ctx.chat_key] = render_time_prompt(
                    state.last_interaction_ts, current_ts, analysis
                )
                if config.debug_log:
                    if analysis.is_long_absence:
                        status = "长期回归（近期活跃）" if analysis.has_recent_activity else "长期未互动"
                    elif analysis.is_long_gap:
                        status = "长间隔（近期活跃）" if analysis.has_recent_activity else "普通忙碌"
                    else:
                        status = "常规"
                    core.logger.success(
                        f"[时间感知] {status}｜间隔：{analysis.interaction_minutes}分钟｜活跃：{analysis.active_minutes}分钟前"
                    )
            await save_state(plugin.store, STORE_SCOPE, STORE_KEY_NAME, user_id, current_ts, current_ts)
            return

        if current_ts - state.last_active_ts > 60:
            await save_state(
                plugin.store,
                STORE_SCOPE,
                STORE_KEY_NAME,
                user_id,
                state.last_interaction_ts,
                current_ts,
            )
    except Exception as exc:
        core.logger.error(f"[时间感知] 逻辑异常：{exc}")
