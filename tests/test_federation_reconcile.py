"""Phase B foundation: live store catches up. No new agents. No Gemini speech."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from federation.atomic import atomic_write_json
from federation.health import AgentHealth
from federation.heartbeat import HeartbeatLog
from federation.law import CapabilityState, HonestStatus
from federation.layers import Layer
from federation.reconcile import reconcile_foundation
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _old_participant(agent_id: str, house: str, root: str) -> dict:
    return {
        "agent_id": agent_id,
        "name": agent_id.title(),
        "version": "1",
        "role": "role",
        "house": house,
        "capabilities": [],
        "tools": [],
        "runtime": {"protocol": "http"},
        "protocol_version": "1",
        "requested_permissions": [],
        "declared_status": "DECLARED",
        "identity_root": root,
    }


def _seed_stale_store(root: Path, monkeypatch: pytest.MonkeyPatch) -> HeartbeatLog:
    participants = root / "participants"
    capabilities = root / "capabilities"
    participants.mkdir(parents=True)
    capabilities.mkdir(parents=True)
    for agent_id, house, ident in (
        ("aster", "hearth_lab", r"D:\Mythos_Hearth\ASTER"),
        ("gemini", "axiom", r"G:\The-Axiom-Codex"),
        ("hearth", "hearth", r"D:\Mythos_Hearth"),
        ("observer", "the_observer", r"D:\The_Observer"),
    ):
        atomic_write_json(participants / f"{agent_id}.json", _old_participant(agent_id, house, ident))
    atomic_write_json(
        capabilities / "aster.hearth_snapshot.json",
        {
            "capability_id": "aster.hearth_snapshot",
            "agent_id": "aster",
            "name": "Hearth snapshot read",
            "state": "VERIFIED",
            "honest_status": "VERIFIED",
            "evidence": {"ok": True, "hearth": "REACHABLE"},
            "lifecycle": ["DISCOVERED", "TESTED", "VERIFIED"],
        },
    )
    atomic_write_json(
        capabilities / "gemini.federation_inbox.json",
        {
            "capability_id": "gemini.federation_inbox",
            "agent_id": "gemini",
            "name": "Receive federation message as Gemini",
            "state": "VERIFIED",
            "honest_status": "VERIFIED",
            "evidence": {"ok": True, "gemini_spoke": False, "message_id": "47b6171fdeadbeef"},
            "lifecycle": ["DISCOVERED", "TESTED", "VERIFIED"],
        },
    )
    bus = LocalFederationBus(root)
    bus.send(sender="aster", recipient="hearth", message_type="capability_query", payload={"ask": "snapshot"})
    bus.send(sender="aster", recipient="gemini", message_type="capability_query", payload={"ask": "who_are_you"})
    now = 3_000_000.0
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now)
    beats = HeartbeatLog(root, stale_after_s=10, offline_after_s=20)
    beats.pulse("aster")
    monkeypatch.setattr("federation.heartbeat.time.time", lambda: now + 40)
    return beats


def test_reconcile_does_not_add_agents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    report = reconcile_foundation(root, beats=beats)
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert ids == {"aster", "gemini", "hearth", "observer"}
    assert "apex" not in ids
    assert "codex" not in ids
    assert report["new_agents"] == []
    assert report["gemini_spoke"] is False
    assert report["full_aster_acceptance"] is False


def test_reconcile_archives_and_versions_manifests(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    old = json.loads((root / "participants" / "aster.json").read_text(encoding="utf-8"))
    assert "manifest_version" not in old
    reconcile_foundation(root, beats=beats)
    archive = list((root / "archive" / "pre_reconcile").glob("aster.json"))
    assert archive
    aster = FederationRegistry(root).get("aster")
    assert aster.manifest_version == "1"
    assert aster.capability_hash
    assert aster.tool_hash
    events = FederationRegistry(root).manifest_events("aster")
    assert events
    assert events[0]["kind"] in {"register", "update"}


def test_reconcile_downgrades_verified_without_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    reconcile_foundation(root, beats=beats)
    gemini_cap = FederationRegistry(root).get_capability("gemini.federation_inbox")
    assert gemini_cap.state != CapabilityState.VERIFIED
    assert gemini_cap.honest_status == HonestStatus.PARTIAL
    p = gemini_cap.provenance
    assert p.get("declared_by") == "gemini"
    assert p.get("verified_at") in (None, "")
    assert p.get("adapter") in (None, "")


def test_reconcile_quarantines_offline_aster_not_hearth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    reconcile_foundation(root, beats=beats)
    registry = FederationRegistry(root)
    rec = registry.get_capability("aster.hearth_snapshot")
    assert rec.honest_status == HonestStatus.UNAVAILABLE
    assert rec.state == CapabilityState.QUARANTINED
    assert registry.agent_health("aster") in {AgentHealth.FAILED, AgentHealth.QUARANTINED}
    assert registry.agent_health("hearth") == AgentHealth.ACTIVE
    assert registry.agent_health("gemini") == AgentHealth.ACTIVE


def test_reconcile_stamps_bus_as_communication_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    reconcile_foundation(root, beats=beats)
    registry = FederationRegistry(root)
    comm = registry.layer_events(Layer.COMMUNICATION)
    assert len(comm) >= 2
    assert not registry.layer_events(Layer.COLLABORATION)


def test_aster_acceptance_file_does_not_claim_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    root = tmp_path / "federation"
    beats = _seed_stale_store(root, monkeypatch)
    path = Path(reconcile_foundation(root, beats=beats)["aster_acceptance"])
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["overall"] != "PASS"
    assert data["stages"]["gemini_response"]["status"] == "NOT STARTED"
    assert data["stages"]["gameworld_invocation"]["status"] == "NOT STARTED"
    assert data["stages"]["observer_http_audit"]["status"] == "NOT STARTED"
    assert data["stages"]["aster_registration"]["status"] == "PASS"
    assert data["evidence"]["capability_hash"]  # from re-saved aster
    assert data["evidence"]["gemini_speech_message_id"] in (None, "")
