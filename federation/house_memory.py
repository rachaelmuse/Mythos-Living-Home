"""Per-house continuity notes. Federation does not own personalities. Not Observer. Not HOME.json."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json, read_json
from federation.authority import domain_owner

# Throwaway fixtures, the auditor, and village kin do not get a federation notebook.
_FORBIDDEN = frozenset({"observer", "heartbeat_probe", "nova", "echo", "solace"})


class HouseNotebook:
    """Owning-agent notes beside the bus. Not a second family_memory. Not a soul merge."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.dir = self.root / "houses"
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, agent_id: str) -> Path:
        return self.dir / agent_id / "notes.json"

    def remember(
        self,
        agent_id: str,
        *,
        text: str,
        event_id: str | None = None,
        kind: str = "work",
        writer: str | None = None,
    ) -> dict[str, Any]:
        owner = str(agent_id or "").strip()
        who = str(writer or owner).strip()
        if not owner or owner in _FORBIDDEN:
            raise PermissionError(f"{owner or 'unknown'} cannot hold a family house notebook")
        if who != owner:
            raise PermissionError(f"{who} cannot write {owner} house memory")
        if domain_owner("agent_memory") != "owning_agent":
            raise PermissionError("agent_memory authority is not owning_agent")
        body = str(text or "").strip()
        if not body:
            raise ValueError("empty house note")
        path = self._path(owner)
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = self.recall(owner)
        note = {
            "agent_id": owner,
            "kind": kind,
            "text": body,
            "event_id": event_id,
            "timestamp": time.time(),
            "authority": "owning_agent",
        }
        rows.append(note)
        atomic_write_json(path, {"agent_id": owner, "notes": rows})
        return note

    def recall(self, agent_id: str) -> list[dict[str, Any]]:
        path = self._path(agent_id)
        if not path.exists():
            return []
        data = read_json(path)
        rows = data.get("notes") if isinstance(data, dict) else None
        return list(rows) if isinstance(rows, list) else []

    def last(self, agent_id: str) -> dict[str, Any] | None:
        rows = self.recall(agent_id)
        return dict(rows[-1]) if rows else None
