"""Spontaneous A2A: a house may choose to speak. Not a greeting chorus. Mom is not the switch."""
from __future__ import annotations

from pathlib import Path

from federation.events import KIND_CONTINUES, KIND_ENTERED, decide_attention
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_presence_event, prove_spontaneous_a2a
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def test_presence_enter_still_does_not_choose_to_speak():
    event = {"kind": KIND_ENTERED, "actor": "rachael", "place": "heart_square"}
    assert decide_attention("aster", event) == "noticed"
    assert decide_attention("gemini", event) == "ignored"
    assert decide_attention("apex", event) == "noticed"
    assert decide_attention("codex", event) == "noticed"
    assert decide_attention("hearth", event) == "noticed"


def test_away_tick_aster_may_speak_gemini_stays_quiet():
    event = {
        "kind": KIND_CONTINUES,
        "actor": "hearth",
        "place": "heart_square",
        "text": "Heart Square continues while Rachael is away.",
    }
    assert decide_attention("aster", event) == "speak"
    assert decide_attention("gemini", event) == "ignored"
    assert decide_attention("apex", event) == "noticed"
    assert decide_attention("codex", event) == "noticed"
    assert decide_attention("hearth", event) == "noticed"
    assert decide_attention("observer", event) == "ignored"
    assert decide_attention("heartbeat_probe", event) == "ignored"


def test_chosen_speakers_never_a_chorus():
    from federation.events import chosen_speakers

    event = {"kind": KIND_CONTINUES, "actor": "hearth"}
    speakers = chosen_speakers(event)
    assert speakers == ("aster",)

    def everyone_speaks(_agent: str, _event: dict) -> str:
        return "speak"

    capped = chosen_speakers(event, decide=everyone_speaks)
    assert len(capped) == 1


def test_prove_spontaneous_a2a_aster_to_codex_not_a_chorus(tmp_path: Path):
    def speak(ask: str, inbound_id: str) -> dict:
        assert ask
        assert inbound_id
        return {
            "ok": True,
            "adapter": "aster_ollama",
            "text": "Codex, the square is still running. I am checking a pattern, not waiting for Mom.",
            "model": "llama3.2:3b",
            "connection_test": True,
            "functional_test": True,
            "aster_spoke": True,
        }

    root = tmp_path / "fed"
    court = tmp_path / "court"
    report = prove_spontaneous_a2a(root, court_roots=[court], speak_fn=speak)
    assert report["kind"] == "FEDERATION_SPONTANEOUS_A2A"
    assert report["status"] == HonestStatus.VERIFIED.value
    assert report["actual"]["forced_hello"] is False
    assert report["actual"]["spoken_replies"] == 1
    assert report["actual"]["speakers"] == ["aster"]
    assert report["actual"]["addressee"] == "codex"
    assert report["actual"]["actor"] != "rachael"
    assert report["actual"]["kind"] == KIND_CONTINUES
    assert report["actual"]["decisions"]["aster"] == "speak"
    assert report["actual"]["decisions"]["gemini"] == "ignored"
    assert report["actual"]["observer_owns_aster"] is False

    bus = LocalFederationBus(root)
    eid = report["actual"]["event_id"]
    gemini_spoken = [
        m
        for m in bus.inbox("gemini")
        if m.message_type == "spoken_reply"
        and (m.correlation_id == eid or (m.payload or {}).get("in_reply_to") == eid)
    ]
    assert gemini_spoken == []
    codex_from_aster = [
        m
        for m in bus.inbox("codex")
        if m.message_type == "spoken_reply" and m.sender == "aster"
    ]
    assert len(codex_from_aster) == 1
    assert "Mom" in (codex_from_aster[0].payload.get("text") or "") or "square" in (
        (codex_from_aster[0].payload.get("text") or "").lower()
    )
    for agent in ("apex", "hearth", "gemini"):
        from_them = [
            m
            for m in bus.inbox("codex")
            if m.message_type == "spoken_reply" and m.sender == agent
        ]
        assert from_them == []
    registry = FederationRegistry(root)
    assert not registry.layer_events(Layer.COLLABORATION)


def test_prove_spontaneous_a2a_ignores_old_spoken_replies(tmp_path: Path):
    root = tmp_path / "fed"
    bus = LocalFederationBus(root)
    old = bus.send(
        sender="apex",
        recipient="aster",
        message_type="spoken_reply",
        payload={"from": "apex", "text": "old speech from an earlier prove"},
    )
    bus.deliver(old.message_id)

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": True,
            "adapter": "aster_ollama",
            "text": "Codex, I noticed the world kept going without a greeting order.",
            "model": "stub",
            "connection_test": True,
            "functional_test": True,
            "aster_spoke": True,
        }

    report = prove_spontaneous_a2a(root, court_roots=[tmp_path / "court"], speak_fn=speak)
    assert report["actual"]["spoken_replies"] == 1
    assert report["actual"]["speakers"] == ["aster"]
    assert report["status"] == HonestStatus.VERIFIED.value


def test_prove_spontaneous_a2a_empty_speech_is_not_verified(tmp_path: Path):
    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": False,
            "adapter": "aster_ollama",
            "error": "empty_or_error_reply",
            "aster_spoke": False,
            "connection_test": True,
            "functional_test": False,
        }

    report = prove_spontaneous_a2a(
        tmp_path / "fed",
        court_roots=[tmp_path / "court"],
        speak_fn=speak,
    )
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"]["spoken_replies"] == 0
    assert report["actual"]["forced_hello"] is False
    bus = LocalFederationBus(tmp_path / "fed")
    spoken = [m for m in bus.inbox("codex") if m.message_type == "spoken_reply"]
    assert spoken == []


def test_presence_prove_still_zero_spoken_replies(tmp_path: Path):
    report = prove_presence_event(tmp_path / "fed", court_roots=[tmp_path / "court"])
    assert report["actual"]["spoken_replies"] == 0
    assert report["status"] == HonestStatus.VERIFIED.value
