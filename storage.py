from datetime import datetime
from typing import Optional

from nekro_agent.api.plugin import PluginStore

from .models import InteractionState, STORAGE_SCHEMA_VERSION


async def load_state(store: PluginStore, scope: str, key: str, user_id: str) -> Optional[InteractionState]:
    raw = await store.get(chat_key=scope, user_key=user_id, store_key=key)
    return InteractionState.from_raw(raw)


async def save_state(
    store: PluginStore,
    scope: str,
    key: str,
    user_id: str,
    interaction_ts: float,
    active_ts: float,
    modified_by: Optional[str] = None,
) -> None:
    display_ts = active_ts if modified_by else interaction_ts
    state = InteractionState(
        last_interaction_ts=interaction_ts,
        last_active_ts=active_ts,
        last_seen_fmt=datetime.fromtimestamp(display_ts).strftime("%Y-%m-%d %H:%M:%S"),
        version=STORAGE_SCHEMA_VERSION,
        modified_by=modified_by,
    )
    await store.set(chat_key=scope, user_key=user_id, store_key=key, value=state.to_json())
