# Mythos Hearth — CONTINUE_LOG

**When:** 2026-07-25  
**Creator:** rachaelmuse23  
**Home:** `D:\Mythos_Hearth`  
**URL:** http://127.0.0.1:8790/

## What improved

### 1. Portable Godot 4.7
- Downloaded official **Godot 4.7-stable standard** Windows 64-bit zip
- Extracted to `D:\Mythos_Hearth\tools\Godot_v4.7\`
  - Exe: `Godot_v4.7-stable_win64.exe` (+ console twin)
- `OPEN_GODOT.bat` now prefers this portable path first, then Mythos_Tools/Godot, then common installs
- Verified: `Godot_v4.7-stable_win64_console.exe --path D:\Mythos_Apex\godot_project --headless --quit` → exit 0 (`Living World initializing…`)
- Updated `GODOT_LINK.md` + `COMPLETE.md`

### 2. Web village deepened
- District hotspots with distinct silhouettes + short flavor (forge=StackForge, cinema=Montage/DLC, library=Q3 locked, gallery=Comfy, hearth=companions)
- Quest HUD checklist on screen: **herb → tea → gift**
- Save complete → **village awake** celebration (banner, lantern dots, canvas glow) + story panel auto-opens once per session
- Companions load Codex male avatar from `web/assets/codex_reference.png` (with fallbacks)
- Keyboard hint overlay (WASD + click), dismissible

### 3. Content sync
- Synced Court `living_game` story, quests, art prompts/queue, montage notes, sprint DEMO/plan/NEEDS into `D:\Mythos_Hearth\data\`
- Server boot sync widened to story/quests/art/sprint/montage

### 4. Gallery / Comfy
- ComfyUI `:8001` was up → generated 2 stills:
  - `web/assets/gallery/hearth_square_dawn.png`
  - `web/assets/gallery/herb_garden_mist.png`
  - copies also in `data/art/renders/`
- Gallery API lists gallery + renders; SVG visions expanded so gallery never feels empty

### 5. Launcher polish
- `START_HEARTH.bat`: kills stale `:8790`, waits for `/api/health`, opens browser, server in minimized window
- Desktop `Mythos Hearth.lnk` refreshed
- `Mythos Studio Tools.bat` menu item **[6] Mythos Hearth**

### 6. Smoke
- HEALTH ok · TOOLS 20 · quest reset→complete + unlock · stories include DEMO · Q3 lore gate · INDEX brand · **PORTABLE_OK**
- Did **not** download Q3; Apex/Codex branding kept distinct (cyan vs gold)

## Key paths
| Item | Path |
|------|------|
| Portable Godot | `D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64.exe` |
| Project | `D:\Mythos_Apex\godot_project` |
| Village URL | http://127.0.0.1:8790/ |
| Start | `D:\Mythos_Hearth\START_HEARTH.bat` |

---

## 2026-07-25 — Asset integration (GameCraft + hubs + tools)

### Added districts (WORLD + village map)
- **arcade** — GameCraft playables
- **sanctuary** — digital-sanctuary
- **overlay** — jarvis_overlay
- **command** — Apex/Codex hubs + action monitor

### Playables (secure `/play/<name>/`)
Allowlisted roots under `D:\Mythos_Apex\media\gamecraft\play\` only (path traversal → 404):
| Playable | URL |
|----------|-----|
| Cozy Valley | http://127.0.0.1:8790/play/cozy_valley/ |
| Desert Island Farm | http://127.0.0.1:8790/play/desert_island_farm/ |
| Matrix Wish | http://127.0.0.1:8790/play/we_added_this_to_your_matrix_if_you_wish_to_use_/ |

UI: Arcade panel + iframe modal; side quest flag `arcade_cozy_played` in `save.json` (preserved on main quest reset).

### New / updated TOOLS
| Tool id | Notes |
|---------|--------|
| `arcade_cozy` / `arcade_desert` / `arcade_matrix` | Hearth play URLs |
| `apex_command` / `apex_hub` / `apex_lounge` | `:8770` paths |
| `codex_command` / `codex_hub` / `codex_lounge` | `:8780` paths |
| `action_monitor` | `D:\Mythos_Apex\mythos_monitor.html` |
| `digital_sanctuary` | folder + palace HTML |
| `jarvis_overlay` | folder + SEPARATION_CONTRACT |
| `godot_play` | `OPEN_GODOT_PLAY.bat` — run `--path` (not editor) |
| `ai_file_sorter` | `OPEN_AI_FILE_SORTER.bat` → Program Files exe |
| `pinokio` | Local Programs `Pinokio.exe` |
| `avatar_workshop` | Apex avatar folder + chat URL |
| `comfyui` | also notes Local Programs ComfyUI |

### Avatars
Synced `D:\Mythos_Apex\avatar\mythos|codex\reference.png` (+ Gemini alts) into `web/assets/`.

### Smoke
- `/api/health` ok · `/play/cozy_valley/` 200 HTML · traversal 404 · `/api/tools` 35 · `/api/playables` 3 ready · arcade side quest sets flag · main quest reset intact
- Did **not** download Q3; did **not** serve E:\found.*

### Launchers added
- `D:\Mythos_Hearth\OPEN_GODOT_PLAY.bat`
- `D:\Mythos_Hearth\OPEN_AI_FILE_SORTER.bat`

---

## 2026-07-25 — Second-wave project wiring

Scanned sibling programs; wired remaining high-value finds into Hearth.

### New playable
| Playable | URL |
|----------|-----|
| Gameworld Console | http://127.0.0.1:8790/play/gameworld/ |

Mirrored from `G:\Mythos_Codex\gameworld_console.html` → `web/play/gameworld/index.html` (allowlisted).

### New tools
| Tool | Opens |
|------|-------|
| `arcade_gameworld` | Hearth `/play/gameworld/` |
| `mythos_spore` | `D:\MythosSpore\LAUNCH_SPORE.bat` |
| `hero_fleet` | Sanctuary `Launch_Hero_Fleet.bat` + `D:\OPENCLAW_HERO_FLEET` |
| `drone_cast` | `D:\Mythos_Apex\drones` (Jarvis/Nova/Percy JSON cast) |

### Smoke
- playables **4/4 ready** · tools include spore/fleet/drones/gameworld · `/play/gameworld/` 200
- Q3 still lore-only; no E:\found.* serving

---

## 2026-07-25 — Continue wave (palace + drones + archives)

### Memory Palace
- `OPEN_SANCTUARY_PALACE.bat` → `palace.exe` on **:8080**
- Tool `digital_sanctuary` now probes/opens `http://127.0.0.1:8080/`

