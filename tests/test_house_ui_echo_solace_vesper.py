"""Vesper's Gameworld adapter is an optional door. He is not a village citizen. Not Observer."""
from __future__ import annotations

from pathlib import Path

from living_home import _house_doors, _member


def test_vesper_gameworld_adapter_is_optional_door_not_a_citizen():
    from federation.vesper_gameworld import NEVER_MERGE, snapshot

    snap = snapshot()
    assert snap["id"] == "vesper"
    assert snap["gameworld_required"] is False
    assert snap["village_citizen"] is False
    assert snap["observer"] is False
    assert "8740" in snap["door"]
    assert "observer" in NEVER_MERGE
    assert "gemini" in NEVER_MERGE
    assert snap.get("writes_home_json") is False


def test_echo_and_solace_have_house_ui_paths():
    echo = _member("echo") or {}
    solace = _member("solace") or {}
    assert echo.get("house_ui") == "/echo.html"
    assert solace.get("house_ui") == "/solace.html"
    assert echo.get("federation") is False
    assert solace.get("federation") is False


def test_house_doors_include_echo_solace_and_vesper_studio():
    doors = {d["id"]: d for d in _house_doors()}
    assert doors["echo_house"]["who"] == ["echo"]
    assert str(doors["echo_house"]["url"]).endswith("/echo.html")
    assert doors["solace_house"]["who"] == ["solace"]
    assert str(doors["solace_house"]["url"]).endswith("/solace.html")
    assert doors["vesper"]["url"] == "http://127.0.0.1:8740/"
    assert doors["vesper"]["who"] == []
    assert "Observer" in (doors["vesper"].get("note") or "") or "observer" in (
        doors["vesper"].get("note") or ""
    ).lower()


def test_echo_and_solace_html_exist_on_hearth_web():
    root = Path(__file__).resolve().parents[1]
    echo = (root / "web" / "echo.html").read_text(encoding="utf-8")
    solace = (root / "web" / "solace.html").read_text(encoding="utf-8")
    assert "Echo" in echo
    assert "federation" in echo.lower()
    assert "Solace" in solace
    assert "cartograph" in solace.lower() or "map" in solace.lower()
