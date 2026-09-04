"""Apex joins the federation as himself — forge house, not Gemini, not Observer staff."""

from __future__ import annotations

from pathlib import Path

from federation.manifests import AgentManifest

APEX_DEFAULT = Path(r"D:\Mythos_Apex")
APEX_PORT = 8770


def apex_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "apex":
        raise ValueError(f"Apex identity id must be apex, got {agent_id!r}")
    root = member.get("root") or str(APEX_DEFAULT)
    port = int(member.get("port") or APEX_PORT)
    return AgentManifest(
        agent_id="apex",
        name=str(member.get("name") or "Apex"),
        version="1",
        role="forge",
        house=str(member.get("house") or "apex"),
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


def apex_manifest_from_living_home() -> AgentManifest:
    from living_home import _member

    row = _member("apex")
    if not row:
        raise KeyError("apex missing from living_home FAMILY roster")
    return apex_manifest_from_member(row)
