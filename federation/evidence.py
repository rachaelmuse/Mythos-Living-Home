"""Machine-readable amendment evidence. Not the full Aster acceptance record."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from federation.atomic import atomic_write_json
from federation.registry import FederationRegistry


def write_amendment_evidence(root: Path, registry: FederationRegistry) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    participants = [p.agent_id for p in registry.list_participants()]
    payload: dict[str, Any] = {
        "kind": "AMENDMENT_PASS",
        "written_at": datetime.now(timezone.utc).isoformat(),
        "participants": participants,
        "aster_registered": "aster" in participants,
        "full_aster_acceptance": False,
        "note": "Foundation amendments 1-5 and refusal-to-lie negatives. Not Gemini speech, not The Axiom Codex notice, not Observer HTTP audit.",
    }
    path = root / "AMENDMENT_PASS.json"
    atomic_write_json(path, payload)
    return path
