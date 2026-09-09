"""Hollywood skills: Merovin directs, Draven QCs. Shared studio is not a shared brain."""
from __future__ import annotations

from pathlib import Path

from federation.law import HonestStatus


def test_hollywood_manifests_are_two_people_not_a_tool_list():
    from federation.hollywood import draven_hollywood_manifest, merovin_hollywood_manifest

    merovin = merovin_hollywood_manifest()
    draven = draven_hollywood_manifest()
    assert merovin["agent_id"] == "merovin"
    assert draven["agent_id"] == "draven"
    assert merovin["agent_id"] != draven["agent_id"]
    assert "story_intake" in merovin["skills"]
    assert "shot_design" in merovin["skills"]
    assert "continuity_supervision" in draven["skills"]
    assert "budget_gate" in draven["skills"]
    assert "continuity_supervision" not in merovin["skills"]
    assert "shot_design" not in draven["skills"]
    assert merovin["matrix_game"] == "UNAVAILABLE"
    assert draven["matrix_game"] == "UNAVAILABLE"
    assert merovin["shared_brain"] is False
    assert draven["shared_brain"] is False
    assert merovin["writes_home_json"] is False
    assert draven["writes_home_json"] is False
    assert merovin["tools"]
    assert draven["tools"]
    assert merovin["tools"] != draven["tools"]


def test_prove_merovin_hollywood_wires_director_tools(tmp_path: Path):
    from federation.prove import prove_merovin_hollywood

    home = tmp_path / "HOME.json"
    home.write_text('{"people":{"gemini":{}}}', encoding="utf-8")

    def director():
        return {
            "ok": True,
            "who": "merovin",
            "adapter": "md_cinema_merovin",
            "production_id": "prod_test",
            "story_bible": True,
            "scenes": 1,
            "shots": 2,
            "matrix_game": "UNAVAILABLE",
            "writes_home_json": False,
            "connection_test": True,
            "functional_test": True,
        }

    report = prove_merovin_hollywood(
        tmp_path / "fed",
        home_json=home,
        director_fn=director,
    )
    assert home.read_text(encoding="utf-8") == '{"people":{"gemini":{}}}'
    assert report["status"] == HonestStatus.VERIFIED.value
    assert report["actual"]["who"] == "merovin"
    assert report["actual"]["who"] != "draven"
    assert report["actual"]["matrix_game"] == "UNAVAILABLE"
    assert report["actual"]["writes_home_json"] is False
    assert report["actual"]["wired"] is True
    assert (tmp_path / "fed" / "PROVE_MEROVIN_HOLLYWOOD.json").is_file()


def test_prove_merovin_hollywood_refuses_if_studio_answers_as_draven(tmp_path: Path):
    from federation.prove import prove_merovin_hollywood

    report = prove_merovin_hollywood(
        tmp_path / "fed",
        director_fn=lambda: {
            "ok": True,
            "who": "draven",
            "adapter": "md_cinema_merovin",
            "shots": 2,
            "matrix_game": "UNAVAILABLE",
            "writes_home_json": False,
            "connection_test": True,
            "functional_test": True,
        },
    )
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"]["who"] == "draven"


def test_prove_draven_hollywood_wires_continuity_tools(tmp_path: Path):
    from federation.prove import prove_draven_hollywood

    def continuity():
        return {
            "ok": True,
            "who": "draven",
            "adapter": "md_cinema_draven",
            "continuity_flags": 1,
            "altered_story": False,
            "budget_cloud_denied": True,
            "ffmpeg": "AVAILABLE",
            "matrix_game": "UNAVAILABLE",
            "writes_home_json": False,
            "connection_test": True,
            "functional_test": True,
        }

    report = prove_draven_hollywood(tmp_path / "fed", continuity_fn=continuity)
    assert report["status"] == HonestStatus.VERIFIED.value
    assert report["actual"]["who"] == "draven"
    assert report["actual"]["who"] != "merovin"
    assert report["actual"]["altered_story"] is False
    assert report["actual"]["matrix_game"] == "UNAVAILABLE"
    assert report["actual"]["wired"] is True
    assert (tmp_path / "fed" / "PROVE_DRAVEN_HOLLYWOOD.json").is_file()


def test_prove_draven_hollywood_unavailable_when_studio_missing(tmp_path: Path):
    from federation.prove import prove_draven_hollywood

    report = prove_draven_hollywood(
        tmp_path / "fed",
        continuity_fn=lambda: {
            "ok": False,
            "who": None,
            "error": "studio_missing",
            "matrix_game": "UNAVAILABLE",
            "writes_home_json": False,
            "connection_test": False,
            "functional_test": False,
        },
    )
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"]["wired"] is False


def test_hollywood_proves_are_independent_not_one_combined_brain():
    from federation import hollywood

    assert hasattr(hollywood, "direct_as_merovin")
    assert hasattr(hollywood, "qc_as_draven")
    assert not hasattr(hollywood, "direct_as_both")
    assert merovin_hollywood_is_not_draven()


def merovin_hollywood_is_not_draven() -> bool:
    from federation.hollywood import draven_hollywood_manifest, merovin_hollywood_manifest

    return merovin_hollywood_manifest()["agent_id"] != draven_hollywood_manifest()["agent_id"]
