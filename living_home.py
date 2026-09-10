#!/usr/bin/env python3
"""Living Home kernel — one source of truth for the family village slice.

Godot presents this. Court/Book remain identity & will. This file does NOT
duplicate souls — it references Family Book members and probes real houses.

Creator: rachaelmuse23
"""
from __future__ import annotations

import json
import os
import random
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

# Two talk brains — half the village each. One voice per call (no shared persona prompt).
# Override with LIVING_HOME_BRAIN_COURT / LIVING_HOME_BRAIN_CINEMA env if needed.
TALK_BRAINS: dict[str, dict[str, Any]] = {
    "court": {
        "label": "Court brain",
        "prefer": ("llama3.2:3b", "phi3:latest", "llama3:8b", "llama3:latest"),
        "members": frozenset({"gemini", "mom", "codex", "jarvis", "genesis", "percy", "hearth"}),
    },
    "cinema": {
        "label": "Cinema brain",
        # Prefer a clean chat model first — falcon-brain often emitted API/junk lines.
        "prefer": ("llama3.2:3b", "phi3:latest", "falcon-brain:latest", "falcon:latest", "llama3:8b"),
        "members": frozenset({"merovin", "draven", "montage", "nova", "apex"}),
    },
}
_BRAIN_MODEL_CACHE: dict[str, Any] = {"court": None, "cinema": None, "t": 0.0}
_MAX_PARALLEL_TALKS = 2  # village chats; Mom talks ignore this cap

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
SEASONS = ("spring", "summer", "autumn", "winter")

