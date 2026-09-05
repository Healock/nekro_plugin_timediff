from datetime import datetime

from .analysis import GapAnalysis, format_duration


def render_time_prompt(previous_ts: float, current_ts: float, analysis: GapAnalysis) -> str:
    context_notes = []
    if analysis.crossed_date:
        context_notes.append("跨越日期")
    if analysis.crossed_evening:
        context_notes.append("昼夜更替")
    context_suffix = f"（{'、'.join(context_notes)}）" if context_notes else ""

    if analysis.is_long_absence:
        if analysis.has_recent_activity:
            hint = "对话间隔较长，但用户近期有活跃记录，可自然承接久别重逢的语境。"
            activity = f"近期活跃：{analysis.active_minutes}分钟前。"
        else:
            hint = "这是一次较长的对话断层，可将本轮视为自然重启，语气保持柔和。"
            activity = "近期活跃：未检测到。"
    elif analysis.is_long_gap:
        if analysis.has_recent_activity:
            hint = "对话间隔与近期活跃并存，可作为轻量背景，默认保持温和自然。"
            activity = f"近期活跃：{analysis.active_minutes}分钟前。"
        else:
            hint = "对话出现自然中断，当前更适合作为新的开启。"
            activity = "近期活跃：未检测到。"
    else:
        hint = "保持对话连贯，注意这不是连续的即时对话。"
        activity = ""

    now_text = datetime.fromtimestamp(current_ts).strftime("%H:%M")
    lines = [
        "【时间感知】",
        f"时间间隔：{analysis.duration_text}{context_suffix}。",
        f"当前时间：{now_text}。",
    ]
    if activity:
        lines.append(activity)
    lines.append(f"语境提示：{hint}")
    return "\n" + "\n".join(lines) + "\n"


def generate_complex_prompt(
    last_ts: float,
    now_ts: float,
    diff_mins: int,
    is_abandonment: bool,
    is_critical_active: bool,
    is_long_gap: bool,
    active_gap: int,
) -> str:
    """兼容旧调用方的提示词入口。"""
    previous_dt = datetime.fromtimestamp(last_ts)
    current_dt = datetime.fromtimestamp(now_ts)
    analysis = GapAnalysis(
        interaction_minutes=diff_mins,
        active_minutes=active_gap,
        duration_text=format_duration(diff_mins),
        is_long_absence=is_abandonment,
        has_recent_activity=is_critical_active,
        is_long_gap=is_long_gap,
        crossed_date=previous_dt.date() != current_dt.date(),
        crossed_evening=previous_dt.hour < 18 <= current_dt.hour,
    )
    return render_time_prompt(last_ts, now_ts, analysis)
