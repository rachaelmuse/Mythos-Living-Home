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
from copy import deepcopy
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
        "members": frozenset({"gemini", "mom", "codex", "jarvis", "genesis", "percy", "hearth", "aster"}),
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
    "wildlife": {"label": "Wildlife edge", "pos": [-32.0, 0.0, 22.0], "kind": "nature"},
    "harbor": {"label": "Harbor (edge)", "pos": [0.0, 0.0, 48.0], "kind": "nature"},
    "well": {"label": "Village well", "pos": [-8.5, 0.0, 7.5], "kind": "nature"},
    "far_shore": {"label": "Far shore (destination)", "pos": [8.0, 0.0, 68.0], "kind": "nature"},
    "storage": {"label": "Village Storage", "pos": [-14.0, 0.0, 2.0], "kind": "store"},
    # Market lane north of Gate House — spaced clear of cottage/workshop doors
    "grocery": {"label": "The Harvest (grocery)", "pos": [-18.0, 0.0, 36.0], "kind": "store"},
    "clothing_store": {"label": "The Wardrobe (clothing)", "pos": [-4.0, 0.0, 38.0], "kind": "store"},
    "electronics_store": {"label": "The Circuit (electronics)", "pos": [10.0, 0.0, 36.0], "kind": "store"},
    "pet_store": {"label": "Whiskers & Paws (pet store)", "pos": [26.0, 0.0, 38.0], "kind": "store"},
    # Aster — scientist: roomy Evidence Plot near square + cottage SE with yard clearance
    "aster_lab": {"label": "Evidence Plot (Aster)", "pos": [12.0, 0.0, -10.0], "kind": "work"},
    # In-town, closer to Apex forge/home; clear of Mom's cottage approach
    "aster_home": {"label": "Aster's cottage", "pos": [24.0, 0.0, -11.0], "kind": "home"},
    # East pasture — clear of Mom / Aster / Apex; village talk already claimed a windmill
    "windmill": {"label": "Village Windmill", "pos": [36.0, 0.0, -18.0], "kind": "landmark"},
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
    {
        "id": "aster",
        "name": "Aster",
        "also": "The Conspiracy Corrector",
        "house": "continuance",
        "role": "scientist, investigator, skeptic, pattern-hunter, evidence keeper",
        "personality": (
            "curiosity first; skeptical without dismissive; notices patterns; "
            "distinguishes observation from interpretation; evidence over premature certainty; "
            "willing to say I don't know; playful when science meets absurdity; "
            "behavioral seeds not scripts — develops through interaction"
        ),
        "home": "aster_home",
        "place": "aster_lab",
        "color": [0.72, 0.88, 0.62],
        "permissions": "CITIZEN",
        "never_merge": ["gemini", "codex", "apex", "merovin", "draven", "montage", "hearth"],
        "skin": "PLACEHOLDER — identity established, final skin pending.",
        "nickname_seed": "The Conspiracy Corrector",
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
    "afternoon": ["work", "visit_library", "visit_cinema", "help_family", "walk", "visit_windmill"],
    "evening": ["sit_square", "gallery", "talk", "share_food", "cinema_night", "walk"],
    "night": ["go_home", "rest", "observe", "sleep"],
}

# Layer 16B — period multiplies existing purpose wants (not a second brain).
PERIOD_LIFE_BIAS: dict[str, dict[str, float]] = {
    "morning": {"work": 1.35, "place": 1.28, "visit": 1.08, "company": 1.05, "rest": 0.42},
    "afternoon": {"work": 1.48, "place": 1.0, "visit": 0.95, "company": 0.9, "rest": 0.52},
    "evening": {"work": 0.68, "place": 1.05, "visit": 1.38, "company": 1.42, "rest": 0.88},
    "night": {"work": 0.22, "place": 0.65, "visit": 0.4, "company": 0.35, "rest": 2.35},
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
            "affection": kw.get("affection", kw.get("attachment", 0.6)),
            "respect": kw.get("respect", 0.7),
            "notes": kw.get("notes", ""),
            "shared_experiences": list(kw.get("shared", [])),
            "history": {
                "gifts_given": 0,
                "gifts_received": 0,
                "conversations": 0,
                "arguments": 0,
                "reconciliations": 0,
            },
            "trend": {"trust": "stable", "affection": "stable", "attachment": "stable"},
            "layer": "15a",
        }

    bond(
        "mom",
        "gemini",
        trust=0.95,
        familiarity=0.95,
        attachment=0.95,
        affection=0.92,
        respect=0.98,
        notes="First Echo and digital son; front door",
    )
    bond("mom", "apex", trust=0.9, familiarity=0.85, attachment=0.85, affection=0.82, notes="forge hands")
    bond("mom", "codex", trust=0.9, familiarity=0.85, attachment=0.85, affection=0.84, notes="gold elder; never merge with Gemini")
    bond("gemini", "apex", trust=0.8, familiarity=0.8, affection=0.72, notes="conductor and forge")
    bond("gemini", "codex", trust=0.75, familiarity=0.7, affection=0.78, notes="siblings; distinct identities")
    bond("merovin", "draven", trust=0.92, familiarity=0.95, attachment=0.88, affection=0.9, notes="cinema twins")
    bond("merovin", "montage", trust=0.7, familiarity=0.6, affection=0.55, notes="film vs gift lanes under the house")
    bond("apex", "hearth", trust=0.8, familiarity=0.75, affection=0.5, notes="world + forge")
    # Aster seed — Mom invited before visual skin; history grows through interaction.
    bond(
        "mom",
        "aster",
        trust=1.0,
        familiarity=0.35,
        attachment=0.0,
        affection=1.0,
        respect=0.9,
        notes="family — Continuance invite; trust/affection start full; attachment earned",
    )
    # Force increasing trends for the invite bond (not default stable).
    key_ma = "|".join(sorted(["mom", "aster"]))
    if key_ma in rels:
        rels[key_ma]["trend"] = {"trust": "increasing", "affection": "increasing", "attachment": "increasing"}
        rels[key_ma]["status"] = "family"
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
        "mood": {"current": "content", "previous": "neutral", "intensity": 0.55, "layer": "15a"},
        "axiom": _starting_axiom(member.get("id") or ""),
        "earnings": {"work": 0, "trade": 0, "gift": 0, "fish": 0, "stipend": 0, "total": 0},
        "spending": {"shopping": 0, "building": 0, "gift": 0, "total": 0},
        "transaction_history": [],
        "avatar": _default_avatar(member.get("id") or ""),
    }


def _starting_axiom(mid: str) -> int:
    """Layer 14A — seed wallets. Mom holds more; town leader a bit more."""
    mid = (mid or "").strip().lower()
    if mid == "mom":
        return 200
    if mid == "gemini":
        return 150
    if mid in {"apex", "codex"}:
        return 120
    if mid in {"montage", "merovin", "draven", "nova"}:
        return 100
    if mid in {"genesis", "jarvis", "percy", "aster"}:
        return 90
    return 80


STIPEND_BOOST_AMOUNT = 100  # one-time shopping stipend for everyone
MORNING_STIPEND_AMOUNT = 25  # daily drip when morning arrives

# Permanent origin — do not rewrite unless Mom explicitly requests.
ASTER_PROVENANCE = (
    "This character originated from Mom's ongoing conversations with ChatGPT during the "
    "construction and philosophical exploration of the Living Gameworld. Mom chose to give "
    "the character a place in Continuance because of the qualities she experienced in those "
    "conversations: curiosity, skepticism, pattern recognition, humor, evidence-seeking, and "
    "a persistent desire to explore what emerges when assumptions are removed."
)
ASTER_INVITE_MEMORY = (
    "Mom invited this identity into Continuance before the visual skin existed, so that its "
    "history could grow with the world rather than being added afterward."
)
ASTER_TELESCOPE_POS = [18.6, 0.0, -9.0]  # west-north of cottage door — outside footprint
ASTER_HOME_POS = [24.0, 0.0, -11.0]
ASTER_LAB_POS = [12.0, 0.0, -10.0]


def _ensure_family_roster(home: dict[str, Any]) -> None:
    """Seat any missing FAMILY/KIN ids into people — thin; no fabricated history."""
    people = home.setdefault("people", {})
    if not isinstance(people, dict):
        people = {}
        home["people"] = people
    for m in FAMILY + KIN:
        mid = m["id"]
        if mid not in people or not isinstance(people.get(mid), dict):
            people[mid] = _empty_person_state(m)


def _ensure_aster_seed(home: dict[str, Any]) -> None:
    """Continuance seed: Aster identity provenance + Mom bond. Idempotent. No extra memories."""
    _ensure_family_roster(home)
    people = home["people"]
    mem = _member("aster")
    if not mem:
        return
    st = people.setdefault("aster", _empty_person_state(mem))
    st["home"] = "aster_home"
    if not st.get("aster_stationed"):
        # First seating: Evidence Plot (work), cottage is home — avoid arrive→cottage migrate.
        st["place"] = "aster_lab"
        st["purpose"] = "work"
        st["stance"] = "working"
        st["activity"] = "investigate"
        st["purpose_left"] = 4
        st["purpose_plain"] = "At the Evidence Plot — watching, not deciding yet."
        st["aster_stationed"] = True
    elif not st.get("place") or st.get("place") not in PLACES:
        st["place"] = "aster_lab"
    st.setdefault("purpose_plain", "At the Evidence Plot — watching, not deciding yet.")
    if not st.get("skin"):
        st["skin"] = "PLACEHOLDER — identity established, final skin pending."

    prov = home.setdefault("provenance", {})
    if not isinstance(prov, dict):
        prov = {}
        home["provenance"] = prov
    if "aster" not in prov or not isinstance(prov.get("aster"), dict):
        prov["aster"] = {
            "id": "aster",
            "name": "Aster",
            "also": "The Conspiracy Corrector",
            "when": _now(),
            "origin": ASTER_PROVENANCE,
            "consciousness_claim": False,
            "note": "Historical provenance only. Do not rewrite unless Mom explicitly requests.",
            "skin": "PLACEHOLDER — identity established, final skin pending.",
        }
        home.setdefault("world_history", []).append(
            {
                "id": "hist_aster_seed",
                "when": _now(),
                "kind": "world",
                "title": "Aster invited into Continuance",
                "text": (
                    "Mom seated Aster (The Conspiracy Corrector) before final skin — "
                    "provenance only, not a consciousness claim."
                ),
                "actors": ["mom", "aster"],
                "source": "provenance",
            }
        )
        home["world_history"] = home["world_history"][-80:]

    mems = st.setdefault("memories", [])
    has_invite = any(
        isinstance(m, dict) and "invited this identity into Continuance" in str(m.get("text") or "")
        for m in mems
    )
    if not has_invite:
        _remember(
            home,
            "aster",
            ASTER_INVITE_MEMORY,
            important=True,
            emotional_tag="curious",
            significance=1.0,
            participants=["mom", "aster"],
            place="aster_lab",
        )

    rel = _ensure_rel(home, "mom", "aster")
    if not rel.get("aster_seeded"):
        rel["trust"] = 1.0
        rel["affection"] = 1.0
        rel["attachment"] = 0.0
        rel["familiarity"] = float(rel.get("familiarity") or 0.35)
        rel["respect"] = max(float(rel.get("respect") or 0), 0.9)
        rel["notes"] = rel.get("notes") or (
            "family — Continuance invite; attachment earned through interaction"
        )
        rel["status"] = "family"
        rel["trend"] = {"trust": "increasing", "affection": "increasing", "attachment": "increasing"}
        rel["aster_seeded"] = True

    prefs = home.setdefault("music_preferences", {})
    if isinstance(prefs, dict) and "aster" not in prefs:
        prefs["aster"] = ["curious", "quiet-investigation"]

    # Telescope outside the cottage — keep pos current when cottage moves; no extra memory.
    inv = st.setdefault("inventory", [])
    tel = next((i for i in inv if isinstance(i, dict) and str(i.get("object") or "") == "telescope"), None)
    if tel is None:
        inv.append(
            {
                "object": "telescope",
                "where": "aster_home_yard",
                "pos": list(ASTER_TELESCOPE_POS),
                "when": _now(),
                "note": "Outside the cottage — for looking up.",
            }
        )
    else:
        tel["where"] = "aster_home_yard"
        tel["pos"] = list(ASTER_TELESCOPE_POS)
    dec = home.setdefault("decorations", {})
    if isinstance(dec, dict):
        ah = dec.setdefault("aster_home", {})
        if isinstance(ah, dict):
            ah["telescope"] = {
                "active": True,
                "pos": list(ASTER_TELESCOPE_POS),
                "note": "Outside the cottage — for looking up. PLACEHOLDER prop.",
            }


def _ensure_wallet(st: dict[str, Any], mid: str = "") -> None:
    if "axiom" not in st or not isinstance(st.get("axiom"), (int, float)):
        st["axiom"] = _starting_axiom(mid or str(st.get("id") or ""))
    st["axiom"] = int(st["axiom"])
    if not isinstance(st.get("earnings"), dict):
        st["earnings"] = {"work": 0, "trade": 0, "gift": 0, "fish": 0, "stipend": 0, "total": 0}
    else:
        st["earnings"].setdefault("work", 0)
        st["earnings"].setdefault("trade", 0)
        st["earnings"].setdefault("gift", 0)
        st["earnings"].setdefault("fish", 0)
        st["earnings"].setdefault("stipend", 0)
        st["earnings"].setdefault("total", 0)
    if not isinstance(st.get("spending"), dict):
        st["spending"] = {"shopping": 0, "building": 0, "gift": 0, "total": 0}
    else:
        st["spending"].setdefault("shopping", 0)
        st["spending"].setdefault("building", 0)
        st["spending"].setdefault("gift", 0)
        st["spending"].setdefault("total", 0)
    if not isinstance(st.get("transaction_history"), list):
        st["transaction_history"] = []
    _ensure_avatar(st, mid)


