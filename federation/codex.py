"""Codex twin joins the federation as himself — never Gemini, not Observer staff."""

from __future__ import annotations

from pathlib import Path

from federation.manifests import AgentManifest

CODEX_DEFAULT = Path(r"G:\Mythos_Codex")
CODEX_PORT = 8780


def codex_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "codex":
        raise ValueError(f"Codex identity id must be codex, got {agent_id!r}")
    root = member.get("root") or str(CODEX_DEFAULT)
    port = int(member.get("port") or CODEX_PORT)
    return AgentManifest(
        agent_id="codex",
        name=str(member.get("name") or "Codex"),
        version="1",
        role="archive",
        house=str(member.get("house") or "codex_twin"),
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


def codex_manifest_from_living_home() -> AgentManifest:
    from living_home import _member

    row = _member("codex")
    if not row:
        raise KeyError("codex missing from living_home FAMILY roster")
    return codex_manifest_from_member(row)
