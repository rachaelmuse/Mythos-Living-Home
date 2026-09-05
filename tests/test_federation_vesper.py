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
