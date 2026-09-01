"""Federation prove scripts. Aster first, then Gemini. Observer never owns them."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from federation.aster import ASTER_IDENTITY_DEFAULT, aster_manifest_from_identity
from federation.audit import FederationAuditView
from federation.court_adapter import CourtFederationAdapter
from federation.gemini import gemini_manifest_from_living_home
from federation.heartbeat import HeartbeatLog
from federation.law import DEFAULT_DATA_ROOT
from federation.manifests import AgentManifest, CapabilityManifest
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _observer_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="observer",
        name="The Observer",
        version="0.1.0",
        role="independent_auditor",
        house="the_observer",
        capabilities=["federation_audit"],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8730", "protocol": "http"},
        protocol_version="1",
        requested_permissions=["read_federation_registry"],
        declared_status="DECLARED",
        identity_root=r"D:\The_Observer",
    )


def _hearth_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="hearth",
        name="Hearth",
        version="1",
        role="village_os",
        house="hearth",
        capabilities=[],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8790", "protocol": "http"},
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth",
    )


def _aster_stub_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="aster",
        name="Aster",
        version="1.0",
        role="weaver",
        house="hearth_lab",
        capabilities=[],
        tools=[],
        runtime={"endpoint": "http://127.0.0.1:8791", "protocol": "http"},
        protocol_version="1",
        requested_permissions=["read_hearth_snapshot"],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth\ASTER",
    )


def _load_aster(identity_path: Path | None) -> AgentManifest:
    path = identity_path or ASTER_IDENTITY_DEFAULT
    if Path(path).exists():
        return aster_manifest_from_identity(path)
    return _aster_stub_manifest()


def _living_home_available() -> bool:
    try:
        from living_home import _member

        return _member("gemini") is not None
    except Exception:
        return False


def _gemini_stub() -> AgentManifest:
    from federation.gemini import gemini_manifest_from_member

    return gemini_manifest_from_member(
        {
            "id": "gemini",
            "name": "Gemini",
            "house": "axiom",
            "root": r"G:\The-Axiom-Codex",
        }
    )


def _try_hearth_snapshot() -> dict:
    aster_root = Path(r"D:\Mythos_Hearth\ASTER")
    if str(aster_root) not in sys.path:
        sys.path.insert(0, str(aster_root))
    try:
        from aster_hearth_bridge import aster_world_context
    except Exception as exc:
        return {"ok": False, "error": f"bridge import failed: {exc}"}
    ctx = aster_world_context()
    reachable = ctx.get("hearth") == "REACHABLE"
    return {"ok": reachable, **ctx}


def prove(root: Path | None = None, identity_path: Path | None = None) -> dict:
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)

    aster = aster_manifest_from_identity(identity_path or ASTER_IDENTITY_DEFAULT)
    registry.register(aster)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
            declared=True,
            adapter_required=True,
            permission_required="read_hearth_snapshot",
        )
    )

    beats.pulse("aster")
    msg = bus.send(
        sender="aster",
        recipient="hearth",
        message_type="capability_query",
        payload={"ask": "snapshot", "from": "aster"},
    )
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient="hearth")

    cap_result = registry.test_capability("aster.hearth_snapshot", _try_hearth_snapshot)
    snap = FederationAuditView(data_root).snapshot()
    report = {
        "declared": "Aster participant + aster.hearth_snapshot + local bus",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "observer_owns_aster": registry.owner_of("aster") is not None,
            "relationship": registry.relationship("observer", "aster"),
            "message_id": msg.message_id,
            "message_status": bus.get(msg.message_id).status,
            "aster_presence": beats.presence("aster").value,
            "observer_presence": beats.presence("observer").value,
            "capability": cap_result,
        },
        "test_performed": [
            "aster identity file → manifest",
            "register aster + observer + hearth as independent participants",
            "bus send/deliver/ack aster → hearth",
            "aster self-pulse only",
            "aster_hearth_bridge snapshot (live if Hearth up)",
        ],
        "result": cap_result["status"],
        "evidence": snap,
        "status": cap_result["status"],
    }
    out = data_root / "PROVE.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def prove_gemini(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
) -> dict:
    """Aster → Gemini delivery. Gemini does not speak. Observer does not own him."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)

    aster = _load_aster(identity_path)
    gemini = gemini_manifest_from_living_home() if _living_home_available() else _gemini_stub()
    registry.register(aster)
    registry.register(gemini)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="gemini.federation_inbox",
            agent_id="gemini",
            name="Receive federation message as Gemini",
            declared=True,
            adapter_required=True,
        )
    )

    payload = {"ask": "who_are_you", "from": "aster", "note": "delivery test — not a spoken Gemini line"}
    msg = bus.send(
        sender="aster",
        recipient="gemini",
        message_type="capability_query",
        payload=payload,
    )
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient="gemini")
    notices = adapter.drop_notice(
        message_id=msg.message_id,
        sender="aster",
        recipient="gemini",
        payload=payload,
    )

    def _try_delivery() -> dict:
        inbox = bus.inbox("gemini")
        found = any(m.message_id == msg.message_id for m in inbox)
        notice_ok = bool(notices) and all(Path(p).exists() for p in notices)
        return {
            "ok": found and bus.get(msg.message_id).status == "acknowledged" and notice_ok,
            "message_id": msg.message_id,
            "inbox_count": len(inbox),
            "court_notices": notices,
            "gemini_spoke": False,
        }

    cap_result = registry.test_capability("gemini.federation_inbox", _try_delivery)
    snap = FederationAuditView(data_root).snapshot()
    report = {
        "declared": "Gemini participant + Aster→Gemini federation delivery + Court notice copy",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "observer_owns_gemini": registry.owner_of("gemini") is not None,
            "relationship": registry.relationship("observer", "gemini"),
            "message_id": msg.message_id,
            "message_status": bus.get(msg.message_id).status,
            "gemini_presence": beats.presence("gemini").value,
            "aster_presence": beats.presence("aster").value,
            "gemini_spoke": False,
            "capability": cap_result,
        },
        "test_performed": [
            "gemini manifest from living_home FAMILY roster (Axiom root)",
            "aster → gemini send/deliver/ack on local bus",
            "Court federation/ notice (not MAS inbox)",
            "no Gemini pulse",
            "no Gemini spoken reply",
        ],
        "result": cap_result["status"],
        "evidence": snap,
        "status": cap_result["status"],
    }
    out = data_root / "PROVE_GEMINI.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


if __name__ == "__main__":
    if "gemini" in sys.argv:
        print(json.dumps(prove_gemini(), indent=2, default=str))
    else:
        print(json.dumps(prove(), indent=2, default=str))
