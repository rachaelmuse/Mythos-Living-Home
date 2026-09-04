"""Neutral participant registry. Nobody here is anyone else's employee."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from federation.atomic import atomic_write_json, read_json
from federation.health import AgentHealth
from federation.heartbeat import HeartbeatLog, Presence
from federation.law import CapabilityState, HonestStatus
from federation.layers import Layer
from federation.manifests import AgentManifest, CapabilityManifest, hash_items


@dataclass
class CapabilityRecord:
    capability_id: str
    agent_id: str
    name: str
    state: CapabilityState
    honest_status: HonestStatus
    evidence: dict[str, Any] = field(default_factory=dict)
    lifecycle: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        data["honest_status"] = self.honest_status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CapabilityRecord:
        return cls(
            capability_id=data["capability_id"],
            agent_id=data["agent_id"],
            name=data.get("name", ""),
            state=CapabilityState(data["state"]),
            honest_status=HonestStatus(data["honest_status"]),
            evidence=dict(data.get("evidence") or {}),
            lifecycle=list(data.get("lifecycle") or []),
            provenance=dict(data.get("provenance") or {}),
        )


class FederationRegistry:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.participants_dir = self.root / "participants"
        self.capabilities_dir = self.root / "capabilities"
        self.events_dir = self.root / "manifest_events"
        self.participants_dir.mkdir(parents=True, exist_ok=True)
        self.capabilities_dir.mkdir(parents=True, exist_ok=True)
        self.events_dir.mkdir(parents=True, exist_ok=True)

    def _events_path(self, agent_id: str) -> Path:
        return self.events_dir / f"{agent_id}.json"

    def _auth_grants_path(self) -> Path:
        return self.root / "authorizations.json"

    def _auth_events_path(self) -> Path:
        return self.root / "authorization_events.json"

    def _layer_events_path(self) -> Path:
        return self.root / "layer_events.json"

    def _health_path(self) -> Path:
        return self.root / "agent_health.json"

    def _read_list(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        data = read_json(path)
        return list(data) if isinstance(data, list) else []

    def _write_list(self, path: Path, rows: list[dict[str, Any]]) -> None:
        atomic_write_json(path, rows)

    def _append_list(self, path: Path, row: dict[str, Any]) -> None:
        rows = self._read_list(path)
        rows.append(row)
        self._write_list(path, rows)

    def _now(self) -> float:
        events_any = list(self.events_dir.glob("*.json"))
        stamp = time.time()
        latest = stamp
        for path in events_any:
            for event in self._read_list(path):
                ts = event.get("timestamp")
                if isinstance(ts, (int, float)) and ts > latest:
                    latest = float(ts)
        if latest >= stamp:
            return latest + 0.001
        return stamp

    def register(self, manifest: AgentManifest) -> AgentManifest:
        path = self.participants_dir / f"{manifest.agent_id}.json"
        cap_hash = hash_items(list(manifest.capabilities))
        tool_hash = hash_items(list(manifest.tools))
        previous: AgentManifest | None = None
        if path.exists():
            previous = AgentManifest.from_dict(read_json(path))

        if previous is None:
            version = 1
            kind = "register"
            changed = True
        elif previous.capability_hash != cap_hash or previous.tool_hash != tool_hash:
            version = int(previous.manifest_version or "1") + 1
            kind = "update"
            changed = True
        else:
            version = int(previous.manifest_version or "1")
            kind = "update"
            changed = False

        stamp = self._now()
        out = replace(
            manifest,
            manifest_version=str(version),
            capability_hash=cap_hash,
            tool_hash=tool_hash,
            timestamp=stamp,
            agent_version=manifest.version,
        )
        atomic_write_json(path, out.to_dict())
        if previous is None or changed:
            self._append_list(
                self._events_path(manifest.agent_id),
                {
                    "kind": kind,
                    "timestamp": stamp,
                    "agent_id": manifest.agent_id,
                    "manifest": out.to_dict(),
                },
            )
        return out

    def manifest_events(self, agent_id: str) -> list[dict[str, Any]]:
        return self._read_list(self._events_path(agent_id))

    def manifest_at(self, agent_id: str, timestamp: float | str) -> AgentManifest:
        events = self.manifest_events(agent_id)
        chosen: dict[str, Any] | None = None
        for event in events:
            if event.get("timestamp") <= timestamp:
                chosen = event
        if chosen is None:
            raise KeyError(f"no manifest for {agent_id} at {timestamp}")
        return AgentManifest.from_dict(chosen["manifest"])

    def get(self, agent_id: str) -> AgentManifest:
        path = self.participants_dir / f"{agent_id}.json"
        if not path.exists():
            raise KeyError(agent_id)
        return AgentManifest.from_dict(read_json(path))

    def list_participants(self) -> list[AgentManifest]:
        return [
            AgentManifest.from_dict(read_json(p))
            for p in sorted(self.participants_dir.glob("*.json"))
        ]

    def owner_of(self, agent_id: str) -> None:
        self.get(agent_id)
        return None

    def supervisor_of(self, agent_id: str) -> None:
        self.get(agent_id)
        return None

    def relationship(self, left: str, right: str) -> str:
        self.get(left)
        self.get(right)
        return "independent_participants"

    def claim_ownership(self, claimant: str, target: str) -> None:
        self.get(claimant)
        self.get(target)
        self._append_list(
            self._auth_events_path(),
            {
                "kind": "identity_merge_rejected",
                "claimant": claimant,
                "target": target,
                "timestamp": time.time(),
            },
        )
        raise PermissionError(
            f"{claimant} may not own {target}; identities never merge"
        )

    def declare_capability(self, manifest: CapabilityManifest) -> CapabilityRecord:
        record = CapabilityRecord(
            capability_id=manifest.capability_id,
            agent_id=manifest.agent_id,
            name=manifest.name,
            state=CapabilityState.DISCOVERED,
            honest_status=HonestStatus.DECLARED,
            evidence={"declared": True, "source": "manifest"},
            lifecycle=[CapabilityState.DISCOVERED.value],
        )
        atomic_write_json(self.capabilities_dir / f"{manifest.capability_id}.json", record.to_dict())
        return record

    def get_capability(self, capability_id: str) -> CapabilityRecord:
        path = self.capabilities_dir / f"{capability_id}.json"
        if not path.exists():
            raise KeyError(capability_id)
        return CapabilityRecord.from_dict(read_json(path))

    def mark_verified(self, capability_id: str, evidence: str) -> None:
        raise PermissionError(
            "VERIFIED only via test_capability with a passing functional test "
            f"(got {evidence!r}). DECLARED is not VERIFIED."
        )

    def _write_capability(self, record: CapabilityRecord) -> None:
        atomic_write_json(
            self.capabilities_dir / f"{record.capability_id}.json",
            record.to_dict(),
        )

    def _artifact_path(self, capability_id: str) -> Path:
        return self.root / "evidence" / f"{capability_id}.json"

    def test_capability(self, capability_id: str, test_fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        record = self.get_capability(capability_id)
        raw = test_fn() or {}
        ok = bool(raw.get("ok"))
        agent = self.get(record.agent_id)
        artifact = self._artifact_path(capability_id)
        atomic_write_json(
            artifact,
            {
                "capability_id": capability_id,
                "ok": ok,
                "result": raw,
                "tested_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        provenance = {
            "declared_by": record.agent_id,
            "manifest_version": agent.manifest_version,
            "capability_hash": agent.capability_hash,
            "adapter": raw.get("adapter") or "",
            "connection_test": bool(raw.get("connection_test", ok)),
            "functional_test": True,
            "verified_at": datetime.now(timezone.utc).isoformat() if ok else None,
            "result": dict(raw),
            "artifact": str(artifact),
        }
        if not ok:
            record.state = CapabilityState.FAILED
            record.honest_status = HonestStatus.FAILED
            record.evidence = dict(raw)
            record.provenance = provenance
            record.lifecycle.append(CapabilityState.FAILED.value)
            self._write_capability(record)
            return {
                "capability_id": capability_id,
                "status": HonestStatus.FAILED.value,
                "result": raw,
            }
        record.state = CapabilityState.VERIFIED
        record.honest_status = HonestStatus.VERIFIED
        record.evidence = dict(raw)
        record.provenance = provenance
        record.lifecycle.extend(
            [CapabilityState.TESTED.value, CapabilityState.VERIFIED.value]
        )
        self._write_capability(record)
        return {
            "capability_id": capability_id,
            "status": HonestStatus.VERIFIED.value,
            "result": raw,
        }

    def authorize(self, requester: str, capability_id: str) -> None:
        self.get(requester)
        self.get_capability(capability_id)
        grants = self._read_list(self._auth_grants_path())
        grants.append(
            {
                "requester": requester,
                "capability_id": capability_id,
                "timestamp": time.time(),
            }
        )
        self._write_list(self._auth_grants_path(), grants)
        self._append_list(
            self._auth_events_path(),
            {
                "kind": "granted",
                "requester": requester,
                "capability_id": capability_id,
                "timestamp": time.time(),
            },
        )

    def _is_authorized(self, requester: str, capability_id: str) -> bool:
        return any(
            g.get("requester") == requester and g.get("capability_id") == capability_id
            for g in self._read_list(self._auth_grants_path())
        )

    def invoke(
        self,
        requester: str,
        capability_id: str,
        fn: Callable[[], dict[str, Any]],
    ) -> dict[str, Any]:
        self.get(requester)
        self.get_capability(capability_id)
        if not self._is_authorized(requester, capability_id):
            self._append_list(
                self._auth_events_path(),
                {
                    "kind": "rejected",
                    "requester": requester,
                    "capability_id": capability_id,
                    "timestamp": time.time(),
                },
            )
            raise PermissionError(
                f"{requester} is not authorized to invoke {capability_id}"
            )
        raw = fn() or {}
        result = dict(raw)
        result["layer"] = Layer.COLLABORATION.value
        self._append_list(
            self._layer_events_path(),
            {
                "layer": Layer.COLLABORATION.value,
                "requester": requester,
                "capability_id": capability_id,
                "timestamp": time.time(),
            },
        )
        return result

    def record_communication(self, message_id: str, sender: str, recipient: str) -> None:
        self._append_list(
            self._layer_events_path(),
            {
                "layer": Layer.COMMUNICATION.value,
                "message_id": message_id,
                "sender": sender,
                "recipient": recipient,
                "timestamp": time.time(),
            },
        )

    def layer_events(self, layer: Layer) -> list[dict[str, Any]]:
        return [e for e in self._read_list(self._layer_events_path()) if e.get("layer") == layer.value]

    def authorization_events(self) -> list[dict[str, Any]]:
        return self._read_list(self._auth_events_path())

    def _read_health(self) -> dict[str, str]:
        path = self._health_path()
        if not path.exists():
            return {}
        data = read_json(path)
        return dict(data) if isinstance(data, dict) else {}

    def agent_health(self, agent_id: str) -> AgentHealth:
        self.get(agent_id)
        stored = self._read_health().get(agent_id)
        if not stored:
            return AgentHealth.ACTIVE
        return AgentHealth(stored)

    def _quarantine_agent_capabilities(self, agent_id: str) -> None:
        for path in self.capabilities_dir.glob("*.json"):
            record = CapabilityRecord.from_dict(read_json(path))
            if record.agent_id != agent_id:
                continue
            record.state = CapabilityState.QUARANTINED
            record.honest_status = HonestStatus.UNAVAILABLE
            record.lifecycle.append(CapabilityState.QUARANTINED.value)
            self._write_capability(record)

    def sync_health(self, beats: HeartbeatLog, *, only_agent_id: str | None = None) -> None:
        health = self._read_health()
        agents = self.list_participants()
        if only_agent_id is not None:
            agents = [a for a in agents if a.agent_id == only_agent_id]
        for agent in agents:
            presence = beats.presence(agent.agent_id)
            if presence == Presence.OFFLINE:
                health[agent.agent_id] = AgentHealth.FAILED.value
                self._quarantine_agent_capabilities(agent.agent_id)
            elif presence == Presence.STALE:
                health[agent.agent_id] = AgentHealth.DEGRADED.value
            elif presence == Presence.READY:
                health[agent.agent_id] = AgentHealth.ACTIVE.value
            else:
                health.setdefault(agent.agent_id, AgentHealth.ACTIVE.value)
        atomic_write_json(self._health_path(), health)
