"""Phase 2 thin — investigation + profession posts. Not quests. Not pods."""
from __future__ import annotations

from living_home_gameplay import look_into, profession_roster, ensure_gameplay


def _home_with_lead() -> dict:
    home: dict = {
        "tick": 3,
        "people": {
            "aster": {"place": "aster_lab", "purpose_plain": "watching"},
            "observer": {"place": "observer_desk", "stance": "working", "talking_to": ""},
        },
        "world_leads": [
            {
                "id": "lead_windmill",
                "description": "The old windmill",
                "status": "rumor",
                "player_involvement": False,
            }
        ],
        "utterances": [],
        "world_history": [],
    }
    ensure_gameplay(home)
    return home


def test_profession_roster_is_posts_not_pods():
    rows = profession_roster()
    ids = {r["id"] for r in rows}
    assert "aster" in ids and "apex" in ids and "observer" in ids
    obs = next(r for r in rows if r["id"] == "observer")
    assert obs["village_work"] is False
    assert "door" in (obs.get("note") or "").lower() or obs["profession"] == "independent_desk"


def test_look_into_marks_investigating_not_a_quest():
    home = _home_with_lead()
    lead = look_into(home, "lead_windmill", place="windmill")
    assert lead is not None
    assert lead["status"] == "investigating"
    assert lead["player_involvement"] is True
    assert lead.get("physical_link") == "windmill"
    assert home["gameplay"]["layer"] == "18b"
    notes = " ".join(str(x.get("text") or "") for x in (lead.get("discovery_history") or []))
    assert "quest" not in notes.lower() or "not a quest" in notes.lower() or "optional" in notes.lower()


def test_look_into_aster_notices_without_speech():
    home = _home_with_lead()
    look_into(home, "lead_windmill", place="windmill")
    ast = home["people"]["aster"]
    assert "Evidence Plot" in str(ast.get("purpose_plain") or "") or "optional" in str(ast.get("purpose_plain") or "").lower()
    assert home.get("utterances") == []


def test_look_into_does_not_hat_observer():
    home = _home_with_lead()
    look_into(home, "lead_windmill", place="windmill")
    obs = home["people"]["observer"]
    assert obs.get("stance") != "talking"
    assert not obs.get("talking_to")
    assert obs.get("place") == "observer_desk"


def test_look_into_missing_lead_returns_none():
    home = _home_with_lead()
    assert look_into(home, "lead_does_not_exist") is None


def test_village_talk_pauses_on_ollama_503():
    import living_home as lh

    lh._OLLAMA_BUSY_UNTIL = 0.0
    assert lh._village_talk_paused() is False
    lh._note_ollama_pressure("HTTP Error 503: model busy")
    assert lh._village_talk_paused() is True
    lh._OLLAMA_BUSY_UNTIL = 0.0


def test_mom_talk_pauses_village_chatter():
    import living_home as lh

    lh._OLLAMA_BUSY_UNTIL = 0.0
    lh._pause_village_for_mom(20.0)
    assert lh._village_talk_paused() is True
    lh._OLLAMA_BUSY_UNTIL = 0.0
