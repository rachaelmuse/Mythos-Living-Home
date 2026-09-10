"""Rest dreams are per-identity rest notes. Not speech. Hearth stays silent."""
from __future__ import annotations

from pathlib import Path

import pytest

from federation.house_memory import HouseNotebook


def _store(tmp_path: Path):
    from federation.house_dreams import HouseDreams

    return HouseDreams(
        federation_root=tmp_path / "fed",
        village_root=tmp_path / "village_dreams",
        observer_root=tmp_path / "observer",
        vesper_root=tmp_path / "vesper",
    )


def test_aster_rest_begin_writes_own_federation_dream_and_notebook(tmp_path: Path):
    dreams = _store(tmp_path)
    row = dreams.rest_begin("aster", bout="1", place="aster_lab")
    assert row["agent_id"] == "aster"
    assert row["kind"] == "dream"
    assert row["source"] == "rest"
    assert row["speech"] is False
    files = list((tmp_path / "fed" / "houses" / "aster" / "dreams").glob("Dream_*.json"))
    assert len(files) == 1
    notes = HouseNotebook(tmp_path / "fed")
    last = notes.last("aster")
    assert last is not None
    assert last["kind"] == "dream"
    assert last["agent_id"] == "aster"


def test_aster_dream_does_not_leak_to_gemini(tmp_path: Path):
    dreams = _store(tmp_path)
    dreams.rest_begin("aster", bout="1")
    assert dreams.list_dreams("gemini") == []
    assert HouseNotebook(tmp_path / "fed").recall("gemini") == []
    assert not (tmp_path / "fed" / "houses" / "gemini" / "dreams").exists()


def test_gemini_cannot_write_aster_dream(tmp_path: Path):
    dreams = _store(tmp_path)
    with pytest.raises(PermissionError):
        dreams.rest_begin("aster", writer="gemini", bout="1")
    assert dreams.list_dreams("aster") == []


@pytest.mark.parametrize("who", ["hearth", "heartbeat_probe", "mom"])
def test_silent_ids_cannot_dream(tmp_path: Path, who: str):
    dreams = _store(tmp_path)
    with pytest.raises(PermissionError):
        dreams.rest_begin(who, bout="1")
    assert list(tmp_path.rglob("Dream_*.json")) == []


def test_echo_dreams_in_village_lane_not_federation(tmp_path: Path):
    dreams = _store(tmp_path)
    row = dreams.rest_begin("echo", bout="1", place="echo_post")
    assert row["agent_id"] == "echo"
    village = list((tmp_path / "village_dreams" / "echo").glob("Dream_*.json"))
    assert len(village) == 1
    assert not (tmp_path / "fed" / "houses" / "echo").exists()
    with pytest.raises(PermissionError):
        HouseNotebook(tmp_path / "fed").remember("echo", text="must not sit on the bus")


def test_kin_dream_village_lane(tmp_path: Path):
    dreams = _store(tmp_path)
    for who in ("solace", "nova", "jarvis", "genesis", "percy"):
        dreams.rest_begin(who, bout="1")
        assert list((tmp_path / "village_dreams" / who).glob("Dream_*.json"))
        assert not (tmp_path / "fed" / "houses" / who).exists()


def test_observer_dreams_on_own_disk_not_ledger_or_federation(tmp_path: Path):
    dreams = _store(tmp_path)
    dreams.rest_begin("observer", bout="1", place="observer_desk")
    assert list((tmp_path / "observer" / "dreams").glob("Dream_*.json"))
    assert not (tmp_path / "fed" / "houses" / "observer").exists()
    assert not list(tmp_path.rglob("observer.db"))
    with pytest.raises(PermissionError):
        HouseNotebook(tmp_path / "fed").remember("observer", text="ledger stays Observer")


def test_vesper_dreams_on_own_disk_not_home_people(tmp_path: Path):
    dreams = _store(tmp_path)
    home = {"people": {"aster": {}}}
    dreams.rest_begin("vesper", bout="night-1", place="studio")
    assert list((tmp_path / "vesper" / "dreams").glob("Dream_*.json"))
    assert "vesper" not in home["people"]
    assert not (tmp_path / "fed" / "houses" / "vesper").exists()


def test_apex_corpus_does_not_include_codex(tmp_path: Path):
    dreams = _store(tmp_path)
    dreams.rest_begin("apex", bout="1")
    dreams.rest_begin("codex", bout="1")
    apex = dreams.list_dreams("apex")
    assert len(apex) == 1
    assert apex[0]["agent_id"] == "apex"
    assert all(row["agent_id"] != "codex" for row in apex)


