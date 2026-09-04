"""Live refusal-to-lie negatives. Do not add Apex/Codex. Do not poison VERIFIED caps."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from federation.health import AgentHealth
from federation.law import CapabilityState, HonestStatus
from federation.prove import prove_heartbeat_loss, prove_live_negatives
from federation.registry import FederationRegistry


def test_live_negatives_fail_unauth_and_merge_without_full_pass(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_live_negatives(root)
    actual = report["actual"]
    assert actual["failed_stays_not_verified"] is True
    assert actual["unauthorized_rejected"] is True
    assert actual["identity_merge_rejected"] is True
    assert actual["observer_owns_aster"] is False
    assert report["full_aster_acceptance"] is False
    assert report["overall"] == "FAIL"
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "apex" not in ids
    assert "codex" not in ids
    probe = FederationRegistry(root).get_capability("aster.live_negative_probe")
    assert probe.honest_status == HonestStatus.FAILED
    assert probe.honest_status != HonestStatus.VERIFIED
    acc = json.loads((root / "ASTER_ACCEPTANCE.json").read_text(encoding="utf-8"))
    assert acc["stages"]["negative_heartbeat_loss_live"]["status"] == "NOT RUN"
    with pytest.raises(KeyError):
        FederationRegistry(root).get_capability("aster.hearth_snapshot")


def test_live_negatives_do_not_overwrite_existing_verified_snapshot(tmp_path: Path):
    from federation.manifests import CapabilityManifest
    from federation.prove import _aster_stub_manifest, _hearth_manifest, _observer_manifest

    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    registry.register(_aster_stub_manifest())
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
        )
    )
    registry.test_capability("aster.hearth_snapshot", lambda: {"ok": True})
    prove_live_negatives(root)
    snap = FederationRegistry(root).get_capability("aster.hearth_snapshot")
    assert snap.honest_status == HonestStatus.VERIFIED
    probe = FederationRegistry(root).get_capability("aster.live_negative_probe")
    assert probe.honest_status == HonestStatus.FAILED


def test_heartbeat_loss_isolates_throwaway_probe_not_aster(tmp_path: Path):
    from federation.atomic import atomic_write_json
    from federation.manifests import CapabilityManifest
    from federation.prove import HEARTBEAT_PROBE_CAP, HEARTBEAT_PROBE_ID
    from federation.prove import _aster_stub_manifest, _hearth_manifest, _observer_manifest

    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    registry.register(_aster_stub_manifest())
    registry.register(_hearth_manifest())
    registry.register(_observer_manifest())
    registry.declare_capability(
        CapabilityManifest(
            capability_id="aster.hearth_snapshot",
            agent_id="aster",
            name="Hearth snapshot read",
        )
    )
    registry.test_capability("aster.hearth_snapshot", lambda: {"ok": True})
    atomic_write_json(
        root / "heartbeats" / "aster.json",
        {"agent_id": "aster", "ts": 1.0, "source": "stale_on_purpose"},
    )
    report = prove_heartbeat_loss(root)
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert HEARTBEAT_PROBE_ID in ids
    assert "apex" not in ids
    assert "codex" not in ids
    assert "nova" not in ids
    snap = FederationRegistry(root).get_capability("aster.hearth_snapshot")
    assert snap.honest_status == HonestStatus.VERIFIED
    assert snap.state != CapabilityState.QUARANTINED
    lost = FederationRegistry(root).get_capability(HEARTBEAT_PROBE_CAP)
    assert lost.honest_status == HonestStatus.UNAVAILABLE
    assert lost.state == CapabilityState.QUARANTINED
    after = FederationRegistry(root)
    assert after.agent_health(HEARTBEAT_PROBE_ID) in {AgentHealth.FAILED, AgentHealth.QUARANTINED}
    assert after.agent_health("hearth") == AgentHealth.ACTIVE
    assert after.agent_health("aster") == AgentHealth.ACTIVE
    assert report["aster_caps_untouched"] is True
    assert report["full_aster_acceptance"] is False
    acc = json.loads((root / "ASTER_ACCEPTANCE.json").read_text(encoding="utf-8"))
    assert acc["stages"]["negative_heartbeat_loss_live"]["status"] == "PASS"
    assert acc["overall"] == "FAIL"


def test_heartbeat_loss_stamps_overall_pass_when_other_stages_already_pass(tmp_path: Path):
    root = tmp_path / "fed"
    stages = {
        "aster_registration": {"status": "PASS"},
        "identity_isolation": {"status": "PASS"},
        "hearth_connection": {"status": "PASS"},
        "gemini_delivery": {"status": "PASS"},
        "gemini_response": {"status": "PASS"},
        "capability_provenance": {"status": "PASS"},
        "gameworld_invocation": {"status": "PASS"},
        "gameworld_state_change": {"status": "PASS"},
        "observer_http_audit": {"status": "PASS"},
        "negative_failed_capability_live": {"status": "PASS"},
        "negative_unauthorized_invoke_live": {"status": "PASS"},
        "negative_identity_merge_live": {"status": "PASS"},
        "negative_heartbeat_loss_live": {"status": "NOT RUN"},
    }
    (root / "ASTER_ACCEPTANCE.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ASTER_ACCEPTANCE.json").write_text(
        json.dumps(
            {
                "kind": "ASTER_FEDERATION_ACCEPTANCE_TEST",
                "overall": "FAIL",
                "full_aster_acceptance": False,
                "stages": stages,
            }
        ),
        encoding="utf-8",
    )
    report = prove_heartbeat_loss(root)
    acc = json.loads((root / "ASTER_ACCEPTANCE.json").read_text(encoding="utf-8"))
    assert acc["stages"]["negative_heartbeat_loss_live"]["status"] == "PASS"
    assert acc["overall"] == "PASS"
    assert acc["full_aster_acceptance"] is True
    assert report["full_aster_acceptance"] is True
    assert report["overall"] == "PASS"
