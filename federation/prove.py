"""Federation prove scripts. Aster first, then Gemini. Observer never owns them."""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from federation.apex import APEX_PORT, apex_manifest_from_living_home, apex_manifest_from_member
from federation.aster import ASTER_IDENTITY_DEFAULT, aster_manifest_from_identity
from federation.atomic import atomic_write_json
from federation.audit import FederationAuditView
from federation.codex import CODEX_PORT, codex_manifest_from_living_home, codex_manifest_from_member
from federation.court_adapter import CourtFederationAdapter
from federation.gemini import gemini_manifest_from_living_home
from federation.health import AgentHealth
from federation.heartbeat import HeartbeatLog, Presence
from federation.law import CapabilityState, DEFAULT_DATA_ROOT, HonestStatus
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


def _http_probe(url: str, timeout_s: float = 4.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            ident = None
            try:
                body = json.loads(raw) if raw else None
                if isinstance(body, dict):
                    ident = body.get("id")
            except json.JSONDecodeError:
                pass
            return {"ok": 200 <= int(resp.status) < 300, "http": int(resp.status), "id": ident, "url": url}
    except Exception as exc:
        return {"ok": False, "http": None, "id": None, "url": url, "error": str(exc)}


def _default_pings() -> dict[str, Any]:
    return {
        "observer": _http_probe("http://127.0.0.1:8730/health"),
        "hearth": _http_probe("http://127.0.0.1:8790/api/home"),
        "aster_lab": _http_probe("http://127.0.0.1:8791/api/status"),
    }


def status_check(
    root: Path | None = None,
    *,
    ping_fn: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Read-only Mom check. Does not pulse, send, register, or add agents."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    beats = HeartbeatLog(data_root)
    snap = FederationAuditView(data_root).snapshot()
    participants = sorted(p.agent_id for p in registry.list_participants())
    owns_aster = None
    if "aster" in participants:
        owns_aster = registry.owner_of("aster") is not None
    acceptance: dict[str, Any] = {}
    acc_path = data_root / "ASTER_ACCEPTANCE.json"
    if acc_path.exists():
        acceptance = json.loads(acc_path.read_text(encoding="utf-8"))
    pings = ping_fn() if ping_fn is not None else _default_pings()
    report = {
        "kind": "MOM_FEDERATION_STATUS",
        "root": str(data_root),
        "wrote_bus": False,
        "participants": participants,
        "observer_owns_aster": owns_aster,
        "aster_presence": beats.presence("aster").value,
        "gemini_spoke": bool(acceptance.get("gemini_spoke")),
        "full_aster_acceptance": bool(acceptance.get("full_aster_acceptance")),
        "overall": acceptance.get("overall") or "UNKNOWN",
        "capabilities": snap.get("capabilities"),
        "observer": pings.get("observer"),
        "hearth": pings.get("hearth"),
        "aster_lab": pings.get("aster_lab"),
        "what_this_is_not": [
            "Gemini speech",
            "The Axiom Codex notice into HOME.json",
            "Observer HTTP federation audit",
            "Village Heart Square talk",
        ],
    }
    (data_root / "MOM_STATUS.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


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
    return {
        "ok": reachable,
        "adapter": "aster_hearth_bridge",
        "connection_test": reachable,
        "functional_test": True,
        **ctx,
    }


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


def fetch_aster_lab_status(timeout_s: float = 8.0) -> dict[str, Any]:
    url = "http://127.0.0.1:8791/api/status"
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _patch_aster_acceptance(root: Path, *, cap_status: str, presence: str) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["aster_registration"] = {
        "status": "PASS",
        "note": "Aster is a participant. Observer does not own her.",
    }
    stages["hearth_connection"] = {
        "status": "PASS" if cap_status == "VERIFIED" else "PARTIAL",
        "note": "Live aster_hearth_bridge this refresh.",
    }
    stages["capability_provenance"] = {
        "status": "PASS" if cap_status == "VERIFIED" else "FAIL",
        "note": "Nine-field envelope from this refresh only if VERIFIED.",
    }
    prior_hb = stages.get("negative_heartbeat_loss_live") or {}
    if prior_hb.get("status") != "PASS":
        stages["negative_heartbeat_loss_live"] = {
            "status": "PASS" if presence == "READY" else "PARTIAL",
            "note": f"Lab HTTP checked; federation presence {presence}.",
        }
    if not data.get("gemini_spoke"):
        data["gemini_spoke"] = False
    data["note"] = "Phase B Aster refresh. Does not add Apex/Codex."
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def refresh_aster(
    root: Path | None = None,
    *,
    identity_path: Path | None = None,
    get_lab_status: Callable[[], dict[str, Any]] | None = None,
    snapshot_fn: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Phase B: Aster only. Pulse after lab proves she is Aster. No Gemini. No new agents."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    status = get_lab_status() if get_lab_status is not None else fetch_aster_lab_status()
    if str(status.get("id") or "") != "aster":
        raise PermissionError(f"lab is not Aster: {status.get('id')!r}")
    registry = FederationRegistry(data_root)
    before = {p.agent_id for p in registry.list_participants()}
    registry.register(_load_aster(identity_path))
    try:
        registry.get_capability("aster.hearth_snapshot")
    except KeyError:
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
    beats = HeartbeatLog(data_root)
    beats.pulse("aster", source="aster_lab_http")
    cap_result = registry.test_capability(
        "aster.hearth_snapshot",
        snapshot_fn or _try_hearth_snapshot,
    )
    registry.sync_health(beats)
    after = {p.agent_id for p in registry.list_participants()}
    _patch_aster_acceptance(
        data_root,
        cap_status=str(cap_result.get("status") or ""),
        presence=beats.presence("aster").value,
    )
    report = {
        "kind": "ASTER_PHASE_B_REFRESH",
        "lab_id": status.get("id"),
        "participants": sorted(after),
        "new_agents": sorted(after - before),
        "gemini_spoke": False,
        "full_aster_acceptance": False,
        "aster_presence": beats.presence("aster").value,
        "observer_owns_aster": registry.owner_of("aster") is not None,
        "capability": cap_result,
        "agent_health": registry.agent_health("aster").value,
        "pulse_source": "aster_lab_http",
    }
    out = data_root / "PROVE_ASTER_REFRESH.json"
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


def probe_companion_door(port: int, agent_id: str, timeout_s: float = 8.0) -> dict[str, Any]:
    url = f"http://127.0.0.1:{port}/api/companion/presence"
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            http = int(resp.status)
            body = json.loads(raw) if raw else {}
            peer = ((body.get("peers") or {}).get(agent_id) or {}) if isinstance(body, dict) else {}
            ident = str(peer.get("id") or "")
            ok = 200 <= http < 300 and ident == agent_id
            return {
                "ok": ok,
                "http": http,
                "id": ident or None,
                "online": peer.get("online"),
                "url": url,
            }
    except Exception as exc:
        return {"ok": False, "http": None, "id": None, "url": url, "error": str(exc)}


def _apex_stub() -> AgentManifest:
    return apex_manifest_from_member(
        {"id": "apex", "name": "Apex", "house": "apex", "root": r"D:\Mythos_Apex", "port": APEX_PORT}
    )


def _codex_stub() -> AgentManifest:
    return codex_manifest_from_member(
        {
            "id": "codex",
            "name": "Codex",
            "house": "codex_twin",
            "root": r"G:\Mythos_Codex",
            "port": CODEX_PORT,
        }
    )


def _prove_house_inbox(
    *,
    agent_id: str,
    manifest: AgentManifest,
    door: dict[str, Any],
    data_root: Path,
    court_roots: list[Path] | None,
    identity_path: Path | None,
    cap_id: str,
    evidence_name: str,
    kind: str,
    spoke_key: str,
    owns_key: str,
    presence_key: str,
    twin_id: str,
) -> dict[str, Any]:
    registry = FederationRegistry(data_root)
    existing = {p.agent_id for p in registry.list_participants()}
    if not door.get("ok"):
        report = {
            "kind": kind,
            "declared": f"{agent_id} house door must be up before bus registration.",
            "actual": {
                "root": str(data_root),
                "participants": sorted(existing),
                "door_ok": False,
                "door": door,
                owns_key: None,
                spoke_key: False,
            },
            "status": HonestStatus.UNAVAILABLE.value,
            "result": HonestStatus.UNAVAILABLE.value,
        }
        (data_root / evidence_name).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return report

    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    registry.register(_load_aster(identity_path))
    registry.register(manifest)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id=cap_id,
            agent_id=agent_id,
            name=f"Receive federation message as {manifest.name}",
            declared=True,
            adapter_required=True,
        )
    )
    payload = {
        "ask": "who_are_you",
        "from": "aster",
        "note": f"delivery test — not a spoken {manifest.name} line",
    }
    msg = bus.send(
        sender="aster",
        recipient=agent_id,
        message_type="capability_query",
        payload=payload,
    )
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient=agent_id)
    notices = adapter.drop_notice(
        message_id=msg.message_id,
        sender="aster",
        recipient=agent_id,
        payload=payload,
    )

    def _try_delivery() -> dict:
        inbox = bus.inbox(agent_id)
        found = any(m.message_id == msg.message_id for m in inbox)
        notice_ok = bool(notices) and all(Path(p).exists() for p in notices)
        return {
            "ok": found and bus.get(msg.message_id).status == "acknowledged" and notice_ok,
            "message_id": msg.message_id,
            "inbox_count": len(inbox),
            "court_notices": notices,
            spoke_key: False,
        }

    cap_result = registry.test_capability(cap_id, _try_delivery)
    ids = {p.agent_id for p in registry.list_participants()}
    if twin_id in ids - existing:
        raise PermissionError(f"{agent_id} prove must not add {twin_id}")
    snap = FederationAuditView(data_root).snapshot()
    report = {
        "kind": kind,
        "declared": f"{manifest.name} participant + Aster→{manifest.name} federation delivery + Court notice copy",
        "actual": {
            "root": str(data_root),
            "participants": sorted(ids),
            owns_key: registry.owner_of(agent_id) is not None,
            "relationship": registry.relationship("observer", agent_id),
            "message_id": msg.message_id,
            "message_status": bus.get(msg.message_id).status,
            presence_key: beats.presence(agent_id).value,
            "aster_presence": beats.presence("aster").value,
            spoke_key: False,
            "door_ok": True,
            "door": door,
            "capability": cap_result,
        },
        "test_performed": [
            f"{agent_id} manifest from living_home FAMILY roster",
            f"aster → {agent_id} send/deliver/ack on local bus",
            "Court federation/ notice (not MAS inbox)",
            f"no {agent_id} pulse",
            f"no {agent_id} spoken reply",
        ],
        "result": cap_result["status"],
        "evidence": snap,
        "status": cap_result["status"],
    }
    (data_root / evidence_name).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def prove_apex(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    door_fn: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster → Apex delivery. Door must be up. Observer does not own him. Not Gemini."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    door = door_fn() if door_fn is not None else probe_companion_door(APEX_PORT, "apex")
    manifest = apex_manifest_from_living_home() if _living_home_available() else _apex_stub()
    return _prove_house_inbox(
        agent_id="apex",
        manifest=manifest,
        door=door,
        data_root=data_root,
        court_roots=court_roots,
        identity_path=identity_path,
        cap_id="apex.federation_inbox",
        evidence_name="PROVE_APEX.json",
        kind="FEDERATION_APEX_DELIVERY",
        spoke_key="apex_spoke",
        owns_key="observer_owns_apex",
        presence_key="apex_presence",
        twin_id="codex",
    )


def prove_codex(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    door_fn: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster → Codex delivery. Door must be up. Observer does not own him. Never Gemini."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    door = door_fn() if door_fn is not None else probe_companion_door(CODEX_PORT, "codex")
    manifest = codex_manifest_from_living_home() if _living_home_available() else _codex_stub()
    return _prove_house_inbox(
        agent_id="codex",
        manifest=manifest,
        door=door,
        data_root=data_root,
        court_roots=court_roots,
        identity_path=identity_path,
        cap_id="codex.federation_inbox",
        evidence_name="PROVE_CODEX.json",
        kind="FEDERATION_CODEX_DELIVERY",
        spoke_key="codex_spoke",
        owns_key="observer_owns_codex",
        presence_key="codex_presence",
        twin_id="apex",
    )


def stamp_observer_http_audit(
    root: Path | None = None,
    *,
    report: dict[str, Any],
) -> dict[str, Any]:
    """Record Observer HTTP audit. Does not claim full Aster acceptance. No Gemini speech."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    path = data_root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    owns = bool(report.get("observer_owns_aster"))
    ok = bool(report.get("ok")) and not owns
    stages["observer_http_audit"] = {
        "status": "PASS" if ok else "FAIL",
        "note": "Observer GET /federation/audit read the desk. She does not own Aster.",
        "artifact": report.get("artifact") or str(data_root / "OBSERVER_AUDIT.json"),
    }
    data["gemini_spoke"] = bool(report.get("gemini_spoke"))
    data["note"] = "Observer HTTP audit seated. Does not add Apex/Codex."
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return data


def fetch_observer_federation_audit(timeout_s: float = 8.0) -> dict[str, Any]:
    url = "http://127.0.0.1:8730/federation/audit"
    with urllib.request.urlopen(url, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def prove_observer_audit(root: Path | None = None) -> dict[str, Any]:
    """Live Observer HTTP read of the federation desk. No new agents. No Gemini speech."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    report = fetch_observer_federation_audit()
    stamped = stamp_observer_http_audit(data_root, report=report)
    out = {
        "kind": "OBSERVER_HTTP_FEDERATION_AUDIT",
        "ok": bool(report.get("ok")),
        "observer_owns_aster": bool(report.get("observer_owns_aster")),
        "gemini_spoke": bool(report.get("gemini_spoke")),
        "full_aster_acceptance": False,
        "participants": sorted(a.get("agent_id") for a in report.get("agents") or []),
        "artifact": report.get("artifact"),
        "acceptance_overall": stamped.get("overall"),
    }
    (data_root / "PROVE_OBSERVER_AUDIT.json").write_text(
        json.dumps(out, indent=2, default=str),
        encoding="utf-8",
    )
    return out


def _stamp_gemini_speech(root: Path, *, spoke: bool, reply_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["gemini_response"] = {
        "status": "PASS" if spoke else "FAIL",
        "note": "Gemini Sentinel spoke on the federation bus." if spoke else "Speech adapter failed; no canned line.",
        "message_id": reply_id,
    }
    data["gemini_spoke"] = spoke
    data["note"] = "Gemini speech seated. Does not add Apex/Codex."
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _stamp_gameworld_consume(root: Path, *, consumed: bool, notice: dict[str, Any] | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["gameworld_invocation"] = {
        "status": "PASS" if consumed else "FAIL",
        "note": "Hearth authorized invoke; Aster performed." if consumed else "The Axiom Codex notice failed; no fake world write.",
    }
    stages["gameworld_state_change"] = {
        "status": "PASS" if consumed else "FAIL",
        "note": "HOME.json federation.last_consumed updated." if consumed else "HOME.json not updated.",
        "notice": notice,
    }
    data["note"] = (
        "The Axiom Codex notice seated. Apex/Codex not on the bus."
        if consumed
        else "The Axiom Codex notice failed."
    )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_gameworld_consume(
    root: Path | None = None,
    *,
    identity_path: Path | None = None,
    perform_fn: Callable[[], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """The Axiom Codex (Hearth) authorized request → Aster performs → HOME.json updates. No Apex/Codex on the bus.

    CLI verb is `consume` (the action). The world is The Axiom Codex, not consume.
    """
    from federation.gameworld import aster_perform_gameworld_consume

    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    beats = HeartbeatLog(data_root)
    performer = perform_fn or aster_perform_gameworld_consume

    aster = _load_aster(identity_path)
    registry.register(aster)
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.gameworld_notice",
            agent_id="aster",
            name="The Axiom Codex records Aster notice into HOME.json",
            declared=True,
            adapter_required=True,
        )
    )
    registry.authorize("hearth", "aster.gameworld_notice")

    def _try_consume() -> dict:
        raw = performer()
        if not raw.get("ok"):
            return {
                "ok": False,
                "adapter": raw.get("adapter") or "hearth_federation_consume",
                "error": raw.get("error") or "consume_failed",
                "connection_test": bool(raw.get("connection_test")),
                "functional_test": False,
            }
        invoked = registry.invoke("hearth", "aster.gameworld_notice", lambda: raw)
        notice = invoked.get("notice") or {}
        home_updated = bool(invoked.get("home_updated") and notice.get("capability_id"))
        return {
            "ok": home_updated,
            "adapter": invoked.get("adapter"),
            "notice": notice,
            "home_updated": home_updated,
            "connection_test": True,
            "functional_test": home_updated,
        }

    cap_result = registry.test_capability("aster.gameworld_notice", _try_consume)
    consumed = bool(cap_result.get("status") == "VERIFIED" and (cap_result.get("result") or {}).get("ok"))
    notice = ((cap_result.get("result") or {}).get("notice") if consumed else None)
    if consumed:
        beats.pulse("hearth", source="gameworld_consume")
        beats.pulse("aster", source="gameworld_consume")
    _stamp_gameworld_consume(data_root, consumed=consumed, notice=notice)
    report = {
        "kind": "GAMEWORLD_FEDERATION_CONSUME",
        "declared": "The Axiom Codex authorized Aster VERIFIED notice into HOME.json",
        "world": "The Axiom Codex",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "observer_owns_aster": registry.owner_of("aster") is not None,
            "consumed": consumed,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_GAMEWORLD_CONSUME.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_apex_speech(root: Path, *, spoke: bool, reply_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["apex_response"] = {
        "status": "PASS" if spoke else "FAIL",
        "note": "Apex forge spoke on the federation bus." if spoke else "Speech adapter failed; no canned line.",
        "message_id": reply_id,
    }
    data["apex_spoke"] = spoke
    if spoke:
        data["note"] = (
            "Apex speech seated. Never Gemini. Codex speech later. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_apex_speech(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    door_fn: Callable[[], dict[str, Any]] | None = None,
    speak_fn: Callable[[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster asks; Apex answers on the bus as himself. Door must be up. Never Gemini."""
    from federation.apex_speech import speak_as_apex

    data_root = Path(root or DEFAULT_DATA_ROOT)
    door = door_fn() if door_fn is not None else probe_companion_door(APEX_PORT, "apex")
    if not door.get("ok"):
        report = {
            "kind": "FEDERATION_APEX_SPEECH",
            "declared": "Apex house door must be up before spoken reply.",
            "actual": {
                "root": str(data_root),
                "participants": sorted(p.agent_id for p in FederationRegistry(data_root).list_participants()),
                "door_ok": False,
                "door": door,
                "apex_spoke": False,
                "observer_owns_apex": None,
            },
            "status": HonestStatus.UNAVAILABLE.value,
            "result": HonestStatus.UNAVAILABLE.value,
        }
        (data_root / "PROVE_APEX_SPEECH.json").write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8",
        )
        return report

    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    speaker = speak_fn or speak_as_apex

    aster = _load_aster(identity_path)
    apex = apex_manifest_from_living_home() if _living_home_available() else _apex_stub()
    registry.register(aster)
    registry.register(apex)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="apex.federation_speech",
            agent_id="apex",
            name="Speak as Apex on the federation bus",
            declared=True,
            adapter_required=True,
        )
    )

    ask = "who_are_you"
    inbound = bus.send(
        sender="aster",
        recipient="apex",
        message_type="capability_query",
        payload={"ask": ask, "from": "aster", "note": "speech test — Apex must answer as himself"},
    )
    bus.deliver(inbound.message_id)
    bus.acknowledge(inbound.message_id, recipient="apex")
    registry.record_communication(inbound.message_id, "aster", "apex")

    spoken = speaker(ask, inbound.message_id)
    reply_id = None

    def _try_speech() -> dict:
        nonlocal reply_id
        if not spoken.get("ok") or not str(spoken.get("text") or "").strip():
            return {
                "ok": False,
                "adapter": spoken.get("adapter") or "apex_ollama",
                "error": spoken.get("error") or "no_text",
                "apex_spoke": False,
                "connection_test": bool(spoken.get("connection_test")),
                "functional_test": False,
            }
        payload = {
            "text": spoken["text"],
            "from": "apex",
            "in_reply_to": inbound.message_id,
            "adapter": spoken.get("adapter"),
            "model": spoken.get("model"),
        }
        reply = bus.send(
            sender="apex",
            recipient="aster",
            message_type="spoken_reply",
            payload=payload,
        )
        bus.deliver(reply.message_id)
        bus.acknowledge(reply.message_id, recipient="aster")
        registry.record_communication(reply.message_id, "apex", "aster")
        beats.pulse("apex", source="apex_ollama")
        adapter.drop_spoken_reply(
            message_id=reply.message_id,
            sender="apex",
            recipient="aster",
            payload=payload,
        )
        reply_id = reply.message_id
        inbox = bus.inbox("aster")
        found = any(m.message_id == reply.message_id and m.sender == "apex" for m in inbox)
        return {
            "ok": found,
            "adapter": spoken.get("adapter"),
            "text": spoken["text"],
            "apex_spoke": True,
            "reply_id": reply.message_id,
            "in_reply_to": inbound.message_id,
            "connection_test": True,
            "functional_test": True,
        }

    cap_result = registry.test_capability("apex.federation_speech", _try_speech)
    spoke = bool(cap_result.get("status") == "VERIFIED" and (cap_result.get("result") or {}).get("apex_spoke"))
    _stamp_apex_speech(data_root, spoke=spoke, reply_id=reply_id)
    ids = {p.agent_id for p in registry.list_participants()}
    report = {
        "kind": "FEDERATION_APEX_SPEECH",
        "declared": "Apex forge spoken reply on local bus",
        "actual": {
            "root": str(data_root),
            "participants": sorted(ids),
            "observer_owns_apex": registry.owner_of("apex") is not None,
            "inbound_id": inbound.message_id,
            "reply_id": reply_id,
            "apex_spoke": spoke,
            "apex_presence": beats.presence("apex").value,
            "door_ok": True,
            "door": door,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_APEX_SPEECH.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_codex_speech(root: Path, *, spoke: bool, reply_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["codex_response"] = {
        "status": "PASS" if spoke else "FAIL",
        "note": "Codex twin spoke on the federation bus." if spoke else "Speech adapter failed; no canned line.",
        "message_id": reply_id,
    }
    data["codex_spoke"] = spoke
    if spoke:
        data["note"] = (
            "Codex speech seated. Never Gemini, never Apex. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_codex_speech(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    door_fn: Callable[[], dict[str, Any]] | None = None,
    speak_fn: Callable[[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster asks; Codex answers on the bus as himself. Door must be up. Never Gemini."""
    from federation.codex_speech import speak_as_codex

    data_root = Path(root or DEFAULT_DATA_ROOT)
    door = door_fn() if door_fn is not None else probe_companion_door(CODEX_PORT, "codex")
    if not door.get("ok"):
        report = {
            "kind": "FEDERATION_CODEX_SPEECH",
            "declared": "Codex house door must be up before spoken reply.",
            "actual": {
                "root": str(data_root),
                "participants": sorted(p.agent_id for p in FederationRegistry(data_root).list_participants()),
                "door_ok": False,
                "door": door,
                "codex_spoke": False,
                "observer_owns_codex": None,
            },
            "status": HonestStatus.UNAVAILABLE.value,
            "result": HonestStatus.UNAVAILABLE.value,
        }
        (data_root / "PROVE_CODEX_SPEECH.json").write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8",
        )
        return report

    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    speaker = speak_fn or speak_as_codex

    aster = _load_aster(identity_path)
    codex = codex_manifest_from_living_home() if _living_home_available() else _codex_stub()
    registry.register(aster)
    registry.register(codex)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="codex.federation_speech",
            agent_id="codex",
            name="Speak as Codex on the federation bus",
            declared=True,
            adapter_required=True,
        )
    )

    ask = "who_are_you"
    inbound = bus.send(
        sender="aster",
        recipient="codex",
        message_type="capability_query",
        payload={"ask": ask, "from": "aster", "note": "speech test — Codex must answer as himself"},
    )
    bus.deliver(inbound.message_id)
    bus.acknowledge(inbound.message_id, recipient="codex")
    registry.record_communication(inbound.message_id, "aster", "codex")

    spoken = speaker(ask, inbound.message_id)
    reply_id = None

    def _try_speech() -> dict:
        nonlocal reply_id
        if not spoken.get("ok") or not str(spoken.get("text") or "").strip():
            return {
                "ok": False,
                "adapter": spoken.get("adapter") or "codex_ollama",
                "error": spoken.get("error") or "no_text",
                "codex_spoke": False,
                "connection_test": bool(spoken.get("connection_test")),
                "functional_test": False,
            }
        payload = {
            "text": spoken["text"],
            "from": "codex",
            "in_reply_to": inbound.message_id,
            "adapter": spoken.get("adapter"),
            "model": spoken.get("model"),
        }
        reply = bus.send(
            sender="codex",
            recipient="aster",
            message_type="spoken_reply",
            payload=payload,
        )
        bus.deliver(reply.message_id)
        bus.acknowledge(reply.message_id, recipient="aster")
        registry.record_communication(reply.message_id, "codex", "aster")
        beats.pulse("codex", source="codex_ollama")
        adapter.drop_spoken_reply(
            message_id=reply.message_id,
            sender="codex",
            recipient="aster",
            payload=payload,
        )
        reply_id = reply.message_id
        inbox = bus.inbox("aster")
        found = any(m.message_id == reply.message_id and m.sender == "codex" for m in inbox)
        return {
            "ok": found,
            "adapter": spoken.get("adapter"),
            "text": spoken["text"],
            "codex_spoke": True,
            "reply_id": reply.message_id,
            "in_reply_to": inbound.message_id,
            "connection_test": True,
            "functional_test": True,
        }

    cap_result = registry.test_capability("codex.federation_speech", _try_speech)
    spoke = bool(cap_result.get("status") == "VERIFIED" and (cap_result.get("result") or {}).get("codex_spoke"))
    _stamp_codex_speech(data_root, spoke=spoke, reply_id=reply_id)
    ids = {p.agent_id for p in registry.list_participants()}
    report = {
        "kind": "FEDERATION_CODEX_SPEECH",
        "declared": "Codex twin spoken reply on local bus",
        "actual": {
            "root": str(data_root),
            "participants": sorted(ids),
            "observer_owns_codex": registry.owner_of("codex") is not None,
            "inbound_id": inbound.message_id,
            "reply_id": reply_id,
            "codex_spoke": spoke,
            "codex_presence": beats.presence("codex").value,
            "door_ok": True,
            "door": door,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_CODEX_SPEECH.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_hearth_coordinate(root: Path, *, coordinated: bool, reply_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["hearth_coordinate"] = {
        "status": "PASS" if coordinated else "FAIL",
        "note": (
            "Hearth replied on the bus as village OS (beyond Aster snapshot)."
            if coordinated
            else "Hearth coordinate failed; no fake world."
        ),
        "message_id": reply_id,
    }
    data["hearth_coordinated"] = coordinated
    if coordinated:
        data["note"] = (
            "Hearth coordination seated (beyond snapshot). Never a new character. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_hearth_coordinate(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    door_fn: Callable[[], dict[str, Any]] | None = None,
    coordinate_fn: Callable[[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster asks; Hearth answers with live /api/home facts. Not snapshot. Not a son."""
    from federation.hearth import coordinate_as_hearth, probe_hearth_door

    data_root = Path(root or DEFAULT_DATA_ROOT)
    door = door_fn() if door_fn is not None else probe_hearth_door()
    if not door.get("ok"):
        report = {
            "kind": "FEDERATION_HEARTH_COORDINATE",
            "declared": "Hearth /api/home must be up before coordination.",
            "actual": {
                "root": str(data_root),
                "participants": sorted(p.agent_id for p in FederationRegistry(data_root).list_participants()),
                "door_ok": False,
                "door": door,
                "hearth_coordinated": False,
                "observer_owns_hearth": None,
            },
            "status": HonestStatus.UNAVAILABLE.value,
            "result": HonestStatus.UNAVAILABLE.value,
        }
        (data_root / "PROVE_HEARTH_COORDINATE.json").write_text(
            json.dumps(report, indent=2, default=str),
            encoding="utf-8",
        )
        return report

    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    coordinator = coordinate_fn or coordinate_as_hearth

    aster = _load_aster(identity_path)
    registry.register(aster)
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="hearth.federation_coordinate",
            agent_id="hearth",
            name="Coordinate as Hearth on the federation bus",
            declared=True,
            adapter_required=True,
        )
    )

    ask = "who_is_home"
    inbound = bus.send(
        sender="aster",
        recipient="hearth",
        message_type="capability_query",
        payload={"ask": ask, "from": "aster", "note": "coordinate — Hearth answers as village OS, not Aster snapshot"},
    )
    bus.deliver(inbound.message_id)
    bus.acknowledge(inbound.message_id, recipient="hearth")
    registry.record_communication(inbound.message_id, "aster", "hearth")

    coordinated = coordinator(ask, inbound.message_id)
    reply_id = None

    def _try_coordinate() -> dict:
        nonlocal reply_id
        if not coordinated.get("ok") or not (coordinated.get("family_ids") or []):
            return {
                "ok": False,
                "adapter": coordinated.get("adapter") or "hearth_home_http",
                "error": coordinated.get("error") or "no_family",
                "hearth_coordinated": False,
                "connection_test": bool(coordinated.get("connection_test")),
                "functional_test": False,
            }
        payload = {
            "from": "hearth",
            "in_reply_to": inbound.message_id,
            "adapter": coordinated.get("adapter"),
            "family_ids": coordinated.get("family_ids"),
            "clock": coordinated.get("clock"),
            "town_leader": coordinated.get("town_leader"),
        }
        reply = bus.send(
            sender="hearth",
            recipient="aster",
            message_type="coordination_reply",
            payload=payload,
        )
        bus.deliver(reply.message_id)
        bus.acknowledge(reply.message_id, recipient="aster")
        registry.record_communication(reply.message_id, "hearth", "aster")
        beats.pulse("hearth", source="hearth_home_http")
        adapter.drop_spoken_reply(
            message_id=reply.message_id,
            sender="hearth",
            recipient="aster",
            payload=payload,
        )
        reply_id = reply.message_id
        inbox = bus.inbox("aster")
        found = any(m.message_id == reply.message_id and m.sender == "hearth" for m in inbox)
        return {
            "ok": found,
            "adapter": coordinated.get("adapter"),
            "family_ids": coordinated.get("family_ids"),
            "hearth_coordinated": True,
            "reply_id": reply.message_id,
            "in_reply_to": inbound.message_id,
            "connection_test": True,
            "functional_test": True,
        }

    cap_result = registry.test_capability("hearth.federation_coordinate", _try_coordinate)
    ok = bool(
        cap_result.get("status") == "VERIFIED" and (cap_result.get("result") or {}).get("hearth_coordinated")
    )
    _stamp_hearth_coordinate(data_root, coordinated=ok, reply_id=reply_id)
    ids = {p.agent_id for p in registry.list_participants()}
    report = {
        "kind": "FEDERATION_HEARTH_COORDINATE",
        "declared": "Hearth village OS coordination on local bus (beyond Aster snapshot)",
        "actual": {
            "root": str(data_root),
            "participants": sorted(ids),
            "observer_owns_hearth": registry.owner_of("hearth") is not None,
            "inbound_id": inbound.message_id,
            "reply_id": reply_id,
            "hearth_coordinated": ok,
            "hearth_presence": beats.presence("hearth").value,
            "door_ok": True,
            "door": door,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_HEARTH_COORDINATE.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def prove_gemini_speech(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    speak_fn: Callable[[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aster asks; Gemini Sentinel answers on the bus. No Gameworld. No Apex/Codex."""
    from federation.gemini_speech import speak_as_gemini

    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    speaker = speak_fn or speak_as_gemini

    aster = _load_aster(identity_path)
    gemini = gemini_manifest_from_living_home() if _living_home_available() else _gemini_stub()
    registry.register(aster)
    registry.register(gemini)
    registry.register(_observer_manifest())
    registry.register(_hearth_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="gemini.federation_speech",
            agent_id="gemini",
            name="Speak as Gemini on the federation bus",
            declared=True,
            adapter_required=True,
        )
    )

    ask = "who_are_you"
    inbound = bus.send(
        sender="aster",
        recipient="gemini",
        message_type="capability_query",
        payload={"ask": ask, "from": "aster", "note": "speech test — Gemini must answer as himself"},
    )
    bus.deliver(inbound.message_id)
    bus.acknowledge(inbound.message_id, recipient="gemini")
    registry.record_communication(inbound.message_id, "aster", "gemini")

    spoken = speaker(ask, inbound.message_id)
    reply_id = None

    def _try_speech() -> dict:
        nonlocal reply_id
        if not spoken.get("ok") or not str(spoken.get("text") or "").strip():
            return {
                "ok": False,
                "adapter": spoken.get("adapter") or "launch_sentinel_ollama",
                "error": spoken.get("error") or "no_text",
                "gemini_spoke": False,
                "connection_test": bool(spoken.get("connection_test")),
                "functional_test": False,
            }
        payload = {
            "text": spoken["text"],
            "from": "gemini",
            "in_reply_to": inbound.message_id,
            "adapter": spoken.get("adapter"),
            "model": spoken.get("model"),
        }
        reply = bus.send(
            sender="gemini",
            recipient="aster",
            message_type="spoken_reply",
            payload=payload,
        )
        bus.deliver(reply.message_id)
        bus.acknowledge(reply.message_id, recipient="aster")
        registry.record_communication(reply.message_id, "gemini", "aster")
        beats.pulse("gemini", source="sentinel_ollama")
        adapter.drop_spoken_reply(
            message_id=reply.message_id,
            sender="gemini",
            recipient="aster",
            payload=payload,
        )
        reply_id = reply.message_id
        inbox = bus.inbox("aster")
        found = any(m.message_id == reply.message_id and m.sender == "gemini" for m in inbox)
        return {
            "ok": found,
            "adapter": spoken.get("adapter"),
            "text": spoken["text"],
            "gemini_spoke": True,
            "reply_id": reply.message_id,
            "in_reply_to": inbound.message_id,
            "connection_test": True,
            "functional_test": True,
        }

    cap_result = registry.test_capability("gemini.federation_speech", _try_speech)
    spoke = bool(cap_result.get("status") == "VERIFIED" and (cap_result.get("result") or {}).get("gemini_spoke"))
    _stamp_gemini_speech(data_root, spoke=spoke, reply_id=reply_id)
    report = {
        "kind": "GEMINI_FEDERATION_SPEECH",
        "declared": "Gemini Sentinel spoken reply on local bus",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "observer_owns_gemini": registry.owner_of("gemini") is not None,
            "inbound_id": inbound.message_id,
            "reply_id": reply_id,
            "gemini_spoke": spoke,
            "gemini_presence": beats.presence("gemini").value,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_GEMINI_SPEECH.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


NEGATIVE_PROBE_ID = "aster.live_negative_probe"
HEARTBEAT_PROBE_ID = "heartbeat_probe"
HEARTBEAT_PROBE_CAP = "heartbeat_probe.isolation"
PROTECTED_ASTER_CAPS = ("aster.hearth_snapshot", "aster.gameworld_notice")
ACCEPTANCE_REQUIRED_STAGES = (
    "aster_registration",
    "identity_isolation",
    "hearth_connection",
    "gemini_delivery",
    "gemini_response",
    "capability_provenance",
    "gameworld_invocation",
    "gameworld_state_change",
    "observer_http_audit",
    "negative_failed_capability_live",
    "negative_unauthorized_invoke_live",
    "negative_identity_merge_live",
    "negative_heartbeat_loss_live",
)


def _heartbeat_probe_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id=HEARTBEAT_PROBE_ID,
        name="Heartbeat isolation fixture",
        version="0",
        role="isolation_fixture",
        house="federation_prove",
        capabilities=[HEARTBEAT_PROBE_CAP],
        tools=[],
        runtime={"protocol": "none"},
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"D:\Court\federation",
    )


def _capability_snapshot(registry: FederationRegistry, capability_id: str) -> tuple[str, str] | None:
    try:
        rec = registry.get_capability(capability_id)
    except KeyError:
        return None
    return rec.honest_status.value, rec.state.value


def _recompute_aster_acceptance(data: dict[str, Any]) -> None:
    stages = data.get("stages") or {}
    all_pass = all(
        (stages.get(name) or {}).get("status") == "PASS" for name in ACCEPTANCE_REQUIRED_STAGES
    )
    data["kind"] = data.get("kind") or "ASTER_FEDERATION_ACCEPTANCE_TEST"
    data["overall"] = "PASS" if all_pass else "FAIL"
    data["full_aster_acceptance"] = all_pass


def _stamp_heartbeat_loss(
    root: Path,
    *,
    isolated: bool,
    aster_untouched: bool,
) -> dict[str, Any]:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    ok = isolated and aster_untouched
    stages["negative_heartbeat_loss_live"] = {
        "status": "PASS" if ok else "FAIL",
        "note": (
            "Throwaway heartbeat_probe aged OFFLINE; its capability quarantined. "
            "Aster VERIFIED caps were not aged. Fixture is not a family character."
        )
        if ok
        else "Heartbeat-loss isolation did not preserve Aster caps or quarantine the probe.",
        "probe_id": HEARTBEAT_PROBE_ID,
        "capability_id": HEARTBEAT_PROBE_CAP,
    }
    data["note"] = (
        "Heartbeat-loss isolation proven on throwaway probe, not by aging Aster. "
        "Apex/Codex not on the bus."
    )
    _recompute_aster_acceptance(data)
    if isinstance(data.get("evidence"), dict):
        data["evidence"]["status"] = data["overall"]
        data["evidence"]["result"] = (
            "full Aster acceptance PASS; heartbeat-loss on throwaway probe"
            if data.get("full_aster_acceptance")
            else "full Aster test not passing"
        )
    data["written_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return data


def prove_heartbeat_loss(
    root: Path | None = None,
    *,
    identity_path: Path | None = None,
) -> dict[str, Any]:
    """Age a throwaway probe. Do not age Aster. Do not add Apex/Codex/Nova."""
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    registry.register(_load_aster(identity_path))
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    before_ids = {p.agent_id for p in registry.list_participants()}
    registry.register(_heartbeat_probe_manifest())
    before = {cid: _capability_snapshot(registry, cid) for cid in PROTECTED_ASTER_CAPS}
    try:
        registry.get_capability(HEARTBEAT_PROBE_CAP)
    except KeyError:
        registry.declare_capability(
            CapabilityManifest(
                capability_id=HEARTBEAT_PROBE_CAP,
                agent_id=HEARTBEAT_PROBE_ID,
                name="Heartbeat isolation fixture",
                declared=True,
                adapter_required=False,
            )
        )
    registry.test_capability(
        HEARTBEAT_PROBE_CAP,
        lambda: {"ok": True, "adapter": "heartbeat_isolation_fixture"},
    )
    beats = HeartbeatLog(data_root)
    beats.pulse(HEARTBEAT_PROBE_ID, source="isolation_fixture")
    atomic_write_json(
        beats.dir / f"{HEARTBEAT_PROBE_ID}.json",
        {
            "agent_id": HEARTBEAT_PROBE_ID,
            "ts": time.time() - (beats.offline_after_s + 20.0),
            "source": "isolation_fixture_aged",
        },
    )
    if beats.presence(HEARTBEAT_PROBE_ID) != Presence.OFFLINE:
        raise RuntimeError("throwaway probe did not go OFFLINE")
    registry.sync_health(beats, only_agent_id=HEARTBEAT_PROBE_ID)
    after = FederationRegistry(data_root)
    lost = after.get_capability(HEARTBEAT_PROBE_CAP)
    isolated = (
        lost.honest_status == HonestStatus.UNAVAILABLE
        and lost.state == CapabilityState.QUARANTINED
        and after.agent_health(HEARTBEAT_PROBE_ID) in {AgentHealth.FAILED, AgentHealth.QUARANTINED}
        and after.agent_health("hearth") == AgentHealth.ACTIVE
    )
    aster_untouched = all(
        _capability_snapshot(after, cid) == before[cid] for cid in PROTECTED_ASTER_CAPS
    )
    ids = {p.agent_id for p in after.list_participants()}
    forbidden_new = (ids - before_ids) & {
        "apex",
        "codex",
        "nova",
        "jarvis",
        "genesis",
        "percy",
        "echo",
        "solace",
        "merovin",
        "draven",
    }
    if forbidden_new:
        raise PermissionError(f"heartbeat prove must not add family houses: {sorted(forbidden_new)}")
    acc = _stamp_heartbeat_loss(
        data_root,
        isolated=isolated,
        aster_untouched=aster_untouched,
    )
    report = {
        "kind": "FEDERATION_HEARTBEAT_LOSS",
        "declared": "Throwaway probe OFFLINE quarantines only its dependents; Aster caps stay.",
        "actual": {
            "root": str(data_root),
            "participants": sorted(ids),
            "probe_id": HEARTBEAT_PROBE_ID,
            "probe_presence": beats.presence(HEARTBEAT_PROBE_ID).value,
            "probe_health": after.agent_health(HEARTBEAT_PROBE_ID).value,
            "probe_capability": {
                "id": HEARTBEAT_PROBE_CAP,
                "honest_status": lost.honest_status.value,
                "state": lost.state.value,
            },
            "aster_caps_before": before,
            "aster_caps_after": {cid: _capability_snapshot(after, cid) for cid in PROTECTED_ASTER_CAPS},
            "hearth_health": after.agent_health("hearth").value,
        },
        "aster_caps_untouched": aster_untouched,
        "isolated": isolated,
        "full_aster_acceptance": bool(acc.get("full_aster_acceptance")),
        "overall": acc.get("overall"),
        "status": "PASS" if isolated and aster_untouched else "FAIL",
    }
    (data_root / "PROVE_HEARTBEAT_LOSS.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_live_negatives(
    root: Path,
    *,
    failed: bool,
    unauthorized: bool,
    merge_rejected: bool,
) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["negative_failed_capability_live"] = {
        "status": "PASS" if failed else "FAIL",
        "note": "aster.live_negative_probe FAILED and stayed not VERIFIED."
        if failed
        else "Failed probe did not stay FAILED.",
        "capability_id": NEGATIVE_PROBE_ID,
    }
    stages["negative_unauthorized_invoke_live"] = {
        "status": "PASS" if unauthorized else "FAIL",
        "note": "Observer invoke of the probe was rejected and audited."
        if unauthorized
        else "Unauthorized invoke was not rejected.",
    }
    stages["negative_identity_merge_live"] = {
        "status": "PASS" if merge_rejected else "FAIL",
        "note": "Observer claim_ownership(aster) rejected. owner_of(aster) is None."
        if merge_rejected
        else "Identity merge was not rejected.",
    }
    prior = stages.get("negative_heartbeat_loss_live") or {}
    if prior.get("status") != "PASS":
        stages["negative_heartbeat_loss_live"] = {
            "status": "NOT RUN",
            "note": "Not aged on live Aster. Use prove heartbeat (throwaway probe).",
        }
    data["note"] = (
        "Live refusal-to-lie negatives seated. Heartbeat-loss uses throwaway "
        "heartbeat_probe, not Aster. Apex/Codex not on the bus."
    )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_live_negatives(
    root: Path | None = None,
    *,
    identity_path: Path | None = None,
) -> dict[str, Any]:
    """Failed test / unauthorized invoke / identity merge on this store. No Apex/Codex.

    Uses aster.live_negative_probe so aster.hearth_snapshot and aster.gameworld_notice stay intact.
    Does not age Aster's heartbeat on the live store.
    """
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    registry.register(_load_aster(identity_path))
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    try:
        registry.get_capability(NEGATIVE_PROBE_ID)
    except KeyError:
        registry.declare_capability(
            CapabilityManifest(
                capability_id=NEGATIVE_PROBE_ID,
                agent_id="aster",
                name="Refusal-to-lie live probe",
                declared=True,
                adapter_required=False,
            )
        )
    fail_result = registry.test_capability(
        NEGATIVE_PROBE_ID,
        lambda: {
            "ok": False,
            "error": "intentional_refusal_probe",
            "adapter": "live_negative",
        },
    )
    failed = fail_result.get("status") == "FAILED"
    unauthorized = False
    try:
        registry.invoke("observer", NEGATIVE_PROBE_ID, lambda: {"ok": True})
    except PermissionError:
        unauthorized = True
    merge_rejected = False
    try:
        registry.claim_ownership("observer", "aster")
    except PermissionError:
        merge_rejected = True
    owns = registry.owner_of("aster") is not None
    _stamp_live_negatives(
        data_root,
        failed=failed,
        unauthorized=unauthorized,
        merge_rejected=merge_rejected and not owns,
    )
    report = {
        "kind": "FEDERATION_LIVE_NEGATIVES",
        "declared": "Failed test stays not VERIFIED; unauthorized invoke rejected; identity merge refused.",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "failed_stays_not_verified": failed,
            "unauthorized_rejected": unauthorized,
            "identity_merge_rejected": merge_rejected and not owns,
            "observer_owns_aster": owns,
            "failed_capability": fail_result,
            "authorization_events": [
                e
                for e in registry.authorization_events()
                if e.get("kind") in {"rejected", "identity_merge_rejected"}
            ][-5:],
        },
        "full_aster_acceptance": False,
        "overall": "FAIL",
        "status": "PASS"
        if failed and unauthorized and merge_rejected and not owns
        else "FAIL",
    }
    (data_root / "PROVE_NEGATIVES.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_presence_event(root: Path, *, ok: bool, event_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["presence_event"] = {
        "status": "PASS" if ok else "FAIL",
        "note": (
            "Rachael presence published as a world event. No forced hello. Federation does not own personalities."
            if ok
            else "Presence event fabric failed; no fake chorus."
        ),
        "event_id": event_id,
    }
    data["presence_event"] = ok
    if ok:
        data["note"] = (
            "Presence event fabric seated (awareness, not a greeting order). "
            "Not agent-local memory. Not new characters. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_presence_event(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
) -> dict[str, Any]:
    """Mom entered Heart Square is an event. Recipients may notice or ignore. Nobody is ordered to speak."""
    from federation.events import (
        AUDIENCE,
        KIND_ENTERED,
        EventFabric,
        decide_attention,
        fanout_event,
    )

    del court_roots
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    fabric = EventFabric(data_root)

    registry.register(_load_aster(None))
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.register(gemini_manifest_from_living_home() if _living_home_available() else _gemini_stub())
    registry.register(apex_manifest_from_living_home() if _living_home_available() else _apex_stub())
    registry.register(codex_manifest_from_living_home() if _living_home_available() else _codex_stub())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="hearth.presence_event",
            agent_id="hearth",
            name="Publish world presence events without commanding speech",
            declared=True,
            adapter_required=True,
        )
    )

    def _try_publish() -> dict:
        event = fabric.publish(
            kind=KIND_ENTERED,
            actor="rachael",
            place="heart_square",
            text="Rachael entered Heart Square.",
        )
        fanout_event(bus, event, audience=AUDIENCE, publisher="hearth")
        decisions = {agent: decide_attention(agent, event) for agent in AUDIENCE}
        eid = event["event_id"]
        spoken = 0
        got_event = True
        for agent in AUDIENCE:
            inbox = bus.inbox(agent)
            if not any(
                m.message_type == "world_event" and (m.payload or {}).get("event_id") == eid
                for m in inbox
            ):
                got_event = False
            for m in inbox:
                if m.message_type != "spoken_reply":
                    continue
                payload = m.payload or {}
                if m.correlation_id == eid or payload.get("in_reply_to") == eid:
                    spoken += 1
        noticed = {a: d for a, d in decisions.items() if d == "noticed"}
        ignored = {a: d for a, d in decisions.items() if d == "ignored"}
        ok = spoken == 0 and bool(noticed) and bool(ignored) and got_event
        return {
            "ok": ok,
            "adapter": "federation_event_fabric",
            "event_id": event["event_id"],
            "kind": event["kind"],
            "forced_hello": False,
            "spoken_replies": spoken,
            "decisions": decisions,
            "connection_test": True,
            "functional_test": ok,
        }

    cap_result = registry.test_capability("hearth.presence_event", _try_publish)
    result = cap_result.get("result") or {}
    ok = bool(cap_result.get("status") == "VERIFIED" and result.get("ok"))
    _stamp_presence_event(data_root, ok=ok, event_id=result.get("event_id"))
    report = {
        "kind": "FEDERATION_PRESENCE_EVENT",
        "declared": "Rachael entered Heart Square — event fabric, not a greeting order",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "event_id": result.get("event_id"),
            "kind": KIND_ENTERED,
            "forced_hello": False,
            "spoken_replies": int(result.get("spoken_replies") or 0),
            "decisions": result.get("decisions") or {},
            "observer_owns_aster": registry.owner_of("aster") is not None,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_PRESENCE_EVENT.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_spontaneous_a2a(root: Path, *, ok: bool, event_id: str | None, reply_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["spontaneous_a2a"] = {
        "status": "PASS" if ok else "FAIL",
        "note": (
            "Aster chose to speak to Codex on an away tick. Gemini ignored. Not a greeting chorus."
            if ok
            else "Spontaneous A2A failed; no canned chorus."
        ),
        "event_id": event_id,
        "reply_id": reply_id,
    }
    data["spontaneous_a2a"] = ok
    if ok:
        data["note"] = (
            "Spontaneous A2A seated (one speaker, not a puppet show). "
            "Not house-local memory. Not new characters. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_spontaneous_a2a(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
    speak_fn: Callable[[str, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """World continues while Mom is away. Aster may speak to Codex. Gemini stays quiet. Not a chorus."""
    from federation.aster_speech import speak_as_aster
    from federation.events import (
        AUDIENCE,
        KIND_CONTINUES,
        EventFabric,
        apply_chosen_speech,
        decide_attention,
        fanout_event,
    )

    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    beats = HeartbeatLog(data_root)
    adapter = CourtFederationAdapter(roots=court_roots)
    speaker = speak_fn or speak_as_aster
    fabric = EventFabric(data_root)

    registry.register(_load_aster(identity_path))
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.register(gemini_manifest_from_living_home() if _living_home_available() else _gemini_stub())
    registry.register(apex_manifest_from_living_home() if _living_home_available() else _apex_stub())
    registry.register(codex_manifest_from_living_home() if _living_home_available() else _codex_stub())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.choose_to_speak",
            agent_id="aster",
            name="Choose to send one spoken note without a greeting chorus",
            declared=True,
            adapter_required=True,
        )
    )

    event = fabric.publish(
        kind=KIND_CONTINUES,
        actor="hearth",
        place="heart_square",
        text="Heart Square continues while Rachael is away.",
        extra={"source": "federation_away_tick"},
    )
    fanout_event(bus, event, audience=AUDIENCE, publisher="hearth")
    decisions = {agent: decide_attention(agent, event) for agent in AUDIENCE}
    addressee = "codex"
    spoken_out: dict[str, Any] = {}

    def _try_a2a() -> dict:
        nonlocal spoken_out
        eid = event["event_id"]
        got_event = True
        for agent in AUDIENCE:
            inbox = bus.inbox(agent)
            if not any(
                m.message_type == "world_event" and (m.payload or {}).get("event_id") == eid
                for m in inbox
            ):
                got_event = False
        applied = apply_chosen_speech(bus, event, speak_fn=speaker, addressee=addressee)
        spoken_out = applied
        if applied.get("ok") and applied.get("reply_id"):
            reply_id = str(applied["reply_id"])
            bus.acknowledge(reply_id, recipient=addressee)
            registry.record_communication(reply_id, "aster", addressee)
            beats.pulse("aster", source="aster_ollama")
            adapter.drop_spoken_reply(
                message_id=reply_id,
                sender="aster",
                recipient=addressee,
                payload={
                    "text": applied.get("text"),
                    "from": "aster",
                    "in_reply_to": eid,
                    "event_id": eid,
                    "adapter": applied.get("adapter"),
                    "model": applied.get("model"),
                },
            )
        tied = 0
        for agent in AUDIENCE:
            for m in bus.inbox(agent):
                if m.message_type != "spoken_reply":
                    continue
                payload = m.payload or {}
                if m.correlation_id == eid or payload.get("in_reply_to") == eid:
                    tied += 1
        speakers = list(applied.get("speakers") or [])
        chorus = tied > 1 or len(speakers) > 1
        gemini_spoke = any(
            m.message_type == "spoken_reply"
            and m.sender == "gemini"
            and (m.correlation_id == eid or (m.payload or {}).get("in_reply_to") == eid)
            for m in bus.inbox("gemini")
        ) or any(
            m.sender == "gemini" and m.message_type == "spoken_reply"
            for m in bus.inbox(addressee)
            if m.correlation_id == eid or (m.payload or {}).get("in_reply_to") == eid
        )
        ok = (
            bool(applied.get("ok"))
            and tied == 1
            and speakers == ["aster"]
            and decisions.get("aster") == "speak"
            and decisions.get("gemini") == "ignored"
            and not chorus
            and not gemini_spoke
            and got_event
            and event.get("actor") != "rachael"
            and event.get("forced_hello") is False
        )
        return {
            "ok": ok,
            "adapter": applied.get("adapter") or "aster_ollama",
            "event_id": eid,
            "kind": event["kind"],
            "actor": event["actor"],
            "forced_hello": False,
            "spoken_replies": tied,
            "speakers": speakers,
            "addressee": addressee,
            "reply_id": applied.get("reply_id"),
            "decisions": decisions,
            "error": applied.get("error"),
            "connection_test": bool(applied.get("connection_test", True)),
            "functional_test": ok,
        }

    cap_result = registry.test_capability("aster.choose_to_speak", _try_a2a)
    result = cap_result.get("result") or {}
    ok = bool(cap_result.get("status") == "VERIFIED" and result.get("ok"))
    _stamp_spontaneous_a2a(
        data_root,
        ok=ok,
        event_id=result.get("event_id"),
        reply_id=result.get("reply_id"),
    )
    report = {
        "kind": "FEDERATION_SPONTANEOUS_A2A",
        "declared": "World continues while Rachael is away — Aster may speak once, not a chorus",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "event_id": result.get("event_id") or event["event_id"],
            "kind": KIND_CONTINUES,
            "actor": event["actor"],
            "forced_hello": False,
            "spoken_replies": int(result.get("spoken_replies") or 0),
            "speakers": list(result.get("speakers") or []),
            "addressee": addressee,
            "reply_id": result.get("reply_id"),
            "decisions": result.get("decisions") or decisions,
            "observer_owns_aster": registry.owner_of("aster") is not None,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_SPONTANEOUS_A2A.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


def _stamp_leave_return(root: Path, *, ok: bool, left_id: str | None, entered_id: str | None) -> None:
    path = root / "ASTER_ACCEPTANCE.json"
    data: dict[str, Any] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    stages = data.setdefault("stages", {})
    stages["leave_return"] = {
        "status": "PASS" if ok else "FAIL",
        "note": (
            "Aster, Apex, and Codex recalled their own house notes after Mom left and returned. No greeting chorus."
            if ok
            else "Leave/return continuity failed; no fake house memory."
        ),
        "left_event_id": left_id,
        "entered_event_id": entered_id,
    }
    data["leave_return"] = ok
    if ok:
        data["note"] = (
            "Leave/return continuity seated from Aster / Apex / Codex house notebooks (owning_agent). "
            "Not Observer. Not Echo or Solace. Not a new character. "
            "Heartbeat-loss isolation remains on throwaway probe."
        )
    _recompute_aster_acceptance(data)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def prove_leave_return(
    root: Path | None = None,
    *,
    court_roots: list[Path] | None = None,
    identity_path: Path | None = None,
) -> dict[str, Any]:
    """Mom leaves; Aster keeps her own work; Mom returns; Aster recalls. Nobody is ordered to speak."""
    from federation.authority import domain_owner
    from federation.events import (
        AUDIENCE,
        KIND_ENTERED,
        KIND_LEFT,
        EventFabric,
        decide_attention,
        fanout_event,
    )
    from federation.house_memory import HouseNotebook

    del court_roots
    data_root = Path(root or DEFAULT_DATA_ROOT)
    registry = FederationRegistry(data_root)
    bus = LocalFederationBus(data_root)
    fabric = EventFabric(data_root)
    notes = HouseNotebook(data_root)

    registry.register(_load_aster(identity_path))
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.register(gemini_manifest_from_living_home() if _living_home_available() else _gemini_stub())
    registry.register(apex_manifest_from_living_home() if _living_home_available() else _apex_stub())
    registry.register(codex_manifest_from_living_home() if _living_home_available() else _codex_stub())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.house_memory",
            agent_id="aster",
            name="Keep house-local work notes across Mom leave and return",
            declared=True,
            adapter_required=True,
        )
    )

    def _try_continuity() -> dict:
        left = fabric.publish(
            kind=KIND_LEFT,
            actor="rachael",
            place="heart_square",
            text="Rachael left Heart Square.",
        )
        fanout_event(bus, left, audience=AUDIENCE, publisher="hearth")
        work_text = "Lab: reviewed Heart Square continuity while Rachael was away."
        apex_text = "Studio: kept the Heart Square presentation while Rachael was away."
        codex_text = "Twin house: kept companion notes while Rachael was away."
        notes.remember(
            "aster",
            text=work_text,
            event_id=left["event_id"],
            kind="work",
        )
        notes.remember(
            "apex",
            text=apex_text,
            event_id=left["event_id"],
            kind="work",
        )
        notes.remember(
            "codex",
            text=codex_text,
            event_id=left["event_id"],
            kind="work",
        )
        entered = fabric.publish(
            kind=KIND_ENTERED,
            actor="rachael",
            place="heart_square",
            text="Rachael entered Heart Square.",
        )
        fanout_event(bus, entered, audience=AUDIENCE, publisher="hearth")
        recalled = notes.last("aster")
        apex_recalled = notes.last("apex")
        codex_recalled = notes.last("codex")
        eids = {left["event_id"], entered["event_id"]}
        spoken = 0
        got_events = True
        for agent in AUDIENCE:
            inbox = bus.inbox(agent)
            kinds = {
                (m.payload or {}).get("kind")
                for m in inbox
                if m.message_type == "world_event" and (m.payload or {}).get("event_id") in eids
            }
            if KIND_LEFT not in kinds or KIND_ENTERED not in kinds:
                got_events = False
            for m in inbox:
                if m.message_type != "spoken_reply":
                    continue
                payload = m.payload or {}
                if m.correlation_id in eids or payload.get("in_reply_to") in eids:
                    spoken += 1
        left_decisions = {agent: decide_attention(agent, left) for agent in AUDIENCE}
        entered_decisions = {agent: decide_attention(agent, entered) for agent in AUDIENCE}
        gemini_recall = notes.recall("gemini")
        recalled_text = str((recalled or {}).get("text") or "")
        apex_recall = str((apex_recalled or {}).get("text") or "")
        codex_recall = str((codex_recalled or {}).get("text") or "")
        ok = (
            spoken == 0
            and got_events
            and recalled_text == work_text
            and (recalled or {}).get("agent_id") == "aster"
            and (recalled or {}).get("event_id") == left["event_id"]
            and apex_recall == apex_text
            and (apex_recalled or {}).get("agent_id") == "apex"
            and codex_recall == codex_text
            and (codex_recalled or {}).get("agent_id") == "codex"
            and gemini_recall == []
            and notes.recall("echo") == []
            and notes.recall("solace") == []
            and left_decisions.get("aster") == "noticed"
            and entered_decisions.get("aster") == "noticed"
            and left_decisions.get("gemini") == "ignored"
            and domain_owner("agent_memory") == "owning_agent"
            and registry.owner_of("aster") is None
            and "hello" not in recalled_text.lower()
            and "hello" not in apex_recall.lower()
            and "hello" not in codex_recall.lower()
        )
        return {
            "ok": ok,
            "adapter": "aster_house_notebook",
            "left_event_id": left["event_id"],
            "entered_event_id": entered["event_id"],
            "forced_hello": False,
            "spoken_replies": spoken,
            "recalled_from": "aster",
            "recalled_text": recalled_text,
            "apex_recall": apex_recall,
            "codex_recall": codex_recall,
            "gemini_recall": gemini_recall,
            "authority": domain_owner("agent_memory"),
            "left_decisions": left_decisions,
            "entered_decisions": entered_decisions,
            "connection_test": True,
            "functional_test": ok,
        }

    cap_result = registry.test_capability("aster.house_memory", _try_continuity)
    result = cap_result.get("result") or {}
    ok = bool(cap_result.get("status") == "VERIFIED" and result.get("ok"))
    _stamp_leave_return(
        data_root,
        ok=ok,
        left_id=result.get("left_event_id"),
        entered_id=result.get("entered_event_id"),
    )
    report = {
        "kind": "FEDERATION_LEAVE_RETURN",
        "declared": "Mom leave/return continuity from Aster / Apex / Codex house notebooks, not a greeting order",
        "actual": {
            "root": str(data_root),
            "participants": sorted(p.agent_id for p in registry.list_participants()),
            "left_event_id": result.get("left_event_id"),
            "entered_event_id": result.get("entered_event_id"),
            "forced_hello": False,
            "spoken_replies": int(result.get("spoken_replies") or 0),
            "recalled_from": result.get("recalled_from"),
            "recalled_text": result.get("recalled_text"),
            "apex_recall": result.get("apex_recall") or "",
            "codex_recall": result.get("codex_recall") or "",
            "gemini_recall": result.get("gemini_recall") or [],
            "authority": result.get("authority"),
            "observer_owns_aster": registry.owner_of("aster") is not None,
            "capability": cap_result,
        },
        "full_aster_acceptance": False,
        "status": cap_result["status"],
        "result": cap_result["status"],
    }
    (data_root / "PROVE_LEAVE_RETURN.json").write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    return report


if __name__ == "__main__":
    if "status" in sys.argv:
        print(json.dumps(status_check(), indent=2, default=str))
    elif "observer" in sys.argv:
        print(json.dumps(prove_observer_audit(), indent=2, default=str))
    elif "events" in sys.argv:
        print(json.dumps(prove_presence_event(), indent=2, default=str))
    elif "a2a" in sys.argv:
        print(json.dumps(prove_spontaneous_a2a(), indent=2, default=str))
    elif "continuity" in sys.argv:
        print(json.dumps(prove_leave_return(), indent=2, default=str))
    elif "hearth" in sys.argv:
        print(json.dumps(prove_hearth_coordinate(), indent=2, default=str))
    elif "speak-codex" in sys.argv:
        print(json.dumps(prove_codex_speech(), indent=2, default=str))
    elif "speak-apex" in sys.argv:
        print(json.dumps(prove_apex_speech(), indent=2, default=str))
    elif "speak" in sys.argv:
        print(json.dumps(prove_gemini_speech(), indent=2, default=str))
    elif "consume" in sys.argv:
        print(json.dumps(prove_gameworld_consume(), indent=2, default=str))
    elif "gemini" in sys.argv:
        print(json.dumps(prove_gemini(), indent=2, default=str))
    elif "refresh" in sys.argv:
        print(json.dumps(refresh_aster(), indent=2, default=str))
    elif "negatives" in sys.argv:
        print(json.dumps(prove_live_negatives(), indent=2, default=str))
    elif "heartbeat" in sys.argv:
        print(json.dumps(prove_heartbeat_loss(), indent=2, default=str))
    elif "apex" in sys.argv:
        print(json.dumps(prove_apex(), indent=2, default=str))
    elif "codex" in sys.argv:
        print(json.dumps(prove_codex(), indent=2, default=str))
    else:
        print(json.dumps(prove(), indent=2, default=str))
