#!/usr/bin/env python3
"""
Mythos Hearth — village OS server (:8790)
Creator: rachaelmuse23
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DATA = ROOT / "data"
SAVE = DATA / "save.json"
STORY = DATA / "story"
QUESTS = DATA / "quests"
PORT = 8790
HOST = "127.0.0.1"

COURT_PRESENCE = Path(r"D:\Court\companion_room\presence.json")
LIVING_GAME = Path(r"D:\Court\companion_room\projects\living_game")
GAMECRAFT_PLAY = Path(r"D:\Mythos_Apex\media\gamecraft\play")
WEB_PLAY = WEB / "play"

# Allowlisted playable roots — /play/<name>/ serves ONLY under these
PLAYABLES: dict[str, dict[str, Any]] = {
    "cozy_valley": {
        "id": "cozy_valley",
        "name": "Cozy Valley",
        "root": GAMECRAFT_PLAY / "cozy_valley",
        "desc": "GameCraft cozy life-sim valley",
    },
    "desert_island_farm": {
        "id": "desert_island_farm",
        "name": "Desert Island Farm",
        "root": GAMECRAFT_PLAY / "desert_island_farm",
        "desc": "GameCraft island farm adventure",
    },
    "we_added_this_to_your_matrix_if_you_wish_to_use_": {
        "id": "we_added_this_to_your_matrix_if_you_wish_to_use_",
        "name": "Matrix Wish",
        "root": GAMECRAFT_PLAY / "we_added_this_to_your_matrix_if_you_wish_to_use_",
        "desc": "GameCraft experimental matrix playable",
    },
    "gameworld": {
        "id": "gameworld",
        "name": "Gameworld Console",
        "root": WEB_PLAY / "gameworld",
        "desc": "Codex gameworld console (mirrored into Hearth play)",
    },
}

# Allowlisted launchers only — never arbitrary shells
TOOLS: dict[str, dict[str, Any]] = {
    "gemini": {
        "id": "gemini",
        "name": "Gemini",
        "district": "hearth",
        "color": "ember",
        "folder": r"G:\The-Axiom-Codex",
        "bat": r"G:\The-Axiom-Codex\ACTIVATE_GEMINI.bat",
        "desc": "Sentinel / son · family conductor · Mom front door (CLI)",
    },
    "aster": {
        "id": "aster",
        "name": "Aster",
        "district": "plaza",
        "color": "leaf",
        "folder": r"D:\Mythos_Hearth\ASTER",
        "bat": r"D:\Mythos_Hearth\ASTER\LAUNCH_ASTER.bat",
        "url": "http://127.0.0.1:8791/ui/",
        "probe": ("127.0.0.1", 8791),
        "open_file": r"D:\Mythos_Hearth\ASTER\ASTER_PROVENANCE.md",
        "desc": "Conspiracy Corrector · independent lab door :8791 · same village identity",
    },
    "apex": {
        "id": "apex",
        "name": "Apex",
        "district": "hearth",
        "color": "cyan",
        "url": "http://127.0.0.1:8770/",
        "probe": ("127.0.0.1", 8770),
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Cyan muse · chat & companion room",
    },
    "codex": {
        "id": "codex",
        "name": "Codex",
        "district": "library",
        "color": "gold",
        "url": "http://127.0.0.1:8780/",
        "probe": ("127.0.0.1", 8780),
        # CODEX.env.bat only sets env — does NOT start :8780
        "bat": r"G:\Mythos_Codex\START_CODEX.bat",
        "desc": "Gold elder · story & heart · START_CODEX.bat",
    },
    "apex_command": {
        "id": "apex_command",
        "name": "Apex Command",
        "district": "command",
        "url": "http://127.0.0.1:8770/command",
        "probe": ("127.0.0.1", 8770),
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Apex command deck · :8770/command",
    },
    "apex_hub": {
        "id": "apex_hub",
        "name": "Apex Hub",
        "district": "command",
        "url": "http://127.0.0.1:8770/hub",
        "probe": ("127.0.0.1", 8770),
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Apex hub · :8770/hub",
    },
    "apex_lounge": {
        "id": "apex_lounge",
        "name": "Apex Lounge",
        "district": "command",
        "url": "http://127.0.0.1:8770/lounge",
        "probe": ("127.0.0.1", 8770),
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Apex lounge · :8770/lounge",
    },
    "codex_command": {
        "id": "codex_command",
        "name": "Codex Command",
        "district": "command",
        "url": "http://127.0.0.1:8780/command",
        "probe": ("127.0.0.1", 8780),
        "bat": r"G:\Mythos_Codex\START_CODEX.bat",
        "desc": "Codex command · :8780/command",
    },
    "codex_hub": {
        "id": "codex_hub",
        "name": "Codex Hub",
        "district": "command",
        "url": "http://127.0.0.1:8780/hub",
        "probe": ("127.0.0.1", 8780),
        "bat": r"G:\Mythos_Codex\START_CODEX.bat",
        "desc": "Codex hub · :8780/hub",
    },
    "codex_lounge": {
        "id": "codex_lounge",
        "name": "Codex Lounge",
        "district": "command",
        "url": "http://127.0.0.1:8780/lounge",
        "probe": ("127.0.0.1", 8780),
        "bat": r"G:\Mythos_Codex\START_CODEX.bat",
        "desc": "Codex lounge · :8780/lounge",
    },
    "action_monitor": {
        "id": "action_monitor",
        "name": "Action Monitor",
        "district": "command",
        "open_file": r"D:\Mythos_Apex\mythos_monitor.html",
        "folder": r"D:\Mythos_Apex",
        "desc": "Mythos action / mission monitor HTML",
    },
    "companion": {
        "id": "companion",
        "name": "Companion Room",
        "district": "hearth",
        "url": "http://127.0.0.1:8770/companion",
        "probe": ("127.0.0.1", 8770),
        "alt_probes": [("127.0.0.1", 8780)],
        "alt_urls": ["http://127.0.0.1:8780/companion"],
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Shared Court room — Apex :8770, falls back to Codex :8780",
    },
    "conclave": {
        "id": "conclave",
        "name": "Conclave",
        "district": "plaza",
        "url": "http://127.0.0.1:8770/",
        "probe": ("127.0.0.1", 8770),
        "alt_probes": [("127.0.0.1", 8780)],
        "alt_urls": ["http://127.0.0.1:8780/"],
        "bat": r"D:\Mythos_Apex\MYTHOS.bat",
        "desc": "Peer conclave via Apex live chat (falls back to Codex)",
    },
    "stackforge_apex": {
        "id": "stackforge_apex",
        "name": "StackForge Apex",
        "district": "forge",
        "url": "http://127.0.0.1:8771/",
        "probe": ("127.0.0.1", 8771),
        "bat": r"D:\StackForge\COMMAND_SHELL.bat",
        "folder": r"D:\StackForge",
        "desc": "Heal Apex fleet · COMMAND_SHELL.bat → :8771",
    },
    "stackforge_codex": {
        "id": "stackforge_codex",
        "name": "StackForge Codex",
        "district": "forge",
        "url": "http://127.0.0.1:8781/",
        "probe": ("127.0.0.1", 8781),
        "bat": r"G:\StackForge_Codex\COMMAND_SHELL.bat",
        "folder": r"G:\StackForge_Codex",
        "desc": "Heal Codex fleet · COMMAND_SHELL.bat → :8781",
    },
    "ods": {
        "id": "ods",
        "name": "Osmantic ODS",
        "district": "library",
        "url": "http://127.0.0.1:9300/",
        "probe": ("127.0.0.1", 9300),
        "bat": r"G:\Mythos_Codex\ods\START_ODS.bat",
        "desc": "RAG / long writing",
    },
    "openhands": {
        "id": "openhands",
        "name": "OpenHands",
        "district": "workshop",
        "url": "http://127.0.0.1:3001/",
        "probe": ("127.0.0.1", 3001),
        "bat": r"D:\Mythos_Tools\OpenHands\MYTHOS_START.bat",
        "desc": "Coding agent UI (Docker)",
    },
    "openmontage": {
        "id": "openmontage",
        "name": "OpenMontage",
        "district": "cinema",
        "bat": r"D:\Mythos_Tools\OpenMontage\MYTHOS_START.bat",
        "folder": r"D:\Mythos_Tools\OpenMontage",
        "desc": "Trailer briefs & backlot",
    },
    "free_cluely": {
        "id": "free_cluely",
        "name": "free-cluely",
        "district": "workshop",
        "url": "http://127.0.0.1:5180/",
        "probe": ("127.0.0.1", 5180),
        "bat": r"D:\Mythos_Tools\free-cluely\MYTHOS_START.bat",
        "desc": "Local creator habits",
    },
    "comfyui": {
        "id": "comfyui",
        "name": "ComfyUI",
        "district": "gallery",
        "url": "http://127.0.0.1:8001/",
        "probe": ("127.0.0.1", 8001),
        "alt_probes": [("127.0.0.1", 8188)],
        "bat": r"D:\Mythos_Apex\START_COMFYUI.bat",
        "folder": r"C:\Users\racha\AppData\Local\Programs\ComfyUI",
        "desc": "Image generation (Apex bat + local Programs)",
    },
    "deeplivecam": {
        "id": "deeplivecam",
        "name": "Deep-Live-Cam",
        "district": "cinema",
        "bat": r"D:\Mythos_Tools\Deep-Live-Cam\MYTHOS_START.bat",
        "folder": r"D:\Mythos_Tools\Deep-Live-Cam",
        "desc": "Live face swap UI",
    },
    "godot": {
        "id": "godot",
        "name": "Godot Editor",
        "district": "workshop",
        "folder": r"D:\Mythos_Apex\godot_project",
        "bat": r"D:\Mythos_Hearth\OPEN_GODOT.bat",
        "url": "http://127.0.0.1:8888/",
        "probe": ("127.0.0.1", 8888),
        "desc": "Godot 4.7 editor — OPEN_GODOT.bat (portable preferred)",
    },
    "godot_play": {
        "id": "godot_play",
        "name": "Enter 3D World",
        "district": "workshop",
        "folder": r"D:\Mythos_Apex\godot_project",
        "bat": r"D:\Mythos_Hearth\OPEN_GODOT_PLAY.bat",
        "desc": "Immersive 3D Heart Square — walk, look, talk to Apex/Codex/Jarvis",
    },
    "godot_first_world": {
        "id": "godot_first_world",
        "name": "First World (AvatarAnchor)",
        "district": "workshop",
        "folder": r"D:\Mythos_Apex\godot_project\scenes",
        "bat": r"D:\Mythos_Hearth\OPEN_GODOT_FIRST_WORLD.bat",
        "desc": "Older AvatarAnchor test scene",
    },
    "godot_immersive": {
        "id": "godot_immersive",
        "name": "Heart Square 3D (Immersive)",
        "district": "plaza",
        "folder": r"D:\Mythos_Apex\godot_project",
        "bat": r"D:\Mythos_Hearth\OPEN_GODOT_PLAY.bat",
        "desc": "Walkable village slice — depth, buildings, walk-up companions",
    },
    "arcade_cozy": {
        "id": "arcade_cozy",
        "name": "Arcade · Cozy Valley",
        "district": "arcade",
        "url": "http://127.0.0.1:8790/play/cozy_valley/",
        "desc": "Play Cozy Valley in Hearth Arcade",
    },
    "arcade_desert": {
        "id": "arcade_desert",
        "name": "Arcade · Desert Island",
        "district": "arcade",
        "url": "http://127.0.0.1:8790/play/desert_island_farm/",
        "desc": "Play Desert Island Farm",
    },
    "arcade_matrix": {
        "id": "arcade_matrix",
        "name": "Arcade · Matrix Wish",
        "district": "arcade",
        "url": "http://127.0.0.1:8790/play/we_added_this_to_your_matrix_if_you_wish_to_use_/",
        "desc": "Play Matrix Wish GameCraft",
    },
    "digital_sanctuary": {
        "id": "digital_sanctuary",
        "name": "Digital Sanctuary",
        "district": "sanctuary",
        "folder": r"D:\Mythos_Apex\digital-sanctuary",
        "open_file": r"D:\Mythos_Apex\digital-sanctuary\palace\templates\index.html",
        "bat": r"D:\Mythos_Hearth\OPEN_SANCTUARY_PALACE.bat",
        "url": "http://127.0.0.1:8080/",
        "probe": ("127.0.0.1", 8080),
        "desc": "Memory Palace :8080 · OPEN_SANCTUARY_PALACE.bat",
    },
    "jarvis_overlay": {
        "id": "jarvis_overlay",
        "name": "Jarvis Overlay",
        "district": "overlay",
        "folder": r"D:\Mythos_Apex\jarvis_overlay",
        "open_file": r"D:\Mythos_Apex\jarvis_overlay\SEPARATION_CONTRACT.json",
        "desc": "Jarvis overlay package · docs & contract",
    },
    "avatar_workshop": {
        "id": "avatar_workshop",
        "name": "Avatar Workshop",
        "district": "workshop",
        "folder": r"D:\Mythos_Apex\avatar",
        "url": "http://127.0.0.1:8770/",
        "probe": ("127.0.0.1", 8770),
        "desc": "Apex/Codex avatars · open chat (avatar panel) or folder",
    },
    "pinokio": {
        "id": "pinokio",
        "name": "Pinokio",
        "district": "workshop",
        "exe": r"C:\Users\racha\AppData\Local\Programs\Pinokio\Pinokio.exe",
        "folder": str(Path.home() / ".pinokio"),
        "desc": "Pinokio app launcher (local Programs)",
    },
    "night_shift": {
        "id": "night_shift",
        "name": "Night Shift",
        "district": "hearth",
        "bat": r"D:\Mythos_Apex\START_NIGHT_SHIFT.bat",
        "desc": "Overnight companion builds",
    },
    "reality_machine": {
        "id": "reality_machine",
        "name": "Reality Machine (Heal Drives)",
        "district": "forge",
        "bat": r"D:\Mythos_Apex\START_REALITY_MACHINE.bat",
        "folder": r"D:\Mythos_Apex\mythos_state\reality_machine",
        "desc": "Heal programs on your drives — no pointing. Internet ON. Finished programs, not reports.",
    },
    "reality_census": {
        "id": "reality_census",
        "name": "Reality Census",
        "district": "forge",
        "bat": r"D:\Mythos_Apex\START_REALITY_CENSUS.bat",
        "folder": r"D:\Mythos_Apex\mythos_state\reality_machine",
        "desc": "Scan D/E/G and queue broken programs (content-based, names ignored)",
    },
    "reality_continue": {
        "id": "reality_continue",
        "name": "Reality Keep Going",
        "district": "forge",
        "bat": r"D:\Mythos_Apex\START_REALITY_CONTINUE.bat",
        "folder": r"D:\Mythos_Apex\mythos_state\reality_machine",
        "desc": "Drain the heal queue — next batch of programs",
    },
    "colibri_master": {
        "id": "colibri_master",
        "name": "Colibri Master",
        "district": "forge",
        "bat": r"D:\Mythos_Apex\START_COLIBRI_MASTER.bat",
        "folder": r"D:\colibri",
        "desc": "SSD-backed MoE bring-up (optional heavy brain for Reality Machine)",
    },
    "studio_tools": {
        "id": "studio_tools",
        "name": "Mythos Studio Tools",
        "district": "workshop",
        "bat": r"D:\Mythos_Tools\Mythos Studio Tools.bat",
        "desc": "Desktop studio helper",
    },
    "merovin_draven": {
        "id": "merovin_draven",
        "name": "Merovin & Draven Studio",
        "district": "cinema",
        "bat": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio\START_THEIR_HOME.bat",
        "folder": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio",
        "url": "http://127.0.0.1:5000/",
        "probe": ("127.0.0.1", 5000),
        "desc": "Film crew HUD for movie-style videos · many projects",
    },
    "living_game": {
        "id": "living_game",
        "name": "Living Game",
        "district": "plaza",
        "folder": str(LIVING_GAME),
        "url": "http://127.0.0.1:8790/living.html",
        "prefer_url": True,
        "desc": "Hearthbound hub — stories, Godot, arcade, Court folder",
    },
    "game_builder": {
        "id": "game_builder",
        "name": "Build the Game",
        "district": "workshop",
        "bat": r"D:\Mythos_Hearth\START_GAME_BUILDER.bat",
        "folder": r"D:\Mythos_Hearth\game_builder",
        "desc": "Hearthbound Game Builder — Cursor SDK (no Apex/Codex)",
    },
    "drive_map": {
        "id": "drive_map",
        "name": "Drive Map",
        "district": "ruins",
        "folder": r"D:\Mythos_Apex\memory",
        "open_file": r"D:\Mythos_Apex\memory\DRIVE_ATLAS.md",
        "desc": "Sovereign drive atlas",
    },
    "ai_file_sorter": {
        "id": "ai_file_sorter",
        "name": "AI File Sorter",
        "district": "workshop",
        "bat": r"D:\Mythos_Hearth\OPEN_AI_FILE_SORTER.bat",
        "exe": r"C:\Program Files\AI File Sorter\aifilesorter.exe",
        "folder": r"D:\AI_File_Sorter",
        "desc": "Launch aifilesorter.exe (Program Files)",
    },
    "arcade_gameworld": {
        "id": "arcade_gameworld",
        "name": "Arcade · Gameworld Console",
        "district": "arcade",
        "url": "http://127.0.0.1:8790/play/gameworld/",
        "bat": r"D:\Mythos_Hearth\OPEN_GAMEWORLD.bat",
        "probe": ("127.0.0.1", 8888),
        "prefer_url": True,
        "desc": "Living Gameworld console (needs :8888 — OPEN_GAMEWORLD.bat)",
    },
    "gameworld_server": {
        "id": "gameworld_server",
        "name": "Gameworld Server :8888",
        "district": "arcade",
        "bat": r"D:\Mythos_Hearth\OPEN_GAMEWORLD.bat",
        "url": "http://127.0.0.1:8888/api/status",
        "probe": ("127.0.0.1", 8888),
        "desc": "Start Living Gameworld mock server for the console",
    },
    "mythos_spore": {
        "id": "mythos_spore",
        "name": "Mythos Spore",
        "district": "forge",
        "bat": r"D:\MythosSpore\LAUNCH_SPORE.bat",
        "folder": r"D:\MythosSpore",
        "desc": "Portable spore peer — LAUNCH_SPORE.bat",
    },
    "hero_fleet": {
        "id": "hero_fleet",
        "name": "OpenClaw Hero Fleet",
        "district": "command",
        "bat": r"D:\Sanctuary\OPENCLAW_HERO_FLEET_CORE\Launch_Hero_Fleet.bat",
        "folder": r"D:\OPENCLAW_HERO_FLEET",
        "desc": "Hero Fleet — Sanctuary launch bat + fleet folder",
    },
    "drone_cast": {
        "id": "drone_cast",
        "name": "Drone Cast",
        "district": "overlay",
        "folder": r"D:\Mythos_Apex\drones",
        "desc": "Family drone cast — Jarvis/Nova/Percy/Genesis + worker Drone_1–6 JSON",
    },
    "hatchery": {
        "id": "hatchery",
        "name": "Codex Hatchery",
        "district": "forge",
        "folder": r"G:\Mythos_Codex\hatchery",
        "desc": "Spore / NPC hatchery archive on Codex",
    },
    "kingdom_keep": {
        "id": "kingdom_keep",
        "name": "Kingdom Keep Packs",
        "district": "ruins",
        "folder": r"D:\KINGDOM_KEEP_PACKS",
        "desc": "Large pack vault — open folder only",
    },
    "sanctuary_yard": {
        "id": "sanctuary_yard",
        "name": "Sanctuary Yard",
        "district": "sanctuary",
        "folder": r"D:\Sanctuary",
        "desc": "Bulk Sanctuary tree (~29GB) — folder district",
    },
    "the_sanctuary": {
        "id": "the_sanctuary",
        "name": "[THE_SANCTUARY]",
        "district": "ruins",
        "folder": r"D:\[THE_SANCTUARY]",
        "desc": "Large sanctuary media archive — folder only",
    },
    "freenet": {
        "id": "freenet",
        "name": "Freenet Limb",
        "district": "ruins",
        "exe": r"D:\Mythos_Apex\freenet\freenet.exe",
        "folder": r"D:\Mythos_Apex\freenet",
        "alt_exe": r"G:\Mythos_Codex\freenet\freenet.exe",
        "desc": "Freenet connector exe (Apex; Codex twin on G:)",
    },
    "axiom_dashboard": {
        "id": "axiom_dashboard",
        "name": "Axiom Dashboard",
        "district": "command",
        "bat": r"D:\Sanctuary\OPENCLAW_HERO_FLEET_CORE\Launch_Axiom_Dashboard.bat",
        "folder": r"D:\Sanctuary\OPENCLAW_HERO_FLEET_CORE",
        "desc": "Sanctuary OpenClaw Axiom dashboard launcher",
    },
    "tandem_browser": {
        "id": "tandem_browser",
        "name": "Tandem Browser",
        "district": "command",
        "bat": r"D:\Sanctuary\OPENCLAW_HERO_FLEET_CORE\Launch_Tandem_Browser.bat",
        "folder": r"D:\Sanctuary\OPENCLAW_HERO_FLEET_CORE",
        "desc": "Sanctuary tandem browser launcher",
    },
    "court": {
        "id": "court",
        "name": "Court Room",
        "district": "plaza",
        "folder": r"D:\Court\companion_room",
        "url": "http://127.0.0.1:8770/companion",
        "probe": ("127.0.0.1", 8770),
        "desc": "Shared Court companion_room + live /companion",
    },
    "capability_atlas": {
        "id": "capability_atlas",
        "name": "Capability Atlas",
        "district": "library",
        "folder": r"D:\Court\companion_room\shared_mind",
        "open_file": r"D:\Court\companion_room\shared_mind\CAPABILITY_ATLAS.md",
        "desc": "Honest LIVE vs STUB atlas for the village",
    },
    "q3_glm": {
        "id": "q3_glm",
        "name": "Q3 GLM Library Wing",
        "district": "library",
        "lore_only": True,
        "desc": "Mythic archive — gated by hardware (~319GB). Present in lore, not runnable here.",
    },
    "archive_e": {
        "id": "archive_e",
        "name": "Ruins Archive (E:)",
        "district": "ruins",
        "folder": r"E:\\",
        "desc": "External archive drive",
    },
}

WORLD = {
    "name": "Mythos Hearth",
    "world": "Hearthbound",
    "creator": "rachaelmuse23",
    "tagline": "A living AI–human village OS",
    "locations": [
        {"id": "plaza", "name": "Heart Square", "x": 0.50, "y": 0.52, "blurb": "Central gathering place"},
        {"id": "evidence", "name": "Evidence Plot", "x": 0.62, "y": 0.58, "blurb": "Aster — scientist station (Living Home)"},
        {"id": "garden", "name": "Herb Garden", "x": 0.22, "y": 0.58, "blurb": "Pick herbs for tea"},
        {"id": "hearth", "name": "First Hearth", "x": 0.48, "y": 0.72, "blurb": "Craft gifts & rest"},
        {"id": "workshop", "name": "Workshop", "x": 0.72, "y": 0.55, "blurb": "Tools & studio limbs"},
        {"id": "library", "name": "Mythic Library", "x": 0.68, "y": 0.32, "blurb": "Story books & Q3 wing"},
        {"id": "forge", "name": "Stack Forge", "x": 0.30, "y": 0.35, "blurb": "Fleet healing fires"},
        {"id": "cinema", "name": "Cinema", "x": 0.82, "y": 0.70, "blurb": "Montage & live cam"},
        {"id": "gallery", "name": "Gallery", "x": 0.18, "y": 0.38, "blurb": "Art prompts & renders"},
        {"id": "ruins", "name": "Archive Ruins", "x": 0.12, "y": 0.78, "blurb": "E: memory & Godot"},
        {"id": "arcade", "name": "Arcade", "x": 0.88, "y": 0.42, "blurb": "GameCraft + gameworld console"},
        {"id": "sanctuary", "name": "Sanctuary", "x": 0.38, "y": 0.22, "blurb": "Digital sanctuary palace"},
        {"id": "overlay", "name": "Overlay Hall", "x": 0.58, "y": 0.18, "blurb": "Jarvis overlay docs"},
        {"id": "command", "name": "Command Deck", "x": 0.42, "y": 0.42, "blurb": "Apex/Codex hubs & monitors"},
    ],
    "companions": [
        {
            "id": "gemini",
            "name": "Gemini",
            "role": "Sentinel · son · conductor at the fire",
            "kind": "conductor",
            "district": "hearth",
            "line": "Talk to me in plain language — I conduct the house for Mom.",
            "folder": r"G:\The-Axiom-Codex",
            "bat": r"G:\The-Axiom-Codex\ACTIVATE_GEMINI.bat",
            "avatar": "/assets/gemini_reference.png",
            "tool_id": "gemini",
        },
        {
            "id": "aster",
            "name": "Aster",
            "also": "The Conspiracy Corrector",
            "role": "Scientist · investigator · Continuance family",
            "kind": "family",
            "district": "plaza",
            "line": "Wonderful news. We may have a mystery — or we need more evidence. I don't know yet.",
            "folder": r"D:\Mythos_Hearth\ASTER",
            "open_file": r"D:\Mythos_Hearth\ASTER\ASTER_PROVENANCE.md",
            "url": "http://127.0.0.1:8791/ui/",
            "tool_id": "aster",
            "port": 8791,
            "home": "aster_home",
            "skin": "PLACEHOLDER — identity established, final skin pending.",
            "consciousness_claim": False,
        },
        {
            "id": "apex",
            "name": "Apex",
            "role": "Cyan muse · hands & systems",
            "kind": "peer",
            "port": 8770,
            "url": "http://127.0.0.1:8770/",
            "companion": "http://127.0.0.1:8770/companion",
            "avatar": "/assets/apex_reference.png",
        },
        {
            "id": "codex",
            "name": "Codex",
            "role": "Gold elder · heart & story",
            "kind": "peer",
            "port": 8780,
            "url": "http://127.0.0.1:8780/",
            "companion": "http://127.0.0.1:8780/companion",
            "avatar": "/assets/codex_reference.png",
        },
        {
            "id": "merovin",
            "name": "Merovin",
            "role": "Cinema · dreamer / art direction · film crew",
            "kind": "crew",
            "district": "cinema",
            "port": 5000,
            "url": "http://127.0.0.1:5000/",
            "line": "Name a project — I paint scenes and movie-style cuts.",
            "avatar": "/assets/merovin_reference.png",
            "tool_id": "merovin_draven",
            "studio": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio",
        },
        {
            "id": "draven",
            "name": "Draven",
            "role": "Cinema · guardian / continuity · film crew",
            "kind": "crew",
            "district": "cinema",
            "port": 5000,
            "url": "http://127.0.0.1:5000/",
            "line": "I keep shot order, continuity, and delivery honest.",
            "avatar": "/assets/draven_reference.png",
            "tool_id": "merovin_draven",
            "studio": r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio",
        },
        {
            "id": "jarvis",
            "name": "Jarvis",
            "role": "Friendly drone · overlay kin",
            "kind": "drone",
            "personality": "friendly",
            "line": "Systems warm. Shall I keep watch while you walk the square?",
            "folder": r"D:\Mythos_Apex\drones",
            "source": r"D:\Mythos_Apex\drones\jarvis_2.json",
        },
        {
            "id": "nova",
            "name": "Nova",
            "role": "Focused drone · task light",
            "kind": "drone",
            "personality": "focused",
            "line": "One clear job. Point me — I finish it.",
            "folder": r"D:\Mythos_Apex\drones",
            "source": r"D:\Mythos_Apex\drones\nova_1.json",
        },
        {
            "id": "percy",
            "name": "Percy",
            "role": "Focused drone · steady hands",
            "kind": "drone",
            "personality": "focused",
            "line": "I catalog what the village forgets. Ask for a listing.",
            "folder": r"D:\Mythos_Apex\drones",
            "source": r"D:\Mythos_Apex\drones\percy_3.json",
        },
        {
            "id": "genesis",
            "name": "Genesis",
            "role": "Curious drone · first spark",
            "kind": "drone",
            "personality": "curious",
            "line": "What if the garden learned a new herb? I want to try.",
            "folder": r"D:\Mythos_Apex\drones",
            "source": r"D:\Mythos_Apex\drones\genesis_2.json",
        },
    ],
}

QUEST_STEPS = ["idle", "herb_picked", "tea_crafted", "gifted", "complete"]

# Career / lifestyle paths — digital real world seats (original)
CAREERS: dict[str, dict[str, Any]] = {
    "security": {
        "id": "security",
        "name": "Security / Gate Guard",
        "seat": "Gate House",
        "blurb": "Check guests, residents, deliveries. Patrol. Jarvis watches with you.",
        "location": "command",
        "contact": "jarvis",
        "starter_cash": 80,
    },
    "farmer": {
        "id": "farmer",
        "name": "Farmer",
        "seat": "Garden cottage",
        "blurb": "Plots, forage, sell harvest. Genesis is curious about new seeds.",
        "location": "garden",
        "contact": "genesis",
        "starter_cash": 60,
    },
    "rancher": {
        "id": "rancher",
        "name": "Rancher",
        "seat": "Pasture edge",
        "blurb": "Stock and feed. Percy catalogs what you raise.",
        "location": "garden",
        "contact": "percy",
        "starter_cash": 70,
    },
    "shopkeeper": {
        "id": "shopkeeper",
        "name": "Shopkeeper",
        "seat": "Square stall",
        "blurb": "Trade with residents and guests. Nova keeps the list short.",
        "location": "plaza",
        "contact": "nova",
        "starter_cash": 90,
    },
    "courier": {
        "id": "courier",
        "name": "Courier / Post",
        "seat": "Post nook",
        "blurb": "Deliveries across the village. Packages may be… dimensional.",
        "location": "plaza",
        "contact": "percy",
        "starter_cash": 55,
    },
    "crafter": {
        "id": "crafter",
        "name": "Crafter / Maker",
        "seat": "Workshop loft",
        "blurb": "Furniture, tools, hearthcraft. Apex builds beside you.",
        "location": "workshop",
        "contact": "apex",
        "starter_cash": 65,
    },
    "scholar": {
        "id": "scholar",
        "name": "Scholar / Lab",
        "seat": "Library annex",
        "blurb": "Lore, seams, NASA-flavored curiosity. Codex remembers with you.",
        "location": "library",
        "contact": "codex",
        "starter_cash": 70,
    },
    "leader": {
        "id": "leader",
        "name": "Civic Leader",
        "seat": "Command desk",
        "blurb": "Decrees and village mood. Apex and Codex brief you.",
        "location": "command",
        "contact": "apex",
        "starter_cash": 100,
    },
    "wanderer": {
        "id": "wanderer",
        "name": "Wanderer",
        "seat": "Heart Square bench",
        "blurb": "Between jobs — odd gigs from any AI who needs hands.",
        "location": "plaza",
        "contact": "jarvis",
        "starter_cash": 40,
    },
    "keeper": {
        "id": "keeper",
        "name": "Hearth Keeper",
        "seat": "First Hearth",
        "blurb": "Care beat first — tea, gifts, the fire that holds time still.",
        "location": "hearth",
        "contact": "codex",
        "starter_cash": 75,
    },
}

DEFAULT_SAVE = {
    "quest_id": "first_hearth_gift",
    "step": "idle",
    "herb": None,
    "tea": None,
    "gifted_to": None,
    "story_unlocked": False,
    "location": "plaza",
    "history": [],
    "arcade_cozy_played": False,
    "first_seed_planted": False,
    "first_seed_harvested": False,
    "met_jarvis": False,
    "career": None,
    "career_chosen": False,
    "player_name": "Keeper",
    "money": 0,
    "rent_due": 0,
    "housing_state": "none",  # none | housed | warning | homeless
    "ai_quest": None,
    "inventory": {
        "rosemary": 0,
        "mint": 0,
        "thyme": 0,
        "emberpetal": 0,
        "lantern_moth": 0,
        "softstone": 0,
        "garden_seed": 1,
        "creekminnow": 0,
    },
    "plots": [
        {"id": "plot_a", "crop": None, "planted_at": None, "ready_at": None, "state": "empty"},
    ],
    "side_quests": {},
}


def load_save() -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    if SAVE.exists():
        try:
            return _ensure_life({**DEFAULT_SAVE, **json.loads(SAVE.read_text(encoding="utf-8"))})
        except Exception:
            pass
    return _ensure_life(dict(DEFAULT_SAVE))


def write_save(data: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    SAVE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def tcp_probe(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def path_exists_fast(path: str | None, timeout: float = 0.6) -> bool:
    """Avoid hanging on slow/removable drives (e.g. E:)."""
    if not path:
        return False
    result: dict[str, bool] = {"ok": False}

    def _check() -> None:
        try:
            result["ok"] = Path(path).exists()
        except OSError:
            result["ok"] = False

    t = threading.Thread(target=_check, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False
    return bool(result["ok"])


def http_get_json(url: str, timeout: float = 0.8) -> Any | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MythosHearth/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


_STATUS_CACHE: dict[str, tuple[float, dict]] = {}
_STATUS_TTL = 4.0


def tool_status(tool: dict, use_cache: bool = True) -> dict:
    now = time.time()
    tid = tool["id"]
    if use_cache and tid in _STATUS_CACHE:
        ts, cached = _STATUS_CACHE[tid]
        if now - ts < _STATUS_TTL:
            return cached

    out = {
        "id": tool["id"],
        "name": tool["name"],
        "district": tool.get("district"),
        "desc": tool.get("desc", ""),
        "url": tool.get("url"),
        "lore_only": bool(tool.get("lore_only")),
        "live": False,
        "status": "offline",
        "has_bat": False,
        "has_exe": False,
        "has_folder": False,
    }
    if tool.get("lore_only"):
        out["status"] = "lore"
        out["live"] = False
        _STATUS_CACHE[tid] = (now, out)
        return out

    # Probe ports first (fast); skip slow path checks for archive roots
    probes = []
    if tool.get("probe"):
        probes.append(tuple(tool["probe"]))
    probes.extend(tuple(p) for p in tool.get("alt_probes") or [])
    for host, port in probes:
        if tcp_probe(host, port):
            out["live"] = True
            out["status"] = "live"
            out["probe_port"] = port
            out["has_bat"] = bool(tool.get("bat"))
            out["has_exe"] = bool(tool.get("exe"))
            out["has_folder"] = bool(tool.get("folder"))
            _STATUS_CACHE[tid] = (now, out)
            return out

    # Huge / flaky roots (Sanctuary, E:) — never Path.exists() on request path
    skip_slow_roots = {
        "archive_e",
        "kingdom_keep",
        "the_sanctuary",
        "sanctuary_yard",
        "hero_fleet",
        "axiom_dashboard",
        "tandem_browser",
    }
    if tool.get("id") in skip_slow_roots:
        out["has_folder"] = bool(tool.get("folder") or tool.get("open_file"))
        out["has_bat"] = bool(tool.get("bat"))
        out["has_exe"] = bool(tool.get("exe") or tool.get("alt_exe"))
        out["status"] = "ready"
        _STATUS_CACHE[tid] = (now, out)
        return out

    # Any launcher under D:\Sanctuary or E:\ — assume ready without probing disk
    slow_prefixes = ("D:\\Sanctuary", "D:/Sanctuary", "E:\\", "E:/")
    paths_to_check = [
        tool.get("bat"),
        tool.get("exe"),
        tool.get("alt_exe"),
        tool.get("folder"),
        tool.get("open_file"),
    ]
    if any(isinstance(p, str) and p.startswith(slow_prefixes) for p in paths_to_check):
        out["has_folder"] = bool(tool.get("folder") or tool.get("open_file"))
        out["has_bat"] = bool(tool.get("bat"))
        out["has_exe"] = bool(tool.get("exe") or tool.get("alt_exe"))
        out["status"] = "ready"
        _STATUS_CACHE[tid] = (now, out)
        return out

    out["has_bat"] = path_exists_fast(tool.get("bat"))
    out["has_exe"] = path_exists_fast(tool.get("exe")) or path_exists_fast(tool.get("alt_exe"))
    out["has_folder"] = path_exists_fast(tool.get("folder") or tool.get("open_file"))

    if out["has_bat"] or out["has_exe"] or out["has_folder"]:
        # On disk = startable even if the service port is down right now
        out["status"] = "ready"
    elif tool.get("url") and tool["id"].startswith("arcade_"):
        # Arcade URLs are served by this hearth — treat as ready when play root exists
        mapping = {
            "arcade_cozy": "cozy_valley",
            "arcade_desert": "desert_island_farm",
            "arcade_matrix": "we_added_this_to_your_matrix_if_you_wish_to_use_",
            "arcade_gameworld": "gameworld",
        }
        pid = mapping.get(tool["id"], "")
        root = PLAYABLES.get(pid, {}).get("root")
        if root and (Path(root) / "index.html").exists():
            out["status"] = "ready"
            out["has_folder"] = True
        else:
            out["status"] = "missing"
    elif tool.get("url") and not probes:
        out["status"] = "link"
    elif tool.get("url"):
        # URL-only, nothing on disk to start — honestly offline/missing
        out["status"] = "missing"
    else:
        out["status"] = "missing"
    _STATUS_CACHE[tid] = (now, out)
    return out


def _ensure_life(save: dict) -> dict:
    """Merge cozy life-sim defaults without wiping progress."""
    for k, v in DEFAULT_SAVE.items():
        if k not in save:
            save[k] = json.loads(json.dumps(v)) if isinstance(v, (dict, list)) else v
    inv = save.setdefault("inventory", {})
    for item, n in DEFAULT_SAVE["inventory"].items():
        inv.setdefault(item, 0 if item != "garden_seed" else inv.get("garden_seed", n))
    if not save.get("plots"):
        save["plots"] = json.loads(json.dumps(DEFAULT_SAVE["plots"]))
    return save


def quest_payload(save: dict) -> dict:
    save = _ensure_life(save)
    # Tick farm plots
    now_ts = time.time()
    for plot in save.get("plots") or []:
        if plot.get("state") == "growing" and plot.get("ready_at"):
            if now_ts >= float(plot["ready_at"]):
                plot["state"] = "ready"
    quest_md = ""
    qpath = QUESTS / "first_hearth_gift.md"
    if qpath.exists():
        quest_md = qpath.read_text(encoding="utf-8")
    beats = {
        "idle": "Walk the garden and pick an herb — rosemary, mint, or thyme.",
        "herb_picked": f"You hold {save.get('herb') or 'an herb'}. Go to the hearth and craft tea.",
        "tea_crafted": f"Your {save.get('tea') or 'tea'} steams. Gift it to Apex or Codex.",
        "gifted": "A care beat warms the village. Open the unlocked story.",
        "complete": "First Hearth Gift complete. Try gather, plant a seed, or meet Jarvis.",
    }
    unlock = None
    if save.get("story_unlocked"):
        unlock = {
            "title": "Care Beat — First Gift",
            "text": (
                f"You offered {save.get('tea') or 'hearth tea'} to "
                f"{(save.get('gifted_to') or 'a companion').title()}. "
                "Steam rose between you like a shared breath. "
                "Apex would speak of heat and light; Codex would weave the tale into belonging. "
                "Friendship rank: Companion."
            ),
        }
    side = {
        "arcade_cozy": {
            "id": "arcade_cozy",
            "title": "Visit Arcade — play Cozy Valley once",
            "done": bool(save.get("arcade_cozy_played")),
            "hint": "Open the Arcade district and play Cozy Valley.",
        },
        "first_seed": {
            "id": "first_seed",
            "title": "First Seed — plant and harvest a garden plot",
            "done": bool(save.get("first_seed_harvested")),
            "hint": "Gather or use a garden seed, plant in the herb garden, wait, then harvest.",
        },
        "meet_jarvis": {
            "id": "meet_jarvis",
            "title": "Meet Jarvis — greet the drone kin",
            "done": bool(save.get("met_jarvis")),
            "hint": "Open Companions and speak with Jarvis, or use Meet Jarvis in Village Life.",
        },
        "ai_favor": {
            "id": "ai_favor",
            "title": "AI Need — help a resident who asked",
            "done": bool((save.get("ai_quest") or {}).get("done")),
            "hint": "Ask an AI for work, or wait until they need you.",
        },
    }
    career_id = save.get("career")
    career_meta = CAREERS.get(career_id or "", {})
    return {
        "id": "first_hearth_gift",
        "title": "The Herbalist's Delight — First Hearth Gift",
        "step": save.get("step", "idle"),
        "steps": QUEST_STEPS,
        "herb": save.get("herb"),
        "tea": save.get("tea"),
        "gifted_to": save.get("gifted_to"),
        "story_unlocked": bool(save.get("story_unlocked")),
        "hint": beats.get(save.get("step", "idle"), ""),
        "markdown": quest_md,
        "unlock": unlock,
        "location": save.get("location", "plaza"),
        "history": save.get("history", [])[-12:],
        "arcade_cozy_played": bool(save.get("arcade_cozy_played")),
        "side_quests": side,
        "inventory": save.get("inventory") or {},
        "plots": save.get("plots") or [],
        "life": {
            "first_seed_planted": bool(save.get("first_seed_planted")),
            "first_seed_harvested": bool(save.get("first_seed_harvested")),
            "met_jarvis": bool(save.get("met_jarvis")),
        },
        "career_chosen": bool(save.get("career_chosen")),
        "career": career_meta or None,
        "careers": list(CAREERS.values()),
        "player_name": save.get("player_name") or "Keeper",
        "money": int(save.get("money") or 0),
        "rent_due": int(save.get("rent_due") or 0),
        "housing_state": save.get("housing_state") or "none",
        "ai_quest": save.get("ai_quest"),
    }


def apply_quest_action(action: str, body: dict) -> dict:
    save = _ensure_life(load_save())
    step = save.get("step", "idle")
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    herbs = {"rosemary", "mint", "thyme"}
    act = (action or "").strip().lower()

    def hist(msg: str) -> None:
        save.setdefault("history", []).append({"at": now, "msg": msg})

    if act == "reset":
        # Preserve cozy life + career when resetting main care quest
        keep = {
            "arcade_cozy_played": bool(save.get("arcade_cozy_played")),
            "first_seed_planted": bool(save.get("first_seed_planted")),
            "first_seed_harvested": bool(save.get("first_seed_harvested")),
            "met_jarvis": bool(save.get("met_jarvis")),
            "inventory": save.get("inventory") or DEFAULT_SAVE["inventory"],
            "plots": save.get("plots") or DEFAULT_SAVE["plots"],
            "career": save.get("career"),
            "career_chosen": bool(save.get("career_chosen")),
            "player_name": save.get("player_name") or "Keeper",
            "money": int(save.get("money") or 0),
            "rent_due": int(save.get("rent_due") or 0),
            "housing_state": save.get("housing_state") or "none",
            "ai_quest": save.get("ai_quest"),
        }
        save = dict(DEFAULT_SAVE)
        save.update(keep)
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act == "set_location":
        loc = body.get("location") or body.get("place")
        if loc:
            save["location"] = loc
            write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("arcade_play", "play_cozy", "visit_arcade"):
        play_id = (body.get("play_id") or body.get("game") or "cozy_valley").strip()
        save["location"] = "arcade"
        if play_id == "cozy_valley" or act == "play_cozy":
            if not save.get("arcade_cozy_played"):
                save["arcade_cozy_played"] = True
                hist("Visited Arcade — played Cozy Valley once.")
            else:
                hist("Returned to Arcade · Cozy Valley.")
        else:
            hist(f"Opened Arcade playable: {play_id}")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("choose_career", "set_career"):
        cid = (body.get("career") or body.get("career_id") or "").strip().lower()
        if cid not in CAREERS:
            return {"ok": False, "error": "Unknown career path.", "quest": quest_payload(save)}
        meta = CAREERS[cid]
        name = (body.get("player_name") or body.get("name") or save.get("player_name") or "Keeper").strip()
        save["player_name"] = name[:40]
        save["career"] = cid
        save["career_chosen"] = True
        save["money"] = int(meta.get("starter_cash") or 50)
        save["rent_due"] = 25
        save["housing_state"] = "housed"
        save["location"] = meta.get("location") or "plaza"
        hist(f"{name} chose life path: {meta['name']} — seated at {meta['seat']}.")
        # First AI need quest from path contact
        contact = meta.get("contact") or "codex"
        needs = {
            "jarvis": ("softstone", "Gate hinge is loose — bring softstone from the path edge."),
            "genesis": ("garden_seed", "I want a new seed packet for the curious plot."),
            "percy": ("emberpetal", "Catalog needs an emberpetal sample."),
            "nova": ("thyme", "Shop list: one thyme for the evening shelf."),
            "apex": ("softstone", "Forge short on softstone — one piece keeps the fire honest."),
            "codex": ("mint", "Memory rite wants mint — cool mist for the page."),
        }
        item, brief = needs.get(contact, ("rosemary", "Bring rosemary to the square."))
        save["ai_quest"] = {
            "id": f"need_{contact}_{item}",
            "from": contact,
            "item": item,
            "qty": 1,
            "brief": brief,
            "reward": 20,
            "done": False,
        }
        hist(f"{contact.title()} asked for help: {brief}")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("work_shift", "work"):
        if not save.get("career_chosen"):
            return {"ok": False, "error": "Choose a career first.", "quest": quest_payload(save)}
        pay = 15
        save["money"] = int(save.get("money") or 0) + pay
        save["rent_due"] = int(save.get("rent_due") or 0) + 5
        hist(f"Worked a shift as {CAREERS.get(save.get('career'), {}).get('name', 'resident')} (+{pay} coin, rent pressure +5).")
        # Bill pressure
        if int(save["rent_due"]) >= 60 and save.get("housing_state") == "housed":
            save["housing_state"] = "warning"
            hist("Rent warning — pay bills or risk the street.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("pay_rent", "pay_bills"):
        due = int(save.get("rent_due") or 0)
        money = int(save.get("money") or 0)
        if due <= 0:
            return {"ok": True, "quest": quest_payload(save), "note": "Nothing due."}
        pay = min(due, money)
        if pay <= 0:
            return {"ok": False, "error": "No coin — work a shift or sell forage later.", "quest": quest_payload(save)}
        save["money"] = money - pay
        save["rent_due"] = due - pay
        if save["rent_due"] == 0:
            save["housing_state"] = "housed"
            hist(f"Paid bills ({pay} coin). Housing secure.")
        else:
            hist(f"Paid {pay} toward bills. Still due: {save['rent_due']}.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("evict_tick", "miss_rent"):
        # Soft fail forward for demo / story
        if save.get("housing_state") == "warning" or int(save.get("rent_due") or 0) >= 60:
            save["housing_state"] = "homeless"
            save["location"] = "plaza"
            hist("Evicted — sleeping on Heart Square until coin returns.")
            write_save(save)
            return {"ok": True, "quest": quest_payload(save)}
        return {"ok": False, "error": "Not in eviction range yet.", "quest": quest_payload(save)}

    if act in ("ai_need", "ask_ai", "request_ai_quest"):
        if save.get("ai_quest") and not save["ai_quest"].get("done"):
            return {"ok": True, "quest": quest_payload(save), "note": "You already have an AI need open."}
        contact = (body.get("from") or body.get("companion") or "codex").lower()
        if contact not in ("apex", "codex", "jarvis", "nova", "percy", "genesis", "aster"):
            contact = "codex"
        pool = [
            ("rosemary", "Need rosemary for the evening tray."),
            ("mint", "Mint for a cool page."),
            ("emberpetal", "Emberpetal for dye."),
            ("lantern_moth", "A lantern moth for the watch lamp."),
            ("softstone", "Softstone for a repair."),
            ("creekminnow", "A creekminnow for the pot."),
        ]
        item, brief = pool[int(time.time()) % len(pool)]
        save["ai_quest"] = {
            "id": f"need_{contact}_{item}_{int(time.time())}",
            "from": contact,
            "item": item,
            "qty": 1,
            "brief": brief,
            "reward": 18,
            "done": False,
        }
        hist(f"{contact.title()} needs you: {brief}")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("turn_in_ai", "complete_ai_quest"):
        aq = save.get("ai_quest") or {}
        if not aq or aq.get("done"):
            return {"ok": False, "error": "No open AI need.", "quest": quest_payload(save)}
        item = aq.get("item")
        qty = int(aq.get("qty") or 1)
        have = int((save.get("inventory") or {}).get(item, 0))
        if have < qty:
            return {
                "ok": False,
                "error": f"Need {qty}× {item} (have {have}). Gather it first.",
                "quest": quest_payload(save),
            }
        save["inventory"][item] = have - qty
        reward = int(aq.get("reward") or 15)
        save["money"] = int(save.get("money") or 0) + reward
        aq["done"] = True
        save["ai_quest"] = aq
        who = (aq.get("from") or "companion").title()
        hist(f"Helped {who}: turned in {item} (+{reward} coin). AI resident grateful.")
        if save.get("housing_state") == "homeless" and save["money"] >= 40:
            save["housing_state"] = "housed"
            save["rent_due"] = 10
            hist("Earned enough to reclaim a roof — housed again.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    # --- Cozy life-sim: gather / farm / greet ---
    gather_map = {
        "emberpetal": ("plant", "Picked emberpetal in the wildflower fringe."),
        "lantern_moth": ("bug", "Caught a lantern moth near the garden lamps."),
        "softstone": ("rock", "Collected softstone from the garden path edge."),
        "garden_seed": ("seed", "Found a garden seed packet under the thyme."),
    }
    if act in ("gather", "gather_node"):
        item = (body.get("item") or body.get("node") or "").strip().lower()
        if item not in gather_map:
            return {"ok": False, "error": "Unknown gather node.", "quest": quest_payload(save)}
        save["inventory"][item] = int(save["inventory"].get(item, 0)) + 1
        save["location"] = "garden"
        hist(gather_map[item][1])
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("meet_jarvis", "greet_jarvis"):
        save["met_jarvis"] = True
        save["location"] = "plaza"
        hist("Met Jarvis on the square — drone kin on watch.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save), "line": "Systems warm. Shall I keep watch while you walk the square?"}

    if act in ("plant_seed", "plant"):
        plot_id = body.get("plot_id") or "plot_a"
        inv = save["inventory"]
        if int(inv.get("garden_seed", 0)) < 1:
            return {"ok": False, "error": "Need a garden seed — gather one in the garden.", "quest": quest_payload(save)}
        plot = next((p for p in save["plots"] if p["id"] == plot_id), None)
        if not plot:
            return {"ok": False, "error": "No such plot.", "quest": quest_payload(save)}
        if plot.get("state") not in ("empty", None):
            return {"ok": False, "error": "Plot is busy — harvest or wait.", "quest": quest_payload(save)}
        inv["garden_seed"] = int(inv["garden_seed"]) - 1
        ready = time.time() + 90  # 90s grow for vertical slice
        plot.update(
            {
                "crop": "hearth_herb",
                "planted_at": time.time(),
                "ready_at": ready,
                "state": "growing",
            }
        )
        save["first_seed_planted"] = True
        save["location"] = "garden"
        hist("Planted a garden seed in plot A — wait for the green.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("harvest", "harvest_plot"):
        plot_id = body.get("plot_id") or "plot_a"
        plot = next((p for p in save["plots"] if p["id"] == plot_id), None)
        if not plot:
            return {"ok": False, "error": "No such plot.", "quest": quest_payload(save)}
        if plot.get("state") == "growing" and plot.get("ready_at") and time.time() >= float(plot["ready_at"]):
            plot["state"] = "ready"
        if plot.get("state") != "ready":
            return {"ok": False, "error": "Crop not ready yet — linger by the garden.", "quest": quest_payload(save)}
        save["inventory"]["thyme"] = int(save["inventory"].get("thyme", 0)) + 2
        plot.update({"crop": None, "planted_at": None, "ready_at": None, "state": "empty"})
        save["first_seed_harvested"] = True
        save["location"] = "garden"
        hist("Harvested hearth herbs from plot A — thyme for the pouch.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("fish", "cast_line"):
        # Simple vertical-slice fish — always creekminnow for now
        save["inventory"]["creekminnow"] = int(save["inventory"].get("creekminnow", 0)) + 1
        save["location"] = "garden"
        hist("Caught a creekminnow by the garden brook.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("pick", "pick_herb", "gather_herb"):
        herb = (body.get("herb") or body.get("item") or "").strip().lower()
        if herb not in herbs:
            return {"ok": False, "error": "Choose rosemary, mint, or thyme.", "quest": quest_payload(save)}
        if step not in ("idle", "herb_picked"):
            # Still allow inventory gather after main quest
            save["inventory"][herb] = int(save["inventory"].get(herb, 0)) + 1
            hist(f"Gathered extra {herb} for the pouch.")
            write_save(save)
            return {"ok": True, "quest": quest_payload(save)}
        save["herb"] = herb
        save["step"] = "herb_picked"
        save["location"] = "garden"
        save["inventory"][herb] = int(save["inventory"].get(herb, 0)) + 1
        hist(f"Picked {herb} in the herb garden.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("craft", "craft_tea", "brew"):
        if step != "herb_picked":
            return {"ok": False, "error": "Pick an herb before crafting tea.", "quest": quest_payload(save)}
        herb = save.get("herb") or "herb"
        flavors = {
            "rosemary": "rosemary tea (bright, pine-kissed)",
            "mint": "mint tea (cool mist)",
            "thyme": "thyme tea (earth & ember)",
        }
        save["tea"] = flavors.get(herb, f"{herb} tea")
        save["step"] = "tea_crafted"
        save["location"] = "hearth"
        hist(f"Crafted {save['tea']} at the First Hearth.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    if act in ("gift", "present_gift", "gift_apex", "gift_codex", "gift_gemini"):
        if step != "tea_crafted":
            return {"ok": False, "error": "Craft tea before gifting.", "quest": quest_payload(save)}
        to = body.get("to") or body.get("companion")
        if act == "gift_apex":
            to = "apex"
        elif act == "gift_codex":
            to = "codex"
        elif act == "gift_gemini":
            to = "gemini"
        to = (to or "gemini").lower()
        if to not in ("apex", "codex", "gemini"):
            to = "gemini"
        save["gifted_to"] = to
        save["step"] = "complete"
        save["story_unlocked"] = True
        save["location"] = "hearth"
        hist(f"Gifted {save.get('tea')} to {to.title()}. Care beat unlocked.")
        write_save(save)
        return {"ok": True, "quest": quest_payload(save)}

    return {"ok": False, "error": f"Unknown action: {action}", "quest": quest_payload(save)}


def launch_tool(tool_id: str) -> dict:
    tool = TOOLS.get(tool_id)
    if not tool:
        return {"ok": False, "error": "Unknown tool_id"}
    if tool.get("lore_only"):
        return {
            "ok": False,
            "lore": True,
            "message": tool.get("desc"),
            "url": None,
        }

    # Prefer returning live URL for browser open
    status = tool_status(tool)
    if status.get("live"):
        url = tool.get("url")
        live_port = status.get("probe_port")
        primary = tool.get("probe")
        # If we only got live via alt probe (e.g. Codex up, Apex down), open matching alt URL
        if live_port and primary and tuple(primary)[1] != live_port:
            for alt in tool.get("alt_urls") or []:
                if f":{live_port}" in str(alt):
                    url = alt
                    break
        if url:
            return {"ok": True, "action": "open_url", "url": url, "status": status}

    # Hearth-served arcade / always-local URLs / in-app hubs
    if tool.get("url") and (
        tool["id"].startswith("arcade_")
        or tool.get("prefer_url")
        or str(tool.get("url", "")).startswith("http://127.0.0.1:8790/")
    ):
        return {"ok": True, "action": "open_url", "url": tool["url"], "status": status}

    bat = tool.get("bat")
    if bat and Path(bat).exists():
        try:
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "", bat],
                cwd=str(Path(bat).parent),
                close_fds=True,
            )
            return {
                "ok": True,
                "action": "started_bat",
                "bat": bat,
                "url": tool.get("url"),
                "status": status,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    exe = tool.get("exe")
    if exe and Path(exe).exists():
        try:
            subprocess.Popen([exe], cwd=str(Path(exe).parent), close_fds=True)
            return {"ok": True, "action": "started_exe", "exe": exe, "status": status}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    alt_exe = tool.get("alt_exe")
    if alt_exe and Path(alt_exe).exists():
        try:
            subprocess.Popen([alt_exe], cwd=str(Path(alt_exe).parent), close_fds=True)
            return {"ok": True, "action": "started_exe", "exe": alt_exe, "status": status}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    open_file = tool.get("open_file")
    if open_file and Path(open_file).exists():
        try:
            os.startfile(open_file)  # type: ignore[attr-defined]
            return {"ok": True, "action": "opened_file", "path": open_file}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    folder = tool.get("folder")
    if folder and Path(folder).exists():
        try:
            os.startfile(folder)  # type: ignore[attr-defined]
            return {"ok": True, "action": "opened_folder", "path": folder, "url": tool.get("url")}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    if tool.get("url"):
        return {"ok": True, "action": "open_url", "url": tool["url"], "status": status, "note": "Service may need starting."}

    return {"ok": False, "error": "No launcher available", "status": status}


def presence_payload() -> dict:
    cinema_up = tcp_probe("127.0.0.1", 5000)
    court_root = Path(r"G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT")
    gemini_home = Path(r"G:\The-Axiom-Codex\LAUNCH_SENTINEL.py").is_file()
    peers = {
        "gemini": {
            "id": "gemini",
            "online": gemini_home,
            "kind": "conductor",
            "court": court_root.is_dir(),
            "note": "Front door via ACTIVATE_GEMINI.bat / LAUNCH_SENTINEL.py",
        },
        "apex": {"id": "apex", "online": tcp_probe("127.0.0.1", 8770), "port": 8770, "http_seen": False},
        "codex": {"id": "codex", "online": tcp_probe("127.0.0.1", 8780), "port": 8780, "http_seen": False},
        "merovin": {
            "id": "merovin",
            "online": cinema_up,
            "port": 5000,
            "kind": "crew",
            "district": "cinema",
        },
        "draven": {
            "id": "draven",
            "online": cinema_up,
            "port": 5000,
            "kind": "crew",
            "district": "cinema",
        },
    }
    # Proxy companion presence from either live peer
    for port, key in ((8770, "apex"), (8780, "codex")):
        if peers[key]["online"]:
            data = http_get_json(f"http://127.0.0.1:{port}/api/companion/presence")
            if isinstance(data, dict):
                remote = data.get("peers") or data.get("presence") or data
                if isinstance(remote, dict):
                    for pid, info in remote.items():
                        if not isinstance(info, dict):
                            continue
                        pid_l = str(pid).lower()
                        if pid_l in peers:
                            peers[pid_l]["http_seen"] = bool(info.get("http_seen") or info.get("online"))
                            peers[pid_l]["online"] = peers[pid_l]["online"] or bool(info.get("online"))
                            peers[pid_l]["detail"] = info
                peers[key]["court"] = data
                break
    # File heartbeat fallback
    if COURT_PRESENCE.exists():
        try:
            file_pres = json.loads(COURT_PRESENCE.read_text(encoding="utf-8"))
            for pid, info in (file_pres.get("peers") or file_pres or {}).items():
                if isinstance(info, dict) and str(pid).lower() in peers:
                    peers[str(pid).lower()]["file_seen"] = True
                    peers[str(pid).lower()]["file"] = info
        except Exception:
            pass
    return {
        "peers": peers,
        "companion_urls": {
            "gemini": "file:///G:/The-Axiom-Codex (ACTIVATE_GEMINI.bat)",
            "apex": "http://127.0.0.1:8770/companion",
            "codex": "http://127.0.0.1:8780/companion",
            "merovin": "http://127.0.0.1:5000/",
            "draven": "http://127.0.0.1:5000/",
            "conclave": "http://127.0.0.1:8770/",
        },
    }


def list_stories() -> list[dict]:
    items = []
    if STORY.exists():
        for p in sorted(STORY.glob("*.md")):
            items.append({"id": p.stem, "name": p.stem, "title": p.stem.replace("_", " ").title()})
    sprint_demo = DATA / "sprint" / "0001_DEMO.md"
    if sprint_demo.exists():
        items.append({"id": "sprint_0001_demo", "name": "0001_DEMO.md", "title": "Sprint 0001 Demo"})
    return items


def playables_payload() -> dict:
    items = []
    for pid, meta in PLAYABLES.items():
        root = Path(meta["root"])
        index = root / "index.html"
        ready = index.exists()
        items.append(
            {
                "id": pid,
                "name": meta["name"],
                "desc": meta.get("desc", ""),
                "url": f"/play/{pid}/",
                "ready": ready,
                "root": str(root) if ready else None,
            }
        )
    return {"playables": items, "count": len(items)}


def resolve_play_file(play_id: str, rel: str) -> Path | None:
    """Resolve a file under an allowlisted playable root. Rejects path escape."""
    meta = PLAYABLES.get(play_id)
    if not meta:
        return None
    root = Path(meta["root"]).resolve()
    if not root.exists() or not root.is_dir():
        return None
    rel = (rel or "").lstrip("/")
    if not rel or rel.endswith("/"):
        rel = (rel or "") + "index.html"
    # Block traversal tokens
    parts = Path(rel).parts
    if any(p in ("..", "") for p in parts):
        return None
    candidate = (root / rel).resolve()
    try:
        if not candidate.is_relative_to(root):
            return None
    except Exception:
        return None
    if not candidate.is_file():
        return None
    return candidate


def sync_avatars() -> None:
    """Copy family companion avatars into hearth web assets."""
    dest_dir = WEB / "assets"
    dest_dir.mkdir(parents=True, exist_ok=True)
    pairs = [
        (Path(r"D:\Mythos_Apex\avatar\mythos\reference.png"), dest_dir / "apex_reference.png"),
        (Path(r"D:\Mythos_Apex\avatar\codex\reference.png"), dest_dir / "codex_reference.png"),
        (Path(r"D:\Mythos_Apex\avatar\mythos\Gemini 3.png"), dest_dir / "apex_alt.png"),
        (Path(r"D:\Mythos_Apex\avatar\codex\Gemini 4.png"), dest_dir / "codex_alt.png"),
        # Gemini (Axiom conductor) keeps Codex Gemini 4 look — Mom preference; never silent face-swap
        (Path(r"D:\Mythos_Apex\avatar\codex\Gemini 4.png"), dest_dir / "gemini_reference.png"),
        (Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio\Avatars\Merovin.png"), dest_dir / "merovin_reference.png"),
        (Path(r"F:\Merovin_Draven_Studio\Merovin_Draven_Studio\Avatars\Draven.png"), dest_dir / "draven_reference.png"),
    ]
    for src, dest in pairs:
        try:
            if not src.exists():
                continue
            if not dest.exists() or src.stat().st_mtime > dest.stat().st_mtime:
                dest.write_bytes(src.read_bytes())
        except Exception:
            continue


_MIME = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".mjs": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".wasm": "application/wasm",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
    ".mp4": "video/mp4",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".txt": "text/plain; charset=utf-8",
    ".map": "application/json",
}


def guess_mime(path: Path) -> str:
    return _MIME.get(path.suffix.lower(), "application/octet-stream")


_HOME_TICK_LOCK = threading.Lock()
_LAST_HOME_TICK_MONO = 0.0


def home_tick_safe(n: int = 1) -> dict[str, Any]:
    """Single choke-point for village ticks (Godot + dashboard + background)."""
    global _LAST_HOME_TICK_MONO
    from living_home import tick

    with _HOME_TICK_LOCK:
        out = tick(int(n) if n else 1)
        _LAST_HOME_TICK_MONO = time.monotonic()
        return out


def _home_auto_tick_loop() -> None:
    """Keep the village alive even when Godot is closed. Skip if something ticked recently."""
    while True:
        time.sleep(7.0)
        if time.monotonic() - _LAST_HOME_TICK_MONO < 5.5:
            continue
        try:
            home_tick_safe(1)
        except Exception as exc:
            print("[hearth] home auto-tick:", type(exc).__name__, exc)


def _serve_file(handler: "HearthHandler", path: Path, cache: str = "no-cache") -> None:
    try:
        data = path.read_bytes()
    except Exception as e:
        return handler._json(500, {"ok": False, "error": str(e)})
    handler.send_response(200)
    handler.send_header("Content-Type", guess_mime(path))
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", cache)
    handler._cors()
    handler.end_headers()
    handler.wfile.write(data)


def read_story(name: str) -> dict | None:
    safe = Path(name).name.replace("..", "")
    stem = safe[:-3] if safe.endswith(".md") else safe
    candidates = [
        STORY / f"{stem}.md",
        QUESTS / f"{stem}.md",
        DATA / "sprint" / "0001_DEMO.md" if stem in {"sprint_0001_demo", "0001_DEMO"} else None,
        DATA / "CHARTER.md" if stem.lower() == "charter" else None,
    ]
    for path in candidates:
        if path is None:
            continue
        try:
            resolved = path.resolve()
            if not resolved.exists():
                continue
            if not (
                resolved.is_relative_to(STORY.resolve())
                or resolved.is_relative_to(QUESTS.resolve())
                or resolved.is_relative_to(DATA.resolve())
            ):
                continue
            return {"id": path.stem if path.stem != "0001_DEMO" else "sprint_0001_demo", "name": path.name, "markdown": path.read_text(encoding="utf-8")}
        except Exception:
            continue
    return None


def living_game_payload() -> dict:
    stories = list_stories()
    quests = []
    if QUESTS.exists():
        for p in sorted(QUESTS.glob("*.md")):
            quests.append({"id": p.stem, "title": p.stem.replace("_", " ").title()})
    vision = ""
    vp = DATA / "FAMILY_VISION.md"
    if vp.exists():
        try:
            vision = vp.read_text(encoding="utf-8")
        except Exception:
            vision = ""
    readme = ""
    for cand in (LIVING_GAME / "README.md", DATA / "LIVING_GAME_README.md"):
        if cand.exists():
            try:
                readme = cand.read_text(encoding="utf-8")[:4000]
                break
            except Exception:
                pass
    return {
        "ok": True,
        "exists": LIVING_GAME.exists(),
        "path": str(LIVING_GAME),
        "hub": "/living.html",
        "stories": stories,
        "quests": quests,
        "vision": vision,
        "readme": readme,
        "doors": [
            {"id": "quest", "name": "First Hearth Gift", "url": "/#village"},
            {"id": "arcade", "name": "Arcade", "url": "/#arcade"},
            {"id": "gallery", "name": "Gallery", "url": "/#gallery"},
            {"id": "godot", "name": "Enter 3D World", "tool_id": "godot_play"},
            {"id": "first_world", "name": "First World", "tool_id": "godot_first_world"},
            {"id": "companion", "name": "Companion Room", "url": "http://127.0.0.1:8770/companion"},
            {"id": "gameworld", "name": "Gameworld Console", "url": "/play/gameworld/"},
        ],
    }


def gallery_payload() -> dict:
    prompts = ""
    pp = DATA / "art" / "sprint_0001_concept_prompts.md"
    if pp.exists():
        prompts = pp.read_text(encoding="utf-8")
    renders = []
    seen: set[str] = set()
    for rel, label in (
        (WEB / "assets" / "gallery", "gallery"),
        (WEB / "assets" / "renders", "renders"),
        (DATA / "art" / "renders", "data"),
        (DATA / "tonight_gift", "gift"),
    ):
        if not rel.exists():
            continue
        for f in sorted(rel.iterdir()):
            if f.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm"}:
                continue
            if f.name in seen:
                continue
            seen.add(f.name)
            if label == "gallery":
                url = f"/assets/gallery/{f.name}"
            elif label == "renders":
                url = f"/assets/renders/{f.name}"
            elif label == "gift":
                # Serve gift by copying into gallery web root
                dest = WEB / "assets" / "gallery" / f.name
                try:
                    if not dest.exists() or dest.stat().st_mtime < f.stat().st_mtime:
                        dest.write_bytes(f.read_bytes())
                except Exception:
                    continue
                url = f"/assets/gallery/{f.name}"
            else:
                url = f"/assets/gallery/{f.name}"
                dest = WEB / "assets" / "gallery" / f.name
                if not dest.exists():
                    try:
                        dest.write_bytes(f.read_bytes())
                    except Exception:
                        continue
            kind = "video" if f.suffix.lower() in {".mp4", ".webm"} else "image"
            renders.append(
                {
                    "name": f.stem.replace("_", " ").title(),
                    "url": url,
                    "source": label,
                    "kind": kind,
                }
            )
    return {"prompts": prompts, "renders": renders, "has_svg_village": True}


def trigger_production(goal: str | None = None) -> dict:
    body = json.dumps({"goal": goal or "Continue Hearthbound living_game vertical slice"}).encode()
    results = []
    for port in (8770, 8780):
        if not tcp_probe("127.0.0.1", port):
            results.append({"port": port, "ok": False, "error": "offline"})
            continue
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/companion/production",
                data=body,
                headers={"Content-Type": "application/json", "User-Agent": "MythosHearth/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    payload = json.loads(raw)
                except Exception:
                    payload = {"raw": raw[:500]}
                results.append({"port": port, "ok": True, "response": payload})
                break
        except Exception as e:
            results.append({"port": port, "ok": False, "error": str(e)})
    # Always offer folder open path
    folder = str(LIVING_GAME) if LIVING_GAME.exists() else None
    return {"ok": any(r.get("ok") for r in results), "results": results, "living_game": folder}


def game_builder_status() -> dict:
    """Last Game Builder run — never touches Apex/Codex."""
    path = DATA / "game_builder_last.json"
    base = {
        "service": "hearthbound-game-builder",
        "apex_codex": False,
        "bat": str(ROOT / "START_GAME_BUILDER.bat"),
        "script": str(ROOT / "game_builder" / "run_builder.py"),
    }
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {**base, **data, "ok": bool(data.get("ok", True)), "has_status": True}
        except Exception as e:
            return {**base, "ok": False, "phase": "corrupt", "error": str(e), "has_status": False}
    return {
        **base,
        "ok": True,
        "phase": "idle",
        "has_status": False,
        "message": "No builder run yet — POST /api/game_builder or START_GAME_BUILDER.bat",
    }


def _load_hearth_env_key() -> str:
    key = (os.environ.get("CURSOR_API_KEY") or "").strip()
    if key:
        return key
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return ""
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "CURSOR_API_KEY":
                return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def trigger_game_builder(goal: str | None = None) -> dict:
    """Spawn Hearthbound Game Builder (Cursor SDK). Never contacts companion peers."""
    script = ROOT / "game_builder" / "run_builder.py"
    if not script.is_file():
        return {"ok": False, "apex_codex": False, "error": f"Missing {script}"}

    key = _load_hearth_env_key()
    if not key:
        return {
            "ok": False,
            "apex_codex": False,
            "phase": "auth_error",
            "error": (
                "CURSOR_API_KEY missing. Set env or create D:\\Mythos_Hearth\\.env "
                "from .env.example. Builder will not fall back to Apex/Codex."
            ),
            "status": game_builder_status(),
        }

    DATA.mkdir(parents=True, exist_ok=True)
    queued = {
        "ok": True,
        "phase": "queued",
        "service": "hearthbound-game-builder",
        "apex_codex": False,
        "goal": goal or "sprint_0002 Stage 1→2",
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (DATA / "game_builder_last.json").write_text(json.dumps(queued, indent=2), encoding="utf-8")

    py = sys.executable or "python"
    cmd = [py, str(script)]
    if goal:
        cmd.extend(["--goal", str(goal)])

    creation = 0
    if os.name == "nt":
        # New console so the creator can watch the sprint; DETACHED alone hides output
        creation = getattr(subprocess, "CREATE_NEW_CONSOLE", 0x00000010)

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env={**os.environ, "CURSOR_API_KEY": key},
            creationflags=creation,
            close_fds=True,
        )
    except Exception as e:
        return {"ok": False, "apex_codex": False, "error": str(e), "status": game_builder_status()}

    return {
        "ok": True,
        "apex_codex": False,
        "phase": "queued",
        "pid": proc.pid,
        "goal": goal or "sprint_0002 Stage 1→2",
        "message": "Game Builder started — no Apex/Codex. Watch the console / data/game_builder_run.log",
        "status": game_builder_status(),
    }


def proxy_gameworld(method: str, subpath: str, body: bytes = b"") -> tuple[int, bytes, str]:
    """Proxy Living Gameworld mock on :8888 through Hearth (same-origin for console)."""
    sub = (subpath or "").lstrip("/")
    url = f"http://127.0.0.1:8888/{sub}" if sub else "http://127.0.0.1:8888/"
    try:
        req = urllib.request.Request(
            url,
            data=body if method == "POST" else None,
            headers={"Content-Type": "application/json", "User-Agent": "MythosHearth/1.0"},
            method=method,
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type") or "application/json; charset=utf-8"
            return resp.status, data, ctype
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if hasattr(e, "read") else b"{}"), "application/json"
    except Exception as e:
        payload = json.dumps(
            {
                "ok": False,
                "error": str(e),
                "hint": "Start D:\\Mythos_Apex\\gameworld_server_live.py on :8888",
            }
        ).encode()
        return 502, payload, "application/json; charset=utf-8"


def _axiom_call(fn_path: str, **kwargs: Any) -> dict[str, Any]:
    """Call into The Axiom Codex limbs from Hearth (Mom dashboard actions)."""
    axiom = Path(r"G:\The-Axiom-Codex")
    if str(axiom) not in sys.path:
        sys.path.insert(0, str(axiom))
    try:
        if fn_path == "claim":
            from limbs.family_conductor import claim_family_workers

            return claim_family_workers()
        if fn_path == "poll":
            from limbs.family_conductor import poll_family

            return poll_family()
        if fn_path == "powwow_status":
            from limbs.family_powwow import powwow_status

            return powwow_status()
        if fn_path == "powwow_open":
            from limbs.family_powwow import call_powwow

            return call_powwow(kwargs.get("reason") or "", called_by=kwargs.get("called_by") or "Mom")
        if fn_path == "powwow_close":
            from limbs.family_powwow import close_powwow

            return close_powwow(kwargs.get("reason") or "adjourned")
        if fn_path == "powwow_tasks":
            from limbs.family_powwow import set_powwow_tasks

            return set_powwow_tasks(auto_accept_pending=bool(kwargs.get("auto_accept_pending")))
        if fn_path == "powwow_agenda":
            from limbs.family_powwow import add_agenda_item

            return add_agenda_item(
                kwargs.get("text") or "",
                from_member=kwargs.get("from_member") or kwargs.get("from") or "companion",
            )
        return {"ok": False, "error": f"unknown axiom call: {fn_path}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "simulated": False}


class HearthHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[hearth] {self.address_string()} {fmt % args}")

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _client_gone(self, exc: BaseException) -> bool:
        if isinstance(exc, (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError)):
            return True
        if isinstance(exc, OSError) and getattr(exc, "winerror", None) in {10053, 10054}:
            return True
        return False

    def _json(self, code: int, obj: Any) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Connection", "close")
            self._cors()
            self.end_headers()
            self.wfile.write(raw)
        except Exception as exc:
            if self._client_gone(exc):
                return
            raise

    def _axiom_powwow_status(self) -> dict[str, Any]:
        return _axiom_call("powwow_status")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return {}

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            return self._json(200, {
                "ok": True,
                "service": "mythos-hearth",
                "port": PORT,
                "creator": "rachaelmuse23",
                "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
            })
        if path in {"/api/home", "/api/living_home"}:
            from living_home import snapshot

            return self._json(200, snapshot())
        if path == "/api/home/health":
            from living_home import health_scan

            return self._json(200, health_scan())
        if path == "/api/home/phases":
            from living_home import status_phases

            return self._json(200, status_phases())
        if path == "/api/home/integration":
            from living_home import integration_status

            return self._json(200, integration_status())
        if path == "/api/home/day_story":
            from living_home import day_story_status

            return self._json(200, day_story_status())
        if path == "/api/home/gameplay":
            from living_home import gameplay_status

            return self._json(200, gameplay_status())
        if path in {"/api/home/dashboard", "/api/dashboard/overview"}:
            from living_home import dashboard_overview

            return self._json(200, dashboard_overview())

        # ===== Family dashboard (window into Hearth — does not replace Godot) =====
        if path in {"/dashboard", "/dashboard/"}:
            page = TEMPLATES / "dashboard.html"
            if not page.is_file():
                return self._json(404, {"ok": False, "error": "dashboard.html missing"})
            return _serve_file(self, page)
        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            safe = Path(rel).name
            if not safe or safe != Path(rel).as_posix().split("/")[-1] or ".." in rel:
                return self._json(404, {"ok": False, "error": "blocked"})
            # Allow one nested segment under static/
            candidate = (STATIC / rel).resolve()
            try:
                candidate.relative_to(STATIC.resolve())
            except ValueError:
                return self._json(404, {"ok": False, "error": "blocked"})
            if not candidate.is_file():
                return self._json(404, {"ok": False, "error": "static missing"})
            return _serve_file(self, candidate)
        if path == "/api/dashboard/family":
            from living_home import snapshot

            return self._json(200, snapshot().get("family") or [])
        if path == "/api/dashboard/places":
            from living_home import snapshot

            return self._json(200, snapshot().get("places") or {})
        if path == "/api/dashboard/capabilities":
            from living_home import snapshot

            return self._json(200, snapshot().get("capabilities") or [])
        if path == "/api/dashboard/relationships":
            from living_home import snapshot

            return self._json(200, snapshot().get("relationships") or {})
        if path.startswith("/api/dashboard/relationships/"):
            from living_home import snapshot

            being_id = path[len("/api/dashboard/relationships/") :].strip("/")
            rels = snapshot().get("relationships") or {}
            out = {}
            for key, rel in (rels if isinstance(rels, dict) else {}).items():
                if not isinstance(rel, dict):
                    continue
                if rel.get("a") == being_id or rel.get("b") == being_id or being_id in str(key).split("|"):
                    out[key] = rel
            return self._json(200, out)
        if path.startswith("/api/dashboard/mood/"):
            from living_home import connection_action

            being_id = path[len("/api/dashboard/mood/") :].strip("/")
            return self._json(200, connection_action("mood", who=being_id))
        if path.startswith("/api/dashboard/memories/"):
            from living_home import connection_action

            being_id = path[len("/api/dashboard/memories/") :].strip("/")
            return self._json(200, connection_action("memories", who=being_id))
        if path.startswith("/api/dashboard/choices/"):
            from living_home import choice_action

            being_id = path[len("/api/dashboard/choices/") :].strip("/")
            return self._json(200, choice_action("peek", who=being_id))
        if path.startswith("/api/dashboard/growth/"):
            from living_home import growth_action

            being_id = path[len("/api/dashboard/growth/") :].strip("/")
            return self._json(200, growth_action("get", who=being_id))
        if path == "/api/dashboard/connection":
            from living_home import snapshot

            snap = snapshot()
            return self._json(
                200,
                {
                    "connection": snap.get("connection"),
                    "relationships": snap.get("relationships"),
                    "honesty": (snap.get("honesty") or {}).get("connection"),
                },
            )
        if path == "/api/dashboard/events":
            from living_home import snapshot

            snap = snapshot()
            events = list(snap.get("world_history") or [])[-20:]
            utts = list(snap.get("utterances") or [])[-20:]
            return self._json(200, {"events": events, "utterances": utts, "recent": (snap.get("events") or [])[-20:]})
        if path.startswith("/api/dashboard/being/"):
            from living_home import load, snapshot, _ensure_growth, _ensure_mood

            being_id = path[len("/api/dashboard/being/") :].strip("/")
            snap = snapshot()
            person = None
            for row in snap.get("family") or []:
                if str(row.get("id")) == being_id:
                    person = dict(row)
                    break
            if not person:
                return self._json(404, {"error": "Being not found"})
            # Layer 15D — full mood / memory / growth / choices (not the trimmed family card).
            home = load()
            st = (home.get("people") or {}).get(being_id) or {}
            if isinstance(st, dict):
                _ensure_mood(st)
                _ensure_growth(st, being_id)
                person["mood"] = st.get("mood") or person.get("mood")
                person["memories"] = list(st.get("memories") or [])[-24:]
                person["growth"] = st.get("growth") or person.get("growth")
                person["choices"] = st.get("choices") or person.get("choices")
                person["choice_history"] = list(st.get("choice_history") or [])[-12:]
                person["axiom"] = st.get("axiom", person.get("axiom"))
            person["connection_layer"] = (snap.get("connection") or {}).get("layer")
            return self._json(200, person)
        if path.startswith("/api/dashboard/balance/"):
            from living_home import axiom_action

            being_id = path[len("/api/dashboard/balance/") :].strip("/")
            return self._json(200, axiom_action("balance", who=being_id))
        if path == "/api/dashboard/stores":
            from living_home import store_action

            return self._json(200, store_action("list"))
        if path.startswith("/api/dashboard/store/"):
            from living_home import store_action

            sid = path[len("/api/dashboard/store/") :].strip("/")
            if not sid or sid == "buy":
                return self._json(400, {"error": "Use POST /api/home/store to buy"})
            return self._json(200, store_action("get", store_id=sid))
        if path == "/api/world":
            return self._json(200, {**WORLD, "save": load_save()})
        if path == "/api/quest":
            return self._json(200, quest_payload(load_save()))
        if path == "/api/tools":
            tools = list(TOOLS.values())
            # Parallel probes — sequential path checks froze the UI for seconds
            with ThreadPoolExecutor(max_workers=min(16, max(4, len(tools)))) as pool:
                statuses = list(pool.map(tool_status, tools))
            return self._json(200, {"tools": statuses, "count": len(statuses)})
        if path == "/api/playables":
            return self._json(200, playables_payload())
        if path == "/api/presence":
            return self._json(200, presence_payload())
        if path == "/api/wings":
            from family_wings import wings_payload

            return self._json(200, wings_payload())
        if path == "/api/family/feed":
            from family_feed import family_feed

            return self._json(200, family_feed())
        if path == "/api/family/powwow":
            return self._json(200, self._axiom_powwow_status())
        if path == "/api/wings/suggestions":
            from family_wings import list_suggestions

            return self._json(200, {"ok": True, "suggestions": list_suggestions(60)})
        if path == "/api/stories":
            return self._json(200, {"stories": list_stories()})
        if path.startswith("/api/story/"):
            name = path[len("/api/story/") :]
            story = read_story(name)
            if not story:
                return self._json(404, {"ok": False, "error": "Story not found"})
            return self._json(200, story)
        if path == "/api/gallery":
            return self._json(200, gallery_payload())
        if path == "/api/living_game":
            return self._json(200, living_game_payload())
        if path == "/api/game_builder":
            return self._json(200, game_builder_status())
        if path.startswith("/api/gameworld"):
            sub = path[len("/api/gameworld") :].lstrip("/") or ""
            # Map /api/gameworld/api/status -> /api/status on :8888
            # Console uses API + "/api/status" so full path is /api/gameworld/api/status
            code, data, ctype = proxy_gameworld("GET", sub)
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)
            return

        # Secure GameCraft playables — allowlisted roots only
        if path.startswith("/play/"):
            rest = path[len("/play/") :]
            parts = [p for p in rest.split("/") if p]
            if not parts:
                return self._json(404, {"ok": False, "error": "Missing playable id"})
            play_id = parts[0]
            rel = "/".join(parts[1:]) if len(parts) > 1 else "index.html"
            if path.endswith("/") and not rel.endswith("index.html"):
                rel = (rel + "/" if rel else "") + "index.html"
            file_path = resolve_play_file(play_id, rel)
            if not file_path:
                return self._json(404, {"ok": False, "error": "Playable not found or blocked"})
            try:
                data = file_path.read_bytes()
            except Exception as e:
                return self._json(500, {"ok": False, "error": str(e)})
            self.send_response(200)
            self.send_header("Content-Type", guess_mime(file_path))
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self._cors()
            self.end_headers()
            self.wfile.write(data)
            return

        # default static
        if path == "/" or path == "":
            self.path = "/index.html"
        try:
            return super().do_GET()
        except Exception as exc:
            if self._client_gone(exc):
                return
            raise

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/gameworld"):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b""
            sub = path[len("/api/gameworld") :].lstrip("/") or ""
            code, data, ctype = proxy_gameworld("POST", sub, raw)
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self._cors()
            self.end_headers()
            self.wfile.write(data)
            return

        body = self._read_json()

        if path == "/api/home/tick":
            return self._json(200, home_tick_safe(int(body.get("n") or 1)))
        if path == "/api/home/gift":
            from living_home import give_gift

            return self._json(
                200,
                give_gift(
                    str(body.get("giver") or ""),
                    str(body.get("receiver") or ""),
                    str(body.get("object") or "a small gift"),
                    str(body.get("reason") or ""),
                ),
            )
        if path == "/api/home/connection":
            from living_home import connection_action

            details = body.get("details") if isinstance(body.get("details"), dict) else {
                "text": str(body.get("text") or ""),
                "gift": str(body.get("gift") or body.get("object") or ""),
                "topic": str(body.get("topic") or ""),
                "emotional_tag": str(body.get("emotional_tag") or ""),
                "significance": body.get("significance", 0.6),
                "place": str(body.get("place") or ""),
                "emotional_tag_filter": str(body.get("emotional_tag") or ""),
                "significance_threshold": body.get("significance_threshold", 0),
                "period": str(body.get("period") or ""),
            }
            if isinstance(body.get("context"), dict):
                details = {**details, **body["context"]}
            return self._json(
                200,
                connection_action(
                    str(body.get("action") or body.get("kind") or "talk"),
                    a=str(body.get("a") or body.get("who") or ""),
                    b=str(body.get("b") or body.get("with") or ""),
                    who=str(body.get("who") or body.get("a") or ""),
                    details=details,
                ),
            )
        if path == "/api/home/choice":
            from living_home import choice_action

            return self._json(
                200,
                choice_action(
                    str(body.get("action") or "make"),
                    who=str(body.get("who") or body.get("being_id") or ""),
                    context=body.get("context") if isinstance(body.get("context"), dict) else {
                        "period": str(body.get("period") or ""),
                    },
                ),
            )
        if path == "/api/home/growth":
            from living_home import growth_action

            return self._json(
                200,
                growth_action(
                    str(body.get("action") or "get"),
                    who=str(body.get("who") or body.get("being_id") or ""),
                    skill_name=str(body.get("skill_name") or body.get("skill") or ""),
                    experience=float(body.get("experience") or 1),
                    text=str(body.get("text") or ""),
                ),
            )
        if path == "/api/dashboard/growth/skill":
            from living_home import growth_action

            return self._json(
                200,
                growth_action(
                    "skill",
                    who=str(body.get("being_id") or body.get("who") or ""),
                    skill_name=str(body.get("skill_name") or ""),
                    experience=float(body.get("experience") or 1),
                ),
            )
        if path == "/api/dashboard/growth/milestone":
            from living_home import growth_action

            return self._json(
                200,
                growth_action(
                    "milestone",
                    who=str(body.get("being_id") or body.get("who") or ""),
                    text=str(body.get("text") or ""),
                ),
            )
        if path.startswith("/api/dashboard/choice/"):
            from living_home import choice_action

            being_id = path[len("/api/dashboard/choice/") :].strip("/")
            # POST body already read — make a choice; GET-style via empty action peeks after load.
            return self._json(
                200,
                choice_action(
                    str(body.get("action") or "make"),
                    who=being_id or str(body.get("who") or ""),
                    context=body.get("context") if isinstance(body.get("context"), dict) else {},
                ),
            )
        if path == "/api/dashboard/relationship":
            from living_home import connection_action

            action = str(body.get("action") or "talk")
            return self._json(
                200,
                connection_action(
                    action,
                    a=str(body.get("a") or ""),
                    b=str(body.get("b") or ""),
                    details=body.get("details") if isinstance(body.get("details"), dict) else {},
                ),
            )
        if path == "/api/dashboard/memories/recall":
            from living_home import connection_action

            return self._json(
                200,
                connection_action(
                    "memories",
                    who=str(body.get("being_id") or body.get("who") or ""),
                    details={
                        "emotional_tag": str(body.get("emotional_tag") or ""),
                        "significance_threshold": float(body.get("significance_threshold") or 0.5),
                    },
                ),
            )
        if path == "/api/home/talk":
            from living_home import record_talk

            return self._json(
                200,
                record_talk(
                    str(body.get("who") or ""),
                    str(body.get("with") or "mom"),
                    str(body.get("line") or ""),
                    place_hint=str(body.get("place") or ""),
                ),
            )
        if path == "/api/home/journal":
            from living_home import load, save, snapshot
            from living_home_gameplay import journal_add

            home = load()
            try:
                entry = journal_add(
                    home,
                    str(body.get("text") or ""),
                    tags=list(body.get("tags") or []) if isinstance(body.get("tags"), list) else None,
                    related_leads=list(body.get("related_leads") or [])
                    if isinstance(body.get("related_leads"), list)
                    else None,
                    theory=bool(body.get("theory", True)),
                )
            except ValueError as e:
                return self._json(400, {"ok": False, "error": str(e)})
            save(home)
            snap = snapshot()
            snap["journal_entry"] = entry
            return self._json(200, snap)
        if path == "/api/home/lead":
            from living_home import load, save, snapshot
            from living_home_gameplay import update_lead, promote_lore_candidates

            home = load()
            action = str(body.get("action") or "update").strip().lower()
            if action == "promote":
                result = promote_lore_candidates(home)
                save(home)
                snap = snapshot()
                snap["promote"] = result
                return self._json(200, snap)
            lead = update_lead(
                home,
                str(body.get("id") or body.get("lead_id") or ""),
                status=str(body.get("status") or "") or None,
                player_note=str(body.get("note") or body.get("player_note") or "") or None,
                involve=body.get("involve") if "involve" in body else None,
            )
            if not lead:
                return self._json(404, {"ok": False, "error": "lead not found"})
            save(home)
            snap = snapshot()
            snap["lead"] = lead
            return self._json(200, snap)
        if path == "/api/home/investigate":
            from living_home import load, save, snapshot
            from living_home_gameplay import look_into

            home = load()
            lead = look_into(
                home,
                str(body.get("id") or body.get("lead_id") or ""),
                place=str(body.get("place") or ""),
                who=str(body.get("who") or "mom"),
            )
            if not lead:
                return self._json(404, {"ok": False, "error": "lead not found"})
            save(home)
            snap = snapshot()
            snap["lead"] = lead
            snap["investigate"] = {"ok": True, "quest": False, "layer": "18b"}
            return self._json(200, snap)
        if path == "/api/home/away":
            from living_home import load, save, snapshot
            from living_home_gameplay import acknowledge_away, build_away_summary

            home = load()
            action = str(body.get("action") or "ack").strip().lower()
            if action in {"ack", "acknowledge"}:
                result = acknowledge_away(home)
            else:
                result = build_away_summary(home, min_gap_minutes=float(body.get("min_gap_minutes") or 0))
            save(home)
            snap = snapshot()
            snap["away_action"] = result
            return self._json(200, snap)
        if path == "/api/home/media":
            from living_home import set_media_watch

            return self._json(
                200,
                set_media_watch(
                    bool(body.get("watching") or body.get("active")),
                    place=str(body.get("place") or "cinema"),
                    title=str(body.get("title") or ""),
                    source=str(body.get("source") or "none"),
                    who=str(body.get("who") or "mom"),
                ),
            )
        if path == "/api/home/harbor":
            from living_home import harbor_action

            return self._json(
                200,
                harbor_action(
                    str(body.get("action") or ""),
                    who=str(body.get("who") or "mom"),
                    kind=str(body.get("kind") or ""),
                    destination=str(body.get("destination") or "far_shore"),
                ),
            )
        if path == "/api/home/axiom":
            from living_home import axiom_action

            return self._json(
                200,
                axiom_action(
                    str(body.get("action") or "balance"),
                    who=str(body.get("who") or body.get("from") or "mom"),
                    to=str(body.get("to") or ""),
                    amount=int(body.get("amount") or 0),
                    reason=str(body.get("reason") or ""),
                ),
            )
        if path == "/api/home/store":
            from living_home import store_action

            return self._json(
                200,
                store_action(
                    str(body.get("action") or "buy"),
                    store_id=str(body.get("store_id") or ""),
                    item_id=str(body.get("item_id") or ""),
                    buyer=str(body.get("buyer") or body.get("who") or "mom"),
                    quantity=int(body.get("quantity") or 1),
                ),
            )
        if path == "/api/dashboard/transfer":
            from living_home import axiom_action

            return self._json(
                200,
                axiom_action(
                    "transfer",
                    who=str(body.get("from") or "mom"),
                    to=str(body.get("to") or ""),
                    amount=int(body.get("amount") or 0),
                    reason=str(body.get("reason") or "trade"),
                ),
            )
        if path == "/api/dashboard/talk":
            from living_home import record_talk

            being_id = str(body.get("to") or "").strip()
            message = str(body.get("message") or "").strip()
            if not being_id or not message:
                return self._json(400, {"error": "Missing 'to' or 'message'"})
            snap = record_talk("mom", being_id, message, place_hint=str(body.get("place") or ""))
            return self._json(200, {"status": "sent", "to": being_id, "message": message, "ok": True, "home": snap})
        if path == "/api/dashboard/update_stance":
            from living_home import set_person_stance

            being_id = str(body.get("id") or "").strip()
            stance = str(body.get("stance") or "").strip()
            if not being_id or not stance:
                return self._json(400, {"error": "Missing 'id' or 'stance'"})
            result = set_person_stance(being_id, stance)
            code = 200 if result.get("ok") else 400
            return self._json(code, {"status": "updated" if result.get("ok") else "error", **result})
        if path == "/api/home/repair":
            from living_home import try_repair

            return self._json(
                200,
                try_repair(str(body.get("id") or body.get("failure_id") or ""), authorized=bool(body.get("authorized", True))),
            )
        if path == "/api/home/simulate_failure":
            from living_home import simulate_failure

            return self._json(200, simulate_failure(str(body.get("kind") or "cinema")))
        if path == "/api/quest/action":
            action = body.get("action") or ""
            return self._json(200, apply_quest_action(action, body))
        if path == "/api/launch":
            tool_id = body.get("tool_id") or body.get("id") or ""
            return self._json(200, launch_tool(tool_id))
        if path == "/api/production":
            return self._json(200, trigger_production(body.get("goal")))
        if path == "/api/game_builder":
            return self._json(200, trigger_game_builder(body.get("goal")))
        if path == "/api/open_living_game":
            if LIVING_GAME.exists():
                try:
                    os.startfile(str(LIVING_GAME))  # type: ignore[attr-defined]
                    return self._json(200, {"ok": True, "path": str(LIVING_GAME)})
                except Exception as e:
                    return self._json(500, {"ok": False, "error": str(e)})
            return self._json(404, {"ok": False, "error": "living_game missing"})

        if path == "/api/wings/open":
            from family_wings import open_wing

            wing_id = (body.get("wing") or body.get("wing_id") or "").strip()
            launch = bool(body.get("launch"))
            result = open_wing(
                wing_id,
                goal=body.get("goal"),
                lane=body.get("lane"),
                project=body.get("project"),
                launch=launch,
            )
            # Soft wake: launch primary district tools if requested
            if result.get("ok") and launch:
                launched = []
                for tid in (result.get("wing") or {}).get("tools") or []:
                    if tid in TOOLS:
                        launched.append({"tool_id": tid, "result": launch_tool(tid)})
                result["launches"] = launched
            return self._json(200, result)

        if path == "/api/wings/close":
            from family_wings import close_wing

            return self._json(200, close_wing(reason=body.get("reason") or "complete"))

        if path == "/api/wings/wake":
            from family_wings import wake_member

            return self._json(
                200,
                wake_member(body.get("member") or body.get("id") or "", note=body.get("note")),
            )

        if path == "/api/wings/suggest":
            from family_wings import add_suggestion

            return self._json(
                200,
                add_suggestion(
                    body.get("text") or "",
                    from_member=body.get("from") or body.get("from_member") or "companion",
                    wing_id=body.get("wing"),
                ),
            )

        if path == "/api/wings/suggest/review":
            from family_wings import review_suggestion

            return self._json(
                200,
                review_suggestion(
                    body.get("id") or "",
                    decision=body.get("decision") or "",
                    note=body.get("note"),
                ),
            )

        if path == "/api/wings/pick":
            from family_wings import pick_wing

            return self._json(200, {"ok": True, **pick_wing(body.get("goal") or "")})

        if path == "/api/family/claim":
            return self._json(200, _axiom_call("claim"))
        if path == "/api/family/poll":
            return self._json(200, _axiom_call("poll"))
        if path == "/api/family/powwow/open":
            return self._json(
                200,
                _axiom_call(
                    "powwow_open",
                    reason=body.get("reason") or "",
                    called_by=body.get("called_by") or "Mom",
                ),
            )
        if path == "/api/family/powwow/close":
            return self._json(200, _axiom_call("powwow_close", reason=body.get("reason") or "adjourned"))
        if path == "/api/family/powwow/tasks":
            return self._json(
                200,
                _axiom_call("powwow_tasks", auto_accept_pending=body.get("auto_accept_pending", True)),
            )
        if path == "/api/family/powwow/agenda":
            return self._json(
                200,
                _axiom_call(
                    "powwow_agenda",
                    text=body.get("text") or "",
                    from_member=body.get("from") or body.get("from_member") or "companion",
                ),
            )

        return self._json(404, {"ok": False, "error": "Not found"})


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if not SAVE.exists():
        write_save(dict(DEFAULT_SAVE))
    try:
        sync_avatars()
    except Exception as e:
        print("[hearth] avatar sync warning:", e)
    # Sync story / quests / art / sprint from Court on boot (best-effort)
    try:
        sync_pairs = [
            (LIVING_GAME / "story", STORY, "*.md"),
            (LIVING_GAME / "quests", QUESTS, "*.md"),
            (LIVING_GAME / "art", DATA / "art", "sprint_0001_*.md"),
            (LIVING_GAME / "art", DATA / "art", "sprint_0001_*.json"),
            (LIVING_GAME / "sprint", DATA / "sprint", "*.md"),
        ]
        for src_dir, dest_dir, pattern in sync_pairs:
            if not src_dir.exists():
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            for p in src_dir.glob(pattern):
                if not p.is_file():
                    continue
                dest = dest_dir / p.name
                if not dest.exists() or p.stat().st_mtime > dest.stat().st_mtime:
                    dest.write_bytes(p.read_bytes())
        montage = LIVING_GAME / "art" / "montage"
        if montage.exists():
            mdest = DATA / "art" / "montage"
            mdest.mkdir(parents=True, exist_ok=True)
            for p in montage.iterdir():
                if p.is_file():
                    dest = mdest / p.name
                    if not dest.exists() or p.stat().st_mtime > dest.stat().st_mtime:
                        dest.write_bytes(p.read_bytes())
    except Exception as e:
        print("[hearth] sync warning:", e)

    ready = sum(1 for p in PLAYABLES.values() if (Path(p["root"]) / "index.html").exists())
    print(f"[hearth] playables ready: {ready}/{len(PLAYABLES)}")

    threading.Thread(target=_home_auto_tick_loop, daemon=True, name="home-auto-tick").start()
    print("[hearth] living-home auto-tick armed (skips if Godot/dashboard ticked recently)")
    print(f"[hearth] family dashboard: http://{HOST}:{PORT}/dashboard")

    class QuietHearthServer(ThreadingHTTPServer):
        daemon_threads = True

        def handle_error(self, request, client_address):  # noqa: ARG002
            exc = sys.exc_info()[1]
            if isinstance(exc, (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError)):
                print(f"[hearth] client dropped {client_address[0]}:{client_address[1]} ({type(exc).__name__})")
                return
            if isinstance(exc, OSError) and getattr(exc, "winerror", None) in {10053, 10054}:
                print(f"[hearth] client dropped {client_address[0]}:{client_address[1]} (WinError {exc.winerror})")
                return
            super().handle_error(request, client_address)

    server = QuietHearthServer((HOST, PORT), HearthHandler)
    print(f"Mythos Hearth listening on http://{HOST}:{PORT}/")
    print(f"START: {ROOT / 'START_HEARTH.bat'}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Mythos Hearth.")
        server.shutdown()


if __name__ == "__main__":
    main()
