"""Phase B foundation: catch the live store up. No new agents. No Gemini speech."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json, read_json
from federation.authority import write_authority_map
from federation.heartbeat import HeartbeatLog
from federation.law import CapabilityState, HonestStatus
from federation.layers import Layer
from federation.registry import FederationRegistry
from federation.transport import FederationMessage


PROVENANCE_KEYS = (
    "declared_by",
    "manifest_version",
    "capability_hash",
    "adapter",
    "connection_test",
    "functional_test",
    "verified_at",
    "result",
    "artifact",
)


def _provenance_complete(provenance: dict[str, Any]) -> bool:
    for key in PROVENANCE_KEYS:
        if key not in provenance:
            return False
        value = provenance[key]
        if key in {"connection_test", "functional_test"}:
            if value is None:
                return False
            continue
        if value in (None, ""):
            return False
    return True


def _copy_json_dir(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for path in src.glob("*.json"):
        shutil.copy2(path, dest / path.name)


def _stamp_bus(root: Path, registry: FederationRegistry) -> list[str]:
    archive = root / "bus" / "archive"
    stamped: list[str] = []
    if not archive.exists():
        return stamped
    seen = {e.get("message_id") for e in registry.layer_events(Layer.COMMUNICATION)}
    for path in sorted(archive.glob("*.json")):
        msg = FederationMessage.from_dict(read_json(path))
        if msg.message_id in seen:
            continue
        registry.record_communication(msg.message_id, msg.sender, msg.recipient)
        seen.add(msg.message_id)
        stamped.append(msg.message_id)
    return stamped


def _downgrade_capabilities(root: Path, registry: FederationRegistry) -> None:
    cap_dir = registry.capabilities_dir
    if not cap_dir.exists():
        return
    for path in sorted(cap_dir.glob("*.json")):
        rec = registry.get_capability(read_json(path)["capability_id"])
        prove_name = {
            "aster.hearth_snapshot": "PROVE.json",
            "gemini.federation_inbox": "PROVE_GEMINI.json",
        }.get(rec.capability_id, "")
        prove_path = root / prove_name if prove_name else None
        artifact = str(prove_path) if prove_path and prove_path.exists() else ""
        existing = dict(rec.provenance or {})
        provenance = {
            "declared_by": existing.get("declared_by") or rec.agent_id,
            "manifest_version": existing.get("manifest_version") or "",
            "capability_hash": existing.get("capability_hash") or "",
            "adapter": existing.get("adapter") or "",
            "connection_test": existing.get("connection_test"),
            "functional_test": existing.get("functional_test"),
            "verified_at": existing.get("verified_at") or None,
            "result": existing.get("result") or dict(rec.evidence or {}),
            "artifact": existing.get("artifact") or artifact,
        }
        # Hashes from a post-reconcile re-save are current, not historical.
        # Do not copy them into a VERIFIED envelope.
        rec.provenance = provenance
        if rec.state == CapabilityState.VERIFIED and not _provenance_complete(provenance):
            rec.state = CapabilityState.TESTED
            rec.honest_status = HonestStatus.PARTIAL
            rec.lifecycle.append("PARTIAL")
        registry._write_capability(rec)


def _write_aster_acceptance(
    root: Path,
    registry: FederationRegistry,
    *,
    message_ids: list[str],
) -> Path:
    aster = registry.get("aster")
    gemini_cap = None
    try:
        gemini_cap = registry.get_capability("gemini.federation_inbox")
    except KeyError:
        pass
    gemini_spoke = bool((gemini_cap.evidence or {}).get("gemini_spoke")) if gemini_cap else False
    stages = {
        "aster_registration": {
            "status": "PASS",
            "note": "Aster is a participant. Observer does not own her.",
        },
        "identity_isolation": {
            "status": "PASS" if registry.owner_of("aster") is None else "FAIL",
            "note": "owner_of(aster) is None",
        },
        "hearth_connection": {
            "status": "PASS" if any(True for _ in (root / "bus" / "inbox" / "hearth").glob("*.json")) or any(
                mid for mid in message_ids
            ) else "PARTIAL",
            "note": "Local bus ack exists. Not a new prove.",
        },
        "gemini_delivery": {
            "status": "PASS" if gemini_cap is not None else "NOT STARTED",
            "note": "Delivery only. Not speech.",
        },
        "gemini_response": {
            "status": "NOT STARTED",
            "note": "Gemini did not speak.",
        },
        "capability_provenance": {
            "status": "FAIL",
            "note": "Live envelope lacked 9 provenance fields. Downgraded.",
        },
        "gameworld_invocation": {
            "status": "NOT STARTED",
            "note": "",
        },
        "gameworld_state_change": {
            "status": "NOT STARTED",
            "note": "",
        },
        "observer_http_audit": {
            "status": "NOT STARTED",
            "note": "FederationAuditView is in-process. Observer HTTP does not read this store.",
        },
        "negative_failed_capability_live": {"status": "NOT STARTED", "note": "Unit tested only."},
        "negative_unauthorized_invoke_live": {"status": "NOT STARTED", "note": "Unit tested only."},
        "negative_heartbeat_loss_live": {"status": "PARTIAL", "note": "sync_health applied this pass."},
        "negative_identity_merge_live": {"status": "NOT STARTED", "note": "Unit tested only."},
    }
    payload = {
        "kind": "ASTER_FEDERATION_ACCEPTANCE_TEST",
        "written_at": datetime.now(timezone.utc).isoformat(),
        "overall": "FAIL",
        "full_aster_acceptance": False,
        "gemini_spoke": gemini_spoke,
        "new_agents": [],
        "stages": stages,
        "evidence": {
            "test_id": "foundation_reconcile_phase_b",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_ids": [p.agent_id for p in registry.list_participants()],
            "message_ids": message_ids,
            "manifest_version": aster.manifest_version,
            "capability_hash": aster.capability_hash,
            "tool_hash": aster.tool_hash,
            "result": "foundation store reconciled; full Aster test not passing",
            "status": "FAIL",
            "evidence_reference": str(root / "ASTER_ACCEPTANCE.json"),
            "gemini_speech_message_id": None,
        },
        "note": "Phase B foundation only. Gemini expansion not started. Gameworld not started.",
    }
    path = root / "ASTER_ACCEPTANCE.json"
    atomic_write_json(path, payload)
    return path


def reconcile_foundation(
    root: Path,
    *,
    beats: HeartbeatLog | None = None,
) -> dict[str, Any]:
    root = Path(root)
    registry = FederationRegistry(root)
    before = {p.agent_id for p in registry.list_participants()}
    archive = root / "archive" / "pre_reconcile"
    _copy_json_dir(registry.participants_dir, archive)
    _copy_json_dir(registry.capabilities_dir, archive)

    write_authority_map(root)
    for agent in list(registry.list_participants()):
        registry.register(agent)

    _downgrade_capabilities(root, registry)
    log = beats or HeartbeatLog(root)
    registry.sync_health(log)
    message_ids = _stamp_bus(root, registry)

    after = {p.agent_id for p in registry.list_participants()}
    acceptance = _write_aster_acceptance(root, registry, message_ids=message_ids)
    return {
        "root": str(root),
        "participants": sorted(after),
        "new_agents": sorted(after - before),
        "gemini_spoke": False,
        "full_aster_acceptance": False,
        "aster_acceptance": str(acceptance),
        "message_ids": message_ids,
        "archived_to": str(archive),
    }


if __name__ == "__main__":
    import json

    from federation.law import DEFAULT_DATA_ROOT

    print(json.dumps(reconcile_foundation(Path(DEFAULT_DATA_ROOT)), indent=2, default=str))
