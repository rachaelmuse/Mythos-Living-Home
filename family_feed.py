#!/usr/bin/env python3
"""Plain-English family feed for Hearth House dashboard — Mom skips screenshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

COURT = Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT")
ACTION_LOG = Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\action_log.jsonl")
EPISODIC = COURT / "episodic" / "family_log.jsonl"
MISSION = COURT / "missions" / "ACTIVE_FAMILY_MISSION.json"
POWWOW = COURT / "powwow" / "ACTIVE_POWWOW.json"
WING = Path(r"D:\Mythos_Hearth\data\wing_state.json")
COURT_WING = COURT / "wing_state.json"


def _tail_jsonl(path: Path, n: int = 40) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _plain_from_action(ev: dict[str, Any]) -> str | None:
    detail = ev.get("detail") if isinstance(ev.get("detail"), dict) else {}
    plain = detail.get("mom_plain")
    if plain:
        return str(plain)
    action = ev.get("action") or "action"
    ok = ev.get("ok")
    if action == "family_claim":
        return f"Family claim finished — ok={ok}. Check mission strip for status."
    if action == "family_conduct":
        st = detail.get("status") or "?"
        return f"Family mission posted — status {st}."
    if action == "family_poll":
        return detail.get("mom_plain") or f"Family poll — ok={ok}."
    return f"{action}: {'ok' if ok else 'issue'}"


def family_feed(limit: int = 25) -> dict[str, Any]:
    """Mom-facing feed: mission + wing + powwow + plain lines (no raw dumps)."""
    mission = None
    if MISSION.is_file():
        try:
            mission = json.loads(MISSION.read_text(encoding="utf-8"))
        except Exception:
            mission = None

    wing = None
    for p in (WING, COURT_WING):
        if p.is_file():
            try:
                wing = json.loads(p.read_text(encoding="utf-8"))
                break
            except Exception:
                pass

    powwow = None
    if POWWOW.is_file():
        try:
            powwow = json.loads(POWWOW.read_text(encoding="utf-8"))
        except Exception:
            pass

    events = []
    for ev in reversed(_tail_jsonl(ACTION_LOG, 50)):
        plain = _plain_from_action(ev)
        if not plain:
            continue
        events.append(
            {
                "when": ev.get("when"),
                "kind": "action",
                "action": ev.get("action"),
                "ok": ev.get("ok"),
                "plain": plain[:500],
            }
        )
        if len(events) >= limit:
            break

    # Episodic highlights
    for ev in reversed(_tail_jsonl(EPISODIC, 30)):
        typ = ev.get("type")
        if typ not in {"conduct", "powwow_open", "powwow_tasks", "powwow_close", "interrupt", "claim"}:
            continue
        events.append(
            {
                "when": ev.get("when"),
                "kind": "episodic",
                "action": typ,
                "ok": True,
                "plain": f"{typ}: {(ev.get('goal') or ev.get('reason') or ev.get('mission_id') or '')[:200]}",
            }
        )

    events.sort(key=lambda x: x.get("when") or "", reverse=True)
    events = events[:limit]

    status_line = "House quiet."
    if mission:
        status_line = (
            f"Mission {mission.get('status')}: {(mission.get('goal') or '')[:140]}"
        )
    if powwow and powwow.get("open"):
        status_line = f"Powwow open — {powwow.get('reason', '')[:120]}"

    return {
        "ok": True,
        "status_line": status_line,
        "mission": {
            "id": (mission or {}).get("id"),
            "status": (mission or {}).get("status"),
            "goal": (mission or {}).get("goal"),
            "delegates": (mission or {}).get("delegates"),
            "wing": (mission or {}).get("wing"),
        }
        if mission
        else None,
        "wing": {
            "active_wing": (wing or {}).get("active_wing"),
            "active_lane": (wing or {}).get("active_lane"),
            "project": (wing or {}).get("project"),
            "roster_active": [
                k for k, v in ((wing or {}).get("roster") or {}).items() if (v or {}).get("mode") == "active"
            ],
        }
        if wing
        else None,
        "powwow": powwow,
        "events": events,
        "tip": "You don’t need screenshots — this feed updates from Gemini’s real actions.",
        "simulated": False,
    }
