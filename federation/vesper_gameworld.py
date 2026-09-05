"""Optional Gameworld door to Vesper's studio.

Vesper exists without The Axiom Codex. Observer remains the village greybox auditor.
This adapter does not make Vesper a village citizen, Ollama hat, or Observer agent.
It does not write HOME.json.
"""
from __future__ import annotations

from typing import Any

DOOR = "http://127.0.0.1:8740/"
NEVER_MERGE = (
    "observer",
    "gemini",
    "codex",
    "apex",
    "aster",
    "merovin",
    "draven",
    "montage",
    "hearth",
    "mom",
    "echo",
    "solace",
)


def snapshot() -> dict[str, Any]:
    return {
        "id": "vesper",
        "name": "Vesper",
        "gameworld_required": False,
        "village_citizen": False,
        "observer": False,
        "writes_home_json": False,
        "door": DOOR,
        "health": "http://127.0.0.1:8740/health",
        "identity": "http://127.0.0.1:8740/api/identity",
        "never_merge": list(NEVER_MERGE),
        "note": (
            "Optional door from Family House to Vesper's own studio. "
            "Gameworld down does not stop him. Village greybox stays Observer. "
            "Not a Heart Square hat."
        ),
    }
