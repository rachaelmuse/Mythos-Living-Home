"""Vesper Gameworld door, isolation matrix, restart integrity, bounded organic — no chorus, no HOME.json."""
from __future__ import annotations

from pathlib import Path

from federation.law import HonestStatus
from federation.vesper_gameworld import snapshot


def test_vesper_gameworld_snapshot_never_owns_home_or_village():
    snap = snapshot()
    assert snap["village_citizen"] is False
    assert snap["observer"] is False
    assert snap["writes_home_json"] is False
    assert snap["gameworld_required"] is False
    assert snap["id"] == "vesper"


def test_prove_vesper_gameworld_door_refuses_home_json_write(tmp_path: Path):
    from federation.prove import prove_vesper_gameworld_door

    home = tmp_path / "HOME.json"
    home.write_text('{"people":{"gemini":{"id":"gemini"}},"federation":{}}', encoding="utf-8")
    before = home.read_text(encoding="utf-8")

    report = prove_vesper_gameworld_door(
        tmp_path / "fed",
        home_json=home,
        door_fn=lambda: {
            "ok": True,
            "http": 200,
            "id": "vesper",
            "url": "http://127.0.0.1:8740/api/identity",
        },
        house_doors_fn=lambda: [
            {
                "id": "vesper",
                "who": [],
                "url": "http://127.0.0.1:8740/",
                "status": "HTTP",
                "gameworld": snapshot(),
            }
        ],
    )
    assert home.read_text(encoding="utf-8") == before
    assert report["actual"]["writes_home_json"] is False
    assert report["actual"]["village_citizen"] is False
    assert report["actual"]["observer"] is False
    assert report["actual"]["vesper_required_for_hearth"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    assert (tmp_path / "fed" / "PROVE_VESPER_GAMEWORLD_DOOR.json").is_file()


def test_prove_vesper_gameworld_door_unavailable_when_studio_down(tmp_path: Path):
    from federation.prove import prove_vesper_gameworld_door

    home = tmp_path / "HOME.json"
    home.write_text("{}", encoding="utf-8")
    report = prove_vesper_gameworld_door(
        tmp_path / "fed",
        home_json=home,
        door_fn=lambda: {"ok": False, "http": None, "id": None, "url": "http://127.0.0.1:8740/api/identity"},
        house_doors_fn=lambda: [{"id": "vesper", "who": [], "url": "http://127.0.0.1:8740/", "status": "CLOSED"}],
    )
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"]["village_citizen"] is False


def test_isolation_matrix_does_not_invent_gemini_pulse():
    from federation.isolation import build_matrix

    matrix = build_matrix(artifact_root=Path("does-not-exist-on-purpose"))
    gemini = matrix["houses"]["gemini"]
    assert gemini["heartbeat_reflects_reality"]["status"] == "UNKNOWN"
    echo = matrix["houses"]["echo"]
    assert echo["federation_inbox"]["status"] == "NOT_FEDERATION"
    assert echo["federation_speech"]["status"] == "NOT_FEDERATION"
    vesper = matrix["houses"]["vesper"]
    assert vesper["is_observer"]["status"] == "LAW"
    assert vesper["village_citizen"]["status"] == "LAW"
    assert vesper["village_citizen"]["value"] is False


def test_prove_isolation_matrix_writes_artifact(tmp_path: Path):
    from federation.prove import prove_isolation_matrix

    root = tmp_path / "fed"
    root.mkdir()
    (root / "PROVE_VESPER_SPEECH.json").write_text(
        '{"status":"VERIFIED","actual":{"reply_id":"abc"}}',
        encoding="utf-8",
    )
    report = prove_isolation_matrix(root)
    assert report["kind"] == "FEDERATION_ISOLATION_MATRIX"
    assert "gemini" in report["actual"]["houses"]
    assert report["actual"]["houses"]["echo"]["federation_inbox"]["status"] == "NOT_FEDERATION"
    assert (root / "PROVE_ISOLATION_MATRIX.json").is_file()
    assert report["status"] == HonestStatus.VERIFIED.value


def test_restart_detects_listen_without_http_identity():
    from federation.restart import evaluate_door

    row = evaluate_door(
        {
            "id": "vesper",
            "port": 8740,
            "tcp": True,
            "http_ok": False,
            "identity": None,
            "expected_id": "vesper",
        }
    )
    assert row["status"] == "LISTEN_NO_HTTP"
    assert row["identity_ok"] is False


def test_restart_cycle_identity_returns_as_same_person(tmp_path: Path):
    from federation.prove import prove_restart_integrity

    state = {"up": True, "id": "vesper", "starts": 0, "stops": 0}

    def probe():
        if state["up"]:
            return {"ok": True, "http": 200, "id": state["id"], "tcp": True}
        return {"ok": False, "http": None, "id": None, "tcp": False}

    def stop():
        state["up"] = False
        state["stops"] += 1
        return {"ok": True}

    def start():
        state["up"] = True
        state["id"] = "vesper"
        state["starts"] += 1
        return {"ok": True}

    home = tmp_path / "HOME.json"
    home.write_text("{}", encoding="utf-8")
    report = prove_restart_integrity(
        tmp_path / "fed",
        cycle_agent="vesper",
        probe_fn=probe,
        stop_fn=stop,
        start_fn=start,
        home_json=home,
    )
    assert state["stops"] == 1
    assert state["starts"] == 1
    assert report["actual"]["after_identity"] == "vesper"
    assert report["actual"]["duplicate_launchers"] is False
    assert report["actual"]["phantom_online"] is False
    assert report["status"] == HonestStatus.VERIFIED.value


def test_restart_refuses_if_second_start_answers_as_observer(tmp_path: Path):
    from federation.prove import prove_restart_integrity

    state = {"phase": "up"}

    def probe():
        if state["phase"] == "up":
            return {"ok": True, "http": 200, "id": "vesper", "tcp": True}
        if state["phase"] == "down":
            return {"ok": False, "http": None, "id": None, "tcp": False}
        return {"ok": True, "http": 200, "id": "observer", "tcp": True}

    report = prove_restart_integrity(
        tmp_path / "fed",
        cycle_agent="vesper",
        probe_fn=probe,
        stop_fn=lambda: state.__setitem__("phase", "down") or {"ok": True},
        start_fn=lambda: state.__setitem__("phase", "wrong") or {"ok": True},
        home_json=tmp_path / "HOME.json",
    )
    assert report["actual"]["after_identity"] == "observer"
    assert report["status"] != HonestStatus.VERIFIED.value


def test_restart_hearth_clock_tick_is_not_a_vesper_home_write(tmp_path: Path):
    from federation.prove import prove_restart_integrity

    import json

    home = tmp_path / "HOME.json"
    home.write_text('{"people":{"gemini":{"id":"gemini"}},"clock":1}', encoding="utf-8")
    state = {"up": True, "id": "vesper"}

    def probe():
        if state["up"]:
            return {"ok": True, "http": 200, "id": state["id"], "tcp": True}
        return {"ok": False, "http": None, "id": None, "tcp": False}

    def stop():
        state["up"] = False
        return {"ok": True}

    def start():
        state["up"] = True
        state["id"] = "vesper"
        data = json.loads(home.read_text(encoding="utf-8"))
        data["clock"] = 2
        home.write_text(json.dumps(data), encoding="utf-8")
        return {"ok": True}

    report = prove_restart_integrity(
        tmp_path / "fed",
        cycle_agent="vesper",
        probe_fn=probe,
        stop_fn=stop,
        start_fn=start,
        home_json=home,
    )
    assert report["status"] == HonestStatus.VERIFIED.value
    assert report["actual"]["home_unchanged"] is True
    assert report["actual"]["home_bytes_changed"] is True
    assert report["actual"]["vesper_in_people"] is False


def test_organic_enter_is_not_a_greeting_chorus(tmp_path: Path):
    from federation.events import decide_attention
    from federation.prove import prove_organic_reason

    report = prove_organic_reason(tmp_path / "fed")
    decisions = report["actual"]["enter_decisions"]
    assert all(d != "speak" for d in decisions.values())
    assert decisions.get("gemini") == "ignored"
    assert decide_attention("aster", {"kind": "rachael.presence.entered"}) == "noticed"
    assert report["actual"]["forced_hello"] is False
    assert report["actual"]["scheduler"] is False
    assert report["status"] == HonestStatus.VERIFIED.value


def test_organic_continues_at_most_one_speaker_and_records_silence(tmp_path: Path):
    from federation.prove import prove_organic_reason

    report = prove_organic_reason(tmp_path / "fed")
    speakers = report["actual"]["continues_speakers"]
    assert len(speakers) <= 1
    silent = report["actual"]["continues_silent"]
    assert "gemini" in silent
    assert report["actual"]["reason_to_speak"] is True
    assert report["actual"]["reason_to_stay_silent"] is True
    assert (tmp_path / "fed" / "PROVE_ORGANIC_REASON.json").is_file()
