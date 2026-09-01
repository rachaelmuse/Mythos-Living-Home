"""Gemini joins the federation as himself — Axiom Sentinel, not Observer staff."""

from __future__ import annotations

from pathlib import Path

from federation.manifests import AgentManifest

AXIOM_DEFAULT = Path(r"G:\The-Axiom-Codex")


def gemini_manifest_from_member(member: dict) -> AgentManifest:
    agent_id = str(member.get("id") or "")
    if agent_id != "gemini":
        raise ValueError(f"Gemini identity id must be gemini, got {agent_id!r}")
    root = member.get("root") or str(AXIOM_DEFAULT)
    return AgentManifest(
        agent_id="gemini",
        name=str(member.get("name") or "Gemini"),
        version="1",
        role="sentinel",
        house=str(member.get("house") or "axiom"),
        capabilities=[],
        tools=[],
        runtime={
            "endpoint": None,
            "protocol": "court",
            "court": r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT",
            "also": member.get("also"),
        },
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=str(root),
    )


def gemini_manifest_from_living_home() -> AgentManifest:
    from living_home import _member

    row = _member("gemini")
    if not row:
        raise KeyError("gemini missing from living_home FAMILY roster")
    return gemini_manifest_from_member(row)