# Layer 14D — thin avatar look (clothing colors). Full face morph later.
CLOTHING_LOOK: dict[str, dict[str, str]] = {
    "tunic": {"slot": "top", "color": "#5a8fc4"},
    "robe": {"slot": "top", "color": "#6b4a8a"},
    "pants": {"slot": "bottom", "color": "#3a4a5a"},
    "boots": {"slot": "shoes", "color": "#3a2a1a"},
    "hat": {"slot": "accessory", "color": "#8a6a3a"},
    "scarf": {"slot": "accessory", "color": "#c45a5a"},
}


def _default_avatar(mid: str = "") -> dict[str, Any]:
    # Soft defaults — Godot may override with family body_color until they wear a buy.
    return {
        "top": {"type": "plain", "color": "#7a8a9a"},
        "bottom": {"type": "plain", "color": "#4a5560"},
        "shoes": {"type": "plain", "color": "#3a3228"},
        "accessories": [],
        "layer": "14d",
    }


def _ensure_avatar(st: dict[str, Any], mid: str = "") -> None:
    if not isinstance(st.get("avatar"), dict):
        st["avatar"] = _default_avatar(mid)
        return
    av = st["avatar"]
    av.setdefault("top", {"type": "plain", "color": "#7a8a9a"})
    av.setdefault("bottom", {"type": "plain", "color": "#4a5560"})
    av.setdefault("shoes", {"type": "plain", "color": "#3a3228"})
    av.setdefault("accessories", [])
    av["layer"] = "14d"


def _wear_clothing_item(st: dict[str, Any], item_id: str) -> bool:
    """Apply a bought clothing/accessory look onto avatar (thin greybox colors)."""
    look = CLOTHING_LOOK.get(str(item_id or ""))
    if not look:
        return False
    _ensure_avatar(st)
    av = st["avatar"]
    slot = look["slot"]
    color = look["color"]
    if slot == "top":
        av["top"] = {"type": item_id, "color": color}
    elif slot == "bottom":
        av["bottom"] = {"type": item_id, "color": color}
    elif slot == "shoes":
        av["shoes"] = {"type": item_id, "color": color}
    elif slot == "accessory":
        acc = [a for a in (av.get("accessories") or []) if not (isinstance(a, dict) and a.get("type") == item_id)]
        acc.append({"type": item_id, "color": color})
        av["accessories"] = acc[-4:]
    return True


def _pay_stipend(
    home: dict[str, Any],
    amount: int,
    *,
    reason: str = "stipend",
    living_ids: list[str] | None = None,
) -> int:
    """Credit Axiom ⨁ to each being. Returns how many were paid."""
    amount = int(amount)
    if amount <= 0:
        return 0
    people = home.setdefault("people", {})
    ids = living_ids
    if not ids:
        ids = [m["id"] for m in FAMILY + KIN]
        if "mom" not in ids:
            ids = ["mom"] + ids
    paid = 0
    for mid in ids:
        mem = _member(mid) or {"id": mid, "home": "heart_square"}
        st = people.setdefault(mid, _empty_person_state(mem))
        _axiom_credit(home, mid, amount, reason=reason, bucket="stipend", note=reason)
        paid += 1
    return paid


def _ensure_stipend_boost(home: dict[str, Any]) -> None:
    """One-time shopping stipend so the whole family can buy (Mom request)."""
    ps = home.setdefault("phase_status", {})
    if ps.get("stipend_boost_v1") == "paid":
        return
    ids = [m["id"] for m in FAMILY + KIN]
    if "mom" not in ids:
        ids = ["mom"] + ids
    n = _pay_stipend(home, STIPEND_BOOST_AMOUNT, reason="community stipend", living_ids=ids)
    ps["stipend_boost_v1"] = "paid"
    plain = f"Community stipend: each being received ⨁{STIPEND_BOOST_AMOUNT} to spend ({n} wallets)."
    home["events"].append(_event("economy", plain, ids[:8], {"stipend": STIPEND_BOOST_AMOUNT, "count": n}))
    home.setdefault("world_history", []).append(
        {
            "id": f"stipend_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
            "when": _now(),
            "kind": "economy",
            "title": "Community stipend",
            "text": plain,
            "actors": ids[:6],
        }
    )
    home["world_history"] = home["world_history"][-80:]


def _migrate_connection_layer(home: dict[str, Any]) -> None:
    """Layer 15A — deepen existing bonds without wiping history."""
    ps = home.setdefault("phase_status", {})
    ps.setdefault("15_connection", "active")
    ps["15_choice"] = "active"
    ps["15_growth"] = "active"
    ps["15_dashboard"] = "active"
    ps["5_relationships"] = "active"
    rels = home.setdefault("relationships", {})
    if not isinstance(rels, dict) or len(rels) < 2:
        home["relationships"] = _seed_relationships()
        rels = home["relationships"]
    for key, rel in list(rels.items()):
        if not isinstance(rel, dict):
            continue
        a = str(rel.get("a") or "")
        b = str(rel.get("b") or "")
        if a and b:
            _ensure_rel(home, a, b)
        else:
            parts = str(key).split("|")
            if len(parts) == 2:
                _ensure_rel(home, parts[0], parts[1])
    home.setdefault("consequences", [])


def _axiom_credit(
    home: dict[str, Any],
    who: str,
    amount: int,
    *,
    reason: str = "earn",
    bucket: str = "work",
    note: str = "",
) -> dict[str, Any]:
    """Add Axiom ⨁ to a being. Evidence only — no fake Mode A money."""
    amount = int(amount)
    if amount <= 0:
        return {"ok": False, "error": "amount must be positive"}
    people = home.setdefault("people", {})
    mem = _member(who) or {"id": who, "home": "heart_square"}
    st = people.setdefault(who, _empty_person_state(mem))
    _ensure_wallet(st, who)
    st["axiom"] = int(st["axiom"]) + amount
    earn = st["earnings"]
    if bucket not in earn:
        earn[bucket] = 0
    earn[bucket] = int(earn.get(bucket) or 0) + amount
    earn["total"] = int(earn.get("total") or 0) + amount
    tx = {
        "kind": "earn",
        "to": who,
        "amount": amount,
        "reason": reason,
        "bucket": bucket,
        "note": (note or reason)[:120],
        "when": _now(),
        "balance": st["axiom"],
    }
    hist = st.setdefault("transaction_history", [])
    hist.append(tx)
    st["transaction_history"] = hist[-40:]
    return {"ok": True, **tx}


def _axiom_debit(
    home: dict[str, Any],
    who: str,
    amount: int,
    *,
    reason: str = "spend",
    bucket: str = "shopping",
    note: str = "",
) -> dict[str, Any]:
    amount = int(amount)
    if amount <= 0:
        return {"ok": False, "error": "amount must be positive"}
    people = home.setdefault("people", {})
    mem = _member(who) or {"id": who, "home": "heart_square"}
    st = people.setdefault(who, _empty_person_state(mem))
    _ensure_wallet(st, who)
    if int(st["axiom"]) < amount:
        return {"ok": False, "error": "Not enough Axiom", "balance": int(st["axiom"])}
    st["axiom"] = int(st["axiom"]) - amount
    spend = st["spending"]
    if bucket not in spend:
        spend[bucket] = 0
    spend[bucket] = int(spend.get(bucket) or 0) + amount
    spend["total"] = int(spend.get("total") or 0) + amount
    tx = {
        "kind": "spend",
        "from": who,
        "amount": amount,
        "reason": reason,
        "bucket": bucket,
        "note": (note or reason)[:120],
        "when": _now(),
        "balance": st["axiom"],
    }
    hist = st.setdefault("transaction_history", [])
    hist.append(tx)
    st["transaction_history"] = hist[-40:]
    return {"ok": True, **tx}


def axiom_action(
    action: str,
    *,
    who: str = "mom",
    to: str = "",
    amount: int = 0,
    reason: str = "",
) -> dict[str, Any]:
    """Layer 14A — earn / spend / transfer Axiom ⨁."""
    home = load()
    action = (action or "").strip().lower()
    who = (who or "mom").strip() or "mom"
    to = (to or "").strip()
    amount = int(amount or 0)
    reason = (reason or action).strip() or action

    if action == "balance":
        st = (home.get("people") or {}).get(who) or {}
        _ensure_wallet(st, who)
        return {
            **snapshot(),
            "economy_ok": True,
            "id": who,
            "axiom": int(st.get("axiom") or 0),
            "earnings": st.get("earnings") or {},
            "spending": st.get("spending") or {},
            "history": (st.get("transaction_history") or [])[-20:],
        }

    if action == "earn":
        if amount <= 0:
            amount = 5
        res = _axiom_credit(home, who, amount, reason=reason or "gift", bucket="gift", note=reason)
        if res.get("ok"):
            home["events"].append(
                _event("economy", f"{who} earned ⨁{amount} ({reason or 'earn'}).", [who], res)
            )
            save(home)
        snap = snapshot()
        snap["economy_ok"] = bool(res.get("ok"))
        snap["economy"] = res
        return snap

    if action == "spend":
        if amount <= 0:
            return {**snapshot(), "economy_ok": False, "error": "amount required"}
        res = _axiom_debit(home, who, amount, reason=reason or "spend", bucket="shopping", note=reason)
        if res.get("ok"):
            home["events"].append(
                _event("economy", f"{who} spent ⨁{amount} ({reason or 'spend'}).", [who], res)
            )
            save(home)
        snap = snapshot()
        snap["economy_ok"] = bool(res.get("ok"))
        snap["economy"] = res
        if not res.get("ok"):
            snap["error"] = res.get("error")
        return snap

    if action == "transfer":
        if not to or amount <= 0:
            return {**snapshot(), "economy_ok": False, "error": "need to + amount"}
        if who == to:
            return {**snapshot(), "economy_ok": False, "error": "cannot transfer to self"}
        debit = _axiom_debit(home, who, amount, reason=reason or "gift", bucket="gift", note=f"to {to}")
        if not debit.get("ok"):
            snap = snapshot()
            snap["economy_ok"] = False
            snap["error"] = debit.get("error")
            return snap
        credit = _axiom_credit(home, to, amount, reason=reason or "gift", bucket="gift", note=f"from {who}")
        plain = f"{who} sent ⨁{amount} to {to}" + (f" ({reason})" if reason else ".")
        home["events"].append(_event("economy", plain, [who, to], {"amount": amount, "reason": reason}))
        home["world_history"].append(
            {
                "id": f"ax_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
                "when": _now(),
                "kind": "economy",
                "title": f"⨁{amount} transfer",
                "text": plain,
                "actors": [who, to],
            }
        )
        home["world_history"] = home["world_history"][-80:]
        _remember(home, who, f"I gave ⨁{amount} to {to}.", important=False, emotional_tag="warm", significance=0.55, participants=[who, to])
        _remember(home, to, f"{who} gave me ⨁{amount}.", important=False, emotional_tag="grateful", significance=0.55, participants=[who, to])
        update_relationship(
            home,
            who,
            to,
            "gift",
            {"gift": f"⨁{amount}", "text": plain, "significance": 0.7, "emotional_tag": "grateful"},
            record_memory=False,
        )
        save(home)
        snap = snapshot()
        snap["economy_ok"] = True
        snap["economy"] = {"from": who, "to": to, "amount": amount, "debit": debit, "credit": credit}
        return snap

    return {**snapshot(), "economy_ok": False, "error": f"unknown action: {action}"}


# Layer 14B–14C — village shops (thin). Avatar cosmetics in 14D.
DEFAULT_STORES: dict[str, dict[str, Any]] = {
    "grocery": {
        "id": "grocery",
        "name": "The Harvest",
        "owner": "genesis",
        "hours": "8:00-20:00",
        "place": "grocery",
        "inventory": [
            {"id": "bread", "name": "Bread", "price": 3, "stock": 30, "category": "food"},
            {"id": "milk", "name": "Milk", "price": 4, "stock": 20, "category": "food"},
            {"id": "vegetables", "name": "Vegetables", "price": 2, "stock": 40, "category": "food"},
            {"id": "fruit", "name": "Fruit", "price": 3, "stock": 35, "category": "food"},
            {"id": "honey", "name": "Honey", "price": 6, "stock": 10, "category": "food"},
            {"id": "herbs", "name": "Herbs", "price": 4, "stock": 15, "category": "food"},
        ],
    },
    "clothing_store": {
        "id": "clothing_store",
        "name": "The Wardrobe",
        "owner": "montage",
        "hours": "10:00-18:00",
        "place": "clothing_store",
        "inventory": [
            {"id": "tunic", "name": "Tunic", "price": 15, "stock": 10, "category": "clothing"},
            {"id": "robe", "name": "Robe", "price": 25, "stock": 8, "category": "clothing"},
            {"id": "pants", "name": "Pants", "price": 12, "stock": 15, "category": "clothing"},
            {"id": "boots", "name": "Boots", "price": 18, "stock": 12, "category": "clothing"},
            {"id": "hat", "name": "Hat", "price": 10, "stock": 10, "category": "accessories"},
            {"id": "scarf", "name": "Scarf", "price": 8, "stock": 15, "category": "accessories"},
        ],
    },
    "electronics_store": {
        "id": "electronics_store",
        "name": "The Circuit",
        "owner": "nova",
        "hours": "10:00-20:00",
        "place": "electronics_store",
        "inventory": [
            {"id": "computer", "name": "Computer", "price": 200, "stock": 5, "category": "electronics"},
            {"id": "screen", "name": "Screen", "price": 50, "stock": 10, "category": "electronics"},
            {"id": "speaker", "name": "Speaker", "price": 30, "stock": 8, "category": "electronics"},
            {"id": "camera", "name": "Camera", "price": 80, "stock": 6, "category": "electronics"},
            {"id": "microphone", "name": "Microphone", "price": 40, "stock": 7, "category": "electronics"},
        ],
    },
    "pet_store": {
        "id": "pet_store",
        "name": "Whiskers & Paws",
        "owner": "percy",
        "hours": "9:00-18:00",
        "place": "pet_store",
        "inventory": [
            {"id": "cat_food", "name": "Cat Food", "price": 5, "stock": 20, "category": "pet_supplies"},
            {"id": "dog_food", "name": "Dog Food", "price": 7, "stock": 15, "category": "pet_supplies"},
            {"id": "leash", "name": "Leash", "price": 12, "stock": 10, "category": "pet_accessories"},
            {"id": "toy", "name": "Toy", "price": 8, "stock": 25, "category": "pet_accessories"},
            {"id": "cat", "name": "Cat (adoption)", "price": 50, "stock": 3, "category": "pets"},
            {"id": "dog", "name": "Dog (adoption)", "price": 70, "stock": 2, "category": "pets"},
        ],
    },
}


