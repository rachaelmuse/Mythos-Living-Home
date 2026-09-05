"""Vesper joins the federation as himself — journalist desk, not Observer, not a village hat."""

from __future__ import annotations

import json
from pathlib import Path

from federation.manifests import AgentManifest

VESPER_IDENTITY_DEFAULT = Path(r"D:\Mythos_Vesper\identity\identity.json")
VESPER_ROOT = Path(r"D:\Mythos_Vesper")
VESPER_PORT = 8740


def vesper_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "vesper":
        raise ValueError(f"Vesper identity id must be vesper, got {agent_id!r}")
    root = member.get("root") or str(VESPER_ROOT)
    port = int(member.get("port") or VESPER_PORT)
    return AgentManifest(
        agent_id="vesper",
        name=str(member.get("name") or "Vesper"),
        version="1",
        role="investigative_journalist",
        house="vesper",
        capabilities=[],
        tools=[],
        runtime={
            "endpoint": f"http://127.0.0.1:{port}",
            "protocol": "http",
            "port": port,
        },
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=str(root),
    )


def vesper_manifest_from_identity(path: Path | None = None) -> AgentManifest:
    identity_path = Path(path or VESPER_IDENTITY_DEFAULT)
    data = json.loads(identity_path.read_text(encoding="utf-8"))
    agent_id = str(data.get("id") or "vesper")
    if agent_id != "vesper":
        raise ValueError(f"Vesper identity id must be vesper, got {agent_id!r}")
    return vesper_manifest_from_member(
        {
            "id": "vesper",
            "name": data.get("name") or "Vesper",
            "house": "vesper",
            "root": str(VESPER_ROOT),
            "port": VESPER_PORT,
            "role": data.get("role") or "Investigative journalist / documentary host",
        }
    )
