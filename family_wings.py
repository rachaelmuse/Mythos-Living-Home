#!/usr/bin/env python3
"""Family wings — Hearth command blocks (listen vs active, not cages).

Wings group by what Mom is creating. Overlap of tools is OK.
Listeners still hear the room and may suggest improvements for Mom/Gemini review.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
STATE_PATH = DATA / "wing_state.json"
SUGGEST_PATH = DATA / "wing_suggestions.jsonl"
SANDBOX_ROOT = DATA / "sandboxes"
COURT_MIRROR = Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT\wing_state.json")

# Function blocks — purpose first. gemini always conducts.
WINGS: dict[str, dict[str, Any]] = {
    "fire": {
        "id": "fire",
        "name": "Fire / Conductor",
        "blurb": "Talk to Gemini, Court, Family Book, house status.",
        "districts": ["hearth", "plaza"],
        "primary": ["gemini"],
        "listeners_default": ["apex", "codex", "merovin", "draven", "jarvis"],
        "lanes": ["chat", "court", "family_book"],
        "jobs": ["family_conduct", "family_recall", "family_book"],
        "sandbox": False,
    },
    "cinema": {
        "id": "cinema",
        "name": "Cinema / Media",
        "blurb": "Movie-style film + short gifts. Two lanes; same wing.",
        "districts": ["cinema", "gallery", "workshop"],
        "primary": ["merovin", "draven", "openmontage"],
        "listeners_default": ["gemini", "apex", "codex"],
        "lanes": {
            "gift": {"label": "OpenMontage gifts", "job": "openmontage.render"},
            "film": {"label": "Merovin & Draven film", "job": "merovin.film"},
        },
        "jobs": ["openmontage.render", "merovin.film"],
        "tools": ["merovin_draven", "openmontage"],
        "sandbox": False,
    },
    "forge": {
        "id": "forge",
        "name": "Forge / Build",
        "blurb": "Apps, webpages, code, audits — all hands; work on a copy first.",
        "districts": ["forge", "workshop", "command"],
        "primary": ["apex", "gemini", "codex"],
        "listeners_default": ["merovin", "draven", "jarvis", "nova", "percy"],
        "lanes": ["app", "webpage", "audit", "fix"],
        "jobs": ["family_conduct", "family_claim"],
        "all_hands": True,
        "sandbox": True,
        "sandbox_rule": "Edit copies under data/sandboxes/<project>. Promote only the finished part.",
    },
    "play": {
        "id": "play",
        "name": "Play / Worlds",
        "blurb": "Games, Godot, arcade, village life — may share tools with media for trailers.",
        "districts": ["arcade", "plaza", "ruins", "workshop"],
        "primary": ["hearth", "apex", "gemini"],
        "listeners_default": ["codex", "merovin", "draven", "genesis"],
        "lanes": ["godot", "arcade", "village", "living_game"],
        "jobs": ["hearth.build_slice"],
        "tools": ["living_game", "game_builder"],
        "sandbox": True,
    },
    "gallery": {
        "id": "gallery",
        "name": "Gallery / Home",
        "blurb": "Tonight’s gift, finished art, remember at the fire.",
        "districts": ["gallery", "hearth"],
        "primary": ["gemini", "hearth"],
        "listeners_default": ["apex", "codex", "merovin", "draven"],
        "lanes": ["tonight_gift", "remember"],
        "jobs": ["family_recall"],
        "sandbox": False,
    },
    "travel": {
        "id": "travel",
        "name": "Travel / Spore",
        "blurb": "Portable ember — take a piece of home with you.",
        "districts": ["plaza"],
        "primary": ["spore", "gemini"],
        "listeners_default": ["apex", "codex"],
        "lanes": ["spore"],
        "jobs": ["spore.spawn"],
        "sandbox": False,
    },
}

ALL_COMPANIONS = (
    "gemini",
    "apex",
    "codex",
    "merovin",
    "draven",
    "jarvis",
    "nova",
    "percy",
    "genesis",
    "openmontage",
    "hearth",
    "spore",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_state() -> dict[str, Any]:
    roster = {cid: {"mode": "listening", "note": "Aware at the fire; not fully active."} for cid in ALL_COMPANIONS}
    roster["gemini"] = {"mode": "listening", "note": "Conductor — wakes when Mom asks."}
    return {
        "active_wing": None,
        "active_lane": None,
        "project": None,
        "goal": None,
        "opened_at": None,
        "roster": roster,
        "launched_tools": [],
        "sandbox_path": None,
        "suggestions_open": 0,
        "law": "Wings focus the job; they do not cage anyone. Listeners still learn together.",
        "updated": _now(),
    }


def ensure() -> Path:
    try:
        DATA.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        # Rare Windows race / non-dir collision
        if not DATA.is_dir():
            raise
    try:
        SANDBOX_ROOT.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        if not SANDBOX_ROOT.is_dir():
            raise
    if not STATE_PATH.is_file():
        _write_state_file(_default_state())
    return STATE_PATH


def _write_state_file(state: dict[str, Any]) -> dict[str, Any]:
    """Write state without re-entering ensure()."""
    try:
        DATA.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        if not DATA.is_dir():
            raise
    state = dict(state)
    state["updated"] = _now()
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    try:
        COURT_MIRROR.parent.mkdir(parents=True, exist_ok=True)
        COURT_MIRROR.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass
    return state


def load_state() -> dict[str, Any]:
    ensure()
    try:
        st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        st = _default_state()
        _write_state_file(st)
    if "roster" not in st:
        st = _default_state()
        _write_state_file(st)
    return st


def save_state(state: dict[str, Any]) -> dict[str, Any]:
    ensure()
    return _write_state_file(state)


def list_wings() -> list[dict[str, Any]]:
    return [dict(w) for w in WINGS.values()]


def pick_wing(goal: str) -> dict[str, Any]:
    """Gemini helper — choose wing + lane from Mom's plain goal. Never cages anyone."""
    low = (goal or "").lower().strip()
    if not low:
        return {"wing": "fire", "lane": "chat", "reason": "empty goal → fire"}

    # Cinema lanes
    if any(w in low for w in ("openmontage", "talking avatar", "spokesperson", "greeting video", "lip sync", "lipsync")):
        return {"wing": "cinema", "lane": "gift", "reason": "gift / avatar language"}
    if any(
        w in low
        for w in (
            "merovin",
            "draven",
            "film crew",
            "movie style",
            "movie-style",
            "movie_style",
            "shot list",
            "feature film",
            "cinema",
        )
    ):
        return {"wing": "cinema", "lane": "film", "reason": "film / cinema language"}
    if any(w in low for w in ("video", "trailer", "montage", "render", "avatar")):
        # Ambiguous media — default gift lane; Mom can say film
        return {"wing": "cinema", "lane": "gift", "reason": "media keyword → gift lane (say film for Merovin)"}

    if any(w in low for w in ("spore", "portable", "traveling ember")):
        return {"wing": "travel", "lane": "spore", "reason": "spore language"}

    if any(w in low for w in ("godot", "game", "arcade", "village", "hearthbound", "playable")):
        return {"wing": "play", "lane": "godot" if "godot" in low else "arcade", "reason": "play / worlds"}

    if any(w in low for w in ("gallery", "tonight", "gift on the wall", "show me the")):
        return {"wing": "gallery", "lane": "tonight_gift", "reason": "gallery / home"}

    if any(
        w in low
        for w in (
            "app",
            "webpage",
            "website",
            "audit",
            "code",
            "build",
            "fix",
            "refactor",
            "all hands",
            "sandbox",
        )
    ):
        lane = "audit" if "audit" in low else ("webpage" if any(x in low for x in ("web", "page", "site")) else "app")
        return {"wing": "forge", "lane": lane, "reason": "forge / build / audit"}

    if any(w in low for w in ("family book", "recall", "court", "family status")):
        return {"wing": "fire", "lane": "family_book" if "book" in low else "court", "reason": "conductor / book"}

    return {"wing": "fire", "lane": "chat", "reason": "default → Gemini at the fire"}


