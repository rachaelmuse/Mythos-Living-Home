"""Presence only from an actual pulse. Registry membership is not a heartbeat."""

from __future__ import annotations

import time
from enum import Enum
from pathlib import Path

from federation.atomic import atomic_write_json, read_json


class Presence(str, Enum):
    READY = "READY"
    STALE = "STALE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class HeartbeatLog:
    def __init__(
        self,
        root: Path,
        *,
        stale_after_s: float = 90.0,
        offline_after_s: float = 180.0,
    ) -> None:
        self.root = Path(root)
        self.dir = self.root / "heartbeats"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.stale_after_s = stale_after_s
        self.offline_after_s = offline_after_s

    def _path(self, agent_id: str) -> Path:
        return self.dir / f"{agent_id}.json"

    def pulse(self, agent_id: str, *, source: str = "self_pulse") -> dict:
        payload = {
            "agent_id": agent_id,
            "ts": time.time(),
            "source": source,
        }
        atomic_write_json(self._path(agent_id), payload)
        return payload

    def last_seen(self, agent_id: str) -> float | None:
        path = self._path(agent_id)
        if not path.exists():
            return None
        data = read_json(path)
        ts = data.get("ts")
        return float(ts) if ts is not None else None

    def presence(self, agent_id: str) -> Presence:
        ts = self.last_seen(agent_id)
        if ts is None:
            return Presence.UNKNOWN
        age = time.time() - ts
        if age < self.stale_after_s:
            return Presence.READY
        if age < self.offline_after_s:
            return Presence.STALE
        return Presence.OFFLINE
