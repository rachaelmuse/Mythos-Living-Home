"""Presence is an event, not a command to speak. Federation does not own personalities."""
from __future__ import annotations

from pathlib import Path

from federation.events import EventFabric, KIND_ENTERED
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_presence_event
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def test_presence_event_is_awareness_not_a_greeting_order(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_presence_event(root, court_roots=[tmp_path / "court"])
    assert report["kind"] == "FEDERATION_PRESENCE_EVENT"
    assert report["actual"]["forced_hello"] is False
    assert report["actual"]["spoken_replies"] == 0
    assert report["status"] == HonestStatus.VERIFIED.value
    bus = LocalFederationBus(root)
    for agent in ("aster", "gemini", "apex", "codex", "hearth"):
        events = [m for m in bus.inbox(agent) if m.message_type == "world_event"]
        assert len(events) == 1
        assert events[0].payload.get("kind") == KIND_ENTERED
        assert events[0].payload.get("actor") == "rachael"
        spoken = [m for m in bus.inbox(agent) if m.message_type == "spoken_reply"]
        assert spoken == []
    decisions = report["actual"]["decisions"]
    assert decisions["aster"] == "noticed"
    assert decisions["gemini"] == "ignored"
    assert decisions["hearth"] == "noticed"
    assert "heartbeat_probe" not in decisions
    assert "nova" not in decisions
    registry = FederationRegistry(root)
    assert not registry.layer_events(Layer.COLLABORATION)
    fabric = EventFabric(root)
    stored = fabric.list_events()
    assert len(stored) == 1
    assert stored[0]["kind"] == KIND_ENTERED


def test_presence_event_ignores_old_spoken_replies_in_inbox(tmp_path: Path):
    root = tmp_path / "fed"
    bus = LocalFederationBus(root)
    old = bus.send(
        sender="apex",
        recipient="aster",
        message_type="spoken_reply",
        payload={"from": "apex", "text": "old speech from an earlier prove"},
    )
    bus.deliver(old.message_id)
    report = prove_presence_event(root, court_roots=[tmp_path / "court"])
    assert report["actual"]["spoken_replies"] == 0
    assert report["status"] == HonestStatus.VERIFIED.value


def test_presence_event_log_survives_for_return_continuity(tmp_path: Path):
    root = tmp_path / "fed"
    prove_presence_event(root, court_roots=[tmp_path / "court"])
    later = EventFabric(root)
    events = later.list_events()
    assert events[0]["kind"] == KIND_ENTERED
    assert events[0]["place"] == "heart_square"
    assert "Rachael entered" in (events[0].get("text") or "")


def test_default_attention_does_not_auto_speak():
    from federation.events import decide_attention

    event = {"kind": KIND_ENTERED, "actor": "rachael", "place": "heart_square"}
    assert decide_attention("aster", event) == "noticed"
    assert decide_attention("gemini", event) == "ignored"
    assert decide_attention("apex", event) == "noticed"
    assert decide_attention("codex", event) == "noticed"
    assert decide_attention("hearth", event) == "noticed"
    assert decide_attention("observer", event) == "ignored"
    assert decide_attention("heartbeat_probe", event) == "ignored"