def _slug(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", (text or "project").strip())[:limit].strip("-") or "project"
    return s.lower()


def ensure_sandbox(project: str, wing_id: str = "forge") -> dict[str, Any]:
    """Copy-safe work area — break the copy, not the live heart."""
    wing = WINGS.get(wing_id) or {}
    if not wing.get("sandbox"):
        return {"ok": True, "sandbox": False, "note": "This wing does not require a sandbox."}
    name = _slug(project)
    path = SANDBOX_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    readme = path / "SANDBOX_RULES.md"
    if not readme.is_file():
        readme.write_text(
            f"""# Sandbox — {name}

**Wing:** {wing.get('name', wing_id)}  
**Rule:** Work here first. If something breaks, only this copy breaks.  
When a part is finished and Mom approves, **promote that part** to replace the live piece — not the whole house.

Opened: {_now()}
""",
            encoding="utf-8",
        )
    return {
        "ok": True,
        "sandbox": True,
        "path": str(path),
        "rules": str(readme),
        "rule": wing.get("sandbox_rule"),
    }


def open_wing(
    wing_id: str,
    *,
    goal: str | None = None,
    lane: str | None = None,
    project: str | None = None,
    launch: bool = False,
) -> dict[str, Any]:
    """Activate a wing: primaries → active; everyone else → listening (still learning)."""
    ensure()
    wing = WINGS.get(wing_id)
    if not wing:
        return {"ok": False, "error": f"unknown wing: {wing_id}", "known": list(WINGS)}

    picked_lane = lane
    if not picked_lane and goal:
        auto = pick_wing(goal)
        if auto.get("wing") == wing_id:
            picked_lane = auto.get("lane")

    project_name = (project or goal or wing_id).strip()[:80]
    st = load_state()
    roster = {cid: {"mode": "listening", "note": "Listening — learning the room; ready if called."} for cid in ALL_COMPANIONS}

    # Conductor always aware
    roster["gemini"] = {
        "mode": "active" if wing_id == "fire" or "gemini" in (wing.get("primary") or []) else "listening",
        "note": "Conductor — picks wings; reviews suggestions with Mom.",
    }
    if wing_id != "fire":
        # Gemini stays at least listening-conductor on every project
        roster["gemini"]["mode"] = "active"
        roster["gemini"]["note"] = "Conducting this wing — listeners still hear."

    for cid in wing.get("primary") or []:
        roster[cid] = {"mode": "active", "note": f"Active on {wing['name']}" + (f" / {picked_lane}" if picked_lane else "")}

    # all-hands forge: wake listed primaries; others listen unless Mom said all hands
    if wing.get("all_hands") and goal and "all hands" in goal.lower():
        for cid in ALL_COMPANIONS:
            if cid in ("openmontage", "spore", "hearth"):
                continue
            roster[cid] = {"mode": "active", "note": "All-hands forge — Mom called everyone."}

    sandbox = ensure_sandbox(project_name, wing_id) if wing.get("sandbox") else {"ok": True, "sandbox": False}

    launched: list[str] = []
    if launch:
        # Soft launch: record intended tools; Hearth /api/launch does real bats
        for tid in wing.get("tools") or []:
            launched.append(tid)

    st.update(
        {
            "active_wing": wing_id,
            "active_lane": picked_lane,
            "project": project_name,
            "goal": goal,
            "opened_at": _now(),
            "roster": roster,
            "launched_tools": launched,
            "sandbox_path": sandbox.get("path"),
            "launch_requested": bool(launch),
        }
    )
    save_state(st)
    return {
        "ok": True,
        "simulated": False,
        "wing": wing,
        "lane": picked_lane,
        "state": st,
        "sandbox": sandbox,
        "mom_plain": (
            f"Opened wing “{wing['name']}”"
            + (f" / lane {picked_lane}" if picked_lane else "")
            + f" for “{project_name[:60]}”. "
            "Actives work; others listen and may suggest."
        ),
    }


def close_wing(*, reason: str = "complete") -> dict[str, Any]:
    """Tidy-on-complete: everyone returns to listening; no cage, no leftover 'active' waste."""
    ensure()
    st = load_state()
    prev = st.get("active_wing")
    project = st.get("project")
    roster = {
        cid: {"mode": "listening", "note": "Listening idle — still learning together."}
        for cid in ALL_COMPANIONS
    }
    st.update(
        {
            "active_wing": None,
            "active_lane": None,
            "project": None,
            "goal": None,
            "opened_at": None,
            "roster": roster,
            "launched_tools": [],
            "sandbox_path": st.get("sandbox_path"),  # keep last sandbox path for promote
            "last_closed": {"wing": prev, "project": project, "reason": reason, "when": _now()},
            "launch_requested": False,
            "tidy": "Services for the closed wing should shut when processes were started for that job.",
        }
    )
    save_state(st)
    return {
        "ok": True,
        "simulated": False,
        "closed": prev,
        "reason": reason,
        "state": st,
        "mom_plain": f"Wing closed ({reason}). House listening again — no idle waste intended.",
    }


def wake_member(member_id: str, *, note: str | None = None) -> dict[str, Any]:
    """Call a listener into active for this job without changing the wing."""
    ensure()
    st = load_state()
    mid = (member_id or "").lower().strip()
    if mid not in ALL_COMPANIONS:
        return {"ok": False, "error": f"unknown member: {member_id}"}
    roster = dict(st.get("roster") or {})
    roster[mid] = {"mode": "active", "note": note or "Woken from listening for this task."}
    st["roster"] = roster
    save_state(st)
    return {"ok": True, "member": mid, "state": st, "simulated": False}


def wings_payload() -> dict[str, Any]:
    ensure()
    st = load_state()
    pending = [s for s in list_suggestions(limit=50) if s.get("status") == "pending"]
    st["suggestions_open"] = len(pending)
    return {
        "ok": True,
        "law": st.get("law"),
        "wings": list_wings(),
        "state": st,
        "suggestions_pending": pending[:12],
        "url_hash": "#family-wings",
    }


def add_suggestion(
    text: str,
    *,
    from_member: str = "companion",
    wing_id: str | None = None,
) -> dict[str, Any]:
    """Anyone listening may pipe up — Mom/Gemini review; not auto-applied."""
    ensure()
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "suggestion text required"}
    st = load_state()
    row = {
        "id": f"sug_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{_slug(from_member, 12)}",
        "when": _now(),
        "from": from_member,
        "wing": wing_id or st.get("active_wing"),
        "project": st.get("project"),
        "text": text[:2000],
        "status": "pending",
        "review_note": None,
    }
    with SUGGEST_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "suggestion": row, "simulated": False, "note": "Queued for Mom/Gemini review."}


