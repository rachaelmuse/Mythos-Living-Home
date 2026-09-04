"""Apex on the federation bus as himself — not Gemini, not Observer staff."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.apex import apex_manifest_from_living_home, apex_manifest_from_member
from federation.court_adapter import CourtFederationAdapter, INBOX_BOX
from federation.heartbeat import Presence
from federation.law import HonestStatus
from federation.prove import prove_apex
from federation.registry import FederationRegistry


def _apex_row() -> dict:
    return {
        "id": "apex",
        "name": "Apex",
        "also": "Hyde",
        "house": "apex",
        "root": r"D:\Mythos_Apex",
        "port": 8770,
        "role": "forge / hands / heavy tools",
    }


def test_apex_manifest_is_himself_not_gemini_or_observer():
    manifest = apex_manifest_from_member(_apex_row())
    assert manifest.agent_id == "apex"
    assert manifest.house == "apex"
    assert manifest.house != "the_observer"
    assert manifest.identity_root == r"D:\Mythos_Apex"
    assert manifest.runtime.get("endpoint") == "http://127.0.0.1:8770"
    assert "gemini" not in (manifest.capabilities or [])


def test_apex_manifest_rejects_other_ids():
    with pytest.raises(ValueError):
        apex_manifest_from_member({"id": "gemini", "name": "Nope", "house": "axiom"})


def test_apex_from_living_home_roster():
    manifest = apex_manifest_from_living_home()
    assert manifest.agent_id == "apex"
    assert "Mythos_Apex" in manifest.identity_root


def test_prove_apex_does_not_register_when_door_down(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_apex(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=lambda: {"ok": False, "http": None, "id": None, "url": "http://127.0.0.1:8770/api/companion/presence"},
    )
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "apex" not in ids
    assert "codex" not in ids
    assert "nova" not in ids
    assert report["actual"]["door_ok"] is False
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"].get("apex_spoke") is not True


def test_prove_apex_delivery_when_door_up(tmp_path: Path):
    court = tmp_path / "court"
    (court / "apex" / INBOX_BOX).mkdir(parents=True)
    keep = court / "apex" / INBOX_BOX / "keep_mas.json"
    keep.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")
    report = prove_apex(
        tmp_path / "fed",
        court_roots=[court],
        door_fn=lambda: {
            "ok": True,
            "http": 200,
            "id": "apex",
            "url": "http://127.0.0.1:8770/api/companion/presence",
        },
    )
    actual = report["actual"]
    assert actual["observer_owns_apex"] is False
    assert "apex" in actual["participants"]
    assert "codex" not in actual["participants"]
    assert "nova" not in actual["participants"]
    assert actual["apex_presence"] == Presence.UNKNOWN.value
    assert actual["message_status"] == "acknowledged"
    assert actual["apex_spoke"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    cap = actual["capability"]
    assert cap["status"] == HonestStatus.VERIFIED.value
    inbox = list((court / "apex" / INBOX_BOX).glob("*.json"))
    assert keep in inbox
    assert all(p.name == "keep_mas.json" for p in inbox)
    fed = list((court / "apex" / "federation").glob("*.json"))
    assert fed