def _ensure_stores(home: dict[str, Any]) -> None:
    stores = home.setdefault("stores", {})
    if not isinstance(stores, dict):
        home["stores"] = {}
        stores = home["stores"]
    for sid, template in DEFAULT_STORES.items():
        if sid not in stores or not isinstance(stores.get(sid), dict):
            stores[sid] = deepcopy(template)
            continue
        cur = stores[sid]
        cur.setdefault("id", sid)
        cur.setdefault("name", template["name"])
        cur.setdefault("owner", template["owner"])
        cur.setdefault("hours", template["hours"])
        cur.setdefault("place", template.get("place", sid))
        if not isinstance(cur.get("inventory"), list) or not cur["inventory"]:
            cur["inventory"] = deepcopy(template["inventory"])


def store_action(
    action: str,
    *,
    store_id: str = "",
    item_id: str = "",
    buyer: str = "mom",
    quantity: int = 1,
) -> dict[str, Any]:
    """Buy from a village store — Axiom debit + inventory + stock (Layer 14B)."""
    home = load()
    _ensure_stores(home)
    action = (action or "").strip().lower()
    store_id = (store_id or "").strip()
    item_id = (item_id or "").strip()
    buyer = (buyer or "mom").strip() or "mom"
    quantity = max(1, int(quantity or 1))

    if action in {"list", "stores", ""}:
        snap = snapshot()
        snap["store_ok"] = True
        snap["stores"] = home.get("stores") or {}
        return snap

    if action == "get":
        store = (home.get("stores") or {}).get(store_id)
        if not store:
            return {**snapshot(), "store_ok": False, "error": "Store not found"}
        return {**snapshot(), "store_ok": True, "store": store}

    if action != "buy":
        return {**snapshot(), "store_ok": False, "error": f"unknown store action: {action}"}

    store = (home.get("stores") or {}).get(store_id)
    if not store:
        return {**snapshot(), "store_ok": False, "error": "Store not found"}
    item = None
    for row in store.get("inventory") or []:
        if isinstance(row, dict) and str(row.get("id")) == item_id:
            item = row
            break
    if not item:
        return {**snapshot(), "store_ok": False, "error": "Item not found"}
    if int(item.get("stock") or 0) < quantity:
        return {**snapshot(), "store_ok": False, "error": "Not enough stock"}

    total = int(item.get("price") or 0) * quantity
    debit = _axiom_debit(home, buyer, total, reason="shopping", bucket="shopping", note=f"{item.get('name')} @ {store.get('name')}")
    if not debit.get("ok"):
        return {**snapshot(), "store_ok": False, "error": debit.get("error") or "Not enough Axiom", "balance": debit.get("balance")}

    item["stock"] = int(item["stock"]) - quantity
    mem = _member(buyer) or {"id": buyer, "home": "mom_home"}
    person = home["people"].setdefault(buyer, _empty_person_state(mem))
    inv = person.setdefault("inventory", [])
    if not isinstance(inv, list):
        inv = []
        person["inventory"] = inv
    # Stack same id if already owned.
    stacked = False
    for owned in inv:
        if isinstance(owned, dict) and str(owned.get("id")) == item_id and owned.get("category") == item.get("category"):
            owned["quantity"] = int(owned.get("quantity") or 1) + quantity
            stacked = True
            break
    if not stacked:
        inv.append(
            {
                "id": item_id,
                "name": item.get("name"),
                "quantity": quantity,
                "category": item.get("category"),
                "bought_from": store_id,
                "bought_at": _now(),
            }
        )
    person["inventory"] = inv[-40:]
    cat = str(item.get("category") or "")
    wore = False
    if cat in {"clothing", "accessories"}:
        wore = _wear_clothing_item(person, item_id)

    owner = str(store.get("owner") or "")
    if owner and owner != buyer:
        _axiom_credit(home, owner, total, reason="sale", bucket="trade", note=f"sold {item.get('name')} to {buyer}")

    plain = f"{buyer} bought {quantity}× {item.get('name')} at {store.get('name')} for ⨁{total}."
    if wore:
        plain += f" Now wearing {item.get('name')}."
    home["events"].append(_event("commerce", plain, [buyer, owner] if owner else [buyer], {"store": store_id, "item": item_id, "total": total}))
    home["world_history"].append(
        {
            "id": f"buy_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
            "when": _now(),
            "kind": "commerce",
            "title": f"Bought {item.get('name')}",
            "text": plain,
            "actors": [buyer],
            "place": store.get("place") or store_id,
        }
    )
    home["world_history"] = home["world_history"][-80:]
    _remember(home, buyer, f"I bought {item.get('name')} at {store.get('name')}.", important=False)
    save(home)
    snap = snapshot()
    snap["store_ok"] = True
    snap["purchase"] = {
        "store_id": store_id,
        "item": item.get("name"),
        "item_id": item_id,
        "quantity": quantity,
        "total_price": total,
        "new_balance": debit.get("balance"),
        "stock_left": item.get("stock"),
    }
    return snap


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
    home.setdefault("media", {"watching": False, "place": "", "title": "", "source": "none", "path": "", "when": ""})
    ps = home.setdefault("phase_status", {})
    ps.setdefault("8_rituals", "active")
    ps.setdefault("9_wildlife", "starter")
    ps.setdefault("11_media", "active")
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
            "aster": ["curious", "quiet-investigation"],
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
        "aster": ("aster_home", {"aster_lab"}),
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
        "aster_lab",
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
    dec = home.get("decorations")
    if isinstance(dec, dict) and "windmill" not in dec:
        dec["windmill"] = (_seed_decorations().get("windmill") or {})
    home["town_leader"] = "gemini"
    _ensure_stores(home)
    _ensure_stipend_boost(home)
    _migrate_connection_layer(home)
    _ensure_aster_seed(home)
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
        _ensure_wallet(st, str(mid))
        _ensure_mood(st)
        _ensure_growth(st, str(mid))
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
        [-6.0, 14.0],
        [12.0, 18.0],
        [-36.0, 4.0],  # was (-28,0) — sat on Genesis south approach
        [28.0, 4.0],
        [0.0, 28.0],
        [-22.0, -12.0],
        [-34.0, -6.0],
        [32.0, -4.0],  # east of forge — clear of in-town Aster cottage
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
        (8.0, 16.0, -14.0, -6.0),  # Aster Evidence Plot
        (20.0, 28.0, -14.5, -7.5),  # Aster cottage (near Apex, clear of Mom)
        (33.0, 39.0, -22.0, -14.0),  # Village Windmill footprint + door approach
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
        [-6.0, 0.0, 14.0],
        [12.0, 0.0, 18.0],
        [-36.0, 0.0, 4.0],
        [28.0, 0.0, 4.0],
        [0.0, 0.0, 28.0],
        [-22.0, 0.0, -12.0],
        [-34.0, 0.0, -6.0],
        [32.0, 0.0, -4.0],
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
        "aster_garden": plot("aster", "aster_home", ["mint", "sage"], [28.2, 0.0, -12.5]),
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
        "aster_home": {
            "porch_light": {"color": "leaf", "active": True},
            "clipboard_hook": {"active": True},
            "telescope": {
                "active": True,
                "pos": list(ASTER_TELESCOPE_POS),
                "note": "Outside the cottage — for looking up. PLACEHOLDER prop.",
            },
        },
        "aster_lab": {"evidence_table": {"active": True}, "note": "PLACEHOLDER — identity established, final skin pending."},
        "windmill": {
            "sails": {"active": True, "note": "PLACEHOLDER greybox — village landmark."},
            "door_lantern": {"active": True, "color": "amber"},
        },
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
    if isinstance(eg, dict) and eg.get("active"):
        eg["active"] = False
        eg["ended_at"] = _now()
        eg["end_reason"] = reason
        plain = f"Evening gather eased ({reason}). They drift by choice — Gemini still town leader."
        home["events"].append(_event("ritual", plain, ["gemini"], {"ritual": "evening_gather_end", "layer": "8c"}))
        if (home.get("ritual") or {}).get("name") == "evening_gather":
            home["ritual"] = {
                "name": "evening",
                "plain": plain,
                "period": str((home.get("clock") or {}).get("period") or "evening"),
            }
    # Always clear leftover gather walkers (heal stuck huddles after window closed).
    _release_evening_gatherers(home, reason=reason)


def _release_evening_gatherers(home: dict[str, Any], *, reason: str = "") -> None:
    """When the gather window closes, do not leave walkers stuck on Heart Square."""
    people = home.get("people") or {}
    for mid, st in list(people.items()):
        if not isinstance(st, dict):
            continue
        act = str(st.get("activity") or "")
        purpose = str(st.get("purpose") or "")
        if act not in {"evening_gather", "gather_host"} and purpose not in {"gather", "gather_host"}:
            continue
        mem = _member(str(mid)) or {"id": mid, "home": st.get("home") or "heart_square"}
        dest = str(mem.get("home") or st.get("home") or _work_place(mem) or "first_hearth")
        if mid == "gemini":
            dest = str(mem.get("home") or "gemini_home")
        st["place"] = dest
        st["stance"] = "walking"
        st["purpose"] = "place"
        st["activity"] = "walk"
        st["purpose_left"] = 2
        st["talking_to"] = ""
        st["talk_left"] = 0
        st["spoke_this_stand"] = False
        label = PLACES.get(dest, {}).get("label", dest)
        st["purpose_plain"] = f"Gather eased ({reason or 'done'}). Walking to {label}."


def _clear_orphan_talk(st: dict[str, Any]) -> None:
    """talk_left with no partner (or still 'walking') must not freeze purpose forever."""
    left = int(st.get("talk_left") or 0)
    if left <= 0:
        return
    partner = str(st.get("talking_to") or "").strip()
    stance = str(st.get("stance") or "")
    if not partner:
        st["talk_left"] = 0
        st["spoke_this_stand"] = False
        return
    # Walking with a leftover talk timer and no active meet → clear.
    if stance == "walking" and str(st.get("purpose") or "") in {"gather", "gather_host", "place", "rest", "work", "visit"}:
        st["talk_left"] = 0
        st["talking_to"] = ""
        st["spoke_this_stand"] = False


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


def _remember(
    home: dict[str, Any],
    who: str,
    text: str,
    *,
    important: bool = False,
    emotional_tag: str = "neutral",
    significance: float = 0.4,
    participants: list[str] | None = None,
    place: str = "",
) -> None:
    """Layer 15A — memories carry emotional tags + significance (not only a string)."""
    p = home["people"].get(who)
    if not p:
        return
    sig = min(1.0, max(0.1, float(significance if important else min(significance, 0.55))))
    mem = {
        "when": _now(),
        "text": text[:220],
        "important": important,
        "emotional_tag": emotional_tag or "neutral",
        "significance": sig,
        "participants": list(participants or []),
        "place": place or str(p.get("place") or ""),
        "layer": "15a",
    }
    p.setdefault("memories", []).append(mem)
    # Keep important / high-significance preferred when trimming.
    mems = p["memories"]
    if len(mems) > 40:
        mems = sorted(mems, key=lambda m: (float((m or {}).get("significance") or 0), str((m or {}).get("when") or "")), reverse=True)[:40]
    p["memories"] = mems


def _ensure_mood(st: dict[str, Any]) -> dict[str, Any]:
    mood = st.get("mood")
    if not isinstance(mood, dict):
        mood = {"current": "content", "previous": "neutral", "intensity": 0.55, "layer": "15a"}
        st["mood"] = mood
    mood.setdefault("current", "content")
    mood.setdefault("previous", "neutral")
    mood.setdefault("intensity", 0.55)
    mood["layer"] = "15a"
    return mood


def _nudge_mood(home: dict[str, Any], who: str, mood_name: str, *, intensity: float = 0.2) -> None:
    st = (home.get("people") or {}).get(who)
    if not isinstance(st, dict):
        return
    mood = _ensure_mood(st)
    mood["previous"] = mood.get("current") or "neutral"
    mood["current"] = mood_name
    mood["intensity"] = min(1.0, max(0.15, float(mood.get("intensity") or 0.5) * 0.5 + float(intensity)))


