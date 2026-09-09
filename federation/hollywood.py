"""Hollywood production skills. Merovin directs. Draven QCs. Matrix-Game stays UNAVAILABLE."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

STUDIO_PACKAGE = Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio\MD_Cinema_Studio")
MATRIX_GAME = "UNAVAILABLE"

MEROVIN_SKILLS = (
    "story_intake",
    "story_bible",
    "shot_design",
    "scene_composition",
    "visual_continuity_of_vision",
)
MEROVIN_TOOLS = (
    "md_cinema.pipeline.intake",
    "md_cinema.bibles.story_bible",
    "md_cinema.pipeline.scenes_shots",
)
DRAVEN_SKILLS = (
    "continuity_supervision",
    "shot_matching",
    "production_diagnostics",
    "budget_gate",
    "edit_preparation",
)
DRAVEN_TOOLS = (
    "md_cinema.continuity.matrix",
    "md_cinema.budget.gate",
    "md_cinema.adapters.editing_ffmpeg",
)


def merovin_hollywood_manifest() -> dict[str, Any]:
    return {
        "agent_id": "merovin",
        "role": "creative_director",
        "skills": list(MEROVIN_SKILLS),
        "tools": list(MEROVIN_TOOLS),
        "adapter": "md_cinema_merovin",
        "matrix_game": MATRIX_GAME,
        "shared_brain": False,
        "writes_home_json": False,
        "owns_resolve": False,
        "note": "Directs the existing MD_Cinema pipeline. Not Draven. Not the video engine.",
    }


def draven_hollywood_manifest() -> dict[str, Any]:
    return {
        "agent_id": "draven",
        "role": "continuity_supervisor",
        "skills": list(DRAVEN_SKILLS),
        "tools": list(DRAVEN_TOOLS),
        "adapter": "md_cinema_draven",
        "matrix_game": MATRIX_GAME,
        "shared_brain": False,
        "writes_home_json": False,
        "owns_resolve": False,
        "note": "QCs the existing MD_Cinema pipeline. Not Merovin. Not the video engine.",
    }


def _studio_available() -> bool:
    return (STUDIO_PACKAGE / "studio_kernel.py").is_file()


def _import_studio() -> None:
    root = str(STUDIO_PACKAGE)
    if root not in sys.path:
        sys.path.insert(0, root)


def direct_as_merovin(
    *,
    story: str | None = None,
    title: str = "Federation Hollywood Merovin",
) -> dict[str, Any]:
    """Call MD_Cinema intake + shots as Merovin. Never as Draven. Never Matrix-Game."""
    empty = {
        "ok": False,
        "who": None,
        "adapter": "md_cinema_merovin",
        "matrix_game": MATRIX_GAME,
        "writes_home_json": False,
        "connection_test": False,
        "functional_test": False,
    }
    if not _studio_available():
        empty["error"] = "studio_missing"
        return empty
    try:
        _import_studio()
        from pipeline.intake import intake_story
        from pipeline.scenes_shots import build_from_bible
        from studio_kernel import append_audit

        sample = story or (
            "A lantern keeper waits at the pier.\n"
            "A stranger arrives with a sealed letter.\n"
            "They trade silence before the storm."
        )
        intake = intake_story(sample, title=title, is_path=False)
        pid = intake["production"]["id"]
        built = build_from_bible(pid, scene_count=1, shots_per_scene=2)
        append_audit(
            "hollywood_director",
            production_id=pid,
            actor="merovin",
            detail={"scenes": len(built["scenes"]), "shots": len(built["shots"])},
        )
        return {
            "ok": True,
            "who": "merovin",
            "adapter": "md_cinema_merovin",
            "production_id": pid,
            "story_bible": bool(intake.get("story_bible")),
            "scenes": len(built["scenes"]),
            "shots": len(built["shots"]),
            "matrix_game": MATRIX_GAME,
            "writes_home_json": False,
            "connection_test": True,
            "functional_test": True,
        }
    except Exception as exc:
        empty["error"] = str(exc)
        empty["connection_test"] = True
        return empty


def qc_as_draven(*, production_id: str | None = None) -> dict[str, Any]:
    """Continuity + budget + ffmpeg probe as Draven. Never as Merovin. Never Matrix-Game."""
    empty = {
        "ok": False,
        "who": None,
        "adapter": "md_cinema_draven",
        "matrix_game": MATRIX_GAME,
        "writes_home_json": False,
        "connection_test": False,
        "functional_test": False,
    }
    if not _studio_available():
        empty["error"] = "studio_missing"
        return empty
    try:
        _import_studio()
        from adapters.editing_ffmpeg import FFmpegEditingAdapter
        from budget.gate import authorize, estimate_generations
        from continuity.matrix import build_stub, check_shot
        from pipeline.intake import intake_story
        from studio_kernel import append_audit

        pid = production_id
        if not pid:
            intake = intake_story(
                "Continuity probe. A known keeper. An unknown guest.",
                title="Federation Hollywood Draven",
                is_path=False,
            )
            pid = intake["production"]["id"]
        build_stub(pid)
        probe_shot = {"id": "shot_hollywood_probe", "characters": ["char_unknown_hollywood"]}
        result = check_shot(pid, probe_shot)
        est_cloud = estimate_generations(video_clips=5, cloud=True)
        denied = authorize(est_cloud, mom_authorized=False)
        ffmpeg = FFmpegEditingAdapter().probe()
        ffmpeg_status = "AVAILABLE" if ffmpeg.get("available") else "UNAVAILABLE"
        flags = list(result.get("flags") or [])
        ok = (
            not bool(result.get("altered_story"))
            and bool(denied.requires_mom_auth or not denied.allowed)
            and ffmpeg.get("ok") is True
        )
        append_audit(
            "hollywood_continuity",
            production_id=pid,
            actor="draven",
            detail={"flags": len(flags), "ffmpeg": ffmpeg_status},
        )
        return {
            "ok": ok,
            "who": "draven",
            "adapter": "md_cinema_draven",
            "production_id": pid,
            "continuity_flags": len(flags),
            "altered_story": bool(result.get("altered_story")),
            "budget_cloud_denied": bool(not denied.allowed),
            "ffmpeg": ffmpeg_status,
            "matrix_game": MATRIX_GAME,
            "writes_home_json": False,
            "connection_test": True,
            "functional_test": ok,
        }
    except Exception as exc:
        empty["error"] = str(exc)
        empty["connection_test"] = True
        return empty
