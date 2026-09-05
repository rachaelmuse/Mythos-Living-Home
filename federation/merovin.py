"""Merovin joins the federation as himself — cinema vision, not Draven, not Observer staff."""

from __future__ import annotations

from pathlib import Path

from federation.manifests import AgentManifest

MEROVIN_DEFAULT = Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio")
CINEMA_PORT = 5000


def merovin_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "merovin":
        raise ValueError(f"Merovin identity id must be merovin, got {agent_id!r}")
    root = member.get("root") or str(MEROVIN_DEFAULT)
    port = int(member.get("port") or CINEMA_PORT)
    return AgentManifest(
        agent_id="merovin",
        name=str(member.get("name") or "Merovin"),
        version="1",
        role="cinema_vision",
        house="merovin",
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


def merovin_manifest_from_living_home() -> AgentManifest:
    from living_home import _member

    row = _member("merovin")
    if not row:
        raise KeyError("merovin missing from living_home FAMILY roster")
    return merovin_manifest_from_member(row)
