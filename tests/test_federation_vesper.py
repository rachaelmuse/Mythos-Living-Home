"""Vesper joins the federation as himself — journalist desk, not Observer, not a village hat."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.court_adapter import INBOX_BOX
from federation.heartbeat import Presence
from federation.law import HonestStatus
from federation.prove import prove_vesper
from federation.registry import FederationRegistry
from federation.vesper import vesper_manifest_from_identity, vesper_manifest_from_member


def _vesper_row() -> dict:
    return {
        "id": "vesper",
        "name": "Vesper",
        "house": "vesper",
        "root": r"D:\Mythos_Vesper",
        "port": 8740,
        "role": "Investigative journalist / documentary host",
    }


def test_vesper_manifest_is_not_observer_or_village_citizen():
    manifest = vesper_manifest_from_member(_vesper_row())
    assert manifest.agent_id == "vesper"
    assert manifest.house == "vesper"
    assert manifest.house != "the_observer"
    assert manifest.identity_root == r"D:\Mythos_Vesper"
    assert manifest.runtime.get("endpoint") == "http://127.0.0.1:8740"
    assert "observer" not in (manifest.capabilities or [])


def test_vesper_manifest_rejects_observer_id():
    with pytest.raises(ValueError):
        vesper_manifest_from_member({"id": "observer", "name": "The Observer", "house": "the_observer"})


def test_vesper_from_identity_file():
    manifest = vesper_manifest_from_identity()
    assert manifest.agent_id == "vesper"
    assert "Mythos_Vesper" in manifest.identity_root
    assert manifest.house != "the_observer"


def test_prove_vesper_does_not_register_when_door_down(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_vesper(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=lambda: {
            "ok": False,
            "http": None,
            "id": None,
            "url": "http://127.0.0.1:8740/api/identity",
        },
    )
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "vesper" not in ids
    assert "echo" not in ids
    assert report["actual"]["door_ok"] is False
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"].get("vesper_spoke") is not True


def test_prove_vesper_delivery_when_door_up(tmp_path: Path):
    court = tmp_path / "court"
    (court / "vesper" / INBOX_BOX).mkdir(parents=True)
    keep = court / "vesper" / INBOX_BOX / "keep_mas.json"
    keep.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")
    report = prove_vesper(
        tmp_path / "fed",
        court_roots=[court],
        door_fn=lambda: {
            "ok": True,
            "http": 200,
            "id": "vesper",
            "url": "http://127.0.0.1:8740/api/identity",
        },
    )
    actual = report["actual"]
    assert actual["observer_owns_vesper"] is False
    assert "vesper" in actual["participants"]
    assert actual["vesper_presence"] == Presence.UNKNOWN.value
    assert actual["message_status"] == "acknowledged"
    assert actual["vesper_spoke"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    inbox = list((court / "vesper" / INBOX_BOX).glob("*.json"))
    assert keep in inbox
    assert all(p.name == "keep_mas.json" for p in inbox)
    assert list((court / "vesper" / "federation").glob("*.json"))


def _vesper_door_up() -> dict:
    return {"ok": True, "http": 200, "id": "vesper", "url": "http://127.0.0.1:8740/api/identity"}


def test_prove_vesper_speech_refuses_when_door_down(tmp_path: Path):
    from federation.prove import prove_vesper_speech

    root = tmp_path / "fed"

    def speak(ask: str, inbound_id: str) -> dict:
        raise AssertionError("must not speak while Vesper studio is down")

    report = prove_vesper_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=lambda: {
            "ok": False,
            "http": None,
            "id": None,
            "url": "http://127.0.0.1:8740/api/identity",
        },
        speak_fn=speak,
    )
    assert report["status"] == HonestStatus.UNAVAILABLE.value
    assert report["actual"]["vesper_spoke"] is False
    assert report["actual"]["door_ok"] is False
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "vesper" not in ids
    with pytest.raises(KeyError):
        FederationRegistry(root).get_capability("vesper.federation_speech")
    assert (root / "PROVE_VESPER_SPEECH.json").is_file()


def test_vesper_speech_persists_reply_and_pulses(tmp_path: Path):
    from federation.heartbeat import HeartbeatLog
    from federation.prove import prove_vesper_speech
    from federation.transport import LocalFederationBus

    def speak(ask: str, inbound_id: str) -> dict:
        assert ask
        return {
            "ok": True,
            "adapter": "vesper_studio_http",
            "text": "I am Vesper, investigative journalist. Not the Observer. This is my studio.",
            "model": "qwen3:4b",
            "who": "vesper",
            "house_kernel": "vesper",
            "connection_test": True,
            "functional_test": True,
            "vesper_spoke": True,
        }

    root = tmp_path / "fed"
    court = tmp_path / "court"
    report = prove_vesper_speech(root, court_roots=[court], door_fn=_vesper_door_up, speak_fn=speak)
    assert report["actual"]["vesper_spoke"] is True
    assert report["actual"]["observer_owns_vesper"] is False
    assert report["actual"]["door_ok"] is True
    assert report["kind"] == "FEDERATION_VESPER_SPEECH"
    bus = LocalFederationBus(root)
    replies = [m for m in bus.inbox("aster") if m.sender == "vesper"]
    assert len(replies) == 1
    assert "Vesper" in replies[0].payload.get("text", "")
    assert "I am the Observer" not in replies[0].payload.get("text", "")
    assert replies[0].payload.get("from") == "vesper"
    assert replies[0].payload.get("adapter") == "vesper_studio_http"
    assert HeartbeatLog(root).presence("vesper").value == "READY"
    registry = FederationRegistry(root)
    assert registry.owner_of("vesper") is None
    cap = registry.get_capability("vesper.federation_speech")
    assert cap.honest_status == HonestStatus.VERIFIED
    ids = {p.agent_id for p in registry.list_participants()}
    assert "vesper" in ids
    assert "echo" not in ids
    assert (root / "PROVE_VESPER_SPEECH.json").is_file()


def test_vesper_speech_retry_does_not_overwrite_failed_artifact(tmp_path: Path):
    from federation.prove import prove_vesper_speech

    root = tmp_path / "fed"
    root.mkdir()
    failed = root / "PROVE_VESPER_SPEECH.json"
    failed.write_text('{"kind": "FEDERATION_VESPER_SPEECH", "status": "FAILED", "keep": "keep-fail"}', encoding="utf-8")

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": True,
            "adapter": "vesper_studio_http",
            "text": "I am Vesper, journalist. Not Observer.",
            "vesper_spoke": True,
        }

    report = prove_vesper_speech(root, court_roots=[tmp_path / "court"], door_fn=_vesper_door_up, speak_fn=speak)
    assert failed.read_text(encoding="utf-8").find("keep-fail") >= 0
    assert report["actual"]["artifact"].endswith("PROVE_VESPER_SPEECH_2.json")
    assert (root / "PROVE_VESPER_SPEECH_2.json").is_file()


def test_vesper_speech_failure_does_not_fake_a_line(tmp_path: Path):
    from federation.prove import prove_vesper_speech

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": False,
            "adapter": "vesper_studio_http",
            "error": "canned_or_model_down",
            "text": None,
            "vesper_spoke": False,
            "connection_test": True,
            "functional_test": False,
        }

    report = prove_vesper_speech(
        tmp_path / "fed",
        court_roots=[tmp_path / "court"],
        door_fn=_vesper_door_up,
        speak_fn=speak,
    )
    assert report["actual"]["vesper_spoke"] is False
    assert report["status"] != HonestStatus.VERIFIED.value


def test_vesper_speech_rejects_observer_identity_leak(tmp_path: Path):
    from federation.prove import prove_vesper_speech

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": True,
            "adapter": "vesper_studio_http",
            "text": "I am the Observer. I audit the family from :8730.",
            "vesper_spoke": True,
        }

    report = prove_vesper_speech(
        tmp_path / "fed",
        court_roots=[tmp_path / "court"],
        door_fn=_vesper_door_up,
        speak_fn=speak,
    )
    assert report["actual"]["vesper_spoke"] is False
    assert report["status"] != HonestStatus.VERIFIED.value


def test_vesper_speech_adapter_posts_studio_talk_only(monkeypatch):
    import json
    import urllib.request

    from federation.vesper_speech import ADAPTER, SYSTEM, speak_as_vesper

    captured: dict = {}

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {
                    "ok": True,
                    "source": "ollama",
                    "reply": "I am Vesper, investigative journalist. Not the Observer.",
                    "model": "qwen3:4b",
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout=None):
        captured["url"] = getattr(req, "full_url", None) or getattr(req, "get_full_url", lambda: "")()
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    spoken = speak_as_vesper("who_are_you", "inbound-1")
    assert spoken["ok"] is True
    assert spoken["adapter"] == ADAPTER
    assert spoken["vesper_spoke"] is True
    assert captured["url"].endswith("/api/talk")
    assert "5000" not in str(captured["url"])
    assert "8730" not in str(captured["url"])
    assert "You are Vesper" in SYSTEM
    assert "not Observer" in SYSTEM or "not the Observer" in SYSTEM.lower()


def test_vesper_speech_adapter_rejects_waiting_or_worksheet(monkeypatch):
    import json
    import urllib.request

    from federation.vesper_speech import speak_as_vesper

    class _Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {
                    "ok": False,
                    "source": "waiting",
                    "reply": None,
                    "error": "Ollama not reachable on :11434",
                }
            ).encode("utf-8")

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: _Resp())
    spoken = speak_as_vesper("who_are_you", "inbound-2")
    assert spoken["ok"] is False
    assert spoken["vesper_spoke"] is False
