"""Matrix-Game adapter: honest UNAVAILABLE on this desk. Not a clip. Not Layer 17. Not identity."""
from __future__ import annotations

from pathlib import Path

from federation.law import HonestStatus


def test_matrix_game_adapter_refuses_on_this_host():
    from federation.matrix_game import MatrixGameAdapter, probe_host

    host = probe_host()
    assert host["engine"] == "UNAVAILABLE"
    assert host["primary_target"] == "3.0"
    assert host["secondary"] == "2.0"
    assert host["layer17_dream_view"] is False
    adapter = MatrixGameAdapter()
    clip = adapter.generate_video(prompt="lantern pier", who="merovin")
    assert clip["ok"] is False
    assert clip["status"] == "UNAVAILABLE"
    assert clip.get("path") in (None, "")
    assert "canned" not in (clip.get("error") or "").lower()
    assert clip.get("who") != "both"


def test_matrix_game_is_not_layer17_and_not_a_shared_brain():
    from federation.matrix_game import MatrixGameAdapter

    adapter = MatrixGameAdapter()
    assert adapter.name == "matrix_game"
    assert adapter.layer17 is False
    assert adapter.shared_brain is False
    merovin = adapter.generate_video(who="merovin")
    draven = adapter.generate_video(who="draven")
    assert merovin.get("who") == "merovin"
    assert draven.get("who") == "draven"
    assert merovin.get("who") != draven.get("who")


def test_prove_matrix_game_adapter_is_honest_unavailable(tmp_path: Path):
    from federation.prove import prove_matrix_game_adapter

    home = tmp_path / "HOME.json"
    home.write_text('{"people":{"gemini":{}}}', encoding="utf-8")
    report = prove_matrix_game_adapter(tmp_path / "fed", home_json=home)
    assert home.read_text(encoding="utf-8") == '{"people":{"gemini":{}}}'
    assert report["actual"]["engine"] == "UNAVAILABLE"
    assert report["actual"]["clip"] is None
    assert report["actual"]["installed"] is False
    assert report["actual"]["layer17"] is False
    assert report["actual"]["writes_home_json"] is False
    assert report["actual"]["simulated"] is False
    assert report["status"] == HonestStatus.VERIFIED.value
    assert (tmp_path / "fed" / "PROVE_MATRIX_GAME_ADAPTER.json").is_file()


def test_prove_matrix_game_fails_if_a_canned_clip_is_invented(tmp_path: Path):
    from federation.prove import prove_matrix_game_adapter

    report = prove_matrix_game_adapter(
        tmp_path / "fed",
        generate_fn=lambda: {
            "ok": True,
            "status": "VERIFIED",
            "path": "/tmp/fake.mp4",
            "who": "merovin",
            "installed": False,
        },
    )
    assert report["status"] != HonestStatus.VERIFIED.value
    assert report["actual"].get("simulated") is True