### Drone cast in village UI
Companions panel now includes **Jarvis · Nova · Percy · Genesis** (kind=`drone`) with walk-up lines; click opens `D:\Mythos_Apex\drones`.

### Archive / limb tools
| Tool | Path |
|------|------|
| `hatchery` | `G:\Mythos_Codex\hatchery` |
| `kingdom_keep` | `D:\KINGDOM_KEEP_PACKS` |
| `sanctuary_yard` | `D:\Sanctuary` |
| `the_sanctuary` | `D:\[THE_SANCTUARY]` |
| `freenet` | lore-only (`advanced_shards\freenet.py`) |
| `godot_first_world` | `OPEN_GODOT_FIRST_WORLD.bat` → Mythos_First_World.tscn |

Main quest unchanged. Q3 still gated.

---

## 2026-07-25 — Final gap close

Was **not** everything yet. Closed remaining scan leftovers:

| Item | Change |
|------|--------|
| Freenet | **LIVE** — `D:\Mythos_Apex\freenet\freenet.exe` (+ Codex alt) |
| Axiom Dashboard | `Launch_Axiom_Dashboard.bat` |
| Tandem Browser | `Launch_Tandem_Browser.bat` |
| Court Room | `D:\Court\companion_room` + companion URL |
| Capability Atlas | opens `CAPABILITY_ATLAS.md` |
| `/api/tools` hang | skip slow exists-checks on huge archive roots |

### Intentionally not LIVE
- **Q3 GLM** — hardware gate (~319GB)
- **Launch_Oasis / Sovereign Home** — bats not present under `OPENCLAW_HERO_FLEET` (folder only via `hero_fleet`)
- Extra GameCraft plays — only the 3 HTML folders exist
- Studio tools dirs already atlas’d (OpenHands/Montage/cluely/DLC)

Smoke: **49 tools** · `/api/tools` ~3.5s · freenet `ready`+exe

---

## 2026-07-25 — Family vision wave

### English concept prompts
All five sprint prompts translated; Chinese negatives removed. Synced to Court + Hearth `art/sprint_0001_concept_prompts.md`.

### Living Game hub (fixed dead launcher)
- Bug: folder-only launch opened Explorer with no in-browser destination
- Fix: **http://127.0.0.1:8790/living.html** hub — stories, Godot, arcade, gallery, companion, Court folder
- Tool `living_game` now `prefer_url` → hub; folder via “Open Court folder”
- Launch toast feedback for folder/bat/exe

### Family vision
- `data/FAMILY_VISION.md` — lifetime village charter
- Footer + hero CTA link to Living Game
- Comfy script `scripts/generate_family_stills.py` for interior / garden / meeting / lanterns stills

## Game Builder (2026-07-25 evening)

- **Hearthbound Game Builder** — Cursor SDK local agent, **no Apex/Codex**
- Package: `game_builder/CHARTER.md`, `sprint_backlog.md`, `prompts/sprint_0002.md`, `run_builder.py`
- Launch: `START_GAME_BUILDER.bat` or Hearth → **Build the game** (`POST /api/game_builder`)
- Needs `CURSOR_API_KEY` in env or `D:\Mythos_Hearth\.env` (see `.env.example`)
- Smoke: `scripts/smoke_game_builder.py` PASS