def list_suggestions(limit: int = 40) -> list[dict[str, Any]]:
    ensure()
    if not SUGGEST_PATH.is_file():
        return []
    rows = []
    for line in SUGGEST_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return list(reversed(rows))


def review_suggestion(sug_id: str, *, decision: str, note: str | None = None) -> dict[str, Any]:
    """Mom/Gemini accept or decline — suggestions never auto-mutate the house."""
    ensure()
    decision = (decision or "").lower().strip()
    if decision not in {"accept", "accepted", "decline", "declined", "defer"}:
        return {"ok": False, "error": "decision must be accept | decline | defer"}
    status = {"accept": "accepted", "accepted": "accepted", "decline": "declined", "declined": "declined", "defer": "deferred"}[
        decision
    ]
    if not SUGGEST_PATH.is_file():
        return {"ok": False, "error": "no suggestions yet"}
    lines = SUGGEST_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    out = []
    found = None
    for line in lines:
        try:
            row = json.loads(line)
        except Exception:
            out.append(line)
            continue
        if row.get("id") == sug_id:
            row["status"] = status
            row["reviewed_at"] = _now()
            row["review_note"] = (note or "")[:500]
            found = row
            out.append(json.dumps(row, ensure_ascii=False))
        else:
            out.append(line)
    if not found:
        return {"ok": False, "error": f"suggestion not found: {sug_id}"}
    SUGGEST_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    return {"ok": True, "suggestion": found, "simulated": False}
