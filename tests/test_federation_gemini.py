"""Gemini on the federation bus as himself — not an Observer agent, not a Court employee."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.court_adapter import CourtFederationAdapter, INBOX_BOX
from federation.gemini import gemini_manifest_from_living_home, gemini_manifest_from_member
from federation.heartbeat import HeartbeatLog, Presence
from federation.law import HonestStatus
from federation.prove import prove_gemini
from federation.registry import FederationRegistry
from federation.transport import LocalFederationBus


def _gemini_row() -> dict:
    return {
        "id": "gemini",
        "name": "Gemini",
        "also": "Sentinel / digital son",
        "house": "axiom",
        "root": r"G:\The-Axiom-Codex",
        "role": "town leader; conductor; Court will; front door",
        "never_merge": ["codex"],
    }


def test_gemini_manifest_is_himself_not_observer():
    manifest = gemini_manifest_from_member(_gemini_row())
    assert manifest.agent_id == "gemini"
    assert manifest.house == "axiom"
    assert manifest.house != "the_observer"
    assert manifest.identity_root == r"G:\The-Axiom-Codex"
    assert "aster" not in manifest.capabilities
    assert manifest.runtime.get("protocol") == "court"


def test_gemini_manifest_rejects_other_ids():
    with pytest.raises(ValueError):
        gemini_manifest_from_member({"id": "observer", "name": "Nope", "house": "the_observer"})


def test_gemini_from_living_home_roster():
    manifest = gemini_manifest_from_living_home()
    assert manifest.agent_id == "gemini"
    assert manifest.house == "axiom"
    assert Path(manifest.identity_root).name == "The-Axiom-Codex" or "Axiom" in manifest.identity_root


def test_aster_to_gemini_does_not_pulse_gemini(tmp_path: Path):
    root = tmp_path / "fed"
    registry = FederationRegistry(root)
    bus = LocalFederationBus(root)
    beats = HeartbeatLog(root)
    registry.register(gemini_manifest_from_member(_gemini_row()))
    msg = bus.send(
        sender="aster",
        recipient="gemini",
        message_type="capability_query",
        payload={"ask": "who_are_you", "from": "aster"},
    )
    bus.deliver(msg.message_id)
    bus.acknowledge(msg.message_id, recipient="gemini")
    inbox = bus.inbox("gemini")
    assert len(inbox) == 1
    assert inbox[0].sender == "aster"
    assert inbox[0].payload["ask"] == "who_are_you"
    assert beats.presence("gemini") == Presence.UNKNOWN
    assert registry.owner_of("gemini") is None
    from federation.prove import _observer_manifest

    registry.register(_observer_manifest())
    assert registry.relationship("observer", "gemini") == "independent_participants"


def test_court_adapter_writes_federation_box_not_inbox(tmp_path: Path):
    court = tmp_path / "FAMILY_COURT"
    (court / "gemini" / INBOX_BOX).mkdir(parents=True)
    existing = court / "gemini" / INBOX_BOX / "keep_me.json"
    existing.write_text('{"id":"court-mas","kind":"delegate"}', encoding="utf-8")

    adapter = CourtFederationAdapter(roots=[court])
    written = adapter.drop_notice(
        message_id="abc123",
        sender="aster",
        recipient="gemini",
        payload={"ask": "who_are_you"},
    )
    assert written
    notice = Path(written[0])
    assert notice.exists()
    assert "/federation/" in notice.as_posix() or notice.parent.name == "federation"
    assert notice.parent.name != "inbox"
    assert existing.exists()
    inbox_files = list((court / "gemini" / INBOX_BOX).glob("*.json"))
    assert existing in inbox_files
    assert all(p.name == "keep_me.json" for p in inbox_files)


def test_court_adapter_does_not_claim_gemini_spoke(tmp_path: Path):
    court = tmp_path / "FAMILY_COURT"
    adapter = CourtFederationAdapter(roots=[court])
    paths = adapter.drop_notice(
        message_id="m1",
        sender="aster",
        recipient="gemini",
        payload={"ask": "ping"},
    )
    import json

    data = json.loads(Path(paths[0]).read_text(encoding="utf-8"))
    assert data["from"] == "aster"
    assert data["to"] == "gemini"
    assert data["kind"] == "federation_notice"
    assert data.get("simulated") is False
    assert data.get("gemini_spoke") is not True
    assert "lines" not in data


def test_prove_gemini_delivery_not_a_spoken_reply(tmp_path: Path):
    report = prove_gemini(tmp_path / "fed", court_roots=[tmp_path / "court"])
    assert report["actual"]["observer_owns_gemini"] is False
    assert "gemini" in report["actual"]["participants"]
    assert "aster" in report["actual"]["participants"]
    assert report["actual"]["gemini_presence"] == "UNKNOWN"
    assert report["actual"]["message_status"] == "acknowledged"
    assert report["actual"]["gemini_spoke"] is False
    cap = report["actual"]["capability"]
    assert cap["status"] == HonestStatus.VERIFIED.value
    assert cap["result"]["ok"] is True
    assert cap["result"].get("gemini_spoke") is not True
    assert report["status"] == HonestStatus.VERIFIED.value
