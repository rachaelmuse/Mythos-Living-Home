"""Hearth coordinates on the federation bus as village OS. Beyond Aster snapshot. Not a son."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.heartbeat import HeartbeatLog
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_hearth_coordinate
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _door_up() -> dict:
    return {
        "ok": True,
        "http": 200,
        "id": "hearth",
        "url": "http://127.0.0.1:8790/api/home",
        "family_ids": ["gemini", "apex", "codex", "aster"],
        "clock": {"period": "night", "day": 3},
        "town_leader": "gemini",
    }


def _door_down() -> dict:
    return {
        "ok": False,
        "http": None,
        "id": None,
        "url": "http://127.0.0.1:8790/api/home",
        "error": "refused",
    }


def test_hearth_coordinate_refuses_when_door_down(tmp_path: Path):
    root = tmp_path / "fed"

    def coordinate(ask: str, inbound_id: str) -> dict:
        raise AssertionError("must not coordinate while Hearth is down")

    report = prove_hearth_coordinate(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_door_down,
        coordinate_fn=coordinate,
    )
    assert report["status"] == HonestStatus.UNAVAILABLE.value
    assert report["actual"]["hearth_coordinated"] is False
    assert report["actual"]["door_ok"] is False
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "hearth" not in ids
    with pytest.raises(KeyError):
        FederationRegistry(root).get_capability("hearth.federation_coordinate")


def test_hearth_coordinate_replies_as_hearth_not_aster_snapshot(tmp_path: Path):
    def coordinate(ask: str, inbound_id: str) -> dict:
        assert ask
        return {
            "ok": True,
            "adapter": "hearth_home_http",
            "family_ids": ["gemini", "apex", "aster"],
            "clock": {"period": "night"},
            "town_leader": "gemini",
            "connection_test": True,
            "functional_test": True,
        }

    root = tmp_path / "fed"
    court = tmp_path / "court"
    report = prove_hearth_coordinate(
        root, court_roots=[court], door_fn=_door_up, coordinate_fn=coordinate
    )
    assert report["actual"]["hearth_coordinated"] is True
    assert report["actual"]["observer_owns_hearth"] is False
    assert report["kind"] == "FEDERATION_HEARTH_COORDINATE"
    bus = LocalFederationBus(root)
    replies = [m for m in bus.inbox("aster") if m.sender == "hearth"]
    assert len(replies) == 1
    assert replies[0].message_type == "coordination_reply"
    assert replies[0].payload.get("from") == "hearth"
    assert "gemini" in (replies[0].payload.get("family_ids") or [])
    assert HeartbeatLog(root).presence("hearth").value == "READY"
    registry = FederationRegistry(root)
    assert registry.owner_of("hearth") is None
    comm = registry.layer_events(Layer.COMMUNICATION)
    assert any(e.get("sender") == "hearth" and e.get("recipient") == "aster" for e in comm)
    assert not registry.layer_events(Layer.COLLABORATION)
    cap = registry.get_capability("hearth.federation_coordinate")
    assert cap.honest_status == HonestStatus.VERIFIED
    ids = {p.agent_id for p in registry.list_participants()}
    assert ids == {"aster", "hearth", "observer"}
    notices = list((court / "aster" / "federation").glob("*_reply.json"))
    assert notices
    data = notices[0].read_text(encoding="utf-8")
    assert '"from": "hearth"' in data
    assert '"gemini_spoke": true' not in data.lower()


def test_hearth_coordinate_failure_does_not_fake_world(tmp_path: Path):
    def coordinate(ask: str, inbound_id: str) -> dict:
        return {"ok": False, "error": "home snapshot missing family", "adapter": "hearth_home_http"}

    root = tmp_path / "fed"
    report = prove_hearth_coordinate(
        root, court_roots=[tmp_path / "court"], door_fn=_door_up, coordinate_fn=coordinate
    )
    assert report["actual"]["hearth_coordinated"] is False
    bus = LocalFederationBus(root)
    assert bus.inbox("aster") == []
    cap = FederationRegistry(root).get_capability("hearth.federation_coordinate")
    assert cap.honest_status == HonestStatus.FAILED
    assert HeartbeatLog(root).presence("hearth").value == "UNKNOWN"
