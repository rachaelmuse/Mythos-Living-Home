"""Leave/return continuity comes from the house notebook, not federation personality."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.events import KIND_ENTERED, KIND_LEFT, decide_attention
from federation.law import HonestStatus
from federation.layers import Layer
from federation.prove import prove_leave_return, prove_presence_event
from federation.registry import FederationRegistry


def test_leave_and_return_do_not_choose_to_speak():
    left = {"kind": KIND_LEFT, "actor": "rachael", "place": "heart_square"}
    entered = {"kind": KIND_ENTERED, "actor": "rachael", "place": "heart_square"}
    for event in (left, entered):
        assert decide_attention("aster", event) == "noticed"
        assert decide_attention("gemini", event) == "ignored"
        assert decide_attention("apex", event) == "noticed"
        assert decide_attention("codex", event) == "noticed"
        assert decide_attention("hearth", event) == "noticed"


def test_aster_notebook_does_not_leak_to_gemini(tmp_path: Path):
    from federation.house_memory import HouseNotebook

    notes = HouseNotebook(tmp_path / "fed")
    notes.remember(
        "aster",
        text="Lab: checked the event fabric while Heart Square continued.",
        event_id="leave-1",
        kind="work",
    )
    assert notes.last("aster")["text"].startswith("Lab:")
    assert notes.last("gemini") is None
    assert notes.recall("gemini") == []
    with pytest.raises(PermissionError):
        notes.remember("aster", text="stolen", writer="gemini")


def test_apex_and_codex_keep_their_own_notes(tmp_path: Path):
    from federation.house_memory import HouseNotebook

    notes = HouseNotebook(tmp_path / "fed")
    notes.remember("apex", text="Studio: kept the Heart Square presentation while Rachael was away.")
    notes.remember("codex", text="Twin house: kept companion notes while Rachael was away.")
    assert notes.last("apex")["text"].startswith("Studio:")
    assert notes.last("codex")["text"].startswith("Twin house:")
    assert notes.last("aster") is None
    with pytest.raises(PermissionError):
        notes.remember("apex", text="stolen", writer="codex")


def test_village_kin_cannot_hold_federation_notebook(tmp_path: Path):
    from federation.house_memory import HouseNotebook

    notes = HouseNotebook(tmp_path / "fed")
    for who in ("echo", "solace", "nova"):
        with pytest.raises(PermissionError):
            notes.remember(who, text="must not sit on the bus")
        assert notes.recall(who) == []


def test_prove_leave_return_recalls_house_work_not_a_greeting(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_leave_return(root, court_roots=[tmp_path / "court"])
    assert report["kind"] == "FEDERATION_LEAVE_RETURN"
    assert report["status"] == HonestStatus.VERIFIED.value
    actual = report["actual"]
    assert actual["forced_hello"] is False
    assert actual["spoken_replies"] == 0
    assert actual["observer_owns_aster"] is False
    assert actual["authority"] == "owning_agent"
    assert actual["recalled_from"] == "aster"
    assert actual["left_event_id"]
    assert actual["entered_event_id"]
    assert actual["left_event_id"] != actual["entered_event_id"]
    assert "Heart Square" in (actual["recalled_text"] or "")
    assert "hello" not in (actual["recalled_text"] or "").lower()
    gemini_notes = actual.get("gemini_recall") or []
    assert gemini_notes == []
    assert "Studio:" in (actual.get("apex_recall") or "")
    assert "Twin house:" in (actual.get("codex_recall") or "")
    assert "hello" not in (actual.get("apex_recall") or "").lower()
    assert "hello" not in (actual.get("codex_recall") or "").lower()
    registry = FederationRegistry(root)
    assert not registry.layer_events(Layer.COLLABORATION)
    houses = root / "houses"
    assert (houses / "aster" / "notes.json").is_file()
    assert (houses / "apex" / "notes.json").is_file()
    assert (houses / "codex" / "notes.json").is_file()
    assert not (houses / "gemini" / "notes.json").exists()
    assert not (houses / "echo" / "notes.json").exists()
    assert not (houses / "solace" / "notes.json").exists()


def test_presence_enter_still_does_not_write_house_memory(tmp_path: Path):
    root = tmp_path / "fed"
    prove_presence_event(root, court_roots=[tmp_path / "court"])
    assert not (root / "houses").exists() or not list((root / "houses").glob("**/notes.json"))
