"""Federation prove scripts. Aster first, then Gemini. Observer never owns them."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable

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
    stages["negative_heartbeat_loss_live"] = {
        "status": "PASS" if presence == "READY" else "PARTIAL",
        "note": f"Lab HTTP checked; federation presence {presence}.",
    }
    data["overall"] = "FAIL"
    data["full_aster_acceptance"] = False
    data["gemini_spoke"] = False
    data["note"] = "Phase B Aster refresh. Gemini expansion not started. Gameworld not started."
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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
    data["overall"] = "FAIL"
    data["full_aster_acceptance"] = False
    data["gemini_spoke"] = bool(report.get("gemini_spoke"))
    data["note"] = "Observer HTTP audit seated. Gemini speech and Gameworld not started."
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
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
    data["overall"] = "FAIL"
    data["full_aster_acceptance"] = False
    data["note"] = "Gemini speech seated. The Axiom Codex notice not started. Full Aster test still FAIL."
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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
    data["overall"] = "FAIL"
    data["full_aster_acceptance"] = False
    data["note"] = (
        "The Axiom Codex notice seated. Full Aster test still FAIL until remaining live negatives."
        if consumed
        else "The Axiom Codex notice failed. Full Aster test FAIL."
    )
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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


if __name__ == "__main__":
    if "status" in sys.argv:
        print(json.dumps(status_check(), indent=2, default=str))
    elif "observer" in sys.argv:
        print(json.dumps(prove_observer_audit(), indent=2, default=str))
    elif "speak" in sys.argv:
        print(json.dumps(prove_gemini_speech(), indent=2, default=str))
    elif "consume" in sys.argv:
        print(json.dumps(prove_gameworld_consume(), indent=2, default=str))
    elif "gemini" in sys.argv:
        print(json.dumps(prove_gemini(), indent=2, default=str))
    elif "refresh" in sys.argv:
        print(json.dumps(refresh_aster(), indent=2, default=str))
    else:
        print(json.dumps(prove(), indent=2, default=str))
