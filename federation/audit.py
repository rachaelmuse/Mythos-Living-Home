"""Read-only federation snapshot. Observer may query this; she does not own it."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from federation.atomic import read_json
from federation.heartbeat import HeartbeatLog
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


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