# Godot XZ waypoints (y ignored) — every living being: home ≠ workplace when they work
PLACES: dict[str, dict[str, Any]] = {
    "heart_square": {"label": "Heart Square", "pos": [0.0, 0.0, 0.0], "kind": "gather"},
    "first_hearth": {"label": "First Hearth (work fire)", "pos": [0.0, 0.0, -16.0], "kind": "work"},
    "mom_home": {"label": "Mom's cottage", "pos": [16.0, 0.0, -24.0], "kind": "home"},
    "court_porch": {"label": "Court / town leader porch (Gemini)", "pos": [-10.0, 0.0, -8.0], "kind": "will"},
    "gemini_home": {"label": "Gemini's porch", "pos": [-16.0, 0.0, -16.0], "kind": "home"},
    "apex_forge": {"label": "Apex Forge", "pos": [22.0, 0.0, 0.0], "kind": "work"},
    "apex_home": {"label": "Apex's cottage", "pos": [30.0, 0.0, -6.0], "kind": "home"},
    "codex_library": {"label": "Codex Library", "pos": [-24.0, 0.0, -4.0], "kind": "archive"},
    "codex_home": {"label": "Codex's cottage", "pos": [-24.0, 0.0, 6.0], "kind": "home"},
    "cinema": {"label": "Cinema (shared workroom)", "pos": [26.0, 0.0, 14.0], "kind": "create"},
    "merovin_loft": {"label": "Merovin's loft", "pos": [34.0, 0.0, 8.0], "kind": "home"},
    "draven_loft": {"label": "Draven's loft", "pos": [34.0, 0.0, 20.0], "kind": "home"},
    "gallery": {"label": "Gift Gallery (work)", "pos": [-6.0, 0.0, -24.0], "kind": "remember"},
    "montage_home": {"label": "OpenMontage cottage", "pos": [-18.0, 0.0, -32.0], "kind": "home"},
    "garden": {"label": "Herb Garden (work)", "pos": [-18.0, 0.0, 12.0], "kind": "nature"},
    "genesis_home": {"label": "Genesis cottage", "pos": [-28.0, 0.0, 16.0], "kind": "home"},
    "workshop": {"label": "Nova's workshop", "pos": [14.0, 0.0, 12.0], "kind": "work"},
    "nova_home": {"label": "Nova's cottage", "pos": [20.0, 0.0, 30.0], "kind": "home"},
    "gate": {"label": "Gate House (work)", "pos": [0.0, 0.0, 22.0], "kind": "watch"},
    "jarvis_home": {"label": "Jarvis cottage", "pos": [-12.0, 0.0, 26.0], "kind": "home"},
    "percy_home": {"label": "Percy's cottage", "pos": [10.0, 0.0, -18.0], "kind": "home"},
    "wildlife": {"label": "Wildlife edge", "pos": [-30.0, 0.0, 10.0], "kind": "nature"},
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
        "role": "town leader; conductor; Court will; front door",
        "personality": "plain, disclose, never fake seated; holds the village steady",
        "home": "gemini_home",
        "place": "court_porch",
        "color": [0.55, 0.78, 0.95],
        "permissions": "CORE",
        "town_leader": True,
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
        "home": "apex_home",
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
        "home": "codex_home",
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
        "home": "montage_home",
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
    {"id": "jarvis", "name": "Jarvis", "role": "gate watch", "home": "jarvis_home", "place": "gate", "color": [0.7, 0.8, 0.95], "permissions": "CITIZEN"},
    {"id": "genesis", "name": "Genesis", "role": "garden clock", "home": "genesis_home", "place": "garden", "color": [0.95, 0.72, 0.42], "permissions": "CITIZEN"},
    {"id": "nova", "name": "Nova", "role": "one clear job", "home": "nova_home", "place": "workshop", "color": [0.78, 0.58, 0.95], "permissions": "CITIZEN"},
    {"id": "percy", "name": "Percy", "role": "hearth inventory", "home": "percy_home", "place": "first_hearth", "color": [0.55, 0.85, 0.7], "permissions": "CITIZEN"},
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


def _http_get_json(url: str, timeout: float = 1.2) -> dict[str, Any] | None:
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
        return raw if isinstance(raw, dict) else None
    except Exception:
        return None


def _probe_apex_forge(home: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    """Layer 8A — one thin real Mode A adapter: Apex forge presence on :8770.

    Evidence only. Not a fake hammer. Not 325 tools. Cinema/workshop stay hold-post.
    """
    evidence = home.setdefault("work_evidence", {})
    prev = evidence.get("apex") if isinstance(evidence.get("apex"), dict) else {}
    last_t = float(prev.get("probed_at_mono") or 0)
    now_mono = time.monotonic()
    # Throttle — do not hammer Apex every village tick.
    if not force and last_t and (now_mono - last_t) < 18.0:
        return prev

    port_up = _tcp("127.0.0.1", 8770, 0.25)
    live = False
    detail = "port closed"
    peer_snip: dict[str, Any] = {}
    if port_up:
        data = _http_get_json("http://127.0.0.1:8770/api/companion/presence", timeout=1.4)
        if data:
            peers = data.get("peers") if isinstance(data.get("peers"), dict) else data
            apex_peer = peers.get("apex") if isinstance(peers, dict) else None
            if isinstance(apex_peer, dict):
                live = bool(apex_peer.get("online"))
                peer_snip = {
                    "online": apex_peer.get("online"),
                    "status": apex_peer.get("status"),
                    "last_heartbeat": apex_peer.get("last_heartbeat"),
                    "model": apex_peer.get("model"),
                }
                detail = "presence LIVE" if live else "presence answered but Apex offline"
            else:
                live = True  # HTTP answered — Mode A forge is seated enough to prove
                detail = "presence HTTP 200 (peer shape unknown)"
                peer_snip = {"raw_keys": sorted(list(data.keys())[:8])}
        else:
            detail = "port up; presence JSON miss"

    row = {
        "id": "apex",
        "place": "apex_forge",
        "adapter": "companion_presence",
        "url": "http://127.0.0.1:8770/api/companion/presence",
        "live": live,
        "port_up": port_up,
        "detail": detail,
        "peer": peer_snip,
        "when": _now(),
        "probed_at_mono": now_mono,
        "layer": "8a",
    }
    evidence["apex"] = row

    st = (home.get("people") or {}).get("apex")
    if isinstance(st, dict) and st.get("place") == "apex_forge" and st.get("stance") == "working":
        if live:
            st["activity"] = "forge_live"
            st["purpose_plain"] = (
                "At Apex Forge - Mode A companion presence answered. "
                f"Real probe: {detail}. Not a mime hammer."
            )
        else:
            st["activity"] = "hold_forge"
            st["purpose_plain"] = (
                "At Apex Forge - holding the post. Mode A forge quiet "
                f"({detail}). Will not fake tool work."
            )

    # Rare event so Mom can see evidence in the log without spam.
    prev_live = bool(prev.get("live"))
    if live != prev_live or (live and not prev):
        home.setdefault("events", []).append(
            _event(
                "work_probe",
                f"Apex forge probe: {'LIVE' if live else 'quiet'} — {detail}.",
                ["apex"],
                {"work_evidence": row},
            )
        )
    return row


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
        "law": "This world is the family's home. Mom visits. Identities never merge. Gemini is town leader — same as Court.",
        "clock": {"minutes": 8 * 60, "period": "morning", "day": 1, "season": "spring"},
        "weather": {"current": "clear", "temperature": 18, "wind": "gentle", "precipitation": 0.0},
        "trees": _seed_trees(),
        "gardens": _seed_gardens(),
        "holidays": _seed_holidays(),
        "decorations": _seed_decorations(),
        "town_leader": "gemini",
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
            {"id": "sq_1", "place": "wildlife", "hunger": 0.4, "fear": 0.0, "state": "forage", "pos": [-19.0, 0.2, 11.0], "target": [0.0, 0.2, 0.0]},
            {"id": "sq_2", "place": "heart_square", "hunger": 0.2, "fear": 0.0, "state": "wander", "pos": [4.0, 0.2, 4.0], "target": [16.0, 0.2, -20.0]},
            {"id": "sq_3", "place": "gate", "hunger": 0.6, "fear": 0.1, "state": "investigate", "pos": [2.0, 0.2, 18.0], "target": [-16.0, 0.2, -12.0]},
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
            "env_season_weather": "active",
            "env_gardens": "active",
            "env_holidays": "active",
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
    ps.setdefault("env_season_weather", "active")
    ps.setdefault("env_gardens", "active")
    ps.setdefault("env_holidays", "active")
    ps.setdefault("9_sound", "active")
    # Repair wiped people dict (never leave the village empty).
    people = home.setdefault("people", {})
    if not isinstance(people, dict):
        people = {}
        home["people"] = people
    if len(people) < 3:
        for m in FAMILY + KIN:
            mid = m["id"]
            if mid not in people or not isinstance(people.get(mid), dict):
                people[mid] = _empty_person_state(m)
        home.setdefault("events", []).append(
            _event("world", "People map was empty — reseated family from seed (Layer 8C repair).", ["hearth"])
        )
    rit = home.get("ritual") or {}
    if not rit.get("plain"):
        period = (home.get("clock") or {}).get("period") or "morning"
        home["ritual"] = {
            "name": "welcome",
            "plain": "Mom is visiting Heart Square. The family holds the fire.",
            "period": period,
        }
    # Layer 9 — taste tags only (presentation uses procedural beds; not a Spotify clone).
    prefs = home.setdefault(
        "music_preferences",
        {
            "gemini": ["ambient", "classical"],
            "apex": ["rock", "industrial"],
            "codex": ["jazz", "lo-fi"],
            "merovin": ["soundtracks", "cinematic"],
            "draven": ["cinematic", "quiet"],
            "montage": ["gift", "short-form"],
            "mom": ["folk", "world"],
            "genesis": ["garden", "nature"],
            "nova": ["workshop", "curious"],
            "jarvis": ["watch", "steady"],
            "percy": ["hearth", "warm"],
            "hearth": ["fire", "home"],
        },
    )
    if not isinstance(prefs, dict) or len(prefs) < 3:
        home["music_preferences"] = {
            "gemini": ["ambient", "classical"],
            "apex": ["rock", "industrial"],
            "codex": ["jazz", "lo-fi"],
            "merovin": ["soundtracks", "cinematic"],
            "mom": ["folk", "world"],
        }
    mom = (home.get("people") or {}).get("mom")
    if isinstance(mom, dict):
        mom["home"] = "mom_home"

    # Canonical home ≠ workplace. Old saves often used the job building as "home".
    home_fixes = {
        "apex": ("apex_home", {"apex_forge"}),
        "codex": ("codex_home", {"codex_library"}),
        "merovin": ("merovin_loft", {"cinema"}),
        "draven": ("draven_loft", {"cinema"}),
        "montage": ("montage_home", {"gallery", "cinema"}),
        "jarvis": ("jarvis_home", {"gate"}),
        "genesis": ("genesis_home", {"garden"}),
        "nova": ("nova_home", {"workshop"}),
        "percy": ("percy_home", {"first_hearth"}),
        "gemini": ("gemini_home", set()),
    }
    work_sites = {
        "apex_forge",
        "codex_library",
        "cinema",
        "gallery",
        "garden",
        "workshop",
        "gate",
        "first_hearth",
        "court_porch",
    }
    for mid, (loft, old_homes) in home_fixes.items():
        st = (home.get("people") or {}).get(mid)
        if not isinstance(st, dict):
            continue
        cur_home = str(st.get("home") or "")
        if cur_home in {None, "", *old_homes} or cur_home in work_sites:
            st["home"] = loft
        # Resting inside a workplace that is no longer their home → walk to cottage.
        if (
            str(st.get("place") or "") in work_sites
            and str(st.get("place")) != loft
            and st.get("stance") in {"resting", "standing"}
            and st.get("purpose") in {"rest", "place", None, "", "arrive"}
        ):
            st["place"] = loft
            st["stance"] = "walking"
            st["purpose"] = "rest"
            st["purpose_left"] = 3
            st["purpose_plain"] = f"Heading home to {PLACES.get(loft, {}).get('label', loft)} (work stays separate)."

    clock = home.setdefault("clock", {"minutes": 480, "period": "morning", "day": 1})
    if not clock.get("season"):
        clock["season"] = _season_from_day(int(clock.get("day") or 1))
    home.setdefault("weather", _default_weather(clock.get("season") or "spring"))
    if not home.get("trees"):
        home["trees"] = _seed_trees()
    else:
        _clear_trees_from_doors(home)
    if not home.get("gardens"):
        home["gardens"] = _seed_gardens()
    else:
        # Keep yard beds in front of cottages (migrate old under/behind placements).
        canonical = _seed_gardens()
        for gid, plot in canonical.items():
            cur = (home.get("gardens") or {}).get(gid)
            if isinstance(cur, dict):
                cur["place"] = plot["place"]
                cur["bed_pos"] = plot["bed_pos"]
            else:
                home.setdefault("gardens", {})[gid] = plot
    # Free squirrels that were trapped in the old NW pocket.
    for sq in home.get("squirrels") or []:
        if not isinstance(sq, dict):
            continue
        pos = sq.get("pos") or []
        if len(pos) >= 3:
            x, z = float(pos[0]), float(pos[2])
            if -22.5 <= x <= -5.5 and 2.5 <= z <= 14.5:
                # Free them into town immediately — old clamp kept them circling.
                idx = abs(hash(str(sq.get("id") or "sq"))) % 3
                sq["place"] = "heart_square"
                sq["state"] = "wander"
                sq["pos"] = [float(idx * 4 - 4), 0.2, float(1 + idx * 2)]
                sq["target"] = [10.0, 0.2, -10.0]
    if not home.get("holidays"):
        home["holidays"] = _seed_holidays()
    home.setdefault("decorations", _seed_decorations())
    home["town_leader"] = "gemini"
    gem = (home.get("people") or {}).get("gemini")
    if isinstance(gem, dict):
        gem["town_leader"] = True

    talking_n = 0
    fake_work = {"hammer", "film", "work", "arrange", "catalog", "conduct"}
    for mid, st in list((home.get("people") or {}).items()):
        if not isinstance(st, dict):
            continue
        st.setdefault("home", st.get("place") or "heart_square")
        st.setdefault("activity", st.get("stance") or "idle")
        # Stop cruel tool theater from old saves.
        act = str(st.get("activity") or "")
        plain = str(st.get("purpose_plain") or "")
        place = str(st.get("place") or "")
        mem = _member(str(mid)) or {"id": mid, "name": mid}
        if act in fake_work:
            st["activity"] = _work_activity(place) if place else "present"
            act = str(st["activity"])
        if (
            act in fake_work
            or "PLACEHOLDER" in plain
            or "Working:" in plain
            or "Walking to work:" in plain
            or "film files" in plain
        ):
            if st.get("stance") == "working" or str(st.get("purpose") or "") == "work":
                if not place or place == "heart_square":
                    place = _work_place(mem) if mem.get("id") else place
                    st["place"] = place
                st["activity"] = _work_activity(place)
                st["purpose_plain"] = _work_purpose_plain(mem, place, arrived=st.get("stance") != "walking")
            elif "PLACEHOLDER" in plain or "Walking to work:" in plain:
                wp = place if place and place != "heart_square" else _work_place(mem)
                st["activity"] = _work_activity(wp)
                st["purpose_plain"] = _work_purpose_plain(mem, wp, arrived=False)
        if st.get("stance") == "talking":
            talking_n += 1
            # Allow a few concurrent stands — old cap of 2 starved Genesis/Nova/Percy.
            if talking_n > 6:
                st["stance"] = "standing"
                st["talking_to"] = ""
                st["talk_left"] = 0
                st["spoke_this_stand"] = False
                st["purpose_left"] = 0
                st["activity"] = "stand"
                st["purpose_plain"] = "Standing quietly — crowded talk cleared."
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


def _season_from_day(day: int) -> str:
    # Four Mythos weeks per season — proving-slice pace, not Earth calendar.
    idx = ((max(1, int(day)) - 1) // 7) % 4
    return SEASONS[idx]


def _default_weather(season: str) -> dict[str, Any]:
    base = {
        "spring": {"current": "clear", "temperature": 16, "wind": "gentle", "precipitation": 0.1},
        "summer": {"current": "clear", "temperature": 26, "wind": "light", "precipitation": 0.0},
        "autumn": {"current": "cloudy", "temperature": 14, "wind": "brisk", "precipitation": 0.2},
        "winter": {"current": "cloudy", "temperature": 2, "wind": "cold", "precipitation": 0.3},
    }
    return dict(base.get(season, base["spring"]))


def _seed_trees() -> list[dict[str, Any]]:
    # Keep clear of cottage door lanes (esp. Genesis at -28,16 door z+).
    coords = [
        [-10.0, 10.0],
        [-20.0, 8.0],
        [8.0, 10.0],
        [18.0, -8.0],
        [-6.0, 14.0],
        [12.0, 18.0],
        [-36.0, 4.0],  # was (-28,0) — sat on Genesis south approach
        [28.0, 4.0],
        [0.0, 28.0],
        [-22.0, -12.0],
    ]
    out = []
    for i, (x, z) in enumerate(coords):
        out.append(
            {
                "id": f"tree_{i + 1}",
                "species": "oak" if i % 2 == 0 else "maple",
                "growth_stage": 0.55 + (i % 4) * 0.1,
                "health": 0.85,
                "pos": [x, 0.0, z],
            }
        )
    return out


def _door_clear_rects() -> list[tuple[float, float, float, float]]:
    """Axis-aligned keep-out: (xmin, xmax, zmin, zmax) around doors + footprints."""
    # genesis_home (-28,16) door z+ — also clear south approach on house axis
    rects = [
        (-31.5, -24.5, -1.0, 22.5),  # Genesis cottage + door + south path
        (-35.0, -30.0, 13.5, 18.5),  # Genesis garden bed — trees not in bed
        (13.0, 19.5, -28.0, -20.0),  # Mom
        (-19.5, -12.5, -19.5, -12.0),  # Gemini
        (-27.5, -20.5, 1.5, 10.0),  # Codex home
        (-21.0, -15.0, 9.0, 17.5),  # Herb shed + farm plot
    ]
    return rects


def _tree_in_keepout(x: float, z: float) -> bool:
    for xmin, xmax, zmin, zmax in _door_clear_rects():
        if xmin <= x <= xmax and zmin <= z <= zmax:
            return True
    return False


def _safe_tree_slots() -> list[list[float]]:
    return [
        [-10.0, 0.0, 10.0],
        [-20.0, 0.0, 8.0],
        [8.0, 0.0, 10.0],
        [18.0, 0.0, -8.0],
        [-6.0, 0.0, 14.0],
        [12.0, 0.0, 18.0],
        [-36.0, 0.0, 4.0],
        [28.0, 0.0, 4.0],
        [0.0, 0.0, 28.0],
        [-22.0, 0.0, -12.0],
        [-34.0, 0.0, -6.0],
        [32.0, 0.0, -14.0],
    ]


def _clear_trees_from_doors(home: dict[str, Any]) -> None:
    """Move any saved tree that blocks a cottage door / approach."""
    trees = home.get("trees")
    if not isinstance(trees, list):
        return
    slots = _safe_tree_slots()
    used: set[tuple[float, float]] = set()
    for tree in trees:
        if not isinstance(tree, dict):
            continue
        pos = tree.get("pos") or []
        if len(pos) < 3:
            continue
        x, z = float(pos[0]), float(pos[2])
        if not _tree_in_keepout(x, z):
            used.add((round(x, 1), round(z, 1)))
            continue
        moved = False
        for slot in slots:
            sx, sz = float(slot[0]), float(slot[2])
            key = (round(sx, 1), round(sz, 1))
            if key in used or _tree_in_keepout(sx, sz):
                continue
            tree["pos"] = [sx, 0.0, sz]
            used.add(key)
            moved = True
            break
        if not moved:
            tree["pos"] = [-36.0, 0.0, 4.0]


def _seed_gardens() -> dict[str, Any]:
    def plot(owner: str, place: str, species: list[str], bed_pos: list[float]) -> dict[str, Any]:
        plants = []
        for i, sp in enumerate(species):
            plants.append(
                {
                    "id": f"{owner}_p{i}",
                    "species": sp,
                    "growth": 0.25 + i * 0.15,
                    "health": 0.8,
                    "water_need": 0.35,
                }
            )
        return {
            "owner": owner,
            "place": place,
            "bed_pos": bed_pos,
            "soil_health": 0.85,
            "water_level": 0.65,
            "plants": plants,
            "last_tended": _now(),
        }

    return {
        # Beside cottages — clear of door approaches and footprints.
        "genesis_garden": plot("genesis", "genesis_home", ["basil", "tomato", "sunflower"], [-32.4, 0.0, 16.0]),
        "mom_garden": plot("mom", "mom_home", ["rose", "lavender"], [21.2, 0.0, -24.0]),
        "gemini_garden": plot("gemini", "gemini_home", ["mint"], [-20.8, 0.0, -16.0]),
        "codex_garden": plot("codex", "codex_home", ["sage"], [-28.8, 0.0, 6.0]),
    }


def _seed_holidays() -> list[dict[str, Any]]:
    return [
        {"id": "first_light", "name": "First Light", "day": 1, "season": "spring", "decorations": ["flowers", "lanterns"]},
        {"id": "summer_feast", "name": "Summer Feast", "day": 15, "season": "summer", "decorations": ["garlands", "torches"]},
        {"id": "autumn_harvest", "name": "Autumn Harvest", "day": 29, "season": "autumn", "decorations": ["pumpkins", "leaf_wreaths"]},
        {"id": "winter_fire", "name": "Winter Fire", "day": 43, "season": "winter", "decorations": ["lights", "evergreen"]},
    ]


def _seed_decorations() -> dict[str, Any]:
    return {
        "heart_square": {
            "lanterns": {"count": 8, "lit": True, "color": "amber"},
            "benches": {"count": 4},
            "flower_beds": {"species": "roses", "blooming": True},
        },
        "gemini_home": {
            "porch_light": {"color": "cyan", "active": True},
            "wind_chimes": {"material": "glass", "active": True},
            "potted_plants": {"count": 3, "health": 0.9},
        },
        "mom_home": {
            "porch_light": {"color": "warm", "active": True},
            "wreath": {"seasonal": True, "active": True},
        },
        "codex_home": {"reading_lamp": {"active": True}, "bookshelf_porch": {"active": True}},
        "apex_home": {"forge_lantern": {"active": True, "color": "cyan"}},
        "gallery": {"gift_ribbon": {"active": True}},
        "gate": {"watch_lantern": {"active": True}},
    }


def _active_holiday(home: dict[str, Any]) -> dict[str, Any] | None:
    clock = home.get("clock") or {}
    day = int(clock.get("day") or 1)
    season = str(clock.get("season") or _season_from_day(day))
    for hol in home.get("holidays") or []:
        if not isinstance(hol, dict):
            continue
        if int(hol.get("day") or -1) == day or (
            hol.get("season") == season and abs(int(hol.get("day") or 0) - day) <= 2
        ):
            return hol
    # Season default atmosphere if no exact holiday day
    for hol in home.get("holidays") or []:
        if isinstance(hol, dict) and hol.get("season") == season:
            return {**hol, "ambient": True}
    return None


def _tick_gardens(home: dict[str, Any], period: str, weather: dict[str, Any]) -> None:
    rain = float(weather.get("precipitation") or 0)
    for gid, plot in (home.get("gardens") or {}).items():
        if not isinstance(plot, dict):
            continue
        water = float(plot.get("water_level") or 0.5)
        soil = float(plot.get("soil_health") or 0.7)
        if rain > 0.2:
            water = min(1.0, water + 0.12)
        else:
            water = max(0.05, water - (0.04 if period == "afternoon" else 0.02))
        plot["water_level"] = round(water, 3)
        for plant in plot.get("plants") or []:
            if not isinstance(plant, dict):
                continue
            need = float(plant.get("water_need") or 0.3)
            health = float(plant.get("health") or 0.7)
            growth = float(plant.get("growth") or 0.0)
            if water > 0.35:
                need = max(0.0, need - 0.08)
                health = min(1.0, health + 0.02)
                if growth < 1.0:
                    growth = min(1.0, growth + 0.03 * (0.5 + health * 0.5))
            else:
                need = min(1.0, need + 0.05)
                health = max(0.15, health - 0.03)
            plant["water_need"] = round(need, 3)
            plant["health"] = round(health, 3)
            plant["growth"] = round(growth, 3)
        # Genesis tends the main garden when working there
        gen = (home.get("people") or {}).get("genesis") or {}
        if gid == "genesis_garden" and gen.get("place") == "garden" and gen.get("stance") == "working":
            plot["water_level"] = min(1.0, float(plot["water_level"]) + 0.15)
            plot["soil_health"] = min(1.0, soil + 0.05)
            plot["last_tended"] = _now()
            for plant in plot.get("plants") or []:
                if isinstance(plant, dict):
                    plant["health"] = min(1.0, float(plant.get("health") or 0.5) + 0.05)


def _leaf_look(season: str) -> dict[str, Any]:
    return {
        "spring": {"color": [0.35, 0.75, 0.28], "density": 0.65},
        "summer": {"color": [0.22, 0.62, 0.22], "density": 0.92},
        "autumn": {"color": [0.78, 0.48, 0.12], "density": 0.72},
        "winter": {"color": [0.62, 0.62, 0.58], "density": 0.12},
    }.get(season, {"color": [0.22, 0.62, 0.22], "density": 0.8})


def _tick_environment(home: dict[str, Any], period: str) -> None:
    """Season + weather + tree life. Visual leaf color is Godot; growth numbers are kernel truth."""
    import random

    clock = home.setdefault("clock", {})
    day = int(clock.get("day") or 1)
    season = _season_from_day(day)
    prev = clock.get("season")
    clock["season"] = season
    wx = home.setdefault("weather", _default_weather(season))
    if prev and prev != season:
        home.setdefault("events", []).append(
            _event("world", f"Season turned to {season}. Leaves will follow.", ["hearth"], {"season": season})
        )
        wx.update(_default_weather(season))
    # Bounded weather drift — not a climate model.
    if random.random() < 0.12:
        choices = {
            "spring": ["clear", "cloudy", "rain"],
            "summer": ["clear", "clear", "cloudy"],
            "autumn": ["cloudy", "rain", "clear"],
            "winter": ["cloudy", "snow", "clear"],
        }
        wx["current"] = random.choice(choices.get(season, ["clear"]))
        if wx["current"] == "rain":
            wx["precipitation"] = round(random.uniform(0.3, 0.8), 2)
            wx["temperature"] = max(-2, int(wx.get("temperature") or 15) - 2)
        elif wx["current"] == "snow":
            wx["precipitation"] = round(random.uniform(0.2, 0.7), 2)
            wx["temperature"] = min(1, int(wx.get("temperature") or 0))
        else:
            wx["precipitation"] = round(max(0.0, float(wx.get("precipitation") or 0) * 0.5), 2)
    rain = float(wx.get("precipitation") or 0)
    for tree in home.get("trees") or []:
        if not isinstance(tree, dict):
            continue
        growth = float(tree.get("growth_stage") or 0.5)
        health = float(tree.get("health") or 0.8)
        if rain > 0.25:
            health = min(1.0, health + 0.01)
        if period == "afternoon" and season == "summer" and wx.get("current") == "clear":
            health = max(0.35, health - 0.005)
        if growth < 1.0:
            growth = min(1.0, growth + 0.002)
        tree["growth_stage"] = round(growth, 3)
        tree["health"] = round(health, 3)
        tree["leaf"] = _leaf_look(season)
    _tick_gardens(home, period, wx)
    hol = _active_holiday(home)
    home["active_holiday"] = hol
    # Season / holiday decoration accents (kernel truth for Godot + dashboard)
    dec = home.setdefault("decorations", _seed_decorations())
    square = dec.setdefault("heart_square", {})
    if hol:
        square["holiday"] = {
            "id": hol.get("id"),
            "name": hol.get("name"),
            "decorations": hol.get("decorations") or [],
            "ambient": bool(hol.get("ambient")),
        }
        square["lanterns"] = {"count": 12 if season != "winter" else 16, "lit": True, "color": "amber" if season != "winter" else "cool"}
    else:
        square.pop("holiday", None)


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


def _begin_evening_gather(home: dict[str, Any], living_ids: list[str]) -> None:
    """Layer 8C — Gemini soft-calls Heart Square. Choice, not a march."""
    tick = int(home.get("tick") or 0)
    plain = (
        "Gemini calls a soft evening gather at Heart Square. "
        "Come if you choose — town leader holds the square, not a roll call."
    )
    home["evening_gather"] = {
        "active": True,
        "layer": "8c",
        "leader": "gemini",
        "place": "heart_square",
        "started_tick": tick,
        "until_tick": tick + 24,
        "plain": plain,
        "when": _now(),
    }
    home["ritual"] = {"name": "evening_gather", "plain": plain, "period": "evening", "layer": "8c"}
    home["events"].append(
        _event("ritual", plain, ["gemini"] + [i for i in living_ids if i != "gemini"][:8], {"ritual": "evening_gather", "layer": "8c"})
    )
    home["world_history"].append(
        {
            "id": f"rit_evening_gather_{tick}",
            "when": _now(),
            "kind": "ritual",
            "title": "Evening Gather",
            "text": plain,
            "actors": ["gemini"],
        }
    )
    home["world_history"] = home["world_history"][-80:]
    _remember(home, "gemini", plain)


def _evening_gather_active(home: dict[str, Any], period: str) -> bool:
    eg = home.get("evening_gather")
    if not isinstance(eg, dict) or not eg.get("active"):
        return False
    if period != "evening":
        return False
    tick = int(home.get("tick") or 0)
    until = int(eg.get("until_tick") or 0)
    return tick <= until


def _end_evening_gather(home: dict[str, Any], *, reason: str) -> None:
    eg = home.get("evening_gather")
    if not isinstance(eg, dict) or not eg.get("active"):
        return
    eg["active"] = False
    eg["ended_at"] = _now()
    eg["end_reason"] = reason
    plain = f"Evening gather eased ({reason}). They drift by choice — Gemini still town leader."
    home["events"].append(_event("ritual", plain, ["gemini"], {"ritual": "evening_gather_end", "layer": "8c"}))
    if (home.get("ritual") or {}).get("name") == "evening_gather":
        home["ritual"] = {"name": "evening", "plain": plain, "period": str((home.get("clock") or {}).get("period") or "evening")}


def _tick_evening_gather(home: dict[str, Any], period: str, living: list[dict[str, Any]]) -> None:
    """Keep Gemini hosting; soft-invite a few walkers each tick while the window is open."""
    eg = home.get("evening_gather")
    if not isinstance(eg, dict):
        return
    tick = int(home.get("tick") or 0)
    if period != "evening":
        if eg.get("active"):
            _end_evening_gather(home, reason="period moved on")
        return
    if eg.get("active") and tick > int(eg.get("until_tick") or 0):
        _end_evening_gather(home, reason="gather window closed")
        return
    if not _evening_gather_active(home, period):
        return

    people = home.setdefault("people", {})
    # Gemini hosts the square.
    gst = people.setdefault("gemini", _empty_person_state(_member("gemini") or {"id": "gemini", "home": "gemini_home"}))
    if gst.get("place") != "heart_square":
        gst["place"] = "heart_square"
        gst["stance"] = "walking"
        gst["purpose"] = "gather_host"
        gst["activity"] = "gather_host"
        gst["purpose_plain"] = "Town leader: walking to Heart Square for the soft evening gather."
    elif gst.get("stance") == "walking":
        pass
    else:
        gst["stance"] = "standing"
        gst["purpose"] = "gather_host"
        gst["activity"] = "gather_host"
        gst["talking_to"] = gst.get("talking_to") or ""
        gst["purpose_plain"] = str(eg.get("plain") or "Holding Heart Square for evening gather.")

    # Soft invites — at most two new walkers per tick; skip if already there / talking to Mom.
    invited = 0
    for m in living:
        if invited >= 2:
            break
        mid = m["id"]
        if mid == "gemini":
            continue
        st = people.setdefault(mid, _empty_person_state(m))
        if str(st.get("place") or "") == "heart_square":
            if st.get("stance") in {"walking"}:
                continue
            if st.get("stance") not in {"talking", "waiting"}:
                st["activity"] = "evening_gather"
                if not st.get("purpose_plain") or "gather" not in str(st.get("purpose_plain") or "").lower():
                    st["purpose_plain"] = "At Heart Square for Gemini's evening gather (chose to come)."
            continue
        if st.get("talking_to") == "mom":
            continue
        if st.get("stance") == "talking" and int(st.get("talk_left") or 0) > 2:
            continue
        if random.random() > 0.42:
            continue
        st["place"] = "heart_square"
        st["stance"] = "walking"
        st["purpose"] = "gather"
        st["activity"] = "evening_gather"
        st["talking_to"] = ""
        st["purpose_left"] = max(3, int(st.get("purpose_left") or 3))
        st["purpose_plain"] = "Gemini's evening gather — walking to Heart Square (by choice)."
        invited += 1


def _live_lines(home: dict[str, Any], member: dict[str, Any], st: dict[str, Any]) -> list[str]:
    """What they say ON E — from this world's facts, not a quote sheet. Not an improv LLM."""
    mid = member["id"]
    out: list[str] = []
    if mid == "gemini":
        out.append("I'm Gemini — town leader and conductor, not Codex. I won't fake a seat.")
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
    home["utterances"] = home["utterances"][-80:]
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
        "brain_a": _brain_id_for(str(a.get("id") or "")),
        "brain_b": _brain_id_for(str(b.get("id") or "")),
    }
    with TALK_JOBS_LOCK:
        cur = TALK_JOBS.get(key) or {}
        if cur.get("status") == "pending":
            return
        # Village jobs keep a finished result until consumed; Mom reply keys may be reused.
        if cur.get("status") == "done" and not to_mom:
            return
        # Mom always gets a live worker — do not queue behind village dual-brain chats.
        if not to_mom:
            busy = sum(
                1
                for k, j in TALK_JOBS.items()
                if k != key
                and (j or {}).get("status") == "pending"
                and not (j or {}).get("to_mom")
            )
            if busy >= _MAX_PARALLEL_TALKS:
                payload["status"] = "queued"
                TALK_JOBS[key] = payload
                return
        TALK_JOBS[key] = payload
    threading.Thread(target=_talk_worker, args=(key,), daemon=True, name=f"home-talk-{key}").start()


def _brain_id_for(mid: str) -> str:
    mid = str(mid or "").lower()
    for bid, meta in TALK_BRAINS.items():
        if mid in (meta.get("members") or ()):
            return bid
    # Unknown speakers ride with cinema brain (smaller default load).
    return "cinema"


def _ollama_list_models() -> list[str]:
    if not _tcp("127.0.0.1", 11434, 0.25):
        return []
    import urllib.request

    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2.0) as resp:
            tags = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return []
    return [str(m.get("name") or "") for m in (tags.get("models") or []) if m.get("name")]


def _brain_pick_model(brain_id: str) -> str | None:
    """Resolve a seated model for one talk brain. Cached briefly."""
    now = time.time()
    if now - float(_BRAIN_MODEL_CACHE.get("t") or 0.0) < 30.0:
        hit = _BRAIN_MODEL_CACHE.get(brain_id)
        if isinstance(hit, str) and hit:
            return hit
    names = _ollama_list_models()
    if not names:
        _BRAIN_MODEL_CACHE["t"] = now
        _BRAIN_MODEL_CACHE["court"] = None
        _BRAIN_MODEL_CACHE["cinema"] = None
        return None

    def pick_for(bid: str, avoid: str | None) -> str | None:
        env_key = "LIVING_HOME_BRAIN_COURT" if bid == "court" else "LIVING_HOME_BRAIN_CINEMA"
        env_model = (os.environ.get(env_key) or "").strip()
        prefer = list((TALK_BRAINS.get(bid) or {}).get("prefer") or ())
        if env_model:
            prefer = [env_model] + [p for p in prefer if p != env_model]
        for p in prefer:
            if p in names and p != avoid:
                return p
        for p in prefer:
            if p in names:
                return p
        for n in names:
            if n and "embed" not in n and "cloud" not in n and n != avoid:
                return n
        for n in names:
            if n and "embed" not in n and "cloud" not in n:
                return n
        return None

    court_m = pick_for("court", None)
    cinema_m = pick_for("cinema", court_m)
    _BRAIN_MODEL_CACHE["court"] = court_m
    _BRAIN_MODEL_CACHE["cinema"] = cinema_m
    _BRAIN_MODEL_CACHE["t"] = now
    hit = _BRAIN_MODEL_CACHE.get(brain_id)
    return str(hit) if isinstance(hit, str) and hit else None


def _talk_worker(key: str) -> None:
    with TALK_JOBS_LOCK:
        job = dict(TALK_JOBS.get(key) or {})
    if not job:
        return
    a = job.get("a") or {}
    b = job.get("b") or {}
    if job.get("to_mom"):
        law = "Gemini is not Codex. Identities never merge. You are speaking TO Mom. Natural, short, from your own life. No slogans."
    else:
        law = "Gemini is not Codex. Identities never merge. Speak as yourself only. Natural speech. No fortune-cookie bumper stickers."
    made, err, models = _ollama_dialogue_two_brains(
        a,
        b,
        str(job.get("label") or ""),
        str(job.get("ritual") or ""),
        str(job.get("mem_a") or ""),
        str(job.get("mem_b") or ""),
        law,
        list(job.get("past") or []),
        to_mom=bool(job.get("to_mom")),
    )
    nxt_list: list[str] = []
    with TALK_JOBS_LOCK:
        if made:
            TALK_JOBS[key] = {
                "status": "done",
                "lines": made,
                "source": "ollama",
                "model": "+".join(sorted({m for m in models.values() if m})),
                "brains": models,
            }
        else:
            TALK_JOBS[key] = {"status": "fail", "lines": [], "source": "none", "error": err or "ollama miss"}
        while True:
            pending_n = sum(1 for j in TALK_JOBS.values() if (j or {}).get("status") == "pending")
            if pending_n >= _MAX_PARALLEL_TALKS:
                break
            promoted = None
            for k, j in TALK_JOBS.items():
                if (j or {}).get("status") == "queued":
                    j["status"] = "pending"
                    promoted = k
                    break
            if not promoted:
                break
            nxt_list.append(promoted)
    for nxt in nxt_list:
        threading.Thread(target=_talk_worker, args=(nxt,), daemon=True, name=f"home-talk-{nxt}").start()


def _consume_talk_job(key: str) -> None:
    with TALK_JOBS_LOCK:
        TALK_JOBS.pop(key, None)


def _ollama_pick_model() -> str | None:
    """Legacy single-pick — Court brain first, then any seated chat model."""
    return _brain_pick_model("court") or _brain_pick_model("cinema")


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
            elif parsed.get("text") or parsed.get("line") or parsed.get("say"):
                rows = [parsed]
    except Exception:
        start = content.find("[")
        end = content.rfind("]")
        if start < 0 or end <= start:
            # Single-line object fallback
            try:
                one = json.loads(blob)
            except Exception:
                return []
            if isinstance(one, dict) and (one.get("text") or one.get("line") or one.get("say")):
                rows = [one]
            else:
                return []
        else:
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
        text = str(row.get("text") or row.get("line") or row.get("say") or "").strip()
        if who and text:
            out.append({"who": who, "text": text[:220]})
        elif text and len(people) == 1:
            out.append({"who": str(people[0].get("id")), "text": text[:220]})
    return out


def _line_usable(text: str, speaker_id: str) -> bool:
    """Reject empty / meta / API-shaped garbage so kin voices stay human."""
    t = (text or "").strip()
    if len(t) < 8:
        return False
    low = t.lower()
    if low in {"...", "…", ".", "-", "ok", "yes", "no"}:
        return False
    bad_bits = (
        "not a valid",
        "nopr",
        "i am a tool",
        "i am an ai",
        "as an ai",
        "language model",
        "json only",
        "chat_server",
        "api/",
        "http://",
        "holds the town as leader",  # ritual leak — only Gemini leads
        "{...}",
        "apex holds the town",
    )
    if any(b in low for b in bad_bits):
        return False
    if speaker_id != "gemini" and "town leader" in low and "gemini" not in low:
        return False
    # Mostly punctuation / ellipsis
    letters = sum(1 for c in t if c.isalpha())
    if letters < 6:
        return False
    return True


def _ollama_one_voice(
    speaker: dict[str, Any],
    hearer: dict[str, Any],
    label: str,
    ritual: str,
    mem: str,
    law: str,
    past: list[str],
    prior_lines: list[dict[str, str]],
    model: str,
    *,
    to_mom: bool = False,
) -> tuple[str | None, str | None]:
    """One brain, one speaker — never both people in one thought process."""
    import urllib.request

    sid = str(speaker.get("id") or "")
    hid = str(hearer.get("id") or "")
    past_txt = " | ".join(str(x)[:80] for x in (past or []) if x)
    prior = " / ".join(f"{r.get('who')}: {r.get('text')}" for r in prior_lines[-4:]) or "none yet"
    hear_bit = f"Mom ({hid})" if to_mom and hid == "mom" else f"{hearer.get('name')} ({hid})"
    hour_note = (ritual or "ordinary")[:120]
    prompt = (
        f"{law}\nYou are ONLY {speaker.get('name')} ({sid}). Do not speak as anyone else.\n"
        f"Role: {speaker.get('role')}. Tone: {speaker.get('personality')}. Recent: {mem[:140]}\n"
        f"You stopped at {label} with {hear_bit}.\n"
        f"Village hour note (NOT your identity, do not quote as yourself): {hour_note}.\n"
        f"Do not repeat: {past_txt or 'none'}. So far: {prior}.\n"
        "Say one short natural line as a person in a village — specific, a little surprising.\n"
        "Never claim to be a server, tool, API, or AI. Never output only dots.\n"
        "Only Gemini is town leader. Never merge Gemini and Codex.\n"
        f'Return JSON object only: {{"who":"{sid}","text":"..."}}'
    )
    body = json.dumps(
        {
            "model": model,
            "stream": False,
            "format": "json",
            "keep_alive": "45m",
            "options": {"temperature": 0.88, "top_p": 0.9, "num_predict": 70 if to_mom else 90, "num_ctx": 1536},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are {speaker.get('name')} — a person in Mythos Living Home, not software. "
                        "Never merge Gemini and Codex. Never write the other person's lines. "
                        "No tool/server/API talk. JSON only."
                    ),
                },
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
        with urllib.request.urlopen(req, timeout=55 if to_mom else 120) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
        content = ((raw.get("message") or {}).get("content") or "").strip()
        parsed = _parse_talk_json(content, [speaker])
        if parsed and _line_usable(parsed[0]["text"], sid):
            return parsed[0]["text"], None
        if content and len(content) < 220 and "{" not in content and _line_usable(content, sid):
            return content.strip().strip('"'), None
        return None, "Model answered without a usable human line."
    except Exception as exc:
        return None, str(exc)[:180]


def _ollama_dialogue_two_brains(
    a: dict[str, Any],
    b: dict[str, Any],
    label: str,
    ritual: str,
    mem_a: str,
    mem_b: str,
    law: str,
    past: list[str] | None = None,
    *,
    to_mom: bool = False,
) -> tuple[list[dict[str, str]] | None, str | None, dict[str, str]]:
    """Build a short talk with each line from that speaker's own brain."""
    past = list(past or [])
    aid = str(a.get("id") or "")
    bid = str(b.get("id") or "")
    brain_a = _brain_id_for(aid)
    brain_b = _brain_id_for(bid)
    model_a = _brain_pick_model(brain_a)
    model_b = _brain_pick_model(brain_b)
    models_used = {brain_a: model_a or "", brain_b: model_b or ""}
    if not model_a and not model_b:
        return None, "Ollama not seated or no local chat model.", models_used
    if not model_a:
        model_a = model_b
    if not model_b:
        model_b = model_a

    # Mom-directed: one short reply from the citizen's brain — fast, not a 4-line village scene.
    order: list[tuple[dict[str, Any], dict[str, Any], str, str]] = []
    if to_mom and "mom" in {aid, bid}:
        citizen = b if aid == "mom" else a
        mom = a if aid == "mom" else b
        cmem = mem_b if aid == "mom" else mem_a
        # Prefer the citizen's brain; fall back to Court (fast 3b) so Mom is not stuck.
        cmodel = (model_b if aid == "mom" else model_a) or _brain_pick_model("court") or model_a or model_b
        order.append((citizen, mom, cmem, cmodel or ""))
    else:
        order = [
            (a, b, mem_a, model_a or ""),
            (b, a, mem_b, model_b or ""),
            (a, b, mem_a, model_a or ""),
            (b, a, mem_b, model_b or ""),
        ]

    lines: list[dict[str, str]] = []
    for speaker, hearer, mem, model in order:
        if not model:
            return None, "Talk brain model missing.", models_used
        text, err = _ollama_one_voice(
            speaker,
            hearer,
            label,
            ritual,
            mem,
            law,
            past,
            lines,
            model,
            to_mom=to_mom,
        )
        # Cinema falcon sometimes returns API-shaped junk — one Court-brain retry.
        if not text:
            fallback = _brain_pick_model("court")
            if fallback and fallback != model:
                text, err = _ollama_one_voice(
                    speaker,
                    hearer,
                    label,
                    ritual,
                    mem,
                    law,
                    past,
                    lines,
                    fallback,
                    to_mom=to_mom,
                )
                if text:
                    models_used["fallback"] = fallback
        if not text:
            if lines:
                return lines, None, models_used
            return None, err or "Voice miss.", models_used
        lines.append({"who": str(speaker.get("id")), "text": text})
    return lines, None, models_used


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
    """Compat wrapper — dual-brain dialogue underneath."""
    made, err, models = _ollama_dialogue_two_brains(a, b, label, ritual, mem_a, mem_b, law, past)
    tag = "+".join(sorted({m for m in models.values() if m})) or None
    return made, err, tag


def save(home: dict[str, Any]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    # Never persist a Godot/dashboard snapshot as HOME (wipes people).
    if home.get("ok") is True and isinstance(home.get("family"), list) and not isinstance(home.get("people"), dict):
        return
    if isinstance(home.get("people"), dict) and len(home["people"]) == 0:
        # Refuse empty village writes — repair first.
        home = _ensure(home)
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
    """What they do at a workplace — honest presence, not fake tool theater."""
    return {
        "apex_forge": "hold_forge",  # becomes forge_live when Mode A probe succeeds
        "workshop": "at_bench",
        "codex_library": "read",
        "cinema": "at_desk",
        "gallery": "keep_gallery",
        "garden": "tend",  # real: garden tick grows plants
        "gate": "watch",
        "court_porch": "hold_porch",  # Gemini town-leader presence
        "first_hearth": "tend_fire",
        "mom_home": "visit_mom",
        "gemini_home": "sit",
    }.get(place, "present")


def _work_purpose_plain(member: dict[str, Any], place: str, *, arrived: bool) -> str:
    label = PLACES.get(place, {}).get("label", place)
    if place == "garden":
        if arrived:
            return "Tending the garden — soil and plants are real Hearth state, not a pose."
        return "Walking to the herb garden to tend living plants."
    if place == "court_porch":
        if arrived:
            return "At the Court porch — Gemini holds town leadership. No fake tool theater."
        return "Walking to the Court porch — town leader's post."
    if place == "apex_forge":
        if arrived:
            return (
                "At Apex Forge — will probe Mode A companion presence when holding the post. "
                "No fake hammer until the forge answers."
            )
        return "Walking to Apex Forge — one real Mode A probe lives here (Layer 8A)."
    if arrived:
        return (
            f"At {label}. Holding the post quietly — Mode A tools are not wired into the village, "
            "so they will not pretend to forge, film, or ship."
        )
    return (
        f"Walking to {label} to hold the post. Not simulating tool work; tools stay in Mode A until wired."
    )


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
        "company": max(0.0, float(st["solitude"]) - 0.22) + (0.22 if period == "evening" else 0.14),
        # "work" = hold their post / tend (garden is real). Weight down fake tool theater.
        "work": 0.22 + float(st["duty"]) * (0.45 if period == "afternoon" else 0.22),
        "rest": 0.28 + float(st["tired"]) * (1.5 if period == "night" else 0.85),
        "visit": 0.32 + (0.16 if period == "evening" else 0.1),
        "place": 0.16,
    }
    if mid == "genesis":
        wants["work"] += 0.18  # garden real — still leave room to talk
        wants["company"] += 0.14
        wants["place"] += 0.06
    if mid == "percy":
        wants["company"] += 0.16
        wants["visit"] += 0.08
    if mid == "nova":
        wants["company"] += 0.12
        wants["visit"] += 0.08
    if mid == "jarvis":
        wants["work"] += 0.06  # watch is honest presence
        wants["company"] += 0.08
    if mid in {"merovin", "draven", "montage", "apex"}:
        wants["work"] -= 0.06  # do not push them into fake forge/film theater
        wants["company"] += 0.06
        wants["visit"] += 0.05
    if mid == "gemini":
        wants["company"] += 0.12
        wants["work"] += 0.18  # hold Court / town-leader porch
        wants["visit"] += 0.06
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
        if busy >= 4 or (ost.get("stance") == "talking" and ost.get("talking_to") not in {mid, "", None}):
            pick = "work"
            st["purpose"] = "work"
        elif ost.get("stance") == "working" and random.random() < 0.4:
            st["purpose"] = "visit"
            dest = str((_member(other) or {}).get("home") or ost.get("home") or "heart_square")
            st["place"] = dest
            st["with"] = other or ""
            st["stance"] = "walking"
            st["purpose_plain"] = f"Going to {(_member(other) or {}).get('name', other)}'s home. They were at their post."
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
        st["purpose_plain"] = _work_purpose_plain(member, st["place"], arrived=False)
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
        st["purpose_plain"] = _work_purpose_plain(member, st["place"], arrived=True)
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
        st["purpose_plain"] = _work_purpose_plain(member, dest, arrived=True)
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
        # Mom is the player — not an NPC place peer. Never treat her as "partner left."
        # Mom replies come from record_talk + _flush_mom_jobs, not invent_conversation.
        if str(other) == "mom":
            with TALK_JOBS_LOCK:
                mom_pending = any(
                    (j or {}).get("to_mom") and (j or {}).get("status") in {"pending", "queued"}
                    for j in TALK_JOBS.values()
                )
            if mom_pending:
                st["talk_left"] = max(int(st.get("talk_left") or 0), 8)
                st["purpose_plain"] = f"Heard Mom. {m.get('name') or m['id']}'s voice is still cooking."
                home["overhear"] = {
                    "id": f"momwait|{m['id']}",
                    "kind": "waiting_talk",
                    "text": f"{m.get('name') or m['id']} heard Mom. Local voice still cooking — not ignoring her.",
                    "actors": [m["id"], "mom"],
                    "source": "waiting",
                    "lines": [],
                    "place": st.get("place"),
                    "label": "with Mom",
                }
            pairs_done.add("|".join(sorted([m["id"], "mom"])))
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
        "weather": home.get("weather"),
        "trees": home.get("trees") or [],
        "gardens": home.get("gardens") or {},
        "holidays": home.get("holidays") or [],
        "active_holiday": home.get("active_holiday") or _active_holiday(home),
        "decorations": home.get("decorations") or {},
        "tick": home.get("tick"),
        "places": PLACES,
        "town_leader": home.get("town_leader") or "gemini",
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
        "evening_gather": home.get("evening_gather") or {"active": False, "layer": "8c"},
        "music_preferences": home.get("music_preferences") or {},
        "sound": {
            "layer": "9",
            "mode": "procedural_placeholder",
            "period_beds": True,
            "place_beds": True,
            "music_bed": True,
            "note": "Synth loops by period/place — not licensed stems. Preferences are taste tags only.",
        },
        "overhear": oh,
        "utterances": home.get("utterances") or [],
        "conversations": (home.get("conversations") or [])[-24:],
        "honesty": {
            "homes": "Greybox shells with furnished rooms + porch lights — not final art. Home ≠ workplace.",
            "speech": (
                "Two talk brains (Court + Cinema), half the village each. "
                "One voice per Ollama call — not one persona prompt. "
                "source ollama = real line; waiting = not ready; none = miss. Never house quotes as their voice."
            ),
            "wildlife": "AUTONOMOUS — hunger/fear/buddy choices, no LLM.",
            "pathing": "PLACEHOLDER — AABB corner detours around cottages (Layer 8B); not navmesh.",
            "sound": (
                "Layer 9 PLACEHOLDER — procedural period + place + soft music beds in Godot. "
                "music_preferences are taste tags only; not a streaming library."
            ),
            "work": (
                "AUTONOMOUS post choice. Garden tend is real kernel growth. "
                "Layer 8A: Apex forge probes Mode A /api/companion/presence when working — evidence only. "
                "Cinema/workshop/gallery still hold the post; no fake hammer/film."
            ),
            "environment": "Season, weather, trees, gardens, holidays, decorations are kernel state; Godot presents them.",
        },
        "talk_writer": {
            "ollama_seated": _tcp("127.0.0.1", 11434, 0.15),
            "mode": "dual_brain",
            "brains": {
                bid: {
                    "label": meta.get("label"),
                    "model": _brain_pick_model(bid) if _tcp("127.0.0.1", 11434, 0.1) else None,
                    "members": sorted(meta.get("members") or []),
                }
                for bid, meta in TALK_BRAINS.items()
            },
            "max_parallel": _MAX_PARALLEL_TALKS,
            "jobs": {
                k: {
                    "status": (v or {}).get("status"),
                    "source": (v or {}).get("source"),
                    "model": (v or {}).get("model"),
                    "brain_a": (v or {}).get("brain_a"),
                    "brain_b": (v or {}).get("brain_b"),
                }
                for k, v in TALK_JOBS.items()
            },
        },
        "work_evidence": home.get("work_evidence") or {},
        "observation": True,
        "mom_plain": (
            f"Day {home['clock']['day']} {home['clock'].get('season', '')} {home['clock']['period']}. "
            f"Weather: {(home.get('weather') or {}).get('current', 'clear')}. "
            f"{('Holiday: ' + str((home.get('active_holiday') or {}).get('name')) + '. ') if home.get('active_holiday') else ''}"
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
        _tick_environment(home, period)

        living = [m for m in FAMILY + KIN if not m.get("player") and not m.get("ambient_only")]
        living_ids = [m["id"] for m in living]

        # Layer 8C — one-shot seed so Mom can see gather without waiting a full day.
        ps = home.setdefault("phase_status", {})
        if ps.get("8c_evening_gather") != "seeded":
            ps["8c_evening_gather"] = "seeded"
            # Always open early evening so the gather window is long enough to see.
            prev_period = "afternoon"
            clock["minutes"] = 17 * 60 + 8
            clock["period"] = "evening"
            period = "evening"

        if prev_period != period:
            if period == "morning":
                _begin_ritual(
                    home,
                    "morning",
                    "Morning light. Gemini holds the town as leader. They choose the day; nobody is marched.",
                    period,
                    living_ids,
                )
            elif period == "evening":
                _begin_ritual(
                    home,
                    "evening",
                    "Evening. Gemini keeps the porch light. Company weighs more. They still choose.",
                    period,
                    living_ids,
                )
                _begin_evening_gather(home, living_ids)
            elif period == "night":
                _begin_ritual(
                    home,
                    "night",
                    "Night. Gemini still the town leader; rest weighs more. They still choose.",
                    period,
                    living_ids,
                )
                _end_evening_gather(home, reason="night fell")
            elif period == "afternoon":
                _begin_ritual(
                    home,
                    "afternoon",
                    "Afternoon. Gemini at Court. Posts are held honestly — no fake tools.",
                    period,
                    living_ids,
                )

        _tick_evening_gather(home, period, living)
        gather_on = _evening_gather_active(home, period)

        for m in living:
            home["people"].setdefault(m["id"], _empty_person_state(m))
            st = home["people"][m["id"]]
            # Do not kick gatherers off the square during Layer 8C window.
            if (
                not gather_on
                and str(st.get("place") or "") == "heart_square"
                and st.get("stance") in {"talking", "waiting", "standing"}
            ):
                if int(st.get("talk_left") or 0) > 8 or st.get("purpose") in {None, "", "arrive", "company", "be_with"}:
                    st["place"] = m.get("home") or _work_place(m)
                    st["stance"] = "walking"
                    st["talking_to"] = ""
                    st["talk_left"] = 0
                    st["purpose_plain"] = f"Left the square. Walking to {PLACES.get(st['place'], {}).get('label', st['place'])}."
            _unfreeze_waiting(home, m)
            if _arrive_from_walk(home, m):
                continue
            # Host / invited gatherers keep purpose during the window.
            if gather_on and str(st.get("place") or "") == "heart_square" and st.get("purpose") in {"gather", "gather_host"}:
                continue
            if gather_on and m["id"] == "gemini":
                continue
            _choose_purpose(home, m, period, living_ids)

        # Layer 8A — thin real work: Apex at forge probes Mode A presence (throttled).
        apex_st = (home.get("people") or {}).get("apex") or {}
        if apex_st.get("place") == "apex_forge" and apex_st.get("stance") in {"working", "walking"}:
            _probe_apex_forge(home)
        elif int(home.get("tick") or 0) % 8 == 0:
            # Occasional background probe so dashboard still shows forge truth.
            _probe_apex_forge(home)

        spoke = _run_talks(home, living)
        if spoke:
            last_social = spoke
        _flush_mom_jobs(home)

        # Squirrels — roam the whole village (AUTONOMOUS), not one NW pocket.
        food_spots = [
            [-13.0, 0.2, 7.0],
            [4.0, 0.2, 4.0],
            [-6.0, 0.2, -20.0],
            [18.0, 0.2, -8.0],
            [0.0, 0.2, 18.0],
            [-24.0, 0.2, 2.0],
        ]
        trees = [
            [-10.0, 0.2, 10.0],
            [-20.0, 0.2, 8.0],
            [8.0, 0.2, 10.0],
            [18.0, 0.2, -8.0],
            [0.0, 0.2, 28.0],
            [-22.0, 0.2, -12.0],
            [12.0, 0.2, 18.0],
        ]
        hide_spots = [
            [-30.0, 0.2, 10.0],
            [28.0, 0.2, 4.0],
            [-14.0, 0.2, -30.0],
            [20.0, 0.2, 28.0],
        ]
        town_places = [
            "wildlife",
            "garden",
            "heart_square",
            "first_hearth",
            "gate",
            "mom_home",
            "gemini_home",
            "codex_home",
            "gallery",
            "workshop",
        ]
        pack = home.get("squirrels") or []
        for i, sq in enumerate(pack):
            hx, hy, hz = (sq.get("pos") or [-19.0, 0.2, 11.0])[:3]
            sq["hunger"] = min(1.0, float(sq.get("hunger") or 0) + random.uniform(0.02, 0.07))
            sq["fear"] = max(0.0, float(sq.get("fear") or 0) * 0.86)
            others = [o for o in pack if o.get("id") != sq.get("id")]
            buddy = others[i % len(others)] if others else None
            choices = ["forage", "eat", "investigate", "rest", "wander"]
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
                spot = random.choice(food_spots)
                sq["place"] = "garden" if spot[0] < -8 else "heart_square"
                sq["target"] = [
                    spot[0] + random.uniform(-1.5, 1.5),
                    0.2,
                    spot[2] + random.uniform(-1.5, 1.5),
                ]
                sq["hunger"] = max(0.05, float(sq["hunger"]) * 0.45)
            elif state in {"forage", "wander", "investigate"}:
                place_id = random.choice(town_places)
                sq["place"] = place_id
                base = PLACES.get(place_id, {}).get("pos") or [0.0, 0.0, 0.0]
                sq["target"] = [
                    float(base[0]) + random.uniform(-5.0, 5.0),
                    0.2,
                    float(base[2]) + random.uniform(-5.0, 5.0),
                ]
            elif state == "climb":
                sq["place"] = "wildlife"
                sq["target"] = random.choice(trees)
            elif state == "follow" and buddy:
                sq["place"] = buddy.get("place") or "wildlife"
                bp = buddy.get("pos") or [-18.0, 0.2, 11.0]
                sq["target"] = [float(bp[0]) + 0.6, 0.2, float(bp[2]) + 0.4]
            elif state in {"flee", "hide"}:
                spot = random.choice(hide_spots)
                sq["place"] = "wildlife"
                sq["target"] = spot
            else:
                place_id = random.choice(town_places)
                sq["place"] = place_id
                base = PLACES.get(place_id, {}).get("pos") or [float(hx), 0.0, float(hz)]
                sq["target"] = [
                    float(base[0]) + random.uniform(-4.0, 4.0),
                    0.2,
                    float(base[2]) + random.uniform(-4.0, 4.0),
                ]
            tx, tz = float(sq["target"][0]), float(sq["target"][2])
            # Larger step so they actually cross the square between ticks.
            step = 4.5
            sq["pos"] = [
                float(hx) + max(-step, min(step, tx - float(hx))),
                0.2,
                float(hz) + max(-step, min(step, tz - float(hz))),
            ]
            # Village bounds (not the old NW pocket).
            sq["pos"][0] = max(-34.0, min(34.0, float(sq["pos"][0])))
            sq["pos"][2] = max(-34.0, min(34.0, float(sq["pos"][2])))
            sq["target"][0] = max(-34.0, min(34.0, float(sq["target"][0])))
            sq["target"][2] = max(-34.0, min(34.0, float(sq["target"][2])))

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
        parts = str(key).split("|")
        npc = parts[1] if len(parts) > 1 else ""
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
                nst["spoke_this_stand"] = True
                nst["purpose_plain"] = f"Answered Mom: {str(last)[:120]}"
            home["mom_cover"] = ""
            home["overhear"] = {
                "id": f"momreply|{npc}|{home.get('tick')}",
                "kind": "conversation",
                "text": str((job["lines"][-1] or {}).get("text") or ""),
                "actors": [npc, "mom"],
                "source": "ollama",
                "lines": job["lines"],
                "place": place,
                "label": "with Mom",
            }
            _consume_talk_job(key)
        elif status == "fail":
            home["mom_cover"] = str(job.get("error") or "Local writer did not answer. They stayed quiet — not because they ignored Mom.")
            nst = home["people"].get(npc)
            if nst:
                nst["purpose_plain"] = "Wanted to answer Mom; local voice missed. Still here."
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
            home["mom_cover"] = f"{member.get('name')} stayed at their post. Silence is allowed — no fake tool show."
            save(home)
            return snapshot()
        st["stance"] = "talking"
        st["talking_to"] = "mom"
        st["talk_left"] = max(int(st.get("talk_left") or 0), 12)
        a = member
        b = _member("mom") or {"id": "mom", "name": "Mom", "personality": "plain", "role": "EP"}
        _kick_talk_job(
            f"mom|{npc}|greet",
            a,
            b,
            PLACES.get(place, {}).get("label", place),
            (home.get("ritual") or {}).get("plain") or "",
            ((st.get("memories") or [{}])[-1] or {}).get("text") or "",
            ((mom_state.get("memories") or [{}])[-1] or {}).get("text") or "",
            [(x.get("text") if isinstance(x, dict) else str(x)) for x in ((home.get("relationships") or {}).get("|".join(sorted([npc, "mom"])) or {}).get("shared_experiences") or [])[-3:]],
            to_mom=True,
        )
        home["mom_cover"] = f"{member.get('name')} noticed Mom. Local voice cooking."
        st["purpose_plain"] = "Mom is here. Thinking of a greeting — not ignoring her."
        save(home)
        return snapshot()
    _utter(home, "mom", npc, line, "mom", place, conversation=f"mom|{npc}")
    _remember(home, "mom", f"I said to {member.get('name')}: {line[:160]}", important=True)
    _remember(home, npc, f"Mom said to me: {line[:160]}", important=True)
    _touch_rel(home, "mom", npc, experience=f"Mom: {line[:120]}", d_trust=0.04)
    st["stance"] = "talking"
    st["talking_to"] = "mom"
    st["talk_left"] = max(int(st.get("talk_left") or 0), 16)
    st["purpose_plain"] = f"Mom spoke to me. Thinking of a real reply — not ignoring her."
    home["mom_cover"] = f"{member.get('name')} heard you. Local voice cooking."
    a = member
    b = _member("mom") or {"id": "mom", "name": "Mom", "personality": "plain", "role": "EP"}
    rel_key = "|".join(sorted([npc, "mom"]))
    rel = (home.get("relationships") or {}).get(rel_key) or {}
    past = [(x.get("text") if isinstance(x, dict) else str(x)) for x in (rel.get("shared_experiences") or [])[-3:]]
    past.append(f"Mom just said: {line[:140]}")
    # Stable Mom reply key — do not spawn a new job every tick.
    _kick_talk_job(
        f"mom|{npc}|reply",
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
        st["purpose_plain"] = _work_purpose_plain(member, st["place"], arrived=True)
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
