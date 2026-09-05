"""时间感知状态模型与旧数据兼容解析。"""

import json
from collections.abc import Mapping
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


STORAGE_SCHEMA_VERSION = "1.0.0"


class InteractionState(BaseModel):
    """跨会话保存的最后交互和活跃时间。"""

    model_config = ConfigDict(extra="ignore")

    last_interaction_ts: float = 0.0
    last_active_ts: float = 0.0
    last_seen_fmt: str = ""
    version: str = STORAGE_SCHEMA_VERSION
    modified_by: Optional[str] = None

    @classmethod
    def from_raw(cls, raw: object) -> Optional["InteractionState"]:
        if raw is None:
            return None
        try:
            payload: Any
            if isinstance(raw, str):
                payload = json.loads(raw)
            elif isinstance(raw, Mapping):
                payload = dict(raw)
            else:
                return None
            if not isinstance(payload, dict):
                return None
            if not payload.get("last_interaction_ts") and payload.get("last_seen_ts"):
                payload["last_interaction_ts"] = payload["last_seen_ts"]
                payload["last_active_ts"] = payload["last_seen_ts"]
            return cls.model_validate(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)
