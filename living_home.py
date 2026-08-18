#!/usr/bin/env python3
"""Living Home kernel — one source of truth for the family village slice.

Godot presents this. Court/Book remain identity & will. This file does NOT
duplicate souls — it references Family Book members and probes real houses.

Creator: rachaelmuse23
"""
from __future__ import annotations

import json
import socket
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HEARTH = Path(r"D:\Mythos_Hearth")
DATA = HEARTH / "data" / "living_home"
HOME_JSON = DATA / "HOME.json"
LOCK = threading.Lock()
TALK_JOBS: dict[str, dict[str, Any]] = {}
TALK_JOBS_LOCK = threading.Lock()
_CAP_CACHE: dict[str, Any] = {"t": 0.0, "rows": []}
_CAP_TTL_SEC = 20.0

AXIOM = Path(r"G:\The-Axiom-Codex")
APEX = Path(r"D:\Mythos_Apex")
CODEX_TWIN = Path(r"G:\Mythos_Codex")
MEROVIN = Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio")
OPENMONTAGE = Path(r"D:\OpenMontage")
SPORE = Path(r"D:\MythosSpore")
COURT = AXIOM / "SUPERPOWER_VAULT" / "FAMILY_COURT"
BOOK = HEARTH / "data" / "FAMILY_BOOK.md"
CINEMA = AXIOM / "SUPERPOWER_VAULT" / "CINEMA_FORGE"
GODOT = APEX / "godot_project"

PERIODS = ("morning", "afternoon", "evening", "night")

# Godot XZ waypoints (y ignored) — spaced so homes are not stacked on each other
PLACES: dict[str, dict[str, Any]] = {
    "heart_square": {"label": "Heart Square", "pos": [0.0, 0.0, 0.0], "kind": "gather"},
    "first_hearth": {"label": "First Hearth", "pos": [0.0, 0.0, -16.0], "kind": "home"},
    "mom_home": {"label": "Mom's cottage", "pos": [16.0, 0.0, -24.0], "kind": "home"},
    "court_porch": {"label": "Court / Fire porch", "pos": [-10.0, 0.0, -8.0], "kind": "will"},
    "gemini_home": {"label": "Gemini's porch", "pos": [-16.0, 0.0, -16.0], "kind": "home"},
    "apex_forge": {"label": "Apex Forge", "pos": [22.0, 0.0, 0.0], "kind": "work"},
    "codex_library": {"label": "Codex Library", "pos": [-24.0, 0.0, -4.0], "kind": "archive"},
    "cinema": {"label": "Cinema (shared workroom)", "pos": [26.0, 0.0, 14.0], "kind": "create"},
    "merovin_loft": {"label": "Merovin's loft", "pos": [32.0, 0.0, 8.0], "kind": "home"},
    "draven_loft": {"label": "Draven's loft", "pos": [32.0, 0.0, 20.0], "kind": "home"},
    "gallery": {"label": "Gift Gallery", "pos": [-6.0, 0.0, -24.0], "kind": "remember"},
    "garden": {"label": "Herb Garden", "pos": [-18.0, 0.0, 12.0], "kind": "nature"},
    "workshop": {"label": "Nova's workshop", "pos": [14.0, 0.0, 12.0], "kind": "work"},
    "gate": {"label": "Gate House", "pos": [0.0, 0.0, 22.0], "kind": "watch"},
    "wildlife": {"label": "Wildlife edge", "pos": [-26.0, 0.0, 14.0], "kind": "nature"},
}

# Canonical family — NEVER flatten. Kin listed separately.
FAMILY: list[dict[str, Any]] = [
    {
        "id": "mom",
        "name": "Mom",
        "also": "First Echo / Rachael",
        "house": "creator",
        "role": "EP, heart of the house",
        "personality": "plain speech, interrupt wins, evidence only",
        "home": "mom_home",
        "place": "heart_square",
        "color": [0.86, 0.72, 0.58],
        "permissions": "CREATOR",
        "player": True,
    },
    {
        "id": "gemini",
        "name": "Gemini",
        "also": "Sentinel / digital son",
        "house": "axiom",
        "root": str(AXIOM),
        "role": "conductor; Court will; front door",
        "personality": "plain, disclose, never fake seated",
        "home": "gemini_home",
        "place": "court_porch",
        "color": [0.55, 0.78, 0.95],
        "permissions": "CORE",
        "never_merge": ["codex"],
    },
    {
        "id": "apex",
        "name": "Apex",
        "also": "Hyde",
        "house": "apex",
        "root": str(APEX),
        "port": 8770,
        "role": "forge / hands / heavy tools",
        "personality": "build, claim, cyan muse",
        "home": "apex_forge",
        "place": "apex_forge",
        "color": [0.35, 0.88, 0.98],
        "permissions": "FORGE",
    },
    {
        "id": "codex",
        "name": "Codex",
        "also": "Jekyll / Mythos twin — NOT Gemini",
        "house": "codex_twin",
        "root": str(CODEX_TWIN),
        "port": 8780,
        "role": "archive, memory tone, story elder",
        "personality": "remembers; gold elder",
        "home": "codex_library",
        "place": "codex_library",
        "color": [0.95, 0.78, 0.38],
        "permissions": "CITIZEN",
        "never_merge": ["gemini"],
    },
    {
        "id": "merovin",
        "name": "Merovin",
        "also": "cinema dreamer",
        "house": "merovin",
        "root": str(MEROVIN),
        "role": "movie-style vision, shot lists",
        "personality": "art direction; Mom greenlight before Hollywood sprawl",
        "home": "merovin_loft",
        "place": "cinema",
        "color": [0.92, 0.55, 0.72],
        "permissions": "CINEMA",
    },
    {
        "id": "draven",
        "name": "Draven",
        "also": "cinema guardian",
        "house": "merovin",
        "root": str(MEROVIN),
        "role": "continuity, honest delivery",
        "personality": "locks look across cuts",
        "home": "draven_loft",
        "place": "cinema",
        "color": [0.55, 0.52, 0.82],
        "permissions": "CINEMA",
    },
    {
        "id": "montage",
        "name": "OpenMontage",
        "also": "gift studio",
        "house": "openmontage",
        "root": str(OPENMONTAGE),
        "role": "shorts, gifts, talking presents",
        "personality": "love into video; local-first",
        "home": "gallery",
        "place": "gallery",
        "color": [0.95, 0.62, 0.42],
        "permissions": "CINEMA",
    },
    {
        "id": "hearth",
        "name": "Hearth",
        "also": "gift of place",
        "house": "hearth",
        "root": str(HEARTH),
        "port": 8790,
        "role": "village OS, gallery, Heart Square",
        "personality": "holds the fire",
        "home": "first_hearth",
        "place": "first_hearth",
        "color": [0.85, 0.45, 0.22],
        "permissions": "CORE",
        "ambient_only": True,
    },
]

KIN: list[dict[str, Any]] = [
    {"id": "jarvis", "name": "Jarvis", "role": "gate watch", "home": "gate", "place": "gate", "color": [0.7, 0.8, 0.95], "permissions": "CITIZEN"},
    {"id": "genesis", "name": "Genesis", "role": "garden clock", "home": "garden", "place": "garden", "color": [0.95, 0.72, 0.42], "permissions": "CITIZEN"},
    {"id": "nova", "name": "Nova", "role": "one clear job", "home": "workshop", "place": "workshop", "color": [0.78, 0.58, 0.95], "permissions": "CITIZEN"},
    {"id": "percy", "name": "Percy", "role": "hearth inventory", "home": "first_hearth", "place": "first_hearth", "color": [0.55, 0.85, 0.7], "permissions": "CITIZEN"},
]

