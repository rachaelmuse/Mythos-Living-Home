"""Canonical manifests. Registration does not verify capabilities."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any


def hash_items(items: list[str]) -> str:
    payload = json.dumps(sorted(items), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class AgentManifest:
    agent_id: str
    name: str
    version: str
    role: str
    house: str
    capabilities: list[str]
    tools: list[str]
    runtime: dict[str, Any]
    protocol_version: str
    requested_permissions: list[str]
    declared_status: str
    identity_root: str
    manifest_version: str = "0"
    capability_hash: str = ""
    tool_hash: str = ""
    timestamp: float | str = ""
    agent_version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentManifest:
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            version=data.get("version", "0"),
            role=data.get("role", ""),
            house=data.get("house", ""),
            capabilities=list(data.get("capabilities") or []),
            tools=list(data.get("tools") or []),
            runtime=dict(data.get("runtime") or {}),
            protocol_version=str(data.get("protocol_version", "1")),
            requested_permissions=list(data.get("requested_permissions") or []),
            declared_status=data.get("declared_status", "DECLARED"),
            identity_root=data.get("identity_root", ""),
            manifest_version=str(data.get("manifest_version", "0")),
            capability_hash=str(data.get("capability_hash", "")),
            tool_hash=str(data.get("tool_hash", "")),
            timestamp=data.get("timestamp", ""),
            agent_version=str(data.get("agent_version") or data.get("version", "")),
        )


@dataclass
class CapabilityManifest:
    capability_id: str
    agent_id: str
    name: str
    declared: bool = True
    adapter_required: bool = False
    permission_required: str = ""
    tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolManifest:
    tool_id: str
    agent_id: str
    name: str
    declared: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
