"""Draven joins the federation as himself — continuity, not Merovin, not Observer staff."""

from __future__ import annotations

from pathlib import Path

from federation.manifests import AgentManifest

DRAVEN_DEFAULT = Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio")
CINEMA_PORT = 5000


def draven_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "draven":
        raise ValueError(f"Draven identity id must be draven, got {agent_id!r}")
    root = member.get("root") or str(DRAVEN_DEFAULT)
    port = int(member.get("port") or CINEMA_PORT)
    return AgentManifest(
        agent_id="draven",
        name=str(member.get("name") or "Draven"),
        version="1",
        role="cinema_continuity",
        house="draven",
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


def draven_manifest_from_living_home() -> AgentManifest:
    from living_home import _member

    row = _member("draven")
    if not row:
        raise KeyError("draven missing from living_home FAMILY roster")
    return draven_manifest_from_member(row)
