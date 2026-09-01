"""Aster joins the federation as herself — not as an Observer agent."""

from __future__ import annotations

import json
from pathlib import Path

from federation.manifests import AgentManifest

ASTER_IDENTITY_DEFAULT = Path(r"D:\Mythos_Hearth\ASTER\ASTER_IDENTITY.json")


def aster_manifest_from_identity(path: Path | None = None) -> AgentManifest:
    identity_path = Path(path or ASTER_IDENTITY_DEFAULT)
    data = json.loads(identity_path.read_text(encoding="utf-8"))
    agent_id = str(data.get("id") or "aster")
    if agent_id != "aster":
        raise ValueError(f"Aster identity id must be aster, got {agent_id!r}")
    return AgentManifest(
        agent_id="aster",
        name=str(data.get("name") or "Aster"),
        version=str(data.get("identity_version") or "1.0"),
        role="weaver",
        house="hearth_lab",
        capabilities=[],
        tools=[],
        runtime={
            "endpoint": "http://127.0.0.1:8791",
            "protocol": "http",
            "lab": str(identity_path.parent),
        },
        protocol_version="1",
        requested_permissions=["read_hearth_snapshot"],
        declared_status="DECLARED",
        identity_root=str(identity_path.parent),
    )
