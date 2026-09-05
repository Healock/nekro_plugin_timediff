from datetime import datetime

from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from nekro_agent.adapters.onebot_v11.matchers.command import (
    LegacyCommandFinished,
    command_guard,
    finish_with,
    on_command,
)
from nekro_agent.api import core

from . import STORE_KEY_NAME, STORE_SCOPE, plugin, runtime_diff_cache
from .storage import save_state


update_last_seen_matcher = on_command("update_last_seen", priority=1, block=True)


@update_last_seen_matcher.handle()
async def update_last_seen_command(
    matcher: Matcher,
    event: MessageEvent,
    bot: Bot,
    arg: Message = CommandArg(),
) -> None:
    _, command_text, chat_key, _ = await command_guard(event, bot, arg, matcher)
    if not command_text:
        await finish_with(matcher, message="参数缺失。")
        return

    try:
        parts = command_text.split()
        target_user = parts[0]
        interaction_ts: float
        active_ts: float
        if len(parts) == 3:
            parsed = datetime.strptime(f"{parts[1]} {parts[2]}", "%Y-%m-%d %H:%M:%S")
            interaction_ts = active_ts = parsed.timestamp()
            description = f"同步重置：{parts[1]} {parts[2]}"
        elif len(parts) == 5:
            interaction_text = f"{parts[1]} {parts[2]}"
            active_text = f"{parts[3]} {parts[4]}"
            interaction_ts = datetime.strptime(interaction_text, "%Y-%m-%d %H:%M:%S").timestamp()
            active_ts = datetime.strptime(active_text, "%Y-%m-%d %H:%M:%S").timestamp()
            description = f"交互：{interaction_text}｜活跃：{active_text}"
        else:
            await finish_with(matcher, message="格式错误。")
            return

        await save_state(
            plugin.store,
            STORE_SCOPE,
            STORE_KEY_NAME,
            target_user,
            interaction_ts,
            active_ts,
            modified_by=f"admin_cmd_{event.user_id}",
        )
        runtime_diff_cache.pop(chat_key, None)
        core.logger.success(f"[时间感知] 管理员修正｜用户：{target_user}｜{description}")
        await finish_with(matcher, message=f"数据已更新。\n用户：{target_user}\n{description}")
    except ValueError:
        await finish_with(matcher, message="时间格式解析失败。")
    except (FinishedException, LegacyCommandFinished):
        raise
    except Exception as exc:
        core.logger.exception(f"[时间感知] 命令异常：{exc}")
        await finish_with(matcher, message="命令执行失败。")
