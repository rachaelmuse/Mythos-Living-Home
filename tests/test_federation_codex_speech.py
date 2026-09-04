"""Codex speaks on the federation bus as himself. Delivery is not speech. Never Gemini."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.heartbeat import HeartbeatLog
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_codex, prove_codex_speech
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _door_up() -> dict:
    return {
        "ok": True,
        "http": 200,
        "id": "codex",
        "online": True,
        "url": "http://127.0.0.1:8780/api/companion/presence",
    }


def _door_down() -> dict:
    return {
        "ok": False,
        "http": None,
        "id": None,
        "url": "http://127.0.0.1:8780/api/companion/presence",
        "error": "refused",
    }


def test_prove_codex_delivery_still_does_not_speak(tmp_path: Path):
    report = prove_codex(tmp_path / "fed", court_roots=[tmp_path / "court"], door_fn=_door_up)
    assert report["actual"]["codex_spoke"] is False


def test_prove_codex_speech_refuses_when_door_down(tmp_path: Path):
    root = tmp_path / "fed"

    def speak(ask: str, inbound_id: str) -> dict:
        raise AssertionError("must not speak while the Codex door is down")

    report = prove_codex_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_door_down,
        speak_fn=speak,
    )
    assert report["status"] == HonestStatus.UNAVAILABLE.value
    assert report["actual"]["codex_spoke"] is False
    assert report["actual"]["door_ok"] is False
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "codex" not in ids
    with pytest.raises(KeyError):
        FederationRegistry(root).get_capability("codex.federation_speech")


def test_codex_speech_persists_reply_and_pulses(tmp_path: Path):
    def speak(ask: str, inbound_id: str) -> dict:
        assert ask
        return {
            "ok": True,
            "adapter": "codex_ollama",
            "text": "I am Codex, archive twin of Mythos_Codex. Aster reached me on the federation bus.",
            "model": "llama3.2:3b",
            "connection_test": True,
            "functional_test": True,
            "codex_spoke": True,
        }

    root = tmp_path / "fed"
    court = tmp_path / "court"
    report = prove_codex_speech(root, court_roots=[court], door_fn=_door_up, speak_fn=speak)
    assert report["actual"]["codex_spoke"] is True
    assert report["actual"]["observer_owns_codex"] is False
    assert report["actual"]["door_ok"] is True
    assert report["kind"] == "FEDERATION_CODEX_SPEECH"
    bus = LocalFederationBus(root)
    replies = [m for m in bus.inbox("aster") if m.sender == "codex"]
    assert len(replies) == 1
    assert "Codex" in replies[0].payload.get("text", "")
    assert replies[0].payload.get("from") == "codex"
    assert replies[0].payload.get("in_reply_to")
    assert HeartbeatLog(root).presence("codex").value == "READY"
    registry = FederationRegistry(root)
    assert registry.owner_of("codex") is None
    comm = registry.layer_events(Layer.COMMUNICATION)
    assert any(e.get("sender") == "codex" and e.get("recipient") == "aster" for e in comm)
    assert not registry.layer_events(Layer.COLLABORATION)
    cap = registry.get_capability("codex.federation_speech")
    assert cap.honest_status == HonestStatus.VERIFIED
    ids = {p.agent_id for p in registry.list_participants()}
    assert "codex" in ids
    assert "apex" not in ids
    assert "gemini" not in ids
    notices = list((court / "aster" / "federation").glob("*_reply.json"))
    assert notices
    data = notices[0].read_text(encoding="utf-8")
    assert "codex_spoke" in data
    assert '"gemini_spoke": true' not in data.lower()
    assert '"from": "gemini"' not in data


def test_codex_speech_failure_does_not_fake_a_line(tmp_path: Path):
    def speak(ask: str, inbound_id: str) -> dict:
        return {"ok": False, "error": "ollama unreachable", "adapter": "codex_ollama"}

    root = tmp_path / "fed"
    report = prove_codex_speech(root, court_roots=[tmp_path / "court"], door_fn=_door_up, speak_fn=speak)
    assert report["actual"]["codex_spoke"] is False
    bus = LocalFederationBus(root)
    assert bus.inbox("aster") == []
    cap = FederationRegistry(root).get_capability("codex.federation_speech")
    assert cap.honest_status == HonestStatus.FAILED
    assert HeartbeatLog(root).presence("codex").value == "UNKNOWN"


def test_codex_speech_system_is_not_gemini():
    from federation.codex_speech import SYSTEM

    assert "You are Codex" in SYSTEM
    assert "not Gemini" in SYSTEM
    assert "not Apex" in SYSTEM
    assert "Mythos_Codex" in SYSTEM
