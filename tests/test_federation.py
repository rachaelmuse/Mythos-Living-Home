"""Federation boundary: participants, not employees. DECLARED is not VERIFIED."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.audit import FederationAuditView
from federation.heartbeat import HeartbeatLog, Presence
from federation.law import CapabilityState, HonestStatus
from federation.manifests import AgentManifest, CapabilityManifest
from federation.prove import prove
from federation.registry import FederationRegistry
from federation.reviewer import UnavailableReviewer
from federation.transport import DuplicateMessage, LocalFederationBus


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path / "federation"


def _aster_manifest() -> AgentManifest:
    return AgentManifest(
        agent_id="aster",
        name="Aster",
        version="1.0",
        role="weaver",
        house="hearth_lab",
        capabilities=["environmental_sync"],
        tools=["aster.hearth_snapshot"],
        runtime={"endpoint": "http://127.0.0.1:8791", "protocol": "http"},
        protocol_version="1",
        requested_permissions=["read_hearth_snapshot"],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth\ASTER",
    )


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


def test_registering_family_does_not_make_them_observer_agents(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster_manifest())
    registry.register(_observer_manifest())
    gemini = AgentManifest(
        agent_id="gemini",
        name="Gemini",
        version="1",
        role="sentinel",
        house="axiom",
        capabilities=["court_packets"],
        tools=[],
        runtime={"endpoint": None, "protocol": "court"},
        protocol_version="1",
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"G:\The-Axiom-Codex",
    )
    registry.register(gemini)

    participants = {p.agent_id for p in registry.list_participants()}
    assert participants == {"aster", "observer", "gemini"}
    assert registry.owner_of("gemini") is None
    assert registry.owner_of("aster") is None
    assert registry.supervisor_of("aster") is None
    obs = registry.get("observer")
    assert "gemini" not in obs.capabilities
    assert registry.relationship("observer", "gemini") == "independent_participants"


def test_declared_capability_is_not_verified(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster_manifest())
    cap = CapabilityManifest(
        capability_id="aster.hearth_snapshot",
        agent_id="aster",
        name="Hearth snapshot read",
        declared=True,
        adapter_required=True,
        permission_required="read_hearth_snapshot",
    )
    registry.declare_capability(cap)
    record = registry.get_capability("aster.hearth_snapshot")
    assert record.state == CapabilityState.DISCOVERED
    assert record.honest_status == HonestStatus.DECLARED
    assert record.state != CapabilityState.VERIFIED
    with pytest.raises(PermissionError):
        registry.mark_verified("aster.hearth_snapshot", evidence="function exists")


def test_verify_requires_passing_functional_test(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
            declared=True,
        )
    )

    def fake_fail() -> dict:
        return {"ok": False, "error": "hearth down"}

    result = registry.test_capability("aster.hearth_snapshot", fake_fail)
    assert result["status"] == HonestStatus.FAILED.value
    assert registry.get_capability("aster.hearth_snapshot").state == CapabilityState.FAILED

    def fake_pass() -> dict:
        return {"ok": True, "hearth": "REACHABLE", "evidence": "snapshot object"}

    result = registry.test_capability("aster.hearth_snapshot", fake_pass)
    assert result["status"] == HonestStatus.VERIFIED.value
    rec = registry.get_capability("aster.hearth_snapshot")
    assert rec.state == CapabilityState.VERIFIED
    assert rec.evidence["hearth"] == "REACHABLE"


def test_heartbeat_only_updates_from_actual_pulse(root: Path):
    registry = FederationRegistry(root)
    beats = HeartbeatLog(root)
    registry.register(_aster_manifest())
    registry.register(_observer_manifest())

    assert beats.presence("aster") == Presence.UNKNOWN
    assert beats.last_seen("aster") is None

    beats.pulse("aster")
    assert beats.presence("aster") == Presence.READY
    assert beats.last_seen("aster") is not None
    assert beats.last_seen("observer") is None
    assert beats.presence("observer") == Presence.UNKNOWN


def test_stale_then_offline_from_age(root: Path, monkeypatch: pytest.MonkeyPatch):
    beats = HeartbeatLog(root, stale_after_s=10, offline_after_s=30)
    now = 1_000_000.0
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now)
    beats.pulse("aster")
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now + 15)
    assert beats.presence("aster") == Presence.STALE
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now + 40)
    assert beats.presence("aster") == Presence.OFFLINE


def test_bus_delivers_acks_and_keeps_history(root: Path):
    bus = LocalFederationBus(root)
    msg = bus.send(
        sender="aster",
        recipient="hearth",
        message_type="capability_query",
        payload={"ask": "snapshot"},
    )
    assert msg.message_id
    assert msg.status == "pending"
    delivered = bus.deliver(msg.message_id)
    assert delivered.status == "delivered"
    inbox = bus.inbox("hearth")
    assert len(inbox) == 1
    assert inbox[0].payload["ask"] == "snapshot"
    ack = bus.acknowledge(msg.message_id, recipient="hearth")
    assert ack.status == "acknowledged"
    history = bus.history(msg.message_id)
    assert history is not None
    assert Path(history).exists()
    assert bus.get(msg.message_id).attempts >= 1


def test_duplicate_message_id_rejected(root: Path):
    bus = LocalFederationBus(root)
    msg = bus.send(sender="aster", recipient="gemini", message_type="ping", payload={})
    with pytest.raises(DuplicateMessage):
        bus.send(
            sender="aster",
            recipient="gemini",
            message_type="ping",
            payload={},
            message_id=msg.message_id,
        )


def test_aster_manifest_from_identity_file(tmp_path: Path):
    from federation.aster import aster_manifest_from_identity

    identity = tmp_path / "ASTER_IDENTITY.json"
    identity.write_text(
        '{"id":"aster","name":"Aster","role":"Scientist","home":"aster_home"}',
        encoding="utf-8",
    )
    manifest = aster_manifest_from_identity(identity)
    assert manifest.agent_id == "aster"
    assert manifest.house != "the_observer"
    assert "gemini" not in manifest.capabilities


def test_unavailable_reviewer_does_not_fabricate_analysis():
    gpt = UnavailableReviewer("gpt")
    status = gpt.availability()
    assert status["status"] == "UNAVAILABLE"
    assert status["adapter"] == "NOT CONFIGURED"
    assert status["credentials"] == "NOT PRESENT"
    assert status["last_verified"] == "NEVER"
    result = gpt.submit_review({"question": "Who benefited?", "evidence": []})
    assert result["status"] == "UNAVAILABLE"
    assert "analysis" not in result or not result.get("analysis")
    assert "DeepSeek reviewed" not in str(result)
    assert "GPT reviewed" not in str(result)
    with pytest.raises(RuntimeError):
        gpt.receive_result("no-such-review")


def test_audit_view_does_not_make_observer_the_owner(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster_manifest())
    registry.register(_observer_manifest())
    snap = FederationAuditView(root).snapshot()
    assert snap["owned_by"] is None
    assert snap["observer_is_supervisor"] is False
    by_id = {a["agent_id"]: a for a in snap["agents"]}
    assert by_id["aster"]["owner"] is None
    assert by_id["aster"]["presence"] == "UNKNOWN"


def test_prove_aster_from_real_identity(tmp_path: Path):
    identity = Path(r"D:\Mythos_Hearth\ASTER\ASTER_IDENTITY.json")
    if not identity.exists():
        pytest.skip("Aster identity not on this machine")
    report = prove(tmp_path / "fed", identity_path=identity)
    assert report["actual"]["observer_owns_aster"] is False
    assert report["actual"]["relationship"] == "independent_participants"
    assert "aster" in report["actual"]["participants"]
    assert "observer" in report["actual"]["participants"]
    assert report["actual"]["observer_presence"] == "UNKNOWN"
    assert report["actual"]["aster_presence"] == "READY"
    assert report["actual"]["message_status"] == "acknowledged"
    assert report["status"] in {"VERIFIED", "FAILED"}
