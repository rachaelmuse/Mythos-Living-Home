"""The Axiom Codex records a VERIFIED Aster notice into HOME.json. Not Apex/Codex."""
from __future__ import annotations

from pathlib import Path

from federation.heartbeat import HeartbeatLog
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_gameworld_consume
from federation.registry import FederationRegistry


def test_gameworld_consume_updates_world_and_stays_not_full_acceptance(tmp_path: Path):
    notice = {
        "capability_id": "aster.gameworld_notice",
        "requester": "hearth",
        "performer": "aster",
        "at": "2026-09-01T00:00:00+00:00",
        "result": {"hearth": "REACHABLE"},
        "layer": "COLLABORATION",
    }

    def perform() -> dict:
        return {
            "ok": True,
            "adapter": "hearth_federation_consume",
            "notice": notice,
            "home_updated": True,
            "connection_test": True,
            "functional_test": True,
        }

    root = tmp_path / "fed"
    report = prove_gameworld_consume(root, perform_fn=perform)
    assert report["world"] == "The Axiom Codex"
    assert report["actual"]["consumed"] is True
    assert report["full_aster_acceptance"] is False
    assert report["actual"]["observer_owns_aster"] is False
    cap = FederationRegistry(root).get_capability("aster.gameworld_notice")
    assert cap.honest_status == HonestStatus.VERIFIED
    collab = FederationRegistry(root).layer_events(Layer.COLLABORATION)
    assert any(e.get("capability_id") == "aster.gameworld_notice" for e in collab)
    assert HeartbeatLog(root).presence("hearth").value == "READY"
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert ids == {"aster", "hearth", "observer"}


def test_gameworld_consume_failure_does_not_fake_world(tmp_path: Path):
    def perform() -> dict:
        return {"ok": False, "error": "hearth_unreachable", "adapter": "hearth_federation_consume"}

    root = tmp_path / "fed"
    report = prove_gameworld_consume(root, perform_fn=perform)
    assert report["actual"]["consumed"] is False
    cap = FederationRegistry(root).get_capability("aster.gameworld_notice")
    assert cap.honest_status == HonestStatus.FAILED
    assert not FederationRegistry(root).layer_events(Layer.COLLABORATION)
