"""Codex twin on the federation bus as himself — never Gemini, not Observer staff."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.codex import codex_manifest_from_living_home, codex_manifest_from_member
from federation.court_adapter import INBOX_BOX
from federation.heartbeat import Presence
from federation.law import HonestStatus
from federation.prove import prove_codex
from federation.registry import FederationRegistry


def _codex_row() -> dict:
    return {
        "id": "codex",
        "name": "Codex",
        "also": "Jekyll / Mythos twin — NOT Gemini",
        "house": "codex_twin",
        "root": r"G:\Mythos_Codex",
        "port": 8780,
        "role": "archive, memory tone, story elder",
        "never_merge": ["gemini"],
    }


def test_codex_manifest_is_himself_not_gemini():
    manifest = codex_manifest_from_member(_codex_row())
    assert manifest.agent_id == "codex"
    assert manifest.house == "codex_twin"
    assert manifest.house != "axiom"
    assert manifest.identity_root == r"G:\Mythos_Codex"
    assert manifest.runtime.get("endpoint") == "http://127.0.0.1:8780"


def test_codex_manifest_rejects_gemini_id():
    with pytest.raises(ValueError):
        codex_manifest_from_member({"id": "gemini", "name": "Gemini", "house": "axiom"})


def test_codex_from_living_home_roster():
    manifest = codex_manifest_from_living_home()
    assert manifest.agent_id == "codex"
    assert "Mythos_Codex" in manifest.identity_root or "Codex" in manifest.identity_root


def test_prove_codex_does_not_register_when_door_down(tmp_path: Path):
    root = tmp_path / "fed"
    report = prove_codex(
        root,
        court_roots=[tmp_path / "court"],
        door_fn=lambda: {"ok": False, "http": 404, "id": None, "url": "http://127.0.0.1:8780/api/companion/presence"},
    )
    ids = {p.agent_id for p in FederationRegistry(root).list_participants()}
    assert "codex" not in ids
    assert "apex" not in ids
    assert report["actual"]["door_ok"] is False
    assert report["status"] != HonestStatus.VERIFIED.value


def test_prove_codex_delivery_when_door_up(tmp_path: Path):
    court = tmp_path / "court"
    (court / "codex" / INBOX_BOX).mkdir(parents=True)
    keep = court / "codex" / INBOX_BOX / "keep_mas.json"
    keep.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")
    report = prove_codex(
        tmp_path / "fed",
        court_roots=[court],
        door_fn=lambda: {
            "ok": True,
            "http": 200,
            "id": "codex",
            "url": "http://127.0.0.1:8780/api/companion/presence",
        },
    )
    actual = report["actual"]
    assert actual["observer_owns_codex"] is False
    assert "codex" in actual["participants"]
    assert "apex" not in actual["participants"]
    assert actual["codex_presence"] == Presence.UNKNOWN.value
    assert actual["codex_spoke"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    inbox = list((court / "codex" / INBOX_BOX).glob("*.json"))
    assert keep in inbox
    assert all(p.name == "keep_mas.json" for p in inbox)
