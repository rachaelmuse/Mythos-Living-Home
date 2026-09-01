"""Amendments 1–8: foundation only. Delivery is not collaboration. Observer does not own anyone."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.authority import AUTHORITY, domain_owner, write_authority_map
from federation.evidence import write_amendment_evidence
from federation.health import AgentHealth
from federation.heartbeat import HeartbeatLog
from federation.layers import Layer
from federation.law import CapabilityState, HonestStatus
from federation.manifests import AgentManifest, CapabilityManifest
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path / "federation"


def _aster() -> AgentManifest:
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


def _observer() -> AgentManifest:
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


def _hearth() -> AgentManifest:
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


def test_authority_map_does_not_give_observer_the_family(root: Path):
    write_authority_map(root)
    assert domain_owner("investigative_ledger") == "observer"
    assert domain_owner("observer_identity") == "observer"
    assert domain_owner("federation_communication") == "hearth_federation"
    assert domain_owner("family_membership") == "hearth_federation"
    assert domain_owner("gameworld_state") == "hearth_gameworld"
    assert domain_owner("agent_tools") == "owning_agent"
    assert AUTHORITY["capability_verification"] == "federation_verification_layer"
    assert AUTHORITY["capability_ownership"] != "federation_verification_layer"
    path = root / "AUTHORITY.json"
    assert path.exists()


def test_manifest_versions_and_history(root: Path):
    registry = FederationRegistry(root)
    first = registry.register(_aster())
    assert first.manifest_version == "1"
    assert first.capability_hash
    assert first.tool_hash
    events = registry.manifest_events("aster")
    assert len(events) == 1
    assert events[0]["kind"] == "register"

    changed = _aster()
    changed.capabilities = ["environmental_sync", "lab_notes"]
    second = registry.register(changed)
    assert second.manifest_version == "2"
    assert second.capability_hash != first.capability_hash
    events = registry.manifest_events("aster")
    assert len(events) == 2
    old = registry.manifest_at("aster", events[0]["timestamp"])
    assert old.capabilities == ["environmental_sync"]
    assert "lab_notes" not in old.capabilities


def test_verified_capability_keeps_provenance(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot",
            declared=True,
            adapter_required=True,
        )
    )
    registry.test_capability(
        "aster.hearth_snapshot",
        lambda: {"ok": True, "hearth": "REACHABLE", "adapter": "aster_hearth_bridge"},
    )
    rec = registry.get_capability("aster.hearth_snapshot")
    p = rec.provenance
    assert p["declared_by"] == "aster"
    assert p["manifest_version"] == "1"
    assert p["capability_hash"]
    assert p["adapter"] == "aster_hearth_bridge"
    assert p["connection_test"]
    assert p["functional_test"]
    assert p["verified_at"]
    assert p["result"]["hearth"] == "REACHABLE"
    assert p["artifact"]
    assert rec.state == CapabilityState.VERIFIED


def test_failed_capability_is_not_verified(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.declare_capability(
        CapabilityManifest(capability_id="aster.sync", agent_id="aster", name="sync")
    )
    registry.test_capability("aster.sync", lambda: {"ok": False, "error": "no hearth"})
    rec = registry.get_capability("aster.sync")
    assert rec.state != CapabilityState.VERIFIED
    assert rec.honest_status == HonestStatus.FAILED
    assert rec.provenance.get("verified_at") in (None, "")


def test_unauthorized_invoke_rejected_and_audit(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.register(_hearth())
    registry.register(_observer())
    registry.declare_capability(
        CapabilityManifest(capability_id="aster.hearth_snapshot", agent_id="aster", name="snap")
    )
    registry.test_capability("aster.hearth_snapshot", lambda: {"ok": True})
    with pytest.raises(PermissionError):
        registry.invoke("observer", "aster.hearth_snapshot", lambda: {"ok": True})
    events = registry.authorization_events()
    assert any(e["kind"] == "rejected" and e["requester"] == "observer" for e in events)
    registry.authorize("hearth", "aster.hearth_snapshot")
    result = registry.invoke("hearth", "aster.hearth_snapshot", lambda: {"ok": True, "synced": True})
    assert result["ok"] is True
    assert result["layer"] == Layer.COLLABORATION.value
    collab = registry.layer_events(Layer.COLLABORATION)
    assert any(e.get("capability_id") == "aster.hearth_snapshot" for e in collab)


def test_delivery_is_not_recorded_as_collaboration(root: Path):
    registry = FederationRegistry(root)
    bus = LocalFederationBus(root)
    msg = bus.send(sender="aster", recipient="gemini", message_type="ping", payload={})
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient="gemini")
    registry.record_communication(msg.message_id, "aster", "gemini")
    assert registry.layer_events(Layer.COMMUNICATION)
    assert not registry.layer_events(Layer.COLLABORATION)


def test_heartbeat_loss_degrades_dependents_not_the_whole_federation(
    root: Path, monkeypatch: pytest.MonkeyPatch
):
    registry = FederationRegistry(root)
    beats = HeartbeatLog(root, stale_after_s=10, offline_after_s=20)
    registry.register(_aster())
    registry.register(_hearth())
    registry.declare_capability(
        CapabilityManifest(capability_id="aster.hearth_snapshot", agent_id="aster", name="snap")
    )
    registry.test_capability("aster.hearth_snapshot", lambda: {"ok": True})
    now = 2_000_000.0
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now)
    beats.pulse("aster")
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now + 40)
    registry.sync_health(beats)
    rec = registry.get_capability("aster.hearth_snapshot")
    assert rec.honest_status == HonestStatus.UNAVAILABLE
    assert rec.state == CapabilityState.QUARANTINED
    assert registry.agent_health("aster") in {AgentHealth.FAILED, AgentHealth.QUARANTINED}
    assert registry.agent_health("hearth") == AgentHealth.ACTIVE
    assert registry.get("hearth").agent_id == "hearth"


def test_identity_merge_attempt_rejected(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster())
    registry.register(_observer())
    with pytest.raises(PermissionError):
        registry.claim_ownership("observer", "aster")
    assert registry.owner_of("aster") is None
    events = registry.authorization_events()
    assert any(e["kind"] == "identity_merge_rejected" for e in events)


def test_amendment_evidence_record(root: Path):
    registry = FederationRegistry(root)
    registry.register(_aster())
    path = write_amendment_evidence(root, registry)
    data = path.read_text(encoding="utf-8")
    assert "AMENDMENT_PASS" in data
    assert "aster" in data.lower()