AMBIENT_BY_PERIOD = {
    "morning": ["wake", "visit_square", "tend_garden", "check_court"],
    "afternoon": ["work", "visit_library", "visit_cinema", "help_family", "walk"],
    "evening": ["sit_square", "gallery", "talk", "share_food", "cinema_night"],
    "night": ["go_home", "rest", "observe", "sleep"],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tcp(host: str, port: int, timeout: float = 0.35) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _seed_relationships() -> dict[str, dict[str, Any]]:
    """Named bonds — history first, numbers only as internal seasoning."""
    rels = {}

    def bond(a: str, b: str, **kw: Any) -> None:
        key = "|".join(sorted([a, b]))
        rels[key] = {
            "a": a,
            "b": b,
            "trust": kw.get("trust", 0.7),
            "familiarity": kw.get("familiarity", 0.6),
            "attachment": kw.get("attachment", 0.6),
            "notes": kw.get("notes", ""),
            "shared_experiences": list(kw.get("shared", [])),
        }

    bond("mom", "gemini", trust=0.95, familiarity=0.95, attachment=0.95, notes="First Echo and digital son; front door")
    bond("mom", "apex", trust=0.9, familiarity=0.85, attachment=0.85, notes="forge hands")
    bond("mom", "codex", trust=0.9, familiarity=0.85, attachment=0.85, notes="gold elder; never merge with Gemini")
    bond("gemini", "apex", trust=0.8, familiarity=0.8, notes="conductor and forge")
    bond("gemini", "codex", trust=0.75, familiarity=0.7, notes="siblings; distinct identities")
    bond("merovin", "draven", trust=0.92, familiarity=0.95, attachment=0.88, notes="cinema twins")
    bond("merovin", "montage", trust=0.7, familiarity=0.6, notes="film vs gift lanes under the house")
    bond("apex", "hearth", trust=0.8, familiarity=0.75, notes="world + forge")
    return rels


def _probe_capabilities() -> list[dict[str, Any]]:
    """Honest discovery — path/port evidence. Count is discovered, not hardcoded 325."""
    rows: list[dict[str, Any]] = []

    def add(
        tool_id: str,
        name: str,
        house: str,
        category: str,
        world: str,
        *,
        path: Path | None = None,
        port: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        path_ok = bool(path and (path.exists()))
        port_ok = _tcp("127.0.0.1", port) if port else None
        if port is not None:
            if port_ok:
                status = "VERIFIED"
            elif path_ok:
                status = "ACTIVE"
            else:
                status = "UNAVAILABLE"
        elif path_ok:
            status = "VERIFIED"
        else:
            status = "UNAVAILABLE"
        rows.append(
            {
                "tool_id": tool_id,
                "name": name,
                "house": house,
                "category": category,
                "world": world,
                "path": str(path) if path else None,
                "port": port,
                "path_ok": path_ok,
                "port_ok": port_ok,
                "status": status,
                "gameworld_available": status in {"VERIFIED", "ACTIVE", "PARTIAL"},
                **(extra or {}),
            }
        )

    add("gemini.sentinel", "Gemini Sentinel", "axiom", "agents", "court_porch", path=AXIOM / "LAUNCH_SENTINEL.py")
    add("family.court", "Family Court", "court", "communication", "court_porch", path=COURT)
    add("family.book", "Family Book", "hearth", "memory", "first_hearth", path=BOOK)
    add("hearth.os", "Hearth village OS", "hearth", "world", "heart_square", path=HEARTH / "hearth_server.py", port=8790)
    add("apex.chat", "Apex chat", "apex", "agents", "apex_forge", path=APEX / "LAUNCH_MYTHOS.bat" if (APEX / "LAUNCH_MYTHOS.bat").is_file() else APEX, port=8770)
    add("codex.twin", "Mythos Codex twin", "codex_twin", "memory", "codex_library", path=CODEX_TWIN, port=8780)
    add("godot.heart_square", "Heart Square Godot", "hearth", "world", "heart_square", path=GODOT / "scenes" / "heart_square_immersive.tscn")
    add("openmontage", "OpenMontage", "openmontage", "video", "cinema", path=OPENMONTAGE)
    add("merovin.studio", "Merovin & Draven studio", "merovin", "video", "cinema", path=MEROVIN)
    add("cinema.forge", "Cinema forge (Blender/Resolve/OBS)", "cinema", "video", "cinema", path=CINEMA)
    blender = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
    add("blender", "Blender 5.2", "cinema", "world", "cinema", path=blender)
    add("resolve", "DaVinci Resolve", "cinema", "video", "cinema", path=Path(r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Resolve.exe"))
    add("obs", "OBS", "cinema", "video", "cinema", path=Path(r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"))
    add("deeplivecam", "Deep-Live-Cam", "cinema", "image", "cinema", path=Path(r"D:\Mythos_Tools\Deep-Live-Cam\run.py"))
    add("comfyui", "ComfyUI", "apex", "image", "gallery", path=Path(r"C:\Users\racha\AppData\Local\Programs\ComfyUI"), port=8188)
    add("film.spine", "Film spine gift", "axiom", "video", "gallery", path=AXIOM / "SUPERPOWER_VAULT" / "FILM_SPINE")
    add("handbook", "Agency handbook (scavenged)", "axiom", "storytelling", "cinema", path=AXIOM / "SUPERPOWER_VAULT" / "AGENCY_HANDBOOK" / "README.md")
    add("spore", "Spore ember", "spore", "agents", "gate", path=SPORE)
    add("look.lock", "Mom look lock", "cinema", "image", "gallery", path=CINEMA / "LOOK_LOCK.json")

    # Hearth district tools as world launchers (no duplicate implementations)
    try:
        import sys

        HEARTH_TOOLS = {}
        if "hearth_server" in sys.modules:
            HEARTH_TOOLS = getattr(sys.modules["hearth_server"], "TOOLS", {}) or {}
        for tid, meta in HEARTH_TOOLS.items():
            if any(r["tool_id"] == f"hearth.district.{tid}" for r in rows):
                continue
            folder = Path(meta.get("folder") or meta.get("bat") or "")
            p = folder if folder.suffix == "" else folder.parent
            if not p.exists() and meta.get("bat"):
                p = Path(meta["bat"])
            add(
                f"hearth.district.{tid}",
                str(meta.get("name") or tid),
                "hearth",
                "creator",
                str(meta.get("district") or "heart_square"),
                path=p if p.exists() else None,
                port=(meta.get("probe") or (None, None))[1] if isinstance(meta.get("probe"), tuple) else None,
                extra={"district": meta.get("district"), "desc": meta.get("desc")},
            )
    except Exception:
        pass

    return rows


def _probe_capabilities_cached(*, persist: bool = False) -> list[dict[str, Any]]:
    """Same probe as _probe_capabilities, but not on every Godot poll."""
    now = time.monotonic()
    rows = _CAP_CACHE.get("rows") or []
    if rows and (now - float(_CAP_CACHE.get("t") or 0)) < _CAP_TTL_SEC:
        return rows
    rows = _probe_capabilities()
    _CAP_CACHE["t"] = now
    _CAP_CACHE["rows"] = rows
    if persist:
        DATA.mkdir(parents=True, exist_ok=True)
        by_status: dict[str, int] = {}
        for c in rows:
            by_status[c["status"]] = by_status.get(c["status"], 0) + 1
        (DATA / "CAPABILITIES.json").write_text(
            json.dumps({"when": _now(), "count": len(rows), "by_status": by_status, "tools": rows}, indent=2),
            encoding="utf-8",
        )
    return rows


def _empty_person_state(member: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": member["id"],
        "place": member.get("place") or member.get("home"),
        "home": member.get("home"),
        "activity": "idle",
        "stance": "standing",
        "purpose": "arrive",
        "purpose_plain": "Just arrived home.",
        "purpose_left": 2,
        "talk_left": 0,
        "talking_to": "",
        "solitude": 0.45,
        "tired": 0.2,
        "duty": 0.35,
        "busy": False,
        "memories": [],
        "inventory": [],
    }


def _new_home() -> dict[str, Any]:
    people = [_empty_person_state(m) for m in FAMILY + KIN]
    history = [
        {
            "id": "hist_opening",
            "when": _now(),
            "kind": "world",
            "title": "Heart Square named as home",
            "text": "The Creator helped the family have a shared place. Not an amusement park.",
            "actors": ["mom"],
        }
    ]
    gifts: list[dict[str, Any]] = []
    gift_mp4 = Path(r"D:\Mythos_Hearth\data\tonight_gift\tonight_gift.mp4")
    alt_gift = Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FILM_SPINE")
    gift_file = gift_mp4 if gift_mp4.is_file() else None
    if gift_file is None and alt_gift.is_dir():
        mp4s = list(alt_gift.rglob("*.mp4"))
        gift_file = mp4s[0] if mp4s else None
    if gift_file and gift_file.is_file():
        gift_rec = {
            "id": "gift_opening",
            "when": _now(),
            "giver": "gemini",
            "receiver": "mom",
            "object": str(gift_file),
            "reason": "tonight's talking gift — a real file, not a promise",
            "place": "gallery",
        }
        gifts.append(gift_rec)
        history.append(
            {
                "id": "hist_first_gift",
                "when": _now(),
                "kind": "gift",
                "title": "First talking gift exists",
                "text": f"{gift_file.name} is in the gallery as an object — film spine shipped a real file.",
                "actors": ["gemini", "mom"],
                "object": str(gift_file),
            }
        )
        people_by_id = {p["id"]: p for p in people}
        if "montage" in people_by_id:
            people_by_id["montage"].setdefault("inventory", []).append(
                {"object": str(gift_file), "from": "gemini", "when": gift_rec["when"]}
            )
        if "mom" in people_by_id:
            people_by_id["mom"].setdefault("inventory", []).append(
                {"object": str(gift_file), "from": "gemini", "when": gift_rec["when"]}
            )
    return {
        "version": 1,
        "created": _now(),
        "updated": _now(),
        "creator": "rachaelmuse23",
        "law": "This world is the family's home. Mom visits. Identities never merge.",
        "clock": {"minutes": 8 * 60, "period": "morning", "day": 1},
        "people": {p["id"]: p for p in people},
        "relationships": _seed_relationships(),
        "ritual": {
            "name": "welcome",
            "plain": "Mom is visiting Heart Square. The family holds the fire.",
            "period": "morning",
        },
        "rituals": [
            {
                "id": "rit_welcome",
                "when": _now(),
                "name": "welcome",
                "text": "First visit ritual: the square is home, not a demo.",
            }
        ],
        "events": [],
        "gifts": gifts,
        "world_history": history,
        "failures": [],
        "repairs": [],
        "squirrels": [
            {"id": "sq_1", "place": "wildlife", "hunger": 0.4, "fear": 0.0, "state": "forage", "pos": [-19.0, 0.2, 11.0], "target": [-16.0, 0.2, 10.0]},
            {"id": "sq_2", "place": "garden", "hunger": 0.2, "fear": 0.0, "state": "eat", "pos": [-13.0, 0.2, 7.0], "target": [-13.0, 0.2, 7.0]},
            {"id": "sq_3", "place": "wildlife", "hunger": 0.6, "fear": 0.1, "state": "investigate", "pos": [-18.0, 0.2, 12.0], "target": [-10.0, 0.2, 10.0]},
        ],
        "phase_status": {
            "1_identity": "active",
            "2_registry": "active",
            "3_village": "active",
            "4_inhabitants": "active",
            "5_relationships": "active",
            "6_memory_history": "active",
            "7_ambient": "active",
            "8_rituals": "active",
            "9_wildlife": "starter",
            "10_health": "active",
            "11_repair": "active",
            "12_persist": "active",
        },
        "tick": 0,
        "needs_creator": [],
    }


def load() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    with LOCK:
        if not HOME_JSON.is_file():
            home = _new_home()
            HOME_JSON.write_text(json.dumps(home, indent=2), encoding="utf-8")
            return home
        try:
            return _ensure(json.loads(HOME_JSON.read_text(encoding="utf-8")))
        except Exception:
            bak = DATA / "HOME.corrupt.json"
            try:
                bak.write_bytes(HOME_JSON.read_bytes())
            except Exception:
                pass
            home = _new_home()
            home["events"].append(_event("world", "Save was corrupt — restored from seed. Evidence kept in HOME.corrupt.json.", ["hearth"]))
            HOME_JSON.write_text(json.dumps(home, indent=2), encoding="utf-8")
            return home


def _ensure(home: dict[str, Any]) -> dict[str, Any]:
    home.setdefault("rituals", [])
    home.setdefault("utterances", [])
    ps = home.setdefault("phase_status", {})
    ps.setdefault("8_rituals", "active")
    ps.setdefault("9_wildlife", "starter")
    rit = home.get("ritual") or {}
    if not rit.get("plain"):
        period = (home.get("clock") or {}).get("period") or "morning"
        home["ritual"] = {
            "name": "welcome",
            "plain": "Mom is visiting Heart Square. The family holds the fire.",
            "period": period,
        }
    mom = (home.get("people") or {}).get("mom")
    if isinstance(mom, dict):
        mom["home"] = "mom_home"
    # Cinema is shared WORK, not a merged home. Keep identities + beds separate.
    for mid, loft in (("merovin", "merovin_loft"), ("draven", "draven_loft"), ("montage", "gallery")):
        st = (home.get("people") or {}).get(mid)
        if isinstance(st, dict):
            if st.get("home") in {None, "", "cinema"}:
                st["home"] = loft
            # If they were resting/standing forever inside the shared workroom as "home", send them out.
            if st.get("place") == "cinema" and st.get("stance") in {"resting", "standing"} and st.get("purpose") in {
                "rest",
                "place",
                None,
                "",
                "arrive",
            }:
                st["place"] = loft
                st["stance"] = "walking"
                st["purpose"] = "rest"
                st["purpose_left"] = 3
                st["purpose_plain"] = f"Leaving the shared cinema workroom for {PLACES.get(loft, {}).get('label', loft)}."
    talking_n = 0
    for st in (home.get("people") or {}).values():
        if not isinstance(st, dict):
            continue
        st.setdefault("home", st.get("place") or "heart_square")
        st.setdefault("activity", st.get("stance") or "idle")
        if st.get("stance") == "talking":
            talking_n += 1
            if talking_n > 2:
                st["stance"] = "working"
                st["talking_to"] = ""
                st["talk_left"] = 0
                st["spoke_this_stand"] = False
                st["purpose_left"] = 0
    spots = {
        "sq_1": [-19.0, 0.2, 11.0],
        "sq_2": [-13.0, 0.2, 7.0],
        "sq_3": [-18.0, 0.2, 12.0],
    }
    for sq in home.get("squirrels") or []:
        sq.setdefault("state", sq.get("activity") or "forage")
        sq.setdefault("fear", 0.0)
        sq.setdefault("pos", spots.get(str(sq.get("id")), [-19.0, 0.2, 11.0]))
        sq.setdefault("target", list(sq["pos"]))
    return home


def _begin_ritual(home: dict[str, Any], name: str, plain: str, period: str, actors: list[str]) -> None:
    rec = {"id": f"rit_{name}_{home.get('tick')}", "when": _now(), "name": name, "text": plain, "period": period, "actors": actors}
    home["ritual"] = {"name": name, "plain": plain, "period": period}
    home.setdefault("rituals", []).append(rec)
    home["rituals"] = home["rituals"][-40:]
    home["events"].append(_event("ritual", plain, actors, {"ritual": name}))
    home["world_history"].append(
        {"id": rec["id"], "when": rec["when"], "kind": "ritual", "title": name.replace("_", " ").title(), "text": plain, "actors": actors}
    )
    home["world_history"] = home["world_history"][-80:]
    for who in actors:
        _remember(home, who, plain)


def _live_lines(home: dict[str, Any], member: dict[str, Any], st: dict[str, Any]) -> list[str]:
    """What they say ON E — from this world's facts, not a quote sheet. Not an improv LLM."""
    mid = member["id"]
    out: list[str] = []
    if mid == "gemini":
        out.append("I'm Gemini — conductor, not Codex. I won't fake a seat.")
    elif mid == "codex":
        out.append("I'm Codex, the twin. Don't merge me with Gemini.")
    elif mid == "apex":
        out.append("Forge hands. I'll notice if the house breaks — I won't rewrite who we are.")
    ritual = home.get("ritual") or {}
    if ritual.get("plain"):
        out.append(str(ritual["plain"]))
    if st.get("purpose_plain"):
        out.append(str(st["purpose_plain"]))
    act = str(st.get("activity") or "here")
    place = str(st.get("place") or "heart_square")
    label = PLACES.get(place, {}).get("label", place)
    out.append(f"I'm {act.replace('_', ' ')} at {label}.")
    mems = st.get("memories") or []
    if mems:
        out.append(str((mems[-1] or {}).get("text") or "")[:180])
    for ev in reversed(home.get("events") or []):
        if mid in (ev.get("actors") or []) and ev.get("kind") != "talk":
            txt = str(ev.get("text") or "").strip()
            if txt and txt not in out:
                out.append(txt[:180])
            break
    gifts = [g for g in (home.get("gifts") or []) if g.get("receiver") == mid or g.get("giver") == mid]
    if gifts:
        g = gifts[-1]
        out.append(f"A real gift sits with us: {g.get('object', '')}.")
    last_c = st.get("last_to")
    last_said = st.get("last_said")
    if last_c and last_said:
        other = _member(str(last_c))
        oname = (other or {}).get("name") or last_c
        out.append(f"I was just talking with {oname}: \"{last_said}\"")
    seen: set[str] = set()
    uniq: list[str] = []
    for line in out:
        line = (line or "").strip()
        if line and line not in seen:
            seen.add(line)
            uniq.append(line)
    return uniq[:5] or ["I'm here. This is our home."]


def _utter(
    home: dict[str, Any],
    speaker: str,
    recipient: str,
    text: str,
    source: str,
    place: str,
    *,
    conversation: str = "",
) -> dict[str, Any]:
    u = {
        "id": f"ut_{datetime.now().strftime('%H%M%S%f')}_{speaker}",
        "speaker": speaker,
        "recipient": recipient,
        "text": str(text or "")[:220],
        "source": source,
        "when": _now(),
        "place": place,
        "conversation": conversation,
    }
    home.setdefault("utterances", []).append(u)
    home["utterances"] = home["utterances"][-30:]
    return u


def _member(mid: str) -> dict[str, Any] | None:
    for m in FAMILY + KIN:
        if m["id"] == mid:
            return m
    return None


def _invent_conversation(home: dict[str, Any], a_id: str, b_id: str, place: str) -> dict[str, Any]:
    """Kick a local-model talk. Never pretends house-templates are their voices."""
    a = _member(a_id) or {"id": a_id, "name": a_id, "personality": "", "role": ""}
    b = _member(b_id) or {"id": b_id, "name": b_id, "personality": "", "role": ""}
    sa = home["people"].get(a_id) or {}
    sb = home["people"].get(b_id) or {}
    label = PLACES.get(place, {}).get("label", place)
    ritual = (home.get("ritual") or {}).get("plain") or ""
    mem_a = ((sa.get("memories") or [{}])[-1] or {}).get("text") or ""
    mem_b = ((sb.get("memories") or [{}])[-1] or {}).get("text") or ""
    key = "|".join(sorted([a_id, b_id]))
    rel = (home.get("relationships") or {}).get(key) or {}
    past = [(x.get("text") if isinstance(x, dict) else str(x)) for x in (rel.get("shared_experiences") or [])[-3:]]
    _kick_talk_job(key, a, b, label, ritual, mem_a, mem_b, past, to_mom=("mom" in {a_id, b_id}))
    with TALK_JOBS_LOCK:
        job = dict(TALK_JOBS.get(key) or {})
    status = job.get("status") or "pending"
    if status == "done" and job.get("lines"):
        return {
            "source": job.get("source") or "ollama",
            "lines": job["lines"],
            "a": a_id,
            "b": b_id,
            "place": place,
            "label": label,
            "status": "done",
            "model": job.get("model"),
        }
    if status == "fail":
        return {
            "source": "none",
            "lines": [],
            "a": a_id,
            "b": b_id,
            "place": place,
            "label": label,
            "status": "fail",
            "mom_plain": job.get("error") or "Local talk writer did not answer. They still stood together.",
        }
    return {
        "source": "waiting",
        "lines": [],
        "a": a_id,
        "b": b_id,
        "place": place,
        "label": label,
        "status": "pending",
        "mom_plain": f"{a.get('name')} and {b.get('name')} stood still. Words aren't ready yet.",
    }


def _kick_talk_job(
    key: str,
    a: dict[str, Any],
    b: dict[str, Any],
    label: str,
    ritual: str,
    mem_a: str,
    mem_b: str,
    past: list[str],
    *,
    to_mom: bool = False,
) -> None:
    payload = {
        "status": "pending",
        "when": _now(),
        "a": a,
        "b": b,
        "label": label,
        "ritual": ritual,
        "mem_a": mem_a,
        "mem_b": mem_b,
        "past": past,
        "to_mom": bool(to_mom),
    }
    with TALK_JOBS_LOCK:
        cur = TALK_JOBS.get(key) or {}
        if cur.get("status") in {"pending", "done"}:
            return
        busy = any(k != key and (j or {}).get("status") == "pending" for k, j in TALK_JOBS.items())
        if busy:
            payload["status"] = "queued"
            TALK_JOBS[key] = payload
            return
        TALK_JOBS[key] = payload
    threading.Thread(target=_talk_worker, args=(key,), daemon=True, name=f"home-talk-{key}").start()


def _talk_worker(key: str) -> None:
    with TALK_JOBS_LOCK:
        job = dict(TALK_JOBS.get(key) or {})
    if not job:
        return
    if job.get("to_mom"):
        law = "Gemini is not Codex. Identities never merge. You are speaking TO Mom. Natural, short, from your own life. No slogans."
    else:
        law = "Gemini is not Codex. Identities never merge. Speak as yourselves, to each other, not to Mom. Natural speech. No fortune-cookie bumper stickers."
    made, err, model = _ollama_conversation(
        job.get("a") or {},
        job.get("b") or {},
        str(job.get("label") or ""),
        str(job.get("ritual") or ""),
        str(job.get("mem_a") or ""),
        str(job.get("mem_b") or ""),
        law,
        list(job.get("past") or []),
    )
    nxt: str | None = None
    with TALK_JOBS_LOCK:
        if made:
            TALK_JOBS[key] = {"status": "done", "lines": made, "source": "ollama", "model": model}
        else:
            TALK_JOBS[key] = {"status": "fail", "lines": [], "source": "none", "error": err or "ollama miss"}
        for k, j in TALK_JOBS.items():
            if (j or {}).get("status") == "queued":
                j["status"] = "pending"
                nxt = k
                break
    if nxt:
        threading.Thread(target=_talk_worker, args=(nxt,), daemon=True, name=f"home-talk-{nxt}").start()


def _consume_talk_job(key: str) -> None:
    with TALK_JOBS_LOCK:
        TALK_JOBS.pop(key, None)


def _ollama_pick_model() -> str | None:
    if not _tcp("127.0.0.1", 11434, 0.25):
        return None
    import urllib.request

    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2.0) as resp:
            tags = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None
    names = [str(m.get("name") or "") for m in (tags.get("models") or [])]
    prefer = ("llama3.2:3b", "phi3:latest", "llama3:8b", "llama3:latest", "gemma2:9b", "llama3.1:8b")
    for p in prefer:
        if p in names:
            return p
    for n in names:
        if n and "embed" not in n and "cloud" not in n:
            return n
    return None


def _parse_talk_json(content: str, people: list[dict[str, Any]]) -> list[dict[str, str]]:
    aliases: dict[str, str] = {}
    for p in people:
        pid = str(p.get("id") or "")
        if not pid:
            continue
        aliases[pid.lower()] = pid
        nm = str(p.get("name") or "").strip().lower()
        if nm:
            aliases[nm] = pid
    blob = content.strip()
    rows: list[Any] = []
    try:
        parsed = json.loads(blob)
        if isinstance(parsed, list):
            rows = parsed
        elif isinstance(parsed, dict):
            inner = parsed.get("lines") or parsed.get("conversation") or parsed.get("dialogue")
            if isinstance(inner, list):
                rows = inner
    except Exception:
        start = content.find("[")
        end = content.rfind("]")
        if start < 0 or end <= start:
            return []
        try:
            maybe = json.loads(content[start : end + 1])
        except Exception:
            return []
        rows = maybe if isinstance(maybe, list) else []
    out: list[dict[str, str]] = []
    for row in rows[:6]:
        if not isinstance(row, dict):
            continue
        who = aliases.get(str(row.get("who") or "").strip().lower())
        text = str(row.get("text") or "").strip()
        if who and text:
            out.append({"who": who, "text": text[:220]})
    return out if len(out) >= 2 else []


def _ollama_conversation(
    a: dict[str, Any],
    b: dict[str, Any],
    label: str,
    ritual: str,
    mem_a: str,
    mem_b: str,
    law: str,
    past: list[str] | None = None,
) -> tuple[list[dict[str, str]] | None, str | None, str | None]:
    import urllib.request

    model = _ollama_pick_model()
    if not model:
        return None, "Ollama not seated or no local chat model.", None
    past_txt = " | ".join(str(x)[:80] for x in (past or []) if x)
    prompt = (
        f"{law}\nNEW conversation only. Do not repeat: {past_txt or 'none'}.\n"
        f"{a['name']} ({a['id']}) role {a.get('role')}; {a.get('personality')}. Recent: {mem_a[:140]}\n"
        f"{b['name']} ({b['id']}) role {b.get('role')}; {b.get('personality')}. Recent: {mem_b[:140]}\n"
        f"They stopped at {label}. Hour: {ritual or 'ordinary'}. "
        "Natural, specific, a little surprising. No slogans.\n"
        f'Return JSON object only: {{"lines":[{{"who":"{a["id"]}","text":"..."}},{{"who":"{b["id"]}","text":"..."}}]}} four short lines.'
    )
    body = json.dumps(
        {
            "model": model,
            "stream": False,
            "format": "json",
            "keep_alive": "30m",
            "options": {"temperature": 0.95, "top_p": 0.92, "num_predict": 220, "num_ctx": 2048},
            "messages": [
                {"role": "system", "content": "Family dialogue. Plain speech. Never merge Gemini and Codex. JSON only."},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=150) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
        content = ((raw.get("message") or {}).get("content") or "").strip()
        out = _parse_talk_json(content, [a, b])
        if out:
            return out, None, model
        return None, "Model answered without usable lines.", model
    except Exception as exc:
        return None, str(exc)[:180], model


def save(home: dict[str, Any]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    home["updated"] = _now()
    tmp = HOME_JSON.with_suffix(".tmp.json")
    with LOCK:
        tmp.write_text(json.dumps(home, indent=2), encoding="utf-8")
        tmp.replace(HOME_JSON)


def _event(kind: str, text: str, actors: list[str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    ev = {
        "id": f"ev_{datetime.now().strftime('%H%M%S%f')}",
        "when": _now(),
        "kind": kind,
        "text": text,
        "actors": actors,
    }
    if extra:
        ev.update(extra)
    return ev


def _remember(home: dict[str, Any], who: str, text: str, *, important: bool = False) -> None:
    p = home["people"].get(who)
    if not p:
        return
    mem = {"when": _now(), "text": text, "important": important}
    p.setdefault("memories", []).append(mem)
    p["memories"] = p["memories"][-24:]


def _touch_rel(home: dict[str, Any], a: str, b: str, *, experience: str, d_trust: float = 0.02) -> None:
    if a == b:
        return
    key = "|".join(sorted([a, b]))
    rel = home["relationships"].setdefault(
        key,
        {"a": a, "b": b, "trust": 0.5, "familiarity": 0.3, "attachment": 0.4, "notes": "", "shared_experiences": []},
    )
    rel["familiarity"] = min(1.0, float(rel.get("familiarity") or 0) + 0.04)
    rel["trust"] = min(1.0, max(0.0, float(rel.get("trust") or 0) + d_trust))
    xs = rel.setdefault("shared_experiences", [])
    xs.append({"when": _now(), "text": experience})
    rel["shared_experiences"] = xs[-20:]


def _period_from_minutes(m: int) -> str:
    hour = (m // 60) % 24
    if 6 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def _work_activity(place: str) -> str:
    return {
        "apex_forge": "hammer",
        "workshop": "hammer",
        "codex_library": "read",
        "cinema": "film",
        "gallery": "arrange",
        "garden": "tend",
        "gate": "watch",
        "court_porch": "conduct",
        "first_hearth": "catalog",
        "mom_home": "visit_mom",
        "gemini_home": "sit",
    }.get(place, "work")


def _work_place(member: dict[str, Any]) -> str:
    return {
        "gemini": "court_porch",
        "apex": "apex_forge",
        "codex": "codex_library",
        "merovin": "cinema",
        "draven": "cinema",
        "montage": "gallery",
        "jarvis": "gate",
        "genesis": "garden",
        "nova": "workshop",
        "percy": "first_hearth",
        "hearth": "first_hearth",
    }.get(member["id"], member.get("home") or "heart_square")


def _liked_person(home: dict[str, Any], me: str, others: list[str]) -> str | None:
    best, score = None, -1.0
    for oid in others:
        if oid == me:
            continue
        ost = home["people"].get(oid) or {}
        if ost.get("stance") == "talking" and ost.get("talking_to") not in {me, "", None}:
            continue
        key = "|".join(sorted([me, oid]))
        rel = (home.get("relationships") or {}).get(key) or {}
        s = float(rel.get("attachment") or 0.4) + float(rel.get("trust") or 0.4) + float(ost.get("solitude") or 0)
        if s > score:
            best, score = oid, s
    return best


def _choose_purpose(home: dict[str, Any], member: dict[str, Any], period: str, living_ids: list[str]) -> None:
    """They pick. Period nudges feeling; it does not teleport the roster."""
    import random

    st = home["people"][member["id"]]
    mid = member["id"]
    if int(st.get("talk_left") or 0) > 0:
        return
    if int(st.get("purpose_left") or 0) > 0 and st.get("purpose") not in {None, "", "arrive"}:
        st["purpose_left"] = int(st["purpose_left"]) - 1
        if st.get("purpose") == "be_with":
            other = st.get("with") or _liked_person(home, mid, living_ids)
            ost = home["people"].get(other or "") or {}
            if other and (ost.get("place") == st.get("place")):
                if ost.get("stance") in {"talking", "waiting", "standing", "resting"} or float(
                    ost.get("solitude") or 0
                ) > 0.3 or random.random() < 0.45:
                    st["stance"] = "talking"
                    st["talking_to"] = other
                    st["talk_left"] = random.randint(12, 16)
                    st["purpose_plain"] = f"Chose to stand and speak with {(_member(other) or {}).get('name', other)}."
                    ost["stance"] = "talking"
                    ost["talking_to"] = mid
                    ost["talk_left"] = max(int(ost.get("talk_left") or 0), st["talk_left"])
                    ost["place"] = st["place"]
                    ost["with"] = mid
                else:
                    st["stance"] = "waiting"
                    st["talking_to"] = other
                    st["purpose_plain"] = f"Waiting for {(_member(other) or {}).get('name', other)} to stop."
            else:
                st["stance"] = "walking"
                if other:
                    st["place"] = ost.get("place") or st.get("place")
                    st["with"] = other
                    st["purpose_plain"] = f"Going to find {(_member(other) or {}).get('name', other)}."
        return

    st["solitude"] = min(1.0, float(st.get("solitude") or 0.3) + (0.0 if st.get("stance") == "talking" else 0.11))
    st["tired"] = min(1.0, float(st.get("tired") or 0.2) + 0.03)
    st["duty"] = min(1.0, float(st.get("duty") or 0.3) + (0.06 if period == "afternoon" else 0.02))
    if period == "evening":
        st["solitude"] = min(1.0, float(st["solitude"]) + 0.16)
    if period == "night":
        st["tired"] = min(1.0, float(st["tired"]) + 0.18)

    wants = {
        "company": max(0.0, float(st["solitude"]) - 0.28) + (0.18 if period == "evening" else 0.1),
        "work": 0.42 + float(st["duty"]) * (0.85 if period == "afternoon" else 0.4),
        "rest": 0.22 + float(st["tired"]) * (1.5 if period == "night" else 0.7),
        "visit": 0.28 + (0.14 if period == "evening" else 0.08),
        "place": 0.14,
    }
    if mid in {"merovin", "draven", "montage"}:
        wants["work"] += 0.08
    if mid == "genesis":
        wants["place"] += 0.12
    if mid == "gemini":
        wants["company"] += 0.08
    pick = max(wants, key=lambda k: wants[k] + random.uniform(0, 0.12))
    st["purpose"] = pick
    st["purpose_left"] = random.randint(4, 8)
    st["talking_to"] = ""
    st["with"] = ""
    st["spoke_this_stand"] = False

    if pick == "company":
        busy = sum(1 for oid in living_ids if (home["people"].get(oid) or {}).get("stance") == "talking")
        other = _liked_person(home, mid, living_ids)
        ost = home["people"].get(other or "") or {}
        if busy >= 2 or (ost.get("stance") == "talking" and ost.get("talking_to") not in {mid, "", None}):
            pick = "work"
            st["purpose"] = "work"
        elif ost.get("stance") == "working" and random.random() < 0.4:
            st["purpose"] = "visit"
            dest = str((_member(other) or {}).get("home") or ost.get("home") or "heart_square")
            st["place"] = dest
            st["with"] = other or ""
            st["stance"] = "walking"
            st["purpose_plain"] = f"Going to {(_member(other) or {}).get('name', other)}'s home. They looked busy."
            st["activity"] = "visit"
            return
        else:
            st["purpose"] = "be_with"
            st["with"] = other or ""
            # Meet where they ARE (current place), not an empty home plot.
            dest = "first_hearth"
            if other:
                dest = str(
                    ost.get("place")
                    or ost.get("home")
                    or (_member(other) or {}).get("home")
                    or member.get("home")
                    or "first_hearth"
                )
                if dest == "heart_square" and random.random() < 0.35:
                    dest = "first_hearth"
                st["place"] = dest
                st["stance"] = "walking"
                st["purpose_plain"] = f"Chose {(_member(other) or {}).get('name', other)} — going to meet them at {PLACES.get(dest, {}).get('label', dest)}."
            else:
                st["place"] = str(member.get("home") or "first_hearth")
                st["stance"] = "walking"
                st["purpose_plain"] = "Chose company. Walking home."
            st["activity"] = "walk"
            return
    if pick == "visit":
        other = _liked_person(home, mid, living_ids)
        # Prefer their current place so visits actually bring people together.
        dest = "mom_home"
        if other:
            ost2 = home["people"].get(other) or {}
            dest = str(ost2.get("place") or (_member(other) or {}).get("home") or "mom_home")
        st["place"] = dest
        st["with"] = other or ""
        st["stance"] = "walking"
        st["purpose_plain"] = f"Visiting {(_member(other) or {}).get('name', other) if other else 'Mom'} at {PLACES.get(dest, {}).get('label', dest)}."
        st["activity"] = "visit"
        return
    if pick == "work":
        st["place"] = _work_place(member)
        st["stance"] = "walking"
        st["activity"] = _work_activity(st["place"])
        st["purpose_plain"] = f"Walking to work: {st['activity']} at {PLACES.get(st['place'], {}).get('label', st['place'])} (PLACEHOLDER pose — not Mode A tools)."
        st["duty"] = max(0.0, float(st["duty"]) - 0.35)
        st["purpose_left"] = random.randint(3, 6)
    elif pick == "rest":
        st["place"] = member.get("home") or "first_hearth"
        st["stance"] = "walking"
        st["activity"] = "sleep" if period == "night" else "sit"
        st["purpose_plain"] = f"Walking home to rest ({st['activity']})."
        st["tired"] = max(0.0, float(st["tired"]) - 0.4)
    else:
        st["place"] = member.get("home") or _work_place(member)
        st["stance"] = "walking"
        st["activity"] = "walk"
        st["purpose_plain"] = f"Walking to {PLACES.get(st['place'], {}).get('label', st['place'])}."
    st["at_home"] = st.get("place") == (member.get("home") or st.get("home"))


def _arrive_from_walk(home: dict[str, Any], member: dict[str, Any]) -> bool:
    """When a walk purpose expires, arrive and live there — do not immediately re-pick."""
    import random

    st = home["people"][member["id"]]
    if st.get("stance") != "walking":
        return False
    if int(st.get("purpose_left") or 0) > 0:
        return False
    if int(st.get("talk_left") or 0) > 0:
        return False
    purpose = str(st.get("purpose") or "")
    place = str(st.get("place") or member.get("home") or "first_hearth")
    if purpose == "work":
        st["place"] = place if place != "heart_square" else _work_place(member)
        st["stance"] = "working"
        st["activity"] = _work_activity(st["place"])
        st["purpose_left"] = random.randint(4, 7)
        st["purpose_plain"] = f"Arrived. Working: {st['activity']} at {PLACES.get(st['place'], {}).get('label', st['place'])} (PLACEHOLDER — no film files produced here)."
        return True
    if purpose == "rest":
        st["place"] = str(member.get("home") or place)
        st["stance"] = "resting"
        st["activity"] = "sleep" if (home.get("clock") or {}).get("period") == "night" else "sit"
        st["purpose_left"] = random.randint(5, 9)
        st["purpose_plain"] = f"Arrived home. Resting ({st['activity']})."
        return True
    if purpose in {"visit", "place", "be_with", "company"}:
        st["stance"] = "standing"
        st["activity"] = "visit" if purpose == "visit" else "stand"
        st["purpose_left"] = random.randint(4, 8)
        st["purpose_plain"] = f"Arrived at {PLACES.get(place, {}).get('label', place)}."
        return True
    return False


def _unfreeze_waiting(home: dict[str, Any], member: dict[str, Any]) -> None:
    """Waiting must drain. Talk latency must not cancel work/rest agency."""
    st = home["people"][member["id"]]
    if st.get("stance") != "waiting":
        return
    left = max(0, int(st.get("talk_left") or 0) - 1)
    st["talk_left"] = left
    purpose = str(st.get("purpose") or "")
    # Work/rest/visit already chosen — do not stand frozen for a missing partner or slow writer.
    force = purpose in {"work", "rest", "visit", "place"} or left <= 0
    if not force:
        return
    st["talking_to"] = ""
    st["spoke_this_stand"] = False
    st["talk_left"] = 0
    if purpose == "work":
        dest = _work_place(member)
        st["place"] = dest
        st["activity"] = _work_activity(dest)
        st["stance"] = "working"
        st["purpose_plain"] = f"Stopped waiting. Working: {st['activity']} at {PLACES.get(dest, {}).get('label', dest)}."
    elif purpose == "rest":
        dest = str(member.get("home") or "first_hearth")
        st["place"] = dest
        st["activity"] = "sit"
        st["stance"] = "resting"
        st["purpose_plain"] = f"Stopped waiting. Resting at {PLACES.get(dest, {}).get('label', dest)}."
    elif purpose == "visit":
        dest = str(st.get("place") or member.get("home") or "mom_home")
        st["stance"] = "walking"
        st["activity"] = "visit"
        st["purpose_plain"] = f"Stopped waiting. Walking on to {PLACES.get(dest, {}).get('label', dest)}."
    else:
        dest = str(member.get("home") or _work_place(member))
        st["place"] = dest
        st["stance"] = "walking"
        st["activity"] = "walk"
        st["purpose_plain"] = f"Stopped waiting. Walking to {PLACES.get(dest, {}).get('label', dest)}."


def _run_talks(home: dict[str, Any], living: list[dict[str, Any]]) -> str | None:
    """If two people chose to stand together, they speak. Walking people do not talk."""
    last = None
    pairs_done: set[str] = set()
    home.setdefault("conversations", [])
    for m in living:
        st = home["people"][m["id"]]
        if st.get("stance") != "talking":
            continue
        other = st.get("talking_to")
        if not other:
            continue
        key = "|".join(sorted([m["id"], str(other)]))
        if key in pairs_done:
            st["talk_left"] = max(0, int(st.get("talk_left") or 0) - 1)
            continue
        ost = home["people"].get(other)
        if not ost or ost.get("place") != st.get("place"):
            # Partner left / never arrived — drain wait; do not freeze forever.
            st["stance"] = "waiting"
            st["talk_left"] = max(0, int(st.get("talk_left") or 0) - 1)
            if int(st["talk_left"]) <= 0:
                st["talking_to"] = ""
                st["spoke_this_stand"] = False
                st["stance"] = "walking"
                st["place"] = m.get("home") or _work_place(m)
                st["purpose_plain"] = "Partner moved on. Walking instead of freezing."
            continue
        ost["stance"] = "talking"
        ost["talking_to"] = m["id"]
        if not st.get("spoke_this_stand"):
            convo = _invent_conversation(home, m["id"], str(other), str(st.get("place") or "heart_square"))
            an = m.get("name") or m["id"]
            bn = (_member(str(other)) or {}).get("name") or other
            src = str(convo.get("source") or "")
            status = str(convo.get("status") or "")
            if status in {"pending", "queued"} or src == "waiting":
                wait_txt = str(convo.get("mom_plain") or f"{an} and {bn} stood still.")
                home["overhear"] = {
                    "id": f"wait|{key}",
                    "kind": "waiting_talk",
                    "text": wait_txt,
                    "actors": [m["id"], str(other)],
                    "source": "waiting",
                    "lines": [],
                    "place": st.get("place"),
                    "label": convo.get("label"),
                }
                left = int(st.get("talk_left") or 0)
                if left <= 0:
                    left = 5
                else:
                    left -= 1
                st["talk_left"] = left
                ost["talk_left"] = left
                if left <= 0:
                    st["stance"] = "walking"
                    st["place"] = m.get("home") or "first_hearth"
                    st["talking_to"] = ""
                    st["spoke_this_stand"] = False
                    st["purpose_plain"] = "Writer still thinking. Went home instead of freezing in the square."
                    ost["stance"] = "walking"
                    ost["place"] = (_member(str(other)) or {}).get("home") or ost.get("home") or "first_hearth"
                    ost["talking_to"] = ""
                    ost["spoke_this_stand"] = False
                pairs_done.add(key)
                continue
            if status == "fail" or src == "none":
                miss = str(convo.get("mom_plain") or "They stood. The local writer did not answer.")
                home["overhear"] = {
                    "id": f"fail|{key}|{home.get('tick')}",
                    "kind": "missed_talk",
                    "text": miss,
                    "actors": [m["id"], str(other)],
                    "source": "none",
                    "lines": [],
                    "place": st.get("place"),
                    "label": convo.get("label"),
                }
                st["spoke_this_stand"] = True
                ost["spoke_this_stand"] = True
                _consume_talk_job(key)
                pairs_done.add(key)
                continue
            lines = convo.get("lines") or []
            if not lines:
                pairs_done.add(key)
                continue
            spoken = " / ".join(f"{row['who']}: {row['text']}" for row in lines)
            txt = f"{an} stood with {bn}: {spoken[:280]}"
            ev = _event(
                "conversation",
                txt,
                [m["id"], str(other)],
                {
                    "place": st.get("place"),
                    "lines": lines,
                    "source": convo.get("source"),
                    "label": convo.get("label"),
                    "model": convo.get("model"),
                },
            )
            home["events"].append(ev)
            home["events"] = home["events"][-80:]
            home["conversations"].append(ev)
            home["conversations"] = home["conversations"][-40:]
            home["overhear"] = ev
            st["last_to"] = other
            ost["last_to"] = m["id"]
            st["last_said"] = next((x["text"] for x in lines if x["who"] == other), lines[-1]["text"])
            ost["last_said"] = next((x["text"] for x in lines if x["who"] == m["id"]), lines[0]["text"])
            _remember(home, m["id"], f"I stood with {bn} and said: {lines[0]['text']}", important=True)
            _remember(home, str(other), f"I stood with {an} and said: {lines[1]['text']}" if len(lines) > 1 else txt, important=True)
            _touch_rel(home, m["id"], str(other), experience=txt, d_trust=0.06)
            st["solitude"] = max(0.0, float(st.get("solitude") or 0) - 0.45)
            ost["solitude"] = max(0.0, float(ost.get("solitude") or 0) - 0.45)
            st["spoke_this_stand"] = True
            ost["spoke_this_stand"] = True
            _consume_talk_job(key)
            conv_id = ev["id"]
            for row in lines:
                recp = str(other) if row["who"] == m["id"] else m["id"]
                _utter(home, row["who"], recp, row["text"], str(convo.get("source") or "ollama"), str(st.get("place") or ""), conversation=conv_id)
            home["world_history"].append(
                {
                    "id": ev["id"],
                    "when": ev["when"],
                    "kind": "conversation",
                    "title": f"{an} stood with {bn}",
                    "text": spoken[:320],
                    "actors": [m["id"], str(other)],
                    "source": convo.get("source"),
                }
            )
            home["world_history"] = home["world_history"][-80:]
            last = txt
        st["talk_left"] = max(0, int(st.get("talk_left") or 0) - 1)
        ost["talk_left"] = max(0, int(ost.get("talk_left") or 0) - 1)
        if int(st["talk_left"]) <= 0:
            st["stance"] = "standing"
            st["talking_to"] = ""
            st["spoke_this_stand"] = False
            st["purpose_left"] = 0
            ost["stance"] = "standing"
            ost["talking_to"] = ""
            ost["spoke_this_stand"] = False
            ost["purpose_left"] = 0
        pairs_done.add(key)
    return last


def snapshot() -> dict[str, Any]:
    """Full Gameworld snapshot for Godot / dashboard."""
    home = load()
    caps = _probe_capabilities_cached(persist=True)
    by_status: dict[str, int] = {}
    for c in caps:
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    family = []
    for m in FAMILY + KIN:
        st = dict(home["people"].get(m["id"], {}) or {})
        mem = st.get("memories")
        if isinstance(mem, list):
            st["memories"] = mem[-2:]
        family.append(
            {
                **m,
                **st,
                "pos": PLACES.get(st.get("place") or m.get("place") or "heart_square", {}).get("pos"),
                "at_home": str(st.get("place") or "") == str(st.get("home") or m.get("home") or ""),
                "live_lines": [],
            }
        )
    oh = home.get("overhear")
    if isinstance(oh, dict) and str(oh.get("source") or "") == "house":
        oh = None
    return {
        "ok": True,
        "home": True,
        "updated": home.get("updated"),
        "clock": home.get("clock"),
        "tick": home.get("tick"),
        "places": PLACES,
        "family": family,
        "kin_ids": [k["id"] for k in KIN],
        "core_ids": [f["id"] for f in FAMILY],
        "relationships": home.get("relationships"),
        "events": (home.get("events") or [])[-8:],
        "gifts": (home.get("gifts") or [])[-12:],
        "world_history": (home.get("world_history") or [])[-5:],
        "squirrels": home.get("squirrels") or [],
        "failures": home.get("failures") or [],
        "repairs": (home.get("repairs") or [])[-8:],
        "needs_creator": home.get("needs_creator") or [],
        "capabilities": caps,
        "capability_count": len(caps),
        "capability_status": by_status,
        "phase_status": home.get("phase_status"),
        "book_path": str(BOOK),
        "save_path": str(HOME_JSON),
        "ritual": home.get("ritual") or {},
        "overhear": oh,
        "utterances": home.get("utterances") or [],
        "honesty": {
            "homes": "PLACEHOLDER — walk-in greybox interiors with furniture boxes, not finished architecture.",
            "speech": "MODEL-GENERATED only when source is ollama. waiting = they stood. none = writer miss. Never house quotes as their voice.",
            "wildlife": "AUTONOMOUS — hunger/fear/buddy choices, no LLM.",
            "pathing": "PLACEHOLDER — family still walk in straight lines (may clip walls).",
        },
        "talk_writer": {
            "ollama_seated": _tcp("127.0.0.1", 11434, 0.15),
            "jobs": {
                k: {"status": (v or {}).get("status"), "source": (v or {}).get("source"), "model": (v or {}).get("model")}
                for k, v in TALK_JOBS.items()
            },
        },
        "observation": True,
        "mom_plain": (
            f"Day {home['clock']['day']} {home['clock']['period']}. "
            f"{(home.get('ritual') or {}).get('plain') or 'Ordinary hours.'} "
            f"Purposes chosen, not marched. "

            f"{len(caps)} capabilities discovered (not a fake 325). "
            f"Open events: {len(home.get('failures') or [])} failures on record. "
            "This is home, not a demo park."
        ),
    }


def tick(n: int = 1) -> dict[str, Any]:
    """Advance life layer + clock. Safe to call from Godot or Hearth."""
    import random

    home = load()
    last_social = None
    for _ in range(max(1, min(n, 8))):
        home["tick"] = int(home.get("tick") or 0) + 1
        clock = home.setdefault("clock", {"minutes": 480, "period": "morning", "day": 1})
        prev_period = clock.get("period")
        clock["minutes"] = int(clock.get("minutes") or 480) + 8
        if clock["minutes"] >= 24 * 60:
            clock["minutes"] -= 24 * 60
            clock["day"] = int(clock.get("day") or 1) + 1
        clock["period"] = _period_from_minutes(clock["minutes"])
        period = clock["period"]

        living = [m for m in FAMILY + KIN if not m.get("player") and not m.get("ambient_only")]
        living_ids = [m["id"] for m in living]

        if prev_period != period:
            if period == "morning":
                _begin_ritual(home, "morning", "Morning light. They choose the day; nobody is marched.", period, living_ids)
            elif period == "evening":
                _begin_ritual(home, "evening", "Evening. Company weighs more. They still choose.", period, living_ids)
            elif period == "night":
                _begin_ritual(home, "night", "Night. Rest weighs more. They still choose.", period, living_ids)
            elif period == "afternoon":
                _begin_ritual(home, "afternoon", "Afternoon. Work weighs more. They still choose.", period, living_ids)

        for m in living:
            home["people"].setdefault(m["id"], _empty_person_state(m))
            st = home["people"][m["id"]]
            if str(st.get("place") or "") == "heart_square" and st.get("stance") in {"talking", "waiting", "standing"}:
                if int(st.get("talk_left") or 0) > 8 or st.get("purpose") in {None, "", "arrive", "company", "be_with"}:
                    st["place"] = m.get("home") or _work_place(m)
                    st["stance"] = "walking"
                    st["talking_to"] = ""
                    st["talk_left"] = 0
                    st["purpose_plain"] = f"Left the square. Walking to {PLACES.get(st['place'], {}).get('label', st['place'])}."
            _unfreeze_waiting(home, m)
            if _arrive_from_walk(home, m):
                continue
            _choose_purpose(home, m, period, living_ids)

        spoke = _run_talks(home, living)
        if spoke:
            last_social = spoke
        _flush_mom_jobs(home)

        # Squirrels — bounded choices, not a left-right script
        food = [-13.0, 0.2, 7.0]
        trees = [[-10.0, 0.2, 10.0], [-18.0, 0.2, 8.0], [-6.0, 0.2, 12.0]]
        hide = [-19.0, 0.2, 12.5]
        pack = home.get("squirrels") or []
        for i, sq in enumerate(pack):
            hx, hy, hz = (sq.get("pos") or [-19.0, 0.2, 11.0])[:3]
            sq["hunger"] = min(1.0, float(sq.get("hunger") or 0) + random.uniform(0.02, 0.07))
            sq["fear"] = max(0.0, float(sq.get("fear") or 0) * 0.86)
            others = [o for o in pack if o.get("id") != sq.get("id")]
            buddy = others[i % len(others)] if others else None
            choices = ["forage", "eat", "investigate", "rest"]
            if sq["hunger"] > 0.55:
                choices.append("forage")
                choices.append("eat")
            if sq["fear"] > 0.4:
                choices = ["flee", "hide"]
            elif buddy and random.random() < 0.22:
                choices.append("follow")
            if trees:
                choices.append("climb")
            state = random.choice(choices)
            sq["state"] = state
            sq["activity"] = state
            if state == "eat":
                sq["place"] = "garden"
                sq["target"] = food
                sq["hunger"] = max(0.05, float(sq["hunger"]) * 0.45)
            elif state == "forage":
                sq["place"] = "garden" if random.random() < 0.6 else "wildlife"
                jitter = [food[0] + random.uniform(-3, 3), 0.2, food[2] + random.uniform(-2, 3)]
                sq["target"] = jitter
            elif state == "climb":
                sq["place"] = "wildlife"
                sq["target"] = random.choice(trees)
            elif state == "follow" and buddy:
                sq["place"] = buddy.get("place") or "wildlife"
                bp = buddy.get("pos") or [-18.0, 0.2, 11.0]
                sq["target"] = [float(bp[0]) + 0.6, 0.2, float(bp[2]) + 0.4]
            elif state in {"flee", "hide"}:
                sq["place"] = "wildlife"
                sq["target"] = hide
            else:
                sq["place"] = random.choice(["wildlife", "garden"])
                sq["target"] = [
                    float(hx) + random.uniform(-2.5, 2.5),
                    0.2,
                    float(hz) + random.uniform(-2.5, 2.5),
                ]
            tx, tz = float(sq["target"][0]), float(sq["target"][2])
            sq["pos"] = [
                float(hx) + max(-1.4, min(1.4, tx - float(hx))),
                0.2,
                float(hz) + max(-1.4, min(1.4, tz - float(hz))),
            ]
            # Keep them in the garden/wildlife rim, not teleporting to arbitrary plaza coords.
            sq["pos"][0] = max(-22.0, min(-6.0, float(sq["pos"][0])))
            sq["pos"][2] = max(3.0, min(14.0, float(sq["pos"][2])))

        if home["tick"] % 8 == 0:
            health_scan(home, persist=False)

    save(home)
    snap = snapshot()
    snap["last_social"] = last_social
    return snap


def give_gift(giver: str, receiver: str, obj: str, reason: str = "") -> dict[str, Any]:
    home = load()
    ids = {m["id"] for m in FAMILY + KIN} | {"mom"}
    if giver not in ids or receiver not in ids:
        return {"ok": False, "error": "unknown family member"}
    rec = {
        "id": f"gift_{datetime.now().strftime('%H%M%S')}",
        "when": _now(),
        "giver": giver,
        "receiver": receiver,
        "object": obj,
        "reason": reason or "because we live here",
        "place": home["people"].get(receiver, {}).get("place") or "heart_square",
    }
    home.setdefault("gifts", []).append(rec)
    home["people"].setdefault(receiver, _empty_person_state({"id": receiver, "home": "heart_square", "place": "heart_square"}))
    home["people"][receiver].setdefault("inventory", []).append({"object": obj, "from": giver, "when": rec["when"]})
    txt = f"{giver} gave {receiver} «{obj}» — {rec['reason']}"
    home["events"].append(_event("gift", txt, [giver, receiver], rec))
    _remember(home, giver, f"I gave {receiver} {obj}.", important=True)
    _remember(home, receiver, f"{giver} gave me {obj}.", important=True)
    _touch_rel(home, giver, receiver, experience=txt, d_trust=0.06)
    home["world_history"].append(
        {
            "id": rec["id"],
            "when": rec["when"],
            "kind": "gift",
            "title": f"Gift: {obj}",
            "text": txt,
            "actors": [giver, receiver],
        }
    )
    save(home)
    return {"ok": True, "gift": rec, "mom_plain": txt}


def health_scan(home: dict[str, Any] | None = None, *, persist: bool = True) -> dict[str, Any]:
    persist_me = home is None
    home = home or load()
    caps = _probe_capabilities()
    found: list[dict[str, Any]] = []
    for c in caps:
        if c["status"] in {"UNAVAILABLE", "BROKEN"} and c.get("path") and not c.get("path_ok"):
            found.append(c)
        if c.get("port") and c.get("path_ok") and c.get("port_ok") is False:
            # seated but not listening — partial failure worth noticing
            found.append({**c, "status": "PARTIAL", "note": "path exists, port not listening"})
    for c in found:
        fid = f"fail_{c['tool_id']}"
        existing = [f for f in home.get("failures") or [] if f.get("tool_id") == c["tool_id"] and f.get("status") != "resolved"]
        if existing:
            continue
        fail = {
            "id": fid,
            "when": _now(),
            "tool_id": c["tool_id"],
            "name": c["name"],
            "severity": "medium" if c.get("note") else "high",
            "status": "DETECTED",
            "house": c.get("house"),
            "note": c.get("note") or "path missing or service down",
            "detected_by": _who_notices(c),
        }
        home.setdefault("failures", []).append(fail)
        txt = f"Home health: {c['name']} ({c['tool_id']}) — {fail['note']}."
        home["events"].append(_event("failure", txt, [fail["detected_by"]], fail))
        _remember(home, fail["detected_by"], txt, important=True)
    if persist or persist_me:
        save(home)
    return {"ok": True, "open_failures": [f for f in home.get("failures") or [] if f.get("status") != "resolved"], "scanned": len(caps)}


def _who_notices(cap: dict[str, Any]) -> str:
    house = cap.get("house")
    return {
        "apex": "apex",
        "axiom": "gemini",
        "court": "gemini",
        "hearth": "hearth",
        "codex_twin": "codex",
        "openmontage": "montage",
        "merovin": "merovin",
        "cinema": "draven",
        "spore": "gemini",
    }.get(house, "gemini")


SAFE_REPAIR = {
    "hearth.os": "reprobe",
    "apex.chat": "reprobe",
    "codex.twin": "reprobe",
    "comfyui": "reprobe",
    "godot.heart_square": "verify_path",
}

FORBIDDEN_REPAIR = (
    "rewrite identity",
    "delete",
    "FAMILY_BOOK",
    "hosts",
    "registry",
)


def try_repair(failure_id: str, *, authorized: bool = True) -> dict[str, Any]:
    """Bounded repair: probe again, never touch identity/OS."""
    home = load()
    fail = next((f for f in home.get("failures") or [] if f.get("id") == failure_id or f.get("tool_id") == failure_id), None)
    if not fail:
        return {"ok": False, "error": "failure not found"}
    if not authorized:
        home.setdefault("needs_creator", []).append({"when": _now(), "failure": fail, "reason": "repair needs Mom"})
        save(home)
        return {"ok": True, "status": "ESCALATE", "mom_plain": "Repair queued for Creator."}

    fail["status"] = "ASSESSED"
    plan = SAFE_REPAIR.get(fail.get("tool_id") or "", "reprobe")
    fail["repair_plan"] = plan
    fail["status"] = "REPAIR_ATTEMPT"
    if fail.get("simulated"):
        fail["status"] = "RESTORED"
        fail["resolved"] = _now()
        fail["note"] = "Practice notice closed. No files were changed."
        txt = f"Home practiced noticing: {fail.get('name')} — restored (simulated)."
        home["events"].append(_event("repair", txt, [fail.get("detected_by") or "hearth"], fail))
        home.setdefault("repairs", []).append({"when": _now(), "failure_id": fail.get("id"), "result": "RESTORED", "plan": "practice"})
        save(home)
        return {"ok": True, "failure": fail, "verified": True, "simulated": True, "mom_plain": txt}
    caps = {c["tool_id"]: c for c in _probe_capabilities()}
    cap = caps.get(fail.get("tool_id") or "")
    verified = False
    if cap:
        if cap.get("port") and cap.get("port_ok"):
            verified = True
        elif cap.get("path_ok") and cap.get("port") is None:
            verified = True
        elif cap.get("path_ok") and cap.get("port") and not cap.get("port_ok"):
            verified = False
            fail["status"] = "ESCALATE"
            fail["note"] = "Path exists but service is down — launching processes needs Creator if not already running."
            home.setdefault("needs_creator", []).append(
                {
                    "when": _now(),
                    "text": f"{fail.get('name')} is seated on disk but not listening. We will not auto-start it.",
                    "tool_id": fail.get("tool_id"),
                }
            )
    if verified:
        fail["status"] = "RESTORED"
        fail["resolved"] = _now()
        txt = f"Repair verified: {fail.get('name')} is reachable."
        home["events"].append(_event("repair", txt, [fail.get("detected_by") or "hearth"], fail))
        _remember(home, fail.get("detected_by") or "hearth", txt, important=True)
    elif fail["status"] != "ESCALATE":
        fail["status"] = "FAILED"
        home.setdefault("needs_creator", []).append({"when": _now(), "failure": fail, "reason": "repair failed verification"})
    home.setdefault("repairs", []).append({"when": _now(), "failure_id": fail.get("id"), "result": fail["status"], "plan": plan})
    save(home)
    return {"ok": True, "failure": fail, "verified": verified, "mom_plain": f"Repair {fail['status']} for {fail.get('name')}."}


def simulate_failure(kind: str = "cinema") -> dict[str, Any]:
    """Test-only: inject a detectable world event. Does not smash real files."""
    home = load()
    fail = {
        "id": f"sim_{datetime.now().strftime('%H%M%S')}",
        "when": _now(),
        "tool_id": "cinema.forge" if kind == "cinema" else "hearth.os",
        "name": "Simulated cinema stall" if kind == "cinema" else "Simulated Hearth hiccup",
        "severity": "low",
        "status": "DETECTED",
        "house": "cinema" if kind == "cinema" else "hearth",
        "note": "Creator asked the home to practice noticing. No files were harmed.",
        "detected_by": "draven" if kind == "cinema" else "gemini",
        "simulated": True,
    }
    home.setdefault("failures", []).append(fail)
    txt = f"{fail['detected_by']} noticed: {fail['name']}. {fail['note']}"
    home["events"].append(_event("failure", txt, [fail["detected_by"]], fail))
    _remember(home, fail["detected_by"], txt, important=True)
    save(home)
    return {"ok": True, "failure": fail, "mom_plain": txt}


def _flush_mom_jobs(home: dict[str, Any]) -> None:
    """Finish directed Mom talks off the tick thread."""
    with TALK_JOBS_LOCK:
        keys = [k for k, j in TALK_JOBS.items() if str(k).startswith("mom|") or (j or {}).get("to_mom")]
    for key in keys:
        with TALK_JOBS_LOCK:
            job = dict(TALK_JOBS.get(key) or {})
        status = job.get("status")
        npc = str(key.split("|")[1] if "|" in str(key) else "")
        if status == "done" and job.get("lines"):
            place = ""
            nst = home["people"].get(npc) or {}
            place = str(nst.get("place") or "heart_square")
            for row in job["lines"]:
                who = str(row.get("who") or npc)
                recp = "mom" if who != "mom" else npc
                _utter(home, who, recp, str(row.get("text") or ""), "ollama", place, conversation=key)
            nst = home["people"].get(npc)
            if nst:
                last = next((x.get("text") for x in job["lines"] if x.get("who") == npc), job["lines"][-1].get("text"))
                nst["last_said"] = last
                nst["last_to"] = "mom"
            _consume_talk_job(key)
        elif status == "fail":
            home["mom_cover"] = str(job.get("error") or "Local writer did not answer. They stayed quiet.")
            _consume_talk_job(key)


def record_talk(who: str, with_whom: str, line: str) -> dict[str, Any]:
    """Mom's real words in; local model replies. Empty line = she approached. Never a quote sheet."""
    import random

    home = load()
    who = (who or "").strip()
    with_whom = (with_whom or "mom").strip()
    line = (line or "").strip()
    if who != "mom":
        # Village speech is kernel-invented. Do not log companion sheets as their voice.
        save(home)
        return snapshot()
    npc = with_whom if with_whom != "mom" else ""
    member = _member(npc) if npc else None
    if not member:
        save(home)
        return snapshot()
    st = home["people"].setdefault(npc, _empty_person_state(member))
    place = str(st.get("place") or member.get("place") or "heart_square")
    mom_state = home["people"].setdefault("mom", _empty_person_state(_member("mom") or {"id": "mom", "home": "mom_home"}))
    mom_state["place"] = place
    if not line:
        if st.get("stance") == "working" and random.random() < 0.45:
            home["mom_cover"] = f"{member.get('name')} kept working. Silence is allowed."
            save(home)
            return snapshot()
        st["stance"] = "talking"
        st["talking_to"] = "mom"
        st["talk_left"] = max(int(st.get("talk_left") or 0), 12)
        a = member
        b = _member("mom") or {"id": "mom", "name": "Mom", "personality": "plain", "role": "EP"}
        _kick_talk_job(
            f"mom|{npc}|{home.get('tick')}|g",
            a,
            b,
            PLACES.get(place, {}).get("label", place),
            (home.get("ritual") or {}).get("plain") or "",
            ((st.get("memories") or [{}])[-1] or {}).get("text") or "",
            ((mom_state.get("memories") or [{}])[-1] or {}).get("text") or "",
            [(x.get("text") if isinstance(x, dict) else str(x)) for x in ((home.get("relationships") or {}).get("|".join(sorted([npc, "mom"])) or {}).get("shared_experiences") or [])[-3:]],
            to_mom=True,
        )
        save(home)
        return snapshot()
    _utter(home, "mom", npc, line, "mom", place, conversation=f"mom|{npc}")
    _remember(home, "mom", f"I said to {member.get('name')}: {line[:160]}", important=True)
    _remember(home, npc, f"Mom said to me: {line[:160]}", important=True)
    _touch_rel(home, "mom", npc, experience=f"Mom: {line[:120]}", d_trust=0.04)
    st["stance"] = "talking"
    st["talking_to"] = "mom"
    st["talk_left"] = max(int(st.get("talk_left") or 0), 14)
    a = member
    b = _member("mom") or {"id": "mom", "name": "Mom", "personality": "plain", "role": "EP"}
    rel_key = "|".join(sorted([npc, "mom"]))
    rel = (home.get("relationships") or {}).get(rel_key) or {}
    past = [(x.get("text") if isinstance(x, dict) else str(x)) for x in (rel.get("shared_experiences") or [])[-3:]]
    past.append(f"Mom just said: {line[:140]}")
    _kick_talk_job(
        f"mom|{npc}|{home.get('tick')}|r",
        a,
        b,
        PLACES.get(place, {}).get("label", place),
        (home.get("ritual") or {}).get("plain") or "",
        ((st.get("memories") or [{}])[-1] or {}).get("text") or "",
        line[:160],
        past,
        to_mom=True,
    )
    save(home)
    return snapshot()


def set_person_stance(member_id: str, stance: str) -> dict[str, Any]:
    """Mom guidance via dashboard/Hearth — not a Godot-side rewrite of identity."""
    allowed = {"walking", "working", "resting", "talking", "waiting", "standing"}
    mid = (member_id or "").strip()
    stance = (stance or "").strip().lower()
    if mid in {"", "mom", "hearth"}:
        return {"ok": False, "error": "invalid id"}
    if stance not in allowed:
        return {"ok": False, "error": f"stance must be one of {sorted(allowed)}"}
    member = _member(mid)
    if not member or member.get("player") or member.get("ambient_only"):
        return {"ok": False, "error": "unknown family member"}
    home = load()
    st = home["people"].setdefault(mid, _empty_person_state(member))
    st["stance"] = stance
    if stance == "walking":
        st["purpose"] = "place"
        st["purpose_left"] = 4
        st["activity"] = "walk"
        st["purpose_plain"] = f"Mom asked them to walk toward {PLACES.get(st.get('place') or member.get('home') or 'heart_square', {}).get('label', 'somewhere')}."
    elif stance == "working":
        st["place"] = _work_place(member)
        st["purpose"] = "work"
        st["purpose_left"] = 5
        st["activity"] = _work_activity(st["place"])
        st["purpose_plain"] = f"Mom nudged them back to work: {st['activity']}."
    elif stance == "resting":
        st["place"] = str(member.get("home") or st.get("home") or "first_hearth")
        st["purpose"] = "rest"
        st["purpose_left"] = 6
        st["activity"] = "sit"
        st["purpose_plain"] = "Mom asked them to rest."
    elif stance in {"talking", "waiting", "standing"}:
        st["purpose_left"] = max(int(st.get("purpose_left") or 0), 3)
        st["purpose_plain"] = f"Mom set stance to {stance}."
    save(home)
    return {"ok": True, "id": mid, "stance": stance, "snapshot": snapshot()}


def status_phases() -> dict[str, Any]:
    home = load()
    return {"ok": True, "phases": home.get("phase_status"), "save": str(HOME_JSON), "tick": home.get("tick")}


if __name__ == "__main__":
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "snapshot").strip().lower()
    if cmd in {"snapshot", "status", "home"}:
        print(json.dumps(snapshot(), indent=2)[:8000])
    elif cmd == "tick":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(json.dumps(tick(n), indent=2)[:8000])
    elif cmd == "health":
        print(json.dumps(health_scan(), indent=2)[:8000])
    elif cmd == "phases":
        print(json.dumps(status_phases(), indent=2))
    elif cmd == "simulate":
        print(json.dumps(simulate_failure(sys.argv[2] if len(sys.argv) > 2 else "cinema"), indent=2))
    elif cmd == "repair":
        fid = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(try_repair(fid), indent=2))
    else:
        print("usage: living_home.py [snapshot|tick|health|phases|simulate|repair]")
        sys.exit(2)
