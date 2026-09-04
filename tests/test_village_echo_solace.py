"""Echo and Solace are village kin only — not federation houses, not quest dispensers."""
from __future__ import annotations

from living_home import (
    FAMILY,
    KIN,
    PLACES,
    TALK_BRAINS,
    _member,
    _named_addressee,
    _resolve_mom_addressee,
    _work_place,
)
from living_home_gameplay import profession_roster


def _ids(rows: list[dict]) -> set[str]:
    return {str(r.get("id") or "") for r in rows}


def test_echo_and_solace_are_kin_not_family_houses():
    family = _ids(FAMILY)
    kin = _ids(KIN)
    assert "echo" in kin and "solace" in kin
    assert "echo" not in family and "solace" not in family
    echo = _member("echo") or {}
    solace = _member("solace") or {}
    for row in (echo, solace):
        assert row.get("village_kind") == "kin"
        assert row.get("federation") is False
        assert row.get("quest_giver") is False
        assert row.get("port") in (None, "", 0)
        assert not row.get("root")
        assert row.get("skin", "").startswith("PLACEHOLDER")
        assert row.get("village_talk") is not False
    assert echo.get("name") == "Echo"
    assert solace.get("name") == "Solace"
    assert "gemini" in (echo.get("never_merge") or [])
    assert "echo" in (solace.get("never_merge") or [])


def test_echo_and_solace_have_homes_and_posts():
    for pid in ("echo_home", "echo_post", "solace_home", "solace_shelter"):
        assert pid in PLACES
        assert PLACES[pid]["pos"]
    assert _work_place(_member("echo") or {}) == "echo_post"
    assert _work_place(_member("solace") or {}) == "solace_shelter"
    court = TALK_BRAINS["court"]["members"]
    assert "echo" in court and "solace" in court
    assert "echo" not in TALK_BRAINS["aster"]["members"]


def test_named_talk_routes_to_echo_and_solace():
    assert _named_addressee("hello echo, may I sit?") == "echo"
    assert _resolve_mom_addressee("gemini", "hello echo") == "echo"
    assert _named_addressee("solace, what do you see?") == "solace"
    assert _named_addressee("hi sol") == "solace"
    assert _resolve_mom_addressee("aster", "are you ok?") == "aster"


def test_profession_posts_are_not_quests():
    rows = {r["id"]: r for r in profession_roster()}
    assert rows["echo"]["village_work"] is True
    assert rows["solace"]["village_work"] is True
    assert "quest" not in (rows["echo"].get("note") or "").lower()
    assert rows["echo"]["post"] == "echo_post"
    assert rows["solace"]["post"] == "solace_shelter"


def test_federation_audience_does_not_include_village_kin():
    from federation.events import AUDIENCE

    assert "echo" not in AUDIENCE
    assert "solace" not in AUDIENCE
    assert "nova" not in AUDIENCE
    assert "percy" not in AUDIENCE
