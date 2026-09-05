"""Merovin and Draven join the federation as two people. Shared studio is not a merge."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.court_adapter import INBOX_BOX
from federation.draven import draven_manifest_from_living_home, draven_manifest_from_member
from federation.heartbeat import HeartbeatLog, Presence
from federation.law import HonestStatus
from federation.layers import Layer
from federation.merovin import merovin_manifest_from_living_home, merovin_manifest_from_member
from federation.prove import prove_draven, prove_merovin
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _merovin_row() -> dict:
    return {
        "id": "merovin",
        "name": "Merovin",
        "also": "cinema dreamer",
        "house": "merovin",
        "root": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio",
        "role": "movie-style vision, shot lists",
    }


def _draven_row() -> dict:
    return {
        "id": "draven",
        "name": "Draven",
        "also": "cinema guardian",
        "house": "merovin",
        "root": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio",
        "role": "continuity, honest delivery",
    }


def test_merovin_and_draven_are_two_houses_not_one_studio_soul():
    merovin = merovin_manifest_from_member(_merovin_row())
    draven = draven_manifest_from_member(_draven_row())
    assert merovin.agent_id == "merovin"
    assert draven.agent_id == "draven"
    assert merovin.agent_id != draven.agent_id
    assert merovin.house == "merovin"
    assert draven.house == "draven"
    assert merovin.house != draven.house
    assert merovin.identity_root == draven.identity_root
    assert merovin.runtime.get("endpoint") == "http://127.0.0.1:5000"
    assert draven.runtime.get("endpoint") == "http://127.0.0.1:5000"
    assert merovin.house != "the_observer"
    assert draven.house != "the_observer"
    assert merovin.house != "axiom"


def test_merovin_manifest_rejects_draven_id():
    with pytest.raises(ValueError):
        merovin_manifest_from_member({"id": "draven", "name": "Draven", "house": "merovin"})


def test_draven_manifest_rejects_merovin_id():
    with pytest.raises(ValueError):
        draven_manifest_from_member({"id": "merovin", "name": "Merovin", "house": "merovin"})


def test_cinema_manifests_from_living_home_roster():
    merovin = merovin_manifest_from_living_home()
    draven = draven_manifest_from_living_home()
    assert merovin.agent_id == "merovin"
    assert draven.agent_id == "draven"
    assert "Merovin_Draven" in merovin.identity_root or "Merovin" in merovin.identity_root


def test_prove_merovin_does_not_register_when_hud_down(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_merovin(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=lambda: {"ok": False, "http": None, "id": None, "url": "http://127.0.0.1:5000/"},
    )
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "merovin" not in ids
    assert "draven" not in ids
    assert "echo" not in ids
    assert report["actual"]["door_ok"] is False
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"].get("merovin_spoke") is not True


def test_prove_merovin_delivery_does_not_add_draven(tmp_path: Path):
    court = tmp_path / "court"
    (court / "merovin" / INBOX_BOX).mkdir(parents=True)
    keep = court / "merovin" / INBOX_BOX / "keep_mas.json"
    keep.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")
    report = prove_merovin(
        tmp_path / "fed",
        court_roots=[court],
        door_fn=lambda: {"ok": True, "http": 200, "id": "merovin", "url": "http://127.0.0.1:5000/"},
    )
    actual = report["actual"]
    assert actual["observer_owns_merovin"] is False
    assert "merovin" in actual["participants"]
    assert "draven" not in actual["participants"]
    assert "echo" not in actual["participants"]
    assert "solace" not in actual["participants"]
    assert actual["merovin_presence"] == Presence.UNKNOWN.value
    assert actual["message_status"] == "acknowledged"
    assert actual["merovin_spoke"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    inbox = list((court / "merovin" / INBOX_BOX).glob("*.json"))
    assert keep in inbox
    assert all(p.name == "keep_mas.json" for p in inbox)
    assert list((court / "merovin" / "federation").glob("*.json"))


def test_prove_draven_delivery_does_not_add_merovin(tmp_path: Path):
    court = tmp_path / "court"
    (court / "draven" / INBOX_BOX).mkdir(parents=True)
    keep = court / "draven" / INBOX_BOX / "keep_mas.json"
    keep.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")
    report = prove_draven(
        tmp_path / "fed",
        court_roots=[court],
        door_fn=lambda: {"ok": True, "http": 200, "id": "draven", "url": "http://127.0.0.1:5000/"},
    )
    actual = report["actual"]
    assert actual["observer_owns_draven"] is False
    assert "draven" in actual["participants"]
    assert "merovin" not in actual["participants"]
    assert actual["draven_spoke"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    inbox = list((court / "draven" / INBOX_BOX).glob("*.json"))
    assert keep in inbox
    assert all(p.name == "keep_mas.json" for p in inbox)
    assert list((court / "draven" / "federation").glob("*.json"))


def test_cinema_and_vesper_notice_without_joining_the_chorus():
    from federation.events import KIND_CONTINUES, KIND_ENTERED, decide_attention

    entered = {"kind": KIND_ENTERED, "actor": "rachael", "place": "heart_square"}
    continues = {"kind": KIND_CONTINUES, "actor": "hearth", "place": "heart_square"}
    for who in ("merovin", "draven", "vesper"):
        assert decide_attention(who, entered) == "noticed"
        assert decide_attention(who, continues) == "noticed"
        assert decide_attention(who, continues) != "speak"


def _cinema_door_up_merovin() -> dict:
    return {"ok": True, "http": 200, "id": "merovin", "url": "http://127.0.0.1:5000/"}


def _cinema_door_down() -> dict:
    return {
        "ok": False,
        "http": None,
        "id": None,
        "url": "http://127.0.0.1:5000/",
        "error": "refused",
    }


def test_prove_merovin_delivery_still_does_not_speak(tmp_path: Path):
    report = prove_merovin(
        tmp_path / "fed",
        court_roots=[tmp_path / "court"],
        door_fn=_cinema_door_up_merovin,
    )
    assert report["actual"]["merovin_spoke"] is False


def test_prove_merovin_speech_refuses_when_door_down(tmp_path: Path):
    from federation.prove import prove_merovin_speech

    root = tmp_path / "fed"

    def speak(ask: str, inbound_id: str) -> dict:
        raise AssertionError("must not speak while the cinema HUD is down")

    report = prove_merovin_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_cinema_door_down,
        speak_fn=speak,
    )
    assert report["status"] == HonestStatus.UNAVAILABLE.value
    assert report["actual"]["merovin_spoke"] is False
    assert report["actual"]["door_ok"] is False
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "merovin" not in ids
    assert "draven" not in ids
    with pytest.raises(KeyError):
        FederationRegistry(root).get_capability("merovin.federation_speech")
    assert (root / "PROVE_MEROVIN_SPEECH.json").is_file()


def test_merovin_speech_persists_reply_and_pulses(tmp_path: Path):
    from federation.prove import prove_merovin_speech

    def speak(ask: str, inbound_id: str) -> dict:
        assert ask
        return {
            "ok": True,
            "adapter": "cinema_hud_http",
            "text": "I am Merovin, cinema vision of Merovin_Draven_Studio. Aster reached my house, not Draven's.",
            "model": "gemma2:9b",
            "who": "merovin",
            "house_kernel": "merovin",
            "connection_test": True,
            "functional_test": True,
            "merovin_spoke": True,
        }

    root = tmp_path / "fed"
    court = tmp_path / "court"
    report = prove_merovin_speech(root, court_roots=[court], door_fn=_cinema_door_up_merovin, speak_fn=speak)
    assert report["actual"]["merovin_spoke"] is True
    assert report["actual"]["observer_owns_merovin"] is False
    assert report["actual"]["door_ok"] is True
    assert report["kind"] == "FEDERATION_MEROVIN_SPEECH"
    bus = LocalFederationBus(root)
    replies = [m for m in bus.inbox("aster") if m.sender == "merovin"]
    assert len(replies) == 1
    assert "Merovin" in replies[0].payload.get("text", "")
    assert "I am Draven" not in replies[0].payload.get("text", "")
    assert replies[0].payload.get("from") == "merovin"
    assert replies[0].payload.get("in_reply_to")
    assert replies[0].payload.get("adapter") == "cinema_hud_http"
    assert HeartbeatLog(root).presence("merovin").value == "READY"
    registry = FederationRegistry(root)
    assert registry.owner_of("merovin") is None
    comm = registry.layer_events(Layer.COMMUNICATION)
    assert any(e.get("sender") == "merovin" and e.get("recipient") == "aster" for e in comm)
    assert not registry.layer_events(Layer.COLLABORATION)
    cap = registry.get_capability("merovin.federation_speech")
    assert cap.honest_status == HonestStatus.VERIFIED
    ids = {p.agent_id for p in registry.list_participants()}
    assert "merovin" in ids
    assert "draven" not in ids
    assert "gemini" not in ids
    assert "echo" not in ids
    notices = list((court / "aster" / "federation").glob("*_reply.json"))
    assert notices
    data = notices[0].read_text(encoding="utf-8")
    assert "merovin_spoke" in data
    assert '"from": "draven"' not in data
    assert '"from": "gemini"' not in data
    assert (root / "PROVE_MEROVIN_SPEECH.json").is_file()


def test_merovin_speech_does_not_crash_if_draven_already_seated(tmp_path: Path):
    from federation.prove import prove_merovin_speech

    root = tmp_path / "fed"
    FederationRegistry(root).register(draven_manifest_from_member(_draven_row()))

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": True,
            "adapter": "cinema_hud_http",
            "text": "I am Merovin, cinema vision. Not Draven.",
            "who": "merovin",
            "merovin_spoke": True,
        }

    report = prove_merovin_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_cinema_door_up_merovin,
        speak_fn=speak,
    )
    assert report["actual"]["merovin_spoke"] is True
    assert "draven" in report["actual"]["participants"]
    assert report["kind"] == "FEDERATION_MEROVIN_SPEECH"
    assert (root / "PROVE_MEROVIN_SPEECH.json").is_file()


def test_merovin_speech_failure_does_not_fake_a_line(tmp_path: Path):
    from federation.prove import prove_merovin_speech

    def speak(ask: str, inbound_id: str) -> dict:
        return {"ok": False, "error": "cinema chat unreachable", "adapter": "cinema_hud_http"}

    root = tmp_path / "fed"
    report = prove_merovin_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_cinema_door_up_merovin,
        speak_fn=speak,
    )
    assert report["actual"]["merovin_spoke"] is False
    bus = LocalFederationBus(root)
    assert bus.inbox("aster") == []
    cap = FederationRegistry(root).get_capability("merovin.federation_speech")
    assert cap.honest_status == HonestStatus.FAILED
    assert HeartbeatLog(root).presence("merovin").value == "UNKNOWN"


def test_merovin_speech_rejects_draven_identity_leak(tmp_path: Path):
    from federation.prove import prove_merovin_speech

    def speak(ask: str, inbound_id: str) -> dict:
        return {
            "ok": True,
            "adapter": "cinema_hud_http",
            "text": "I am Draven, continuity lock. The shared HUD answered for both of us.",
            "model": "phi3:latest",
            "who": "merovin",
            "connection_test": True,
            "functional_test": True,
            "merovin_spoke": True,
        }

    root = tmp_path / "fed"
    report = prove_merovin_speech(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=_cinema_door_up_merovin,
        speak_fn=speak,
    )
    assert report["actual"]["merovin_spoke"] is False
    assert report["status"] != HonestStatus.VERIFIED.value
    bus = LocalFederationBus(root)
    assert [m for m in bus.inbox("aster") if m.sender == "merovin"] == []


def test_merovin_speech_adapter_posts_who_merovin_only(monkeypatch):
    import json
    import urllib.request

    from federation.merovin_speech import ADAPTER, SYSTEM, speak_as_merovin

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
                    "replies": {"Merovin": "I am Merovin, cinema vision. Not Draven."},
                    "who": "merovin",
                }
            ).encode("utf-8")

    def fake_urlopen(req, timeout=None):
        captured["url"] = getattr(req, "full_url", None) or getattr(req, "get_full_url", lambda: "")()
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _Resp()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    spoken = speak_as_merovin("who_are_you", "inbound-1")
    assert spoken["ok"] is True
    assert spoken["adapter"] == ADAPTER
    assert spoken["adapter"] == "cinema_hud_http"
    assert spoken["merovin_spoke"] is True
    assert "Merovin" in spoken["text"]
    assert captured["url"].endswith("/api/chat")
    assert "5000" in captured["url"]
    assert captured["body"]["who"] == "merovin"
    assert captured["body"]["who"] != "draven"
    assert captured["body"]["who"] != "both"
    assert captured["body"].get("speak") is False
    assert "You are Merovin" in SYSTEM
    assert "not Draven" in SYSTEM
    assert "not Observer" in SYSTEM
    assert "Hearth" not in ADAPTER
    assert "ollama" not in ADAPTER


def test_merovin_speech_adapter_rejects_shared_brain_reply(monkeypatch):
    import json
    import urllib.request

    from federation.merovin_speech import speak_as_merovin

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
                    "replies": {
                        "Merovin": "I am Merovin.",
                        "Draven": "I am Draven.",
                    },
                    "who": "both",
                }
            ).encode("utf-8")

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: _Resp())
    spoken = speak_as_merovin("who_are_you", "inbound-2")
    assert spoken["ok"] is False
    assert spoken["merovin_spoke"] is False
    err = str(spoken.get("error") or "").lower()
    assert "draven" in err or "leak" in err or "both" in err