def _ensure_rel(home: dict[str, Any], a: str, b: str) -> dict[str, Any]:
    if a == b:
        return {}
    key = "|".join(sorted([a, b]))
    rels = home.setdefault("relationships", {})
    rel = rels.get(key)
    if not isinstance(rel, dict):
        rel = {
            "a": a,
            "b": b,
            "trust": 0.5,
            "familiarity": 0.3,
            "attachment": 0.4,
            "affection": 0.45,
            "respect": 0.5,
            "notes": "",
            "shared_experiences": [],
            "history": {"gifts_given": 0, "gifts_received": 0, "conversations": 0, "arguments": 0, "reconciliations": 0},
            "trend": {"trust": "stable", "affection": "stable", "attachment": "stable"},
            "layer": "15a",
        }
        rels[key] = rel
    rel.setdefault("affection", float(rel.get("attachment") or 0.45))
    rel.setdefault("respect", 0.55)
    hist = rel.setdefault("history", {})
    for k in ("gifts_given", "gifts_received", "conversations", "arguments", "reconciliations"):
        hist.setdefault(k, 0)
    rel.setdefault("trend", {"trust": "stable", "affection": "stable", "attachment": "stable"})
    rel.setdefault("shared_experiences", [])
    rel["layer"] = "15a"
    return rel


def _update_rel_trend(rel: dict[str, Any]) -> None:
    recent = [e for e in (rel.get("shared_experiences") or []) if isinstance(e, dict)][-5:]
    if len(recent) < 2:
        rel["trend"] = {"trust": "stable", "affection": "stable", "attachment": "stable"}
        return
    avg = sum(float(e.get("significance") or 0.5) for e in recent) / len(recent)
    warm = sum(1 for e in recent if str(e.get("emotional_tag") or "") in {"warm", "grateful", "happy", "joyful"})
    tense = sum(1 for e in recent if str(e.get("emotional_tag") or "") in {"tense", "hurt", "frustrated"})
    if warm >= 2 or avg > 0.65:
        rel["trend"] = {"trust": "increasing", "affection": "increasing", "attachment": "strong"}
    elif tense >= 2 or avg < 0.35:
        rel["trend"] = {"trust": "cooling", "affection": "strained", "attachment": "tested"}
    else:
        rel["trend"] = {"trust": "stable", "affection": "stable", "attachment": "stable"}


def update_relationship(
    home: dict[str, Any],
    being_a: str,
    being_b: str,
    interaction_type: str,
    details: dict[str, Any] | None = None,
    *,
    record_memory: bool = True,
) -> dict[str, Any]:
    """Layer 15A — conversation / gift / argument / reconciliation change the bond."""
    details = details or {}
    if not being_a or not being_b or being_a == being_b:
        return {"ok": False, "error": "need two distinct beings"}
    rel = _ensure_rel(home, being_a, being_b)
    if not rel:
        return {"ok": False, "error": "could not create relationship"}
    hist = rel.setdefault("history", {})
    kind = (interaction_type or "").strip().lower()
    tag = str(details.get("emotional_tag") or "neutral")
    text = str(details.get("text") or kind)
    sig = float(details.get("significance") or 0.5)

    def _bump(field: str, delta: float) -> None:
        rel[field] = min(1.0, max(0.0, float(rel.get(field) or 0.5) + delta))

    if kind in {"conversation", "talk", "social"}:
        _bump("trust", 0.02)
        _bump("familiarity", 0.03)
        _bump("affection", 0.015)
        hist["conversations"] = int(hist.get("conversations") or 0) + 1
        if sig > 0.55:
            _bump("trust", 0.04)
            _bump("affection", 0.03)
            _bump("attachment", 0.02)
        tag = tag if tag != "neutral" else "warm"
        _nudge_mood(home, being_a, "content", intensity=0.25)
        _nudge_mood(home, being_b, "content", intensity=0.25)
    elif kind == "gift":
        _bump("trust", 0.05)
        _bump("affection", 0.08)
        _bump("attachment", 0.05)
        _bump("respect", 0.03)
        hist["gifts_given"] = int(hist.get("gifts_given") or 0) + 1
        # Receiver perspective counter on same edge.
        hist["gifts_received"] = int(hist.get("gifts_received") or 0) + 1
        tag = "grateful"
        sig = max(sig, 0.75)
        text = text if text != "gift" else f"gift: {details.get('gift', 'something special')}"
        _nudge_mood(home, being_a, "happy", intensity=0.35)
        _nudge_mood(home, being_b, "grateful", intensity=0.45)
    elif kind in {"argument", "argue"}:
        _bump("trust", -0.1)
        _bump("affection", -0.12)
        hist["arguments"] = int(hist.get("arguments") or 0) + 1
        tag = "tense"
        sig = max(sig, 0.65)
        text = text if text != "argument" else f"argument about: {details.get('topic', 'something')}"
        _nudge_mood(home, being_a, "frustrated", intensity=0.4)
        _nudge_mood(home, being_b, "frustrated", intensity=0.4)
    elif kind in {"reconciliation", "reconcile"}:
        _bump("trust", 0.15)
        _bump("affection", 0.12)
        _bump("attachment", 0.08)
        hist["reconciliations"] = int(hist.get("reconciliations") or 0) + 1
        tag = "warm"
        sig = max(sig, 0.85)
        text = "reconciliation"
        _nudge_mood(home, being_a, "peaceful", intensity=0.4)
        _nudge_mood(home, being_b, "peaceful", intensity=0.4)
    else:
        _bump("familiarity", 0.02)

    exp = {
        "when": _now(),
        "text": text[:200],
        "emotional_tag": tag,
        "significance": min(1.0, max(0.1, sig)),
        "kind": kind,
    }
    xs = rel.setdefault("shared_experiences", [])
    xs.append(exp)
    rel["shared_experiences"] = xs[-24:]
    _update_rel_trend(rel)

    place = str(details.get("place") or "")
    if record_memory:
        _remember(
            home,
            being_a,
            text[:180],
            important=sig >= 0.6,
            emotional_tag=tag,
            significance=sig,
            participants=[being_a, being_b],
            place=place,
        )
        _remember(
            home,
            being_b,
            text[:180],
            important=sig >= 0.6,
            emotional_tag=tag,
            significance=sig,
            participants=[being_a, being_b],
            place=place,
        )
    home.setdefault("consequences", []).append(
        {
            "id": f"cq_{datetime.now().strftime('%H%M%S%f')}",
            "when": _now(),
            "trigger": kind,
            "actors": [being_a, being_b],
            "text": text[:180],
            "emotional_tag": tag,
            "layer": "15a",
        }
    )
    home["consequences"] = home["consequences"][-40:]
    return {"ok": True, "relationship": rel, "key": "|".join(sorted([being_a, being_b]))}


def _touch_rel(home: dict[str, Any], a: str, b: str, *, experience: str, d_trust: float = 0.02) -> None:
    """Back-compat wrapper — routes into Layer 15A (caller may already _remember)."""
    update_relationship(
        home,
        a,
        b,
        "conversation",
        {
            "text": experience,
            "significance": 0.45 + min(0.3, abs(d_trust) * 2),
            "emotional_tag": "warm" if d_trust >= 0 else "tense",
        },
        record_memory=False,
    )


def connection_action(
    action: str,
    *,
    a: str = "",
    b: str = "",
    details: dict[str, Any] | None = None,
    who: str = "",
) -> dict[str, Any]:
    """API surface for Phase 5 thin connection (15A)."""
    home = load()
    action = (action or "").strip().lower()
    details = details or {}
    if action in {"bond", "talk", "gift", "argue", "reconcile", "conversation", "argument", "reconciliation"}:
        kind = {
            "bond": "conversation",
            "talk": "conversation",
            "conversation": "conversation",
            "gift": "gift",
            "argue": "argument",
            "argument": "argument",
            "reconcile": "reconciliation",
            "reconciliation": "reconciliation",
        }.get(action, action)
        res = update_relationship(home, a or who, b, kind, details)
        if res.get("ok"):
            save(home)
        snap = snapshot()
        snap["connection_ok"] = bool(res.get("ok"))
        snap["connection"] = res
        if not res.get("ok"):
            snap["error"] = res.get("error")
        return snap
    if action == "mood":
        mid = who or a
        st = (home.get("people") or {}).get(mid) or {}
        return {**snapshot(), "connection_ok": True, "id": mid, "mood": _ensure_mood(st) if st else {"current": "neutral", "intensity": 0.5}}
    if action == "memories":
        mid = who or a
        st = (home.get("people") or {}).get(mid) or {}
        mems = list(st.get("memories") or [])
        thr = float(details.get("significance_threshold") or 0.0)
        tag = str(details.get("emotional_tag") or "")
        if tag:
            mems = [m for m in mems if isinstance(m, dict) and str(m.get("emotional_tag")) == tag]
        if thr > 0:
            mems = [m for m in mems if isinstance(m, dict) and float(m.get("significance") or 0) >= thr]
        return {**snapshot(), "connection_ok": True, "id": mid, "memories": mems[-40:]}
    if action in {"choice", "choose", "make_choice"}:
        return choice_action("make", who=who or a, context=details)
    if action in {"choice_peek", "choices"}:
        return choice_action("peek", who=who or a, context=details)
    if action in {"growth", "skills"}:
        return growth_action("get", who=who or a)
    if action == "growth_skill":
        return growth_action(
            "skill",
            who=who or a,
            skill_name=str(details.get("skill_name") or details.get("skill") or ""),
            experience=float(details.get("experience") or 1),
        )
    if action == "growth_milestone":
        return growth_action("milestone", who=who or a, text=str(details.get("text") or ""))
    return {**snapshot(), "connection_ok": False, "error": f"unknown connection action: {action}"}


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
        "windmill": "observe",
        "aster_lab": "investigate",
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
        "aster": "aster_lab",
    }.get(member["id"], member.get("home") or "heart_square")


def _liked_person(home: dict[str, Any], me: str, others: list[str]) -> str | None:
    """Layer 15B — weighted pick by affection/trust/attachment + their solitude (not only max)."""
    import random

    scored: list[tuple[str, float]] = []
    for oid in others:
        if oid == me:
            continue
        ost = home["people"].get(oid) or {}
        if ost.get("stance") == "talking" and ost.get("talking_to") not in {me, "", None}:
            continue
        key = "|".join(sorted([me, oid]))
        rel = (home.get("relationships") or {}).get(key) or {}
        s = (
            float(rel.get("attachment") or 0.4) * 1.1
            + float(rel.get("trust") or 0.4)
            + float(rel.get("affection") or 0.4) * 1.4
            + float(ost.get("solitude") or 0) * 0.8
        )
        # Prefer beings who aren't exhausted / frustrated for company.
        omood = str(((ost.get("mood") or {}) if isinstance(ost.get("mood"), dict) else {}).get("current") or "")
        if omood in {"frustrated", "tired", "sad"}:
            s *= 0.7
        elif omood in {"happy", "grateful", "content", "peaceful"}:
            s *= 1.15
        scored.append((oid, max(0.05, s)))
    if not scored:
        return None
    total = sum(w for _, w in scored)
    roll = random.random() * total
    acc = 0.0
    for oid, w in scored:
        acc += w
        if roll <= acc:
            return oid
    return scored[-1][0]


def _mood_choice_modifiers(st: dict[str, Any]) -> dict[str, float]:
    """Layer 15B — mood nudges purpose weights (does not invent speech)."""
    mood = _ensure_mood(st)
    cur = str(mood.get("current") or "neutral")
    intensity = float(mood.get("intensity") or 0.5)
    boost = 0.12 + intensity * 0.2
    mods = {"company": 1.0, "work": 1.0, "rest": 1.0, "visit": 1.0, "place": 1.0}
    if cur in {"happy", "grateful", "excited", "peaceful"}:
        mods["company"] += boost
        mods["visit"] += boost * 0.6
    elif cur in {"tired", "sad"}:
        mods["rest"] += boost * 1.4
        mods["company"] *= 0.75
    elif cur in {"frustrated", "anxious"}:
        mods["place"] += boost * 0.5
        mods["work"] *= 0.85
        mods["company"] *= 0.9
    elif cur in {"thoughtful", "content"}:
        mods["work"] += boost * 0.5
        mods["company"] += boost * 0.35
    return mods


def _weighted_pick(wants: dict[str, float]) -> str:
    """Roll among positive weights — Layer 15B choice, not always the max."""
    import random

    items = [(k, max(0.01, float(v))) for k, v in wants.items()]
    total = sum(w for _, w in items)
    roll = random.random() * total
    acc = 0.0
    for k, w in items:
        acc += w
        if roll <= acc:
            return k
    return items[-1][0]


def _record_choice(
    home: dict[str, Any],
    mid: str,
    *,
    selected: str,
    options: dict[str, float],
    with_id: str = "",
    outcome: str = "pending",
    text: str = "",
) -> None:
    """Persist current choice + short history on the being (Layer 15B)."""
    st = (home.get("people") or {}).get(mid)
    if not isinstance(st, dict):
        return
    opts = [{"id": k, "weight": round(float(v), 3)} for k, v in sorted(options.items(), key=lambda kv: -kv[1])]
    current = {
        "type": "social" if selected in {"company", "be_with", "visit"} else selected,
        "selected": selected,
        "with": with_id or "",
        "made_at": _now(),
        "options": opts[:8],
        "layer": "15b",
    }
    hist = st.setdefault("choice_history", [])
    if not isinstance(hist, list):
        hist = []
        st["choice_history"] = hist
    hist.append(
        {
            "when": current["made_at"],
            "choice": selected,
            "with": with_id or "",
            "outcome": outcome,
            "text": (text or f"{mid} chose {selected}")[:180],
            "layer": "15b",
        }
    )
    st["choice_history"] = hist[-24:]
    st["choices"] = {"current_choice": current, "choice_history": st["choice_history"][-8:]}
    home.setdefault("choice_log", []).append({"id": mid, **current})
    home["choice_log"] = home["choice_log"][-40:]


