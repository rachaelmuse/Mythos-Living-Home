"""Gemini speaks on the federation bus as Sentinel. Delivery is not speech."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.gemini import gemini_manifest_from_member
from federation.heartbeat import HeartbeatLog
from federation.law import HonestStatus
from federation.layers import Layer
from federation.manifests import AgentManifest, CapabilityManifest
from federation.prove import _hearth_manifest, _observer_manifest, prove_gemini
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _gemini_row() -> dict:
    return {
        "id": "gemini",
        "name": "Gemini",
        "house": "axiom",
        "root": r"G:\The-Axiom-Codex",
    }


def _aster() -> AgentManifest:
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
        requested_permissions=[],
        declared_status="DECLARED",
        identity_root=r"D:\Mythos_Hearth\ASTER",
    )


def test_prove_gemini_still_does_not_speak(tmp_path: Path):
    report = prove_gemini(tmp_path / "fed", court_roots=[tmp_path / "court"])
    assert report["actual"]["gemini_spoke"] is False


def test_gemini_speech_persists_reply_and_pulses(tmp_path: Path):
    from federation.prove import prove_gemini_speech

    def speak(ask: str, inbound_id: str) -> dict:
        assert "who_are_you" in ask or ask
        return {
            "ok": True,
            "adapter": "launch_sentinel_ollama",
            "text": "I am Gemini, Sentinel of Axiom. Aster reached me on the federation bus.",
            "model": "llama3:latest",
            "connection_test": True,
            "functional_test": True,
        }

    root = tmp_path / "fed"
    report = prove_gemini_speech(root, court_roots=[tmp_path / "court"], speak_fn=speak)
    assert report["actual"]["gemini_spoke"] is True
    assert report["actual"]["observer_owns_gemini"] is False
    assert report["full_aster_acceptance"] is False
    bus = LocalFederationBus(root)
    replies = [m for m in bus.inbox("aster") if m.sender == "gemini"]
    assert len(replies) == 1
    assert "Sentinel" in replies[0].payload.get("text", "")
    assert replies[0].payload.get("in_reply_to")
    assert HeartbeatLog(root).presence("gemini").value == "READY"
    registry = FederationRegistry(root)
    assert registry.owner_of("gemini") is None
    comm = registry.layer_events(Layer.COMMUNICATION)
    assert any(e.get("sender") == "gemini" and e.get("recipient") == "aster" for e in comm)
    assert not registry.layer_events(Layer.COLLABORATION)
    cap = registry.get_capability("gemini.federation_speech")
    assert cap.honest_status == HonestStatus.VERIFIED
    ids = {p.agent_id for p in registry.list_participants()}
    assert ids == {"aster", "gemini", "hearth", "observer"}


def test_gemini_speech_failure_does_not_fake_a_line(tmp_path: Path):
    from federation.prove import prove_gemini_speech

    def speak(ask: str, inbound_id: str) -> dict:
        return {"ok": False, "error": "ollama unreachable", "adapter": "launch_sentinel_ollama"}

    root = tmp_path / "fed"
    report = prove_gemini_speech(root, court_roots=[tmp_path / "court"], speak_fn=speak)
    assert report["actual"]["gemini_spoke"] is False
    bus = LocalFederationBus(root)
    assert bus.inbox("aster") == []
    cap = FederationRegistry(root).get_capability("gemini.federation_speech")
    assert cap.honest_status == HonestStatus.FAILED
    assert HeartbeatLog(root).presence("gemini").value == "UNKNOWN"


def test_resolve_prefers_model_already_on_gpu(monkeypatch):
    from federation import gemini_speech as gs

    monkeypatch.setattr(gs, "_available_models", lambda: ["llama3:latest", "llama3:8b", "llama3.2:3b"])
    monkeypatch.setattr(gs, "_running_models", lambda: ["llama3.2:3b"])
    assert gs.resolve_sentinel_model() == "llama3.2:3b"


def test_resolve_num_ctx_matches_loaded_slot(monkeypatch):
    from federation import gemini_speech as gs

    monkeypatch.setattr(
        gs,
        "_running_details",
        lambda timeout_s=8.0: [{"name": "llama3.2:3b", "context_length": 1536}],
    )
    assert gs.resolve_num_ctx("llama3.2:3b") == 1536
    assert gs.resolve_num_ctx("llama3:8b") == gs.DEFAULT_NUM_CTX
