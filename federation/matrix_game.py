"""Matrix-Game production adapter. Pluggable engine slot. Not identity. Not Layer 17."""
from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

PRIMARY = "3.0"
SECONDARY = "2.0"
KNOWN_INSTALLS = (
    Path(r"D:\Matrix-Game"),
    Path(r"C:\Matrix-Game"),
    Path(r"F:\Matrix-Game"),
    Path(r"G:\Matrix-Game"),
)


def probe_host() -> dict[str, Any]:
    """Hardware + install probe. This Windows 4060 8GB desk cannot host Skywork's tested configs."""
    system = platform.system()
    installed = [str(p) for p in KNOWN_INSTALLS if p.is_dir()]
    linux = system == "Linux"
    reasons = []
    if system != "Linux":
        reasons.append(f"os={system} (Skywork tested Linux)")
    reasons.append("vram=RTX_4060_8GB (3.0 tested A/H; 2.0 needs >=24GB)")
    if not installed:
        reasons.append("no Matrix-Game install tree on known disks")
    return {
        "engine": "UNAVAILABLE",
        "primary_target": PRIMARY,
        "secondary": SECONDARY,
        "os": system,
        "linux": linux,
        "installed_paths": installed,
        "installed": bool(installed),
        "layer17_dream_view": False,
        "reasons": reasons,
        "note": "Do not install on this 4060 expecting demo quality. Adapter returns UNAVAILABLE, not a fake clip.",
    }


class MatrixGameAdapter:
    """Swap-in camera. Merovin/Draven keep their mouths. Village Dream View is a different limb."""

    name = "matrix_game"
    layer17 = False
    shared_brain = False

    def __init__(self, *, host: dict[str, Any] | None = None) -> None:
        self.host = host or probe_host()

    def generate_video(self, **kwargs: Any) -> dict[str, Any]:
        who = str(kwargs.get("who") or "merovin")
        if who == "both":
            who = "merovin"
        host = self.host
        return {
            "ok": False,
            "provider": self.name,
            "operation": "generate_video",
            "status": "UNAVAILABLE",
            "path": None,
            "who": who,
            "installed": bool(host.get("installed")),
            "primary_target": host.get("primary_target") or PRIMARY,
            "secondary": host.get("secondary") or SECONDARY,
            "layer17": False,
            "error": "; ".join(host.get("reasons") or ["engine unavailable"]),
            "meta": dict(host),
        }


def generate_video(*, who: str = "merovin", prompt: str | None = None) -> dict[str, Any]:
    del prompt
    return MatrixGameAdapter().generate_video(who=who)
