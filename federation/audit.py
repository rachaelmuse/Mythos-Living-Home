"""Read-only federation snapshot. Observer may query this; she does not own it."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from federation.atomic import read_json
from federation.heartbeat import HeartbeatLog
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus

_STALE_AFTER_S = 90.0
_OFFLINE_AFTER_S = 180.0


def _presence(root: Path, agent_id: str) -> tuple[str, float | None]:
    path = root / "heartbeats" / f"{agent_id}.json"
    if not path.exists():
        return "UNKNOWN", None
    data = read_json(path)
    ts = data.get("ts")
    if ts is None:
        return "UNKNOWN", None
    last = float(ts)
    age = time.time() - last
    if age < _STALE_AFTER_S:
        return "READY", last
    if age < _OFFLINE_AFTER_S:
        return "STALE", last
    return "OFFLINE", last


def inspect(root: Path | str) -> dict[str, Any]:
    """Read the federation desk without creating it or claiming ownership."""
    data_root = Path(root)
    participants_dir = data_root / "participants"
    if not participants_dir.is_dir():
        return {
            "ok": False,
            "error": "federation_store_missing",
            "root": str(data_root),
            "owned_by": None,
            "observer_is_supervisor": False,
            "observer_owns_aster": False,
            "agents": [],
            "capabilities": [],
            "communications": [],
            "gemini_spoke": False,
        }

    agents = []
    for path in sorted(participants_dir.glob("*.json")):
        raw = read_json(path)
        agent_id = str(raw.get("agent_id") or path.stem)
        presence, last_seen = _presence(data_root, agent_id)
        agents.append(
            {
                "agent_id": agent_id,
                "name": raw.get("name"),
                "house": raw.get("house"),
                "role": raw.get("role"),
                "declared_status": raw.get("declared_status"),
                "presence": presence,
                "last_seen": last_seen,
                "owner": None,
                "supervisor": None,
            }
        )

    caps = []
    cap_dir = data_root / "capabilities"
    if cap_dir.is_dir():
        for path in sorted(cap_dir.glob("*.json")):
            rec = read_json(path)
            state = str(rec.get("state") or "")
            honest = str(rec.get("honest_status") or "")
            evidence = dict(rec.get("evidence") or {})
            caps.append(
                {
                    "capability_id": rec.get("capability_id"),
                    "agent_id": rec.get("agent_id"),
                    "state": state,
                    "honest_status": honest,
                    "declared": honest == "DECLARED" or state == "DISCOVERED",
                    "verified": state == "VERIFIED",
                    "provenance": dict(rec.get("provenance") or {}),
                    "evidence": evidence,
                }
            )

    communications = []
    archive = data_root / "bus" / "archive"
    if archive.is_dir():
        for path in sorted(archive.glob("*.json")):
            raw = read_json(path)
            communications.append(
                {
                    "message_id": raw.get("message_id"),
                    "sender": raw.get("sender"),
                    "recipient": raw.get("recipient"),
                    "status": raw.get("status"),
                    "message_type": raw.get("message_type"),
                }
            )

    gemini_spoke = False
    acceptance = data_root / "ASTER_ACCEPTANCE.json"
    if acceptance.exists():
        acc = read_json(acceptance)
        gemini_spoke = bool(acc.get("gemini_spoke"))
    for cap in caps:
        if cap.get("capability_id") == "gemini.federation_inbox":
            gemini_spoke = gemini_spoke or bool((cap.get("evidence") or {}).get("gemini_spoke"))

    return {
        "ok": True,
        "root": str(data_root),
        "owned_by": None,
        "observer_is_supervisor": False,
        "observer_owns_aster": False,
        "agents": agents,
        "capabilities": caps,
        "communications": communications,
        "gemini_spoke": gemini_spoke,
    }


class FederationAuditView:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.registry = FederationRegistry(self.root)
        self.heartbeats = HeartbeatLog(self.root)
        self.bus = LocalFederationBus(self.root)

    def snapshot(self) -> dict[str, Any]:
        agents = []
        for manifest in self.registry.list_participants():
            agents.append(
                {
                    "agent_id": manifest.agent_id,
                    "name": manifest.name,
                    "house": manifest.house,
                    "role": manifest.role,
                    "declared_status": manifest.declared_status,
                    "presence": self.heartbeats.presence(manifest.agent_id).value,
                    "last_seen": self.heartbeats.last_seen(manifest.agent_id),
                    "owner": None,
                    "supervisor": None,
                }
            )
        caps = []
        cap_dir = self.root / "capabilities"
        if cap_dir.exists():
            for path in sorted(cap_dir.glob("*.json")):
                raw = read_json(path)
                capability_id = raw.get("capability_id")
                if not capability_id:
                    continue
                rec = self.registry.get_capability(capability_id)
                caps.append(
                    {
                        "capability_id": rec.capability_id,
                        "agent_id": rec.agent_id,
                        "state": rec.state.value,
                        "honest_status": rec.honest_status.value,
                        "declared": rec.honest_status.value == "DECLARED"
                        or rec.state.value == "DISCOVERED",
                        "verified": rec.state.value == "VERIFIED",
                    }
                )
        return {
            "owned_by": None,
            "observer_is_supervisor": False,
            "agents": agents,
            "capabilities": caps,
        }
