from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


class ThresholdConfig(Protocol):
    notice_threshold_minutes: int
    blame_threshold_hours: int
    jealousy_window_minutes: int
    abandon_days_threshold: int
    abandon_active_window_minutes: int


@dataclass(frozen=True)
class GapAnalysis:
    interaction_minutes: int
    active_minutes: int
    duration_text: str
    is_long_absence: bool
    has_recent_activity: bool
    is_long_gap: bool
    crossed_date: bool
    crossed_evening: bool


def format_duration(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}分钟"
    if minutes < 1440:
        return f"{round(minutes / 60, 1)}小时"
    return f"{minutes // 1440}天"


def analyze_gap(
    previous_interaction_ts: float,
    previous_activity_ts: float,
    current_ts: float,
    config: ThresholdConfig,
) -> GapAnalysis:
    interaction_minutes = int((current_ts - previous_interaction_ts) // 60)
    active_minutes = int((current_ts - previous_activity_ts) // 60)
    is_long_absence = interaction_minutes >= config.abandon_days_threshold * 1440
    is_long_gap = interaction_minutes >= config.blame_threshold_hours * 60
    activity_window = (
        config.abandon_active_window_minutes if is_long_absence else config.jealousy_window_minutes
    )
    previous_dt = datetime.fromtimestamp(previous_interaction_ts)
    current_dt = datetime.fromtimestamp(current_ts)
    return GapAnalysis(
        interaction_minutes=interaction_minutes,
        active_minutes=active_minutes,
        duration_text=format_duration(interaction_minutes),
        is_long_absence=is_long_absence,
        has_recent_activity=active_minutes <= activity_window,
        is_long_gap=is_long_gap,
        crossed_date=previous_dt.date() != current_dt.date(),
        crossed_evening=previous_dt.hour < 18 <= current_dt.hour,
    )