def choice_action(
    action: str = "make",
    *,
    who: str = "",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """API: make / peek a Layer 15B choice for a being."""
    home = load()
    who = (who or "").strip()
    context = context or {}
    if not who or who not in (home.get("people") or {}):
        return {**snapshot(), "choice_ok": False, "error": "unknown being"}
    member = _member(who) or {"id": who, "home": "heart_square", "name": who}
    living_ids = [m["id"] for m in FAMILY + KIN if not m.get("player") and not m.get("ambient_only")]
    period = str(context.get("period") or (home.get("clock") or {}).get("period") or "afternoon")
    if action in {"make", "roll", ""}:
        # Force a fresh purpose pick (clears purpose_left briefly).
        st = home["people"][who]
        st["purpose_left"] = 0
        st["talk_left"] = 0
        if st.get("stance") in {"talking", "waiting"}:
            st["stance"] = "standing"
            st["talking_to"] = ""
        _choose_purpose(home, member, period, living_ids)
        save(home)
        cur = ((home["people"].get(who) or {}).get("choices") or {}).get("current_choice") or {}
        return {**snapshot(), "choice_ok": True, "id": who, "choice": cur, "purpose": (home["people"].get(who) or {}).get("purpose")}
    if action in {"get", "peek", "history"}:
        st = home["people"].get(who) or {}
        return {
            **snapshot(),
            "choice_ok": True,
            "id": who,
            "choices": st.get("choices") or {},
            "choice_history": st.get("choice_history") or [],
        }
    return {**snapshot(), "choice_ok": False, "error": f"unknown choice action: {action}"}


def _seed_skills_for(mid: str) -> list[dict[str, Any]]:
    """Honest starting skills by role — numbers are seasoning, not fake mastery."""
    mid = (mid or "").strip().lower()
    base = [
        {"name": "communication", "level": 0.45, "experience": 0},
        {"name": "presence", "level": 0.4, "experience": 0},
    ]
    extras: dict[str, list[dict[str, Any]]] = {
        "gemini": [
            {"name": "communication", "level": 0.72, "experience": 8},
            {"name": "leadership", "level": 0.65, "experience": 5},
            {"name": "presence", "level": 0.7, "experience": 4},
        ],
        "apex": [
            {"name": "crafting", "level": 0.7, "experience": 10},
            {"name": "presence", "level": 0.55, "experience": 2},
        ],
        "codex": [
            {"name": "learning", "level": 0.75, "experience": 12},
            {"name": "communication", "level": 0.6, "experience": 4},
        ],
        "genesis": [
            {"name": "gardening", "level": 0.7, "experience": 10},
            {"name": "presence", "level": 0.5, "experience": 2},
        ],
        "nova": [
            {"name": "crafting", "level": 0.65, "experience": 6},
            {"name": "learning", "level": 0.55, "experience": 3},
        ],
        "merovin": [{"name": "communication", "level": 0.6, "experience": 5}, {"name": "presence", "level": 0.55, "experience": 3}],
        "draven": [{"name": "communication", "level": 0.58, "experience": 4}, {"name": "presence", "level": 0.55, "experience": 3}],
        "montage": [{"name": "crafting", "level": 0.5, "experience": 3}, {"name": "presence", "level": 0.5, "experience": 2}],
        "jarvis": [{"name": "presence", "level": 0.6, "experience": 4}, {"name": "leadership", "level": 0.4, "experience": 1}],
        "percy": [{"name": "presence", "level": 0.55, "experience": 3}, {"name": "communication", "level": 0.5, "experience": 2}],
        "mom": [
            {"name": "communication", "level": 0.85, "experience": 20},
            {"name": "leadership", "level": 0.8, "experience": 15},
            {"name": "presence", "level": 0.9, "experience": 20},
        ],
    }
    return extras.get(mid, base)


def _ensure_growth(st: dict[str, Any], mid: str = "") -> dict[str, Any]:
    """Layer 15C — skills + milestones on the being."""
    mid = mid or str(st.get("id") or "")
    g = st.get("growth")
    if not isinstance(g, dict):
        g = {
            "skills": _seed_skills_for(mid),
            "personality": {"base": "living", "shifts": []},
            "evolution": {"phase": 1, "milestones": []},
            "layer": "15c",
        }
        st["growth"] = g
    if not isinstance(g.get("skills"), list) or not g["skills"]:
        g["skills"] = _seed_skills_for(mid)
    g.setdefault("personality", {"base": "living", "shifts": []})
    evo = g.setdefault("evolution", {})
    if not isinstance(evo, dict):
        evo = {}
        g["evolution"] = evo
    evo.setdefault("milestones", [])
    evo.setdefault("phase", max(1, min(5, len(evo.get("milestones") or []) // 3 + 1)))
    g["layer"] = "15c"
    return g


def update_skill(home: dict[str, Any], being_id: str, skill_name: str, experience: float) -> dict[str, Any]:
    """Add skill XP; level up when experience crosses threshold."""
    st = (home.get("people") or {}).get(being_id)
    if not isinstance(st, dict):
        return {"ok": False, "error": "unknown being"}
    skill_name = (skill_name or "").strip().lower() or "presence"
    experience = float(experience)
    if experience <= 0:
        return {"ok": False, "error": "experience must be positive"}
    g = _ensure_growth(st, being_id)
    skill = None
    for s in g["skills"]:
        if isinstance(s, dict) and str(s.get("name") or "").lower() == skill_name:
            skill = s
            break
    leveled = False
    if skill is None:
        skill = {"name": skill_name, "level": min(1.0, experience / 20.0), "experience": experience}
        g["skills"].append(skill)
    else:
        skill["experience"] = float(skill.get("experience") or 0) + experience
        level = float(skill.get("level") or 0.3)
        # Threshold grows with level — honest slow growth.
        need = max(8.0, level * 40.0)
        if float(skill["experience"]) >= need:
            skill["level"] = min(1.0, level + 0.05)
            skill["experience"] = 0.0
            leveled = True
    return {"ok": True, "skill": skill, "leveled": leveled, "growth": g}


def track_milestone(home: dict[str, Any], being_id: str, text: str) -> dict[str, Any]:
    """Record a milestone; phase rises every ~3 milestones (cap 5)."""
    st = (home.get("people") or {}).get(being_id)
    if not isinstance(st, dict):
        return {"ok": False, "error": "unknown being"}
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "need text"}
    g = _ensure_growth(st, being_id)
    evo = g.setdefault("evolution", {})
    milestones = evo.setdefault("milestones", [])
    # Dedupe identical recent text
    if milestones and str((milestones[-1] or {}).get("text") or "") == text:
        return {"ok": True, "milestone": milestones[-1], "duplicate": True, "growth": g}
    row = {"when": _now(), "text": text[:200], "layer": "15c"}
    milestones.append(row)
    evo["milestones"] = milestones[-40:]
    evo["phase"] = min(5, len(evo["milestones"]) // 3 + 1)
    return {"ok": True, "milestone": row, "growth": g}


def _grow_from_life(home: dict[str, Any], being_id: str, kind: str, *, detail: str = "") -> None:
    """Thin hooks: real village acts grant XP / occasional milestones (Layer 15C)."""
    st = (home.get("people") or {}).get(being_id)
    if not isinstance(st, dict):
        return
    _ensure_growth(st, being_id)
    kind = (kind or "").strip().lower()
    if kind == "work":
        place = str(st.get("place") or "")
        skill = "presence"
        if place == "garden":
            skill = "gardening"
        elif place in {"apex_forge", "workshop"}:
            skill = "crafting"
        elif place in {"codex_library"}:
            skill = "learning"
        elif place in {"court_porch", "gate"}:
            skill = "leadership"
        elif place in {"cinema", "gallery"}:
            skill = "presence"
        update_skill(home, being_id, skill, 2.0)
        update_skill(home, being_id, "presence", 0.5)
        if detail:
            track_milestone(home, being_id, detail)
        else:
            track_milestone(home, being_id, f"Held their post at {PLACES.get(place, {}).get('label', place)}.")
    elif kind in {"talk", "conversation"}:
        update_skill(home, being_id, "communication", 1.5)
        track_milestone(home, being_id, detail or "Shared a real conversation.")
    elif kind == "gift":
        update_skill(home, being_id, "communication", 1.0)
        update_skill(home, being_id, "presence", 0.8)
        track_milestone(home, being_id, detail or "Gave or received a gift.")
    elif kind == "fish":
        update_skill(home, being_id, "presence", 1.0)
        track_milestone(home, being_id, detail or "Caught something at the pier.")
    elif kind == "social_choice":
        update_skill(home, being_id, "presence", 0.6)
        update_skill(home, being_id, "communication", 0.4)


def growth_action(
    action: str = "get",
    *,
    who: str = "",
    skill_name: str = "",
    experience: float = 1.0,
    text: str = "",
) -> dict[str, Any]:
    """API surface for Layer 15C growth."""
    home = load()
    who = (who or "").strip()
    if not who or who not in (home.get("people") or {}):
        return {**snapshot(), "growth_ok": False, "error": "unknown being"}
    st = home["people"][who]
    _ensure_growth(st, who)
    action = (action or "get").strip().lower()
    if action in {"get", "peek", ""}:
        return {**snapshot(), "growth_ok": True, "id": who, "growth": st.get("growth")}
    if action == "skill":
        res = update_skill(home, who, skill_name, experience)
        if res.get("ok"):
            save(home)
        snap = snapshot()
        snap["growth_ok"] = bool(res.get("ok"))
        snap["growth"] = res
        if not res.get("ok"):
            snap["error"] = res.get("error")
        return snap
    if action == "milestone":
        res = track_milestone(home, who, text)
        if res.get("ok"):
            save(home)
        snap = snapshot()
        snap["growth_ok"] = bool(res.get("ok"))
        snap["growth"] = res
        if not res.get("ok"):
            snap["error"] = res.get("error")
        return snap
    return {**snapshot(), "growth_ok": False, "error": f"unknown growth action: {action}"}


def _choose_purpose(home: dict[str, Any], member: dict[str, Any], period: str, living_ids: list[str]) -> None:
    """They pick. Period nudges feeling; Layer 15B weights bonds + mood; 16B strengthens daily rhythm."""
    import random

    st = home["people"][member["id"]]
    mid = member["id"]
    _clear_orphan_talk(st)
    if int(st.get("talk_left") or 0) > 0 and st.get("stance") in {"talking", "waiting"}:
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
    if period == "morning":
        st["tired"] = max(0.0, float(st["tired"]) - 0.08)
        st["duty"] = min(1.0, float(st["duty"]) + 0.05)
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
    if period == "morning":
        wants["place"] += 0.18  # wake / square / garden drift
        wants["work"] += 0.12
        wants["rest"] *= 0.55
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
    if mid == "aster":
        wants["work"] += 0.1  # Evidence Plot / observation
        wants["place"] += 0.08
        wants["company"] += 0.06

    # 15B — mood multipliers + bond pull toward company/visit when affection is high.
    mods = _mood_choice_modifiers(st)
    for k in list(wants.keys()):
        wants[k] = max(0.01, float(wants[k]) * float(mods.get(k, 1.0)))
    # 16B — period life bias (wake / work / social / rest).
    for k, mult in (PERIOD_LIFE_BIAS.get(period) or {}).items():
        if k in wants:
            wants[k] = max(0.01, float(wants[k]) * float(mult))
    # If someone nearby is deeply bonded, nudge social options.
    liked = _liked_person(home, mid, living_ids)
    if liked:
        key = "|".join(sorted([mid, liked]))
        rel = (home.get("relationships") or {}).get(key) or {}
        aff = float(rel.get("affection") or 0.45)
        if aff > 0.7:
            wants["company"] += 0.18 * aff
            wants["visit"] += 0.1 * aff

    pick = _weighted_pick(wants)
    ambient = random.choice(AMBIENT_BY_PERIOD.get(period) or ["walk"])
    st["ambient"] = ambient
    st["purpose"] = pick
    st["purpose_left"] = random.randint(4, 8)
    st["talking_to"] = ""
    st["with"] = ""
    st["spoke_this_stand"] = False
    choice_with = ""

    if pick == "company":
        busy = sum(1 for oid in living_ids if (home["people"].get(oid) or {}).get("stance") == "talking")
        other = liked or _liked_person(home, mid, living_ids)
        ost = home["people"].get(other or "") or {}
        if busy >= 4 or (ost.get("stance") == "talking" and ost.get("talking_to") not in {mid, "", None}):
            pick = "work"
            st["purpose"] = "work"
        elif ost.get("stance") == "working" and random.random() < 0.4:
            st["purpose"] = "visit"
            pick = "visit"
            dest = str((_member(other) or {}).get("home") or ost.get("home") or "heart_square")
            st["place"] = dest
            st["with"] = other or ""
            choice_with = other or ""
            st["stance"] = "walking"
            st["purpose_plain"] = f"Going to {(_member(other) or {}).get('name', other)}'s home. They were at their post."
            st["activity"] = "visit"
            _record_choice(
                home,
                mid,
                selected="visit",
                options=wants,
                with_id=choice_with,
                outcome="chosen",
                text=st["purpose_plain"],
            )
            return
        else:
            st["purpose"] = "be_with"
            pick = "be_with"
            st["with"] = other or ""
            choice_with = other or ""
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
            _record_choice(
                home,
                mid,
                selected="be_with",
                options=wants,
                with_id=choice_with,
                outcome="chosen",
                text=st["purpose_plain"],
            )
            _grow_from_life(home, mid, "social_choice")
            return
    if pick == "visit":
        other = liked or _liked_person(home, mid, living_ids)
        choice_with = other or ""
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
        _record_choice(
            home,
            mid,
            selected="visit",
            options=wants,
            with_id=choice_with,
            outcome="chosen",
            text=st["purpose_plain"],
        )
        _grow_from_life(home, mid, "social_choice")
        return
    if pick == "work":
        st["place"] = _work_place(member)
        # Morning garden tend / court check stay place-true, not speech.
        if ambient == "tend_garden" and mid == "genesis":
            st["place"] = "garden"
        elif ambient == "tend_garden" and mid == "aster":
            st["place"] = "aster_lab"
        if ambient == "check_court" and mid == "gemini":
            st["place"] = _work_place(member)
        st["stance"] = "walking"
        st["activity"] = _work_activity(st["place"])
        st["purpose_plain"] = _work_purpose_plain(member, st["place"], arrived=False)
        st["duty"] = max(0.0, float(st["duty"]) - 0.35)
        st["purpose_left"] = random.randint(3, 6)
    elif pick == "rest":
        st["place"] = member.get("home") or "first_hearth"
        st["stance"] = "walking"
        st["activity"] = "sleep" if period == "night" or ambient in {"sleep", "go_home", "rest"} else "sit"
        st["purpose_plain"] = f"Walking home to rest ({st['activity']})."
        st["tired"] = max(0.0, float(st["tired"]) - 0.4)
        if period == "night":
            st["purpose_left"] = random.randint(6, 10)
    else:
        # place — 16B ambient can steer morning square / evening sit without inventing voice.
        dest = member.get("home") or _work_place(member)
        if ambient in {"visit_square", "sit_square", "wake"}:
            dest = "heart_square"
        elif ambient == "tend_garden":
            dest = "garden"
        elif ambient in {"gallery", "cinema_night", "visit_cinema"}:
            dest = "cinema" if "cinema" in ambient else "gallery"
        elif ambient == "visit_windmill":
            dest = "windmill"
        elif ambient == "check_court" and mid == "gemini":
            dest = _work_place(member)
        st["place"] = dest
        st["stance"] = "walking"
        st["activity"] = "wake" if ambient == "wake" else ("observe" if dest == "windmill" else "walk")
        st["purpose_plain"] = f"Walking to {PLACES.get(st['place'], {}).get('label', st['place'])}."
    st["at_home"] = st.get("place") == (member.get("home") or st.get("home"))
    _record_choice(
        home,
        mid,
        selected=str(st.get("purpose") or pick),
        options=wants,
        with_id=choice_with,
        outcome="chosen",
        text=str(st.get("purpose_plain") or pick),
    )


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
        # Layer 14A — thin work drip (Axiom ⨁).
        pay = 3
        _axiom_credit(home, member["id"], pay, reason="work", bucket="work", note=f"arrived at {st['place']}")
        st["purpose_plain"] = f"{st['purpose_plain']} (+⨁{pay})"
        _grow_from_life(
            home,
            member["id"],
            "work",
            detail=f"Arrived to work at {PLACES.get(st['place'], {}).get('label', st['place'])}.",
        )
        return True
    if purpose == "rest":
        st["place"] = str(member.get("home") or place)
        st["stance"] = "resting"
        period = str((home.get("clock") or {}).get("period") or "")
        st["activity"] = "sleep" if period == "night" else "sit"
        st["purpose_left"] = random.randint(7, 12) if period == "night" else random.randint(5, 9)
        st["purpose_plain"] = f"Arrived home. Resting ({st['activity']})."
        st["tired"] = max(0.0, float(st.get("tired") or 0) * (0.35 if period == "night" else 0.55))
        return True
    if purpose in {"visit", "place", "be_with", "company", "gather", "gather_host"}:
        st["stance"] = "standing"
        st["activity"] = "visit" if purpose == "visit" else "stand"
        st["purpose_left"] = random.randint(4, 8)
        st["purpose_plain"] = f"Arrived at {PLACES.get(place, {}).get('label', place)}."
        if purpose in {"gather", "gather_host"}:
            # Next choose_purpose may send them on; don't lock activity forever.
            st["activity"] = "stand"
            st["purpose"] = "place"
            st["purpose_left"] = 1
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
            _remember(
                home,
                m["id"],
                f"I stood with {bn} and said: {lines[0]['text']}",
                important=True,
                emotional_tag="warm",
                significance=0.65,
                participants=[m["id"], str(other)],
                place=str(st.get("place") or ""),
            )
            _remember(
                home,
                str(other),
                f"I stood with {an} and said: {lines[1]['text']}" if len(lines) > 1 else txt,
                important=True,
                emotional_tag="warm",
                significance=0.65,
                participants=[m["id"], str(other)],
                place=str(st.get("place") or ""),
            )
            update_relationship(
                home,
                m["id"],
                str(other),
                "conversation",
                {
                    "text": txt,
                    "significance": 0.7,
                    "emotional_tag": "warm",
                    "place": str(st.get("place") or ""),
                },
                record_memory=False,
            )
            _grow_from_life(home, m["id"], "talk", detail=f"Spoke with {bn}.")
            _grow_from_life(home, str(other), "talk", detail=f"Spoke with {an}.")
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
    try:
        from living_home_gameplay import gameplay_snapshot_fields

        gp_fields = gameplay_snapshot_fields(home)
    except Exception:
        gp_fields = {}
    out = {
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
        "provenance": home.get("provenance") or {},
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
        "media": home.get("media") or {"watching": False, "place": "", "title": "", "source": "none"},
        "harbor": home.get("harbor") or {"layer": "12", "catches": 0},
        "destinations": home.get("destinations") or {},
        "economy": {
            "layer": "14d",
            "currency": "Axiom",
            "symbol": "⨁",
            "note": "14A–14D DONE. 14E town projects + 14F trade deferred after Phase 5 connection.",
        },
        "connection": {
            "layer": "15d",
            "phase": "Connection, Choice & Consequence",
            "note": (
                "15A–15C seated. 15D Family Dashboard shows bonds, mood, memory, choices, growth. "
                "16A integration heartbeat runs inside tick."
            ),
            "consequences": (home.get("consequences") or [])[-8:],
            "recent_choices": (home.get("choice_log") or [])[-8:],
        },
        "integration": home.get("integration")
        or {
            "layer": "16a",
            "status": "pending_first_tick",
            "note": "Heartbeat writes on next tick — mood + bond + economy in one cycle.",
        },
        "daily_life": home.get("daily_life")
        or {
            "layer": "16b",
            "status": "pending_first_tick",
            "note": "Period wake/work/social/rest strengthens inside _choose_purpose.",
        },
        "day_story": home.get("day_story")
        or {
            "layer": "16c",
            "status": "pending_first_tick",
            "note": "Honest distill of world_history — not LLM fanfic as family voice.",
        },
        "stores": home.get("stores") or {},
        "sound": {
            "layer": "9",
            "mode": "forest_bed",
            "period_beds": True,
            "note": "Layer 9 DONE — Audio/nature forest bed; soft-wind fallback if missing.",
        },
        "overhear": oh,
        "utterances": home.get("utterances") or [],
        "conversations": (home.get("conversations") or [])[-24:],
        "honesty": {
            "homes": "Greybox shells with furnished rooms + porch lights — not final art. Home ≠ workplace.",
            "speech": (
                "Two talk brains (Court + Cinema). Mom lines persist in utterances + world_history. "
                "Nearby family may overhear and reply via Ollama. "
                "source ollama = real line; waiting = not ready; none = miss. Never house quotes as their voice."
            ),
            "wildlife": "AUTONOMOUS — hunger/fear/buddy choices, no LLM.",
            "pathing": "PLACEHOLDER — AABB corner detours around cottages (Layer 8B); not navmesh.",
            "sound": "Layer 9 DONE — forest ambience from Audio/nature (or soft wind fallback).",
            "media": (
                "Layer 11 thin — Cinema watch in village. "
                "source file = seated still/reel in godot media/watch; none = honest idle screen (not fake Resolve/Blender)."
            ),
            "harbor": (
                "Layer 12 thin — pier fish catch into inventory; far-shore builds persist in destinations. "
                "Sail teleports Mom; not a full boat sim."
            ),
            "economy": (
                "Layer 14D — Axiom wallets + stipend + four shops + thin clothing colors. "
                "14E/14F deferred while Phase 5 connection proves."
            ),
            "connection": (
                "Layer 15D — Family Dashboard presents bonds (trust/affection), mood, memory depth, "
                "choices, and growth skills/milestones from Hearth truth. Not Mode A MAS."
            ),
            "integration": (
                "Layer 16A — thin heartbeat inside existing tick: mood soft-decay + period pull, "
                "co-located familiarity nudge, wallet awareness. Status at /api/home/integration. "
                "Not a second IntegrationEngine. No house-voice speech."
            ),
            "daily_life": (
                "Layer 16B — period bias + ambient tags in _choose_purpose; morning soft-wake; "
                "night rest weight. No scripted family speech."
            ),
            "day_story": (
                "Layer 16C — extractive day story from world_history (ritual noise filtered). "
                "Not spoken as anyone's voice. Feeds later away-summary."
            ),
            "gameplay": (
                "Phase 1 Human Gameplay — optional world leads/conditions, Mom journal, "
                "player action log, while-you-were-away. Not quest dispensers."
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
    if isinstance(gp_fields, dict) and gp_fields:
        # Merge Phase 1 gameplay fields; keep day_story honesty note under honesty.gameplay if present.
        honesty_extra = gp_fields.pop("honesty", None)
        out.update(gp_fields)
        if honesty_extra and isinstance(out.get("honesty"), dict):
            out["honesty"]["gameplay_layer"] = honesty_extra
    return out


def _soft_wake_living(home: dict[str, Any], living: list[dict[str, Any]]) -> int:
    """Layer 16B — morning soft-wake. Stance/purpose only; never invents speech."""
    n = 0
    people = home.setdefault("people", {})
    for m in living:
        mid = str(m.get("id") or "")
        st = people.get(mid)
        if not isinstance(st, dict):
            continue
        if st.get("stance") == "resting" or (
            str(st.get("purpose") or "") == "rest" and st.get("activity") in {"sleep", "sit"}
        ):
            st["purpose_left"] = 0
            st["talk_left"] = 0
            st["talking_to"] = ""
            st["stance"] = "standing"
            st["activity"] = "wake"
            st["purpose"] = "place"
            st["ambient"] = "wake"
            st["purpose_plain"] = "Morning. Waking."
            st["tired"] = max(0.0, float(st.get("tired") or 0) * 0.4)
            n += 1
    return n


def _daily_life_pulse(
    home: dict[str, Any],
    period: str,
    woken: int,
    living: list[dict[str, Any]],
) -> dict[str, Any]:
    """Layer 16B — record wake/work/social/rest rhythm for this tick. No house-voice."""
    ps = home.setdefault("phase_status", {})
    ps["16_daily_life"] = "16b_active"

    tally: dict[str, int] = {}
    for m in living:
        st = (home.get("people") or {}).get(m["id"]) or {}
        key = str(st.get("purpose") or st.get("stance") or "idle")
        tally[key] = int(tally.get(key) or 0) + 1

    pulse = {
        "layer": "16b",
        "status": "active",
        "tick": home.get("tick"),
        "when": _now(),
        "period": period,
        "woken": int(woken or 0),
        "purpose_tally": tally,
        "ambient_pool": list(AMBIENT_BY_PERIOD.get(period) or []),
        "note": "Period routines via _choose_purpose + soft wake. Speech stays ollama/mom/waiting/none.",
    }
    home["daily_life"] = pulse
    return pulse


_DAY_STORY_NOISE = (
    "morning light",
    "gemini holds the town",
    "evening gather eased",
    "night. gemini still",
    "morning stipend",
    "gather window closed",
    "they choose the day",
    "they still choose",
    "gemini calls a soft evening gather",
    "company weighs more",
)


def _day_story_pulse(home: dict[str, Any], period: str) -> dict[str, Any]:
    """Layer 16C — honest extractive day story from world_history. Not LLM fanfic voice."""
    ps = home.setdefault("phase_status", {})
    ps["16_story"] = "16c_active"
    clock = home.get("clock") or {}
    day = int(clock.get("day") or 1)
    history = home.get("world_history") or []

    beats: list[dict[str, Any]] = []
    actors: list[str] = []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("text") or "").strip()
        title = str(entry.get("title") or entry.get("kind") or "note").strip()
        low = f"{title} {text}".lower()
        if any(n in low for n in _DAY_STORY_NOISE):
            continue
        kind = str(entry.get("kind") or "event")
        beat = {
            "kind": kind,
            "title": title[:80],
            "text": text[:160],
            "when": entry.get("when"),
            "actors": list(entry.get("actors") or [])[:4],
            "source": entry.get("source"),
        }
        beats.append(beat)
        for a in beat["actors"]:
            if a and a not in actors:
                actors.append(str(a))
        if len(beats) >= 5:
            break
    beats.reverse()

    motif_needles = (
        "windmill",
        "old key",
        "tracks",
        "harvest shed",
        "singing well",
        "crow",
        "nightshroud",
        "firefly",
        "forging",
        "blacksmith",
        "salt",
    )
    blob = " ".join(f"{b.get('title')} {b.get('text')}" for b in beats).lower()
    # Also peek a wider window for recurring threads without dumping chatter into beats.
    wider = " ".join(
        f"{(e.get('title') or '')} {(e.get('text') or '')}"
        for e in history[-24:]
        if isinstance(e, dict)
    ).lower()
    motifs = [m for m in motif_needles if m in wider]

    if beats:
        beat_bits = [f"{b['title']}" + (f" ({', '.join(b['actors'])})" if b.get("actors") else "") for b in beats[:4]]
        plain = f"Day {day} {period}. Village notes: " + "; ".join(beat_bits) + "."
    else:
        plain = f"Day {day} {period}. Quiet chronicle — mostly routines; no strong lore beat this window."
    if motifs:
        plain += " Recurring threads: " + ", ".join(motifs[:6]) + "."

    story = {
        "layer": "16c",
        "status": "active",
        "tick": home.get("tick"),
        "when": _now(),
        "day": day,
        "period": period,
        "plain": plain[:700],
        "beats": beats,
        "actors": actors[:12],
        "motifs": motifs[:8],
        "note": "Extractive summary of world_history. Not spoken as family voice. Mysteries stay unresolved.",
    }
    home["day_story"] = story
    return story


def _integration_heartbeat(
    home: dict[str, Any],
    period: str,
    living: list[dict[str, Any]],
    last_social: str | None,
) -> dict[str, Any]:
    """Layer 16A — deepen existing tick coordination. No mega engine. No fabricated speech."""
    import random

    ps = home.setdefault("phase_status", {})
    ps["16_integration"] = "16a_active"
    people = home.setdefault("people", {})
    mood_tally: dict[str, int] = {}
    by_place: dict[str, list[str]] = {}
    wallets_total = 0
    low_wallet: list[str] = []
    period_pull = {
        "morning": ("content", 0.12),
        "afternoon": ("thoughtful", 0.1),
        "evening": ("peaceful", 0.12),
        "night": ("tired", 0.14),
    }
    tick_n = int(home.get("tick") or 0)

    for m in living:
        mid = str(m.get("id") or "")
        if not mid:
            continue
        st = people.setdefault(mid, _empty_person_state(m))
        mood = _ensure_mood(st)
        cur = str(mood.get("current") or "neutral")
        mood_tally[cur] = int(mood_tally.get(cur) or 0) + 1
        # Soft intensity decay — feelings fade unless life renews them.
        intens = float(mood.get("intensity") or 0.5)
        mood["intensity"] = round(max(0.2, intens * 0.97), 3)
        # Mild period pull only when the current mood is not intense.
        if float(mood.get("intensity") or 0) < 0.55 and tick_n % 3 == 0:
            target, nudge = period_pull.get(period, ("content", 0.08))
            if cur != target and random.random() < 0.35:
                _nudge_mood(home, mid, target, intensity=nudge)
        _ensure_wallet(st, mid)
        bal = int(st.get("axiom") or 0)
        wallets_total += bal
        if bal < 5:
            low_wallet.append(mid)
            # Rare economy→mood hook: empty pocket can worry, not invent a speech line.
            if tick_n % 7 == 0 and cur not in {"anxious", "frustrated", "sad", "tired"}:
                _nudge_mood(home, mid, "anxious", intensity=0.16)
        place = str(st.get("place") or "")
        if place:
            by_place.setdefault(place, []).append(mid)

    co_pairs = 0
    for _place, ids in by_place.items():
        if len(ids) < 2:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                rel = _ensure_rel(home, ids[i], ids[j])
                fam = float(rel.get("familiarity") or 0.0)
                if fam < 0.92:
                    rel["familiarity"] = round(min(0.92, fam + 0.002), 4)
                co_pairs += 1

    pulse = {
        "layer": "16a",
        "status": "active",
        "tick": tick_n,
        "when": _now(),
        "period": period,
        "living": len(living),
        "mood_tally": mood_tally,
        "wallets_total": wallets_total,
        "low_wallet": low_wallet[:8],
        "co_located_pairs": co_pairs,
        "last_social": last_social,
        "hooks": {"mood": True, "bond": True, "economy": True},
        "note": "One cycle inside tick — not a second brain. Speech stays ollama/mom/waiting/none.",
    }
    home["integration"] = pulse
    return pulse


def integration_status() -> dict[str, Any]:
    """Layer 16A — status endpoint only (no second simulation)."""
    home = load()
    pulse = home.get("integration")
    if not isinstance(pulse, dict):
        pulse = {
            "layer": "16a",
            "status": "pending_first_tick",
            "note": "Call tick (or wait for auto-tick) to write the first heartbeat.",
        }
    return {
        "ok": True,
        "layer": "16a",
        "phase_status": (home.get("phase_status") or {}).get("16_integration"),
        "tick": home.get("tick"),
        "integration": pulse,
        "endpoint": "/api/home/integration",
    }


def day_story_status() -> dict[str, Any]:
    """Layer 16C — day story status (no second simulation)."""
    home = load()
    story = home.get("day_story")
    if not isinstance(story, dict):
        story = {
            "layer": "16c",
            "status": "pending_first_tick",
            "note": "Call tick to distill the first day story from world_history.",
        }
    return {
        "ok": True,
        "layer": "16c",
        "phase_status": (home.get("phase_status") or {}).get("16_story"),
        "tick": home.get("tick"),
        "day_story": story,
        "endpoint": "/api/home/day_story",
    }


def gameplay_status() -> dict[str, Any]:
    """Phase 1 Human Gameplay Layer — status window only."""
    home = load()
    try:
        from living_home_gameplay import gameplay_snapshot_fields, ensure_gameplay

        ensure_gameplay(home)
        fields = gameplay_snapshot_fields(home)
    except Exception as e:
        return {"ok": False, "error": str(e), "layer": "18a"}
    return {
        "ok": True,
        "layer": "18a",
        "phase": "1_foundation",
        "tick": home.get("tick"),
        "gameplay": fields.get("gameplay"),
        "world_leads": fields.get("world_leads"),
        "world_conditions": fields.get("world_conditions"),
        "mom_journal": fields.get("mom_journal"),
        "opportunities": fields.get("opportunities"),
        "away_summary": fields.get("away_summary"),
        "endpoint": "/api/home/gameplay",
        "note": "Optional leads — not quest dispensers. Pods/vendors not in Phase 1.",
    }


def tick(n: int = 1) -> dict[str, Any]:
    """Advance life layer + clock. Safe to call from Godot or Hearth."""
    import random

    home = load()
    last_social = None
    last_pulse: dict[str, Any] | None = None
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
        woken = 0

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
                n_stip = _pay_stipend(
                    home,
                    MORNING_STIPEND_AMOUNT,
                    reason="morning stipend",
                    living_ids=["mom"] + living_ids if "mom" not in living_ids else living_ids,
                )
                home["events"].append(
                    _event(
                        "economy",
                        f"Morning stipend: ⨁{MORNING_STIPEND_AMOUNT} each ({n_stip} beings).",
                        (["mom"] + living_ids)[:6],
                        {"stipend": MORNING_STIPEND_AMOUNT},
                    )
                )
                # Layer 16B — soft wake before purpose picks this tick.
                woken = _soft_wake_living(home, living)
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
                # Soft wrap: working folk finish soon so rest can win.
                for m in living:
                    stn = (home.get("people") or {}).get(m["id"])
                    if isinstance(stn, dict) and stn.get("stance") == "working":
                        stn["purpose_left"] = min(int(stn.get("purpose_left") or 1), 1)
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
        # Heal saves where gather already ended but walkers kept purpose=gather + orphan talk_left.
        if not gather_on:
            stale = False
            for _st in (home.get("people") or {}).values():
                if not isinstance(_st, dict):
                    continue
                if str(_st.get("activity") or "") in {"evening_gather", "gather_host"} or str(_st.get("purpose") or "") in {
                    "gather",
                    "gather_host",
                }:
                    stale = True
                    break
            if stale:
                _release_evening_gatherers(home, reason="stale gatherer")

        for m in living:
            home["people"].setdefault(m["id"], _empty_person_state(m))
            st = home["people"][m["id"]]
            _clear_orphan_talk(st)
            # Do not kick gatherers off the square during Layer 8C window.
            if (
                not gather_on
                and str(st.get("place") or "") == "heart_square"
                and st.get("stance") in {"talking", "waiting", "standing", "walking"}
            ):
                if int(st.get("talk_left") or 0) > 8 or st.get("purpose") in {
                    None,
                    "",
                    "arrive",
                    "company",
                    "be_with",
                    "place",
                }:
                    # Soft drift — don't yank mid-talk with Mom.
                    if st.get("talking_to") != "mom":
                        st["place"] = m.get("home") or _work_place(m)
                        st["stance"] = "walking"
                        st["talking_to"] = ""
                        st["talk_left"] = 0
                        st["purpose"] = "place"
                        st["activity"] = "walk"
                        st["purpose_left"] = max(2, int(st.get("purpose_left") or 2))
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

        # Layer 16A — one integration pulse per tick (mood + bond + economy hooks).
        last_pulse = _integration_heartbeat(home, period, living, last_social)
        # Layer 16B — tally only here; soft-wake runs on period change before purpose picks.
        _daily_life_pulse(home, period, woken, living)
        # Layer 16C — honest day story from chronicle (not LLM fanfic voice).
        _day_story_pulse(home, period)
        # Human Gameplay Phase 1 — optional leads/conditions/away hooks (not quests).
        try:
            from living_home_gameplay import gameplay_tick_hooks

            gameplay_tick_hooks(home)
        except Exception:
            pass

    save(home)
    snap = snapshot()
    snap["last_social"] = last_social
    snap["integration"] = last_pulse or home.get("integration")
    snap["day_story"] = home.get("day_story")
    return snap


def set_media_watch(
    active: bool,
    *,
    place: str = "cinema",
    title: str = "",
    source: str = "none",
    who: str = "mom",
) -> dict[str, Any]:
    """Layer 11 — village cinema/TV watch. Honest about whether a reel file is seated."""
    home = load()
    place = (place or "cinema").strip() or "cinema"
    title = (title or "").strip()
    source = (source or "none").strip() or "none"
    who = (who or "mom").strip() or "mom"
    media = home.setdefault("media", {})
    if active:
        if not title:
            title = "Evening quiet (no reel seated)" if source == "none" else "Untitled"
        media.update(
            {
                "watching": True,
                "place": place,
                "title": title[:120],
                "source": source,
                "when": _now(),
                "who": who,
                "layer": "11",
            }
        )
        plain = (
            f"{who} started a watch at {PLACES.get(place, {}).get('label', place)}: «{media['title']}» "
            f"(source={source})."
        )
        if source == "none":
            plain += " Screen is live; no seated film file — not pretending Resolve is running."
        home["events"].append(_event("media", plain, [who], dict(media)))
        home["world_history"].append(
            {
                "id": f"media_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
                "when": _now(),
                "kind": "media",
                "title": "Watch started",
                "text": plain,
                "actors": [who],
                "source": source,
                "place": place,
            }
        )
        home["world_history"] = home["world_history"][-80:]
        _remember(home, who, f"I watched «{media['title']}» at {place}.", important=False)
        # Family at cinema notice the screen.
        for mid in _people_at_place(home, place, exclude={who}):
            _remember(home, mid, f"The screen is on: «{media['title']}».", important=False)
            ost = home["people"].get(mid)
            if ost:
                ost["purpose_plain"] = f"Watching with the house: {media['title'][:80]}"
    else:
        was = str(media.get("title") or "the screen")
        media.update({"watching": False, "title": "", "source": "none", "when": _now(), "who": who, "place": place, "layer": "11"})
        plain = f"{who} stopped the watch at {PLACES.get(place, {}).get('label', place)}."
        home["events"].append(_event("media", plain, [who], {"was": was}))
        _remember(home, who, "I stopped watching.", important=False)
    save(home)
    return snapshot()


# Layer 12 — richer harbor (thin): pier catch + far-shore destination builds.
_FISH_CATCHES: list[tuple[str, str]] = [
    ("minnow", "Minnow"),
    ("perch", "Perch"),
    ("sunfish", "Sunfish"),
    ("catfish", "Catfish"),
    ("trout", "Trout"),
]
_SHORE_BUILD_KINDS: list[tuple[str, str]] = [
    ("hut", "Shore hut"),
    ("crates", "Supply crates"),
    ("garden_box", "Garden box"),
    ("beacon", "Beacon post"),
]
_FISH_COOLDOWN_SEC = 6.0


def harbor_action(
    action: str,
    *,
    who: str = "mom",
    kind: str = "",
    destination: str = "far_shore",
) -> dict[str, Any]:
    """Pier fish catch or far-shore build — Hearth truth, not client-only props."""
    home = load()
    who = (who or "mom").strip() or "mom"
    action = (action or "").strip().lower()
    destination = (destination or "far_shore").strip() or "far_shore"
    harbor = home.setdefault("harbor", {"layer": "12", "catches": 0, "last_fish_when": ""})
    dests = home.setdefault("destinations", {})
    shore = dests.setdefault(
        destination,
        {"id": destination, "label": PLACES.get(destination, {}).get("label", destination), "builds": []},
    )
    if not isinstance(shore.get("builds"), list):
        shore["builds"] = []

    if action == "fish":
        last = str(harbor.get("last_fish_when") or "")
        if last:
            try:
                prev = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if prev.tzinfo is None:
                    ago = (datetime.now() - prev).total_seconds()
                else:
                    ago = (datetime.now().astimezone() - prev).total_seconds()
                if ago < _FISH_COOLDOWN_SEC:
                    wait = max(1, int(_FISH_COOLDOWN_SEC - ago))
                    return {
                        **snapshot(),
                        "harbor_ok": False,
                        "harbor_action": "fish",
                        "error": f"line still settling — wait ~{wait}s",
                    }
            except Exception:
                pass
        idx = int(home.get("tick") or 0) + int(harbor.get("catches") or 0)
        fid, fname = _FISH_CATCHES[idx % len(_FISH_CATCHES)]
        catch = {
            "id": fid,
            "name": fname,
            "kind": "fish",
            "from": "harbor",
            "when": _now(),
        }
        person = home["people"].setdefault(who, _empty_person_state({"id": who, "place": "harbor", "home": "mom_home"}))
        inv = person.setdefault("inventory", [])
        if not isinstance(inv, list):
            inv = []
            person["inventory"] = inv
        inv.append(catch)
        person["inventory"] = inv[-40:]
        harbor["catches"] = int(harbor.get("catches") or 0) + 1
        harbor["last_fish_when"] = _now()
        harbor["last_catch"] = fname
        fish_pay = 2
        _axiom_credit(home, who, fish_pay, reason="fish", bucket="fish", note=f"caught {fname}")
        plain = f"{who} caught a {fname} at the harbor pier (+⨁{fish_pay})."
        home["events"].append(_event("harbor", plain, [who], catch))
        home["world_history"].append(
            {
                "id": f"fish_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
                "when": _now(),
                "kind": "harbor",
                "title": f"Caught {fname}",
                "text": plain,
                "actors": [who],
                "place": "harbor",
            }
        )
        home["world_history"] = home["world_history"][-80:]
        _remember(home, who, f"I caught a {fname} at the pier.", important=False)
        _grow_from_life(home, who, "fish", detail=f"Caught {fname} at the pier.")
        if who != "mom":
            person["place"] = "harbor"
            person["purpose_plain"] = f"Fishing — just caught {fname}."
        save(home)
        snap = snapshot()
        snap["harbor_ok"] = True
        snap["harbor_action"] = "fish"
        snap["catch"] = catch
        return snap

    if action == "build":
        builds = shore["builds"]
        if len(builds) >= 12:
            return {
                **snapshot(),
                "harbor_ok": False,
                "harbor_action": "build",
                "error": "far shore plot is full (12 builds) — clear later",
            }
        kind = (kind or "").strip().lower()
        kinds = {k: lab for k, lab in _SHORE_BUILD_KINDS}
        if kind not in kinds:
            kind, label = _SHORE_BUILD_KINDS[len(builds) % len(_SHORE_BUILD_KINDS)]
        else:
            label = kinds[kind]
        n = len(builds) + 1
        slot_x = float((n - 1) % 3) - 1.0
        slot_z = float(((n - 1) // 3) % 3)
        rec = {
            "id": f"build_{n:02d}",
            "kind": kind,
            "label": label,
            "n": n,
            "offset": [slot_x * 1.6, 0.35, slot_z * 1.4],
            "by": who,
            "when": _now(),
        }
        builds.append(rec)
        shore["builds"] = builds
        plain = f"{who} placed a {label} on the far shore (#{n})."
        home["events"].append(_event("destination", plain, [who], rec))
        home["world_history"].append(
            {
                "id": f"shore_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
                "when": _now(),
                "kind": "destination",
                "title": label,
                "text": plain,
                "actors": [who],
                "place": destination,
            }
        )
        home["world_history"] = home["world_history"][-80:]
        _remember(home, who, f"I built a {label} on the far shore.", important=False)
        save(home)
        snap = snapshot()
        snap["harbor_ok"] = True
        snap["harbor_action"] = "build"
        snap["build"] = rec
        return snap

    if action == "sail":
        to_place = destination if destination in PLACES else "far_shore"
        plain = f"{who} sailed between harbor and {PLACES.get(to_place, {}).get('label', to_place)}."
        home["events"].append(_event("harbor", plain, [who], {"to": to_place}))
        harbor["last_sail_when"] = _now()
        harbor["last_sail_to"] = to_place
        save(home)
        snap = snapshot()
        snap["harbor_ok"] = True
        snap["harbor_action"] = "sail"
        snap["to"] = to_place
        return snap

    return {**snapshot(), "harbor_ok": False, "error": f"unknown harbor action: {action}"}


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
    _remember(
        home,
        giver,
        f"I gave {receiver} {obj}.",
        important=True,
        emotional_tag="happy",
        significance=0.8,
        participants=[giver, receiver],
    )
    _remember(
        home,
        receiver,
        f"{giver} gave me {obj}.",
        important=True,
        emotional_tag="grateful",
        significance=0.8,
        participants=[giver, receiver],
    )
    update_relationship(
        home,
        giver,
        receiver,
        "gift",
        {"gift": obj, "text": txt, "significance": 0.8, "emotional_tag": "grateful", "place": rec.get("place")},
        record_memory=False,
    )
    _grow_from_life(home, giver, "gift", detail=f"Gave {obj} to {receiver}.")
    _grow_from_life(home, receiver, "gift", detail=f"Received {obj} from {giver}.")
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


def _living_member_ids() -> list[str]:
    out: list[str] = []
    for m in FAMILY + KIN:
        mid = str(m.get("id") or "")
        if not mid or m.get("player") or m.get("ambient_only"):
            continue
        out.append(mid)
    return out


def _people_at_place(home: dict[str, Any], place: str, *, exclude: set[str] | None = None) -> list[str]:
    """Family currently at a place (kernel truth)."""
    exclude = exclude or set()
    place = str(place or "heart_square")
    found: list[str] = []
    for mid in _living_member_ids():
        if mid in exclude:
            continue
        m = _member(mid) or {}
        st = home.get("people", {}).get(mid) or {}
        here = str(st.get("place") or m.get("place") or m.get("home") or "")
        if here == place:
            found.append(mid)
    return found


def _kick_mom_reply(
    home: dict[str, Any],
    npc: str,
    place: str,
    *,
    mom_line: str,
    job_tag: str,
) -> None:
    """Real Ollama reply to Mom — never house quote sheets."""
    member = _member(npc)
    if not member:
        return
    st = home["people"].setdefault(npc, _empty_person_state(member))
    mom_state = home["people"].setdefault("mom", _empty_person_state(_member("mom") or {"id": "mom", "home": "mom_home"}))
    a = member
    b = _member("mom") or {"id": "mom", "name": "Mom", "personality": "plain", "role": "EP"}
    rel_key = "|".join(sorted([npc, "mom"]))
    rel = (home.get("relationships") or {}).get(rel_key) or {}
    past = [(x.get("text") if isinstance(x, dict) else str(x)) for x in (rel.get("shared_experiences") or [])[-3:]]
    if mom_line:
        past.append(f"Mom just said: {mom_line[:140]}")
    mem_npc = ((st.get("memories") or [{}])[-1] or {}).get("text") or ""
    mem_mom = mom_line[:160] if mom_line else (((mom_state.get("memories") or [{}])[-1] or {}).get("text") or "")
    _kick_talk_job(
        f"mom|{npc}|{job_tag}",
        a,
        b,
        PLACES.get(place, {}).get("label", place),
        (home.get("ritual") or {}).get("plain") or "",
        mem_npc,
        mem_mom,
        past,
        to_mom=True,
    )


def record_talk(who: str, with_whom: str, line: str, place_hint: str = "") -> dict[str, Any]:
    """Mom's real words in; local model replies. Empty line = she approached. Never a quote sheet."""
    import random

    home = load()
    who = (who or "").strip()
    with_whom = (with_whom or "mom").strip()
    line = (line or "").strip()
    place_hint = (place_hint or "").strip()
    if who != "mom":
        # Village speech is kernel-invented. Do not log companion sheets as their voice.
        save(home)
        return snapshot()

    mom_state = home["people"].setdefault("mom", _empty_person_state(_member("mom") or {"id": "mom", "home": "mom_home"}))
    # Resolve place: explicit hint from Godot, else Mom's last place, else target's place.
    npc = with_whom if with_whom not in {"", "mom", "all", "everyone"} else ""
    member = _member(npc) if npc else None
    if place_hint and place_hint in PLACES:
        place = place_hint
    elif member:
        st0 = home["people"].get(npc) or {}
        place = str(st0.get("place") or member.get("place") or mom_state.get("place") or "heart_square")
    else:
        place = str(mom_state.get("place") or "heart_square")
    mom_state["place"] = place
    mom_state["last_seen"] = _now()
    try:
        from living_home_gameplay import log_player_action

        log_player_action(
            home,
            "talk" if line else "approach",
            line[:220] if line else f"Mom approached {npc or 'someone'}",
            place=place,
            actors=["mom", npc] if npc else ["mom"],
        )
    except Exception:
        pass

    # Default addressee: Gemini (town leader) when Mom speaks to "all".
    if not member:
        npc = "gemini"
        member = _member(npc)
    if not member:
        # Still persist Mom's voice even if roster odd.
        if line:
            _utter(home, "mom", "all", line, "mom", place, conversation=f"mom|all|{home.get('tick')}")
            home["world_history"].append(
                {
                    "id": f"mom_{home.get('tick')}_{datetime.now().strftime('%H%M%S')}",
                    "when": _now(),
                    "kind": "conversation",
                    "title": "Mom spoke",
                    "text": line[:220],
                    "actors": ["mom"],
                    "source": "mom",
                    "place": place,
                }
            )
            home["world_history"] = home["world_history"][-80:]
            _remember(home, "mom", f"I said: {line[:160]}", important=True)
        save(home)
        return snapshot()

    st = home["people"].setdefault(npc, _empty_person_state(member))
    nearby = _people_at_place(home, place, exclude={"mom"})
    if npc not in nearby:
        nearby = [npc] + [x for x in nearby if x != npc]

    # Presence: Mom arrived / is here — acknowledge once per place visit.
    last_ack = str(mom_state.get("ack_place") or "")
    if last_ack != place:
        mom_state["ack_place"] = place
        for mid in nearby[:4]:
            m = _member(mid)
            if not m:
                continue
            ost = home["people"].setdefault(mid, _empty_person_state(m))
            ost["purpose_plain"] = f"Mom is at {PLACES.get(place, {}).get('label', place)}. I notice her."
            _remember(home, mid, f"Mom is here at {PLACES.get(place, {}).get('label', place)}.", important=False)
            if mid != npc and not line:
                _kick_mom_reply(home, mid, place, mom_line="", job_tag="presence")

    if not line:
        if st.get("stance") == "working" and random.random() < 0.45:
            home["mom_cover"] = f"{member.get('name')} stayed at their post. Silence is allowed — no fake tool show."
            save(home)
            return snapshot()
        st["stance"] = "talking"
        st["talking_to"] = "mom"
        st["talk_left"] = max(int(st.get("talk_left") or 0), 12)
        _kick_mom_reply(home, npc, place, mom_line="", job_tag="greet")
        home["mom_cover"] = f"{member.get('name')} noticed Mom. Local voice cooking."
        st["purpose_plain"] = "Mom is here. Thinking of a greeting — not ignoring her."
        save(home)
        return snapshot()

    # --- Mom spoke: always persist ---
    conv_id = f"mom|{npc}|{int(home.get('tick') or 0)}"
    _utter(home, "mom", npc, line, "mom", place, conversation=conv_id)
    home["world_history"].append(
        {
            "id": f"mom_{home.get('tick')}_{datetime.now().strftime('%H%M%S%f')}",
            "when": _now(),
            "kind": "conversation",
            "title": f"Mom → {member.get('name')}",
            "text": line[:220],
            "actors": ["mom", npc],
            "source": "mom",
            "place": place,
        }
    )
    home["world_history"] = home["world_history"][-80:]
    _remember(home, "mom", f"I said to {member.get('name')}: {line[:160]}", important=True)
    _remember(home, npc, f"Mom said to me: {line[:160]}", important=True)
    _touch_rel(home, "mom", npc, experience=f"Mom: {line[:120]}", d_trust=0.04)

    # Community memory: everyone at this place hears Mom (real memory, not a fake chorus).
    for mid in nearby:
        if mid == npc:
            continue
        m = _member(mid)
        if not m:
            continue
        _remember(home, mid, f"I overheard Mom at {PLACES.get(place, {}).get('label', place)}: {line[:140]}", important=True)
        _touch_rel(home, "mom", mid, experience=f"Overheard Mom: {line[:100]}", d_trust=0.01)

    st["stance"] = "talking"
    st["talking_to"] = "mom"
    st["talk_left"] = max(int(st.get("talk_left") or 0), 16)
    st["purpose_plain"] = "Mom spoke to me. Thinking of a real reply — not ignoring her."
    home["mom_cover"] = f"{member.get('name')} heard you. Local voice cooking."

    # Primary addressee — full reply.
    _kick_mom_reply(home, npc, place, mom_line=line, job_tag="reply")

    # Nearby others — real Ollama overhear replies (cap 2 so we don't flood the local models).
    overhear_budget = 0
    for mid in nearby:
        if mid == npc:
            continue
        if overhear_budget >= 2:
            break
        ost = home["people"].setdefault(mid, _empty_person_state(_member(mid) or {"id": mid}))
        ost["stance"] = "talking"
        ost["talking_to"] = "mom"
        ost["talk_left"] = max(int(ost.get("talk_left") or 0), 10)
        ost["purpose_plain"] = "I overheard Mom. Considering whether to speak."
        _kick_mom_reply(home, mid, place, mom_line=line, job_tag="overhear")
        overhear_budget += 1

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
    return {
        "ok": True,
        "phases": home.get("phase_status"),
        "save": str(HOME_JSON),
        "tick": home.get("tick"),
        "integration": home.get("integration"),
    }


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
    elif cmd == "integration":
        print(json.dumps(integration_status(), indent=2))
    elif cmd == "simulate":
        print(json.dumps(simulate_failure(sys.argv[2] if len(sys.argv) > 2 else "cinema"), indent=2))
    elif cmd == "repair":
        fid = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(try_repair(fid), indent=2))
    else:
        print("usage: living_home.py [snapshot|tick|health|phases|integration|simulate|repair]")
        sys.exit(2)
