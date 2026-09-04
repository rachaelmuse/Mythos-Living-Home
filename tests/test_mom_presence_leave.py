"""Village leave is a real signal. A 12-minute gap is not Mom leaving."""
from __future__ import annotations

from pathlib import Path

import pytest


def test_mom_leave_publishes_left_not_entered(monkeypatch, tmp_path: Path):
    import living_home as lh

    monkeypatch.setattr(lh, "HOME_JSON", tmp_path / "HOME.json")
    monkeypatch.setattr(lh, "DATA", tmp_path)

    left: list[dict] = []
    entered: list[dict] = []

    def fake_left(**kwargs):
        left.append(kwargs)
        return {"kind": "rachael.presence.left", "event_id": "leave-1"}

    def fake_entered(**kwargs):
        entered.append(kwargs)
        return {"kind": "rachael.presence.entered", "event_id": "enter-1"}

    monkeypatch.setattr("federation.events.publish_mom_left", fake_left)
    monkeypatch.setattr("federation.events.publish_mom_entered", fake_entered)

    snap = lh.mom_presence("heart_square", leaving=True)
    pulse = snap.get("mom_presence") or {}
    assert pulse.get("session_leave") is True
    assert pulse.get("session_enter") is False
    assert left
    assert left[0]["place"] == "heart_square"
    assert not entered


def test_mom_leave_wins_over_session_enter(monkeypatch, tmp_path: Path):
    import living_home as lh

    monkeypatch.setattr(lh, "HOME_JSON", tmp_path / "HOME.json")
    monkeypatch.setattr(lh, "DATA", tmp_path)
    left: list[dict] = []
    monkeypatch.setattr(
        "federation.events.publish_mom_left",
        lambda **kwargs: left.append(kwargs) or {"event_id": "L"},
    )
    monkeypatch.setattr(
        "federation.events.publish_mom_entered",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("enter must not fire on leave")),
    )
    snap = lh.mom_presence("heart_square", session_enter=True, leaving=True)
    assert snap["mom_presence"]["session_leave"] is True
    assert snap["mom_presence"]["session_enter"] is False
    assert left
