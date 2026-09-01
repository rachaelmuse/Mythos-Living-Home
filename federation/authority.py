"""Canonical authority. Observer audits. She does not own the family."""

from __future__ import annotations

from pathlib import Path

from federation.atomic import atomic_write_json

AUTHORITY: dict[str, str] = {
    "observer_identity": "observer",
    "observer_mission": "observer",
    "investigative_ledger": "observer",
    "observer_audit_history": "observer",
    "federation_identity": "hearth_federation",
    "family_membership": "hearth_federation",
    "federation_registration": "hearth_federation",
    "federation_presence": "hearth_federation",
    "federation_communication": "hearth_federation",
    "federation_permissions": "hearth_federation",
    "agent_identity": "owning_agent",
    "agent_memory": "owning_agent",
    "agent_tools": "owning_agent",
    "agent_internal_state": "owning_agent",
    "declared_capabilities": "declaring_agent",
    "capability_verification": "federation_verification_layer",
    "capability_ownership": "owning_agent",
    "tool_ownership": "owning_agent",
    "gameworld_state": "hearth_gameworld",
    "external_reviewer_identity": "external_adapter",
    "invoke_permissions": "federation_security_layer",
}


def domain_owner(domain: str) -> str:
    if domain not in AUTHORITY:
        raise KeyError(domain)
    return AUTHORITY[domain]


def write_authority_map(root: Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "AUTHORITY.json"
    atomic_write_json(path, dict(AUTHORITY))
    return path