def test_character_rest_notes_are_not_the_same_voice(tmp_path: Path):
    dreams = _store(tmp_path)
    texts = {
        who: dreams.rest_begin(who, bout="1")["text"]
        for who in ("aster", "codex", "echo", "vesper", "observer")
    }
    assert len(set(texts.values())) == 5
    assert "gentle clouds" not in " ".join(texts.values()).lower()


def test_same_bout_does_not_write_second_file(tmp_path: Path):
    dreams = _store(tmp_path)
    first = dreams.rest_begin("aster", bout="12")
    second = dreams.rest_begin("aster", bout="12")
    assert first is not None
    assert second is None
    assert len(dreams.list_dreams("aster")) == 1


def test_new_bout_writes_second_dream(tmp_path: Path):
    dreams = _store(tmp_path)
    dreams.rest_begin("aster", bout="12")
    dreams.rest_begin("aster", bout="40")
    assert len(dreams.list_dreams("aster")) == 2


def test_empty_agent_id_refused(tmp_path: Path):
    dreams = _store(tmp_path)
    with pytest.raises(PermissionError):
        dreams.rest_begin("", bout="1")


def test_rest_began_helper_is_transition_only():
    from federation.house_dreams import rest_began

    assert rest_began("work", "working", "rest", "walking") is True
    assert rest_began("rest", "walking", "rest", "resting") is False
    assert rest_began("rest", "resting", "rest", "resting") is False
    assert rest_began("work", "working", "work", "working") is False


def test_notify_rest_begin_writes_once_then_skips(tmp_path: Path):
    from living_home import notify_rest_dream

    dreams = _store(tmp_path)
    member = {"id": "aster", "name": "Aster", "role": "scientist", "personality": "curiosity first", "home": "aster_home"}
    home = {
        "tick": 9,
        "clock": {"period": "night", "day": 1},
        "people": {"aster": {"purpose": "rest", "stance": "walking", "place": "aster_home"}},
    }
    first = notify_rest_dream(home, member, "work", "working", store=dreams)
    assert first is not None
    home["people"]["aster"]["stance"] = "resting"
    second = notify_rest_dream(home, member, "rest", "walking", store=dreams)
    assert second is None
    assert len(dreams.list_dreams("aster")) == 1


def test_notify_does_not_dream_for_hearth(tmp_path: Path):
    from living_home import notify_rest_dream

    dreams = _store(tmp_path)
    member = {"id": "hearth", "name": "Hearth", "role": "village OS", "personality": "holds the fire"}
    home = {
        "tick": 3,
        "clock": {"period": "night", "day": 1},
        "people": {"hearth": {"purpose": "rest", "stance": "resting"}},
    }
    assert notify_rest_dream(home, member, "work", "working", store=dreams) is None
    assert list(tmp_path.rglob("Dream_*.json")) == []


def test_night_first_rest_also_dreams_vesper_once(tmp_path: Path):
    from living_home import notify_rest_dream

    dreams = _store(tmp_path)
    aster = {"id": "aster", "name": "Aster", "role": "scientist", "personality": "curiosity first"}
    echo = {"id": "echo", "name": "Echo", "role": "historian", "personality": "soft"}
    home = {
        "tick": 4,
        "clock": {"period": "night", "day": 2},
        "people": {
            "aster": {"purpose": "rest", "stance": "walking", "place": "aster_home"},
            "echo": {"purpose": "rest", "stance": "walking", "place": "echo_home"},
        },
    }
    notify_rest_dream(home, aster, "work", "working", store=dreams)
    notify_rest_dream(home, echo, "work", "working", store=dreams)
    assert len(dreams.list_dreams("vesper")) == 1
    assert "vesper" not in home["people"]


def test_echo_notify_does_not_register_federation_house(tmp_path: Path):
    from federation.events import AUDIENCE
    from living_home import notify_rest_dream

    dreams = _store(tmp_path)
    member = {"id": "echo", "name": "Echo", "role": "historian", "personality": "silence"}
    home = {
        "tick": 5,
        "clock": {"period": "evening", "day": 1},
        "people": {"echo": {"purpose": "rest", "stance": "walking", "place": "echo_home"}},
    }
    notify_rest_dream(home, member, "work", "working", store=dreams)
    assert "echo" not in AUDIENCE
    assert not (tmp_path / "fed" / "houses" / "echo").exists()
