# Mythos Hearth — COMPLETE

**Creator:** rachaelmuse23  
**Home:** `D:\Mythos_Hearth`  
**Start:** `D:\Mythos_Hearth\START_HEARTH.bat` → **http://127.0.0.1:8790/**  
**Status:** Finished vertical-slice product (usable today) + portable Godot 4.7

## What shipped

| Surface | Status |
|---------|--------|
| Double-click START bat (kills stale :8790, waits healthy, opens browser) | **Shipped** |
| Polished web UI (ember gold / forest night / mist; Fraunces + Outfit; brand-first hero) | **Shipped** |
| Playable village canvas (WASD/arrows + click; district flavor text; keys overlay) | **Shipped** |
| First Hearth Gift quest (herb → tea → gift checklist + celebration) | **Shipped** |
| Quest persistence `data/save.json` | **Shipped** |
| Districts panel with LIVE TCP probes + allowlisted Launch | **Shipped** |
| Companions pane (Codex/Apex avatars from `web/assets/`, presence) | **Shipped** |
| Story codex (Court living_game sync + sprint DEMO) | **Shipped** |
| Gallery (SVG visions + Comfy stills in `web/assets/gallery/`) | **Shipped** |
| Production sprint POST + open living_game folder | **Shipped** |
| Desktop shortcut + Studio Tools menu item [6] | **Shipped** |
| Portable Godot 4.7 standard under `tools\Godot_v4.7\` | **Shipped** |

## Districts / tools wired

- Apex `:8770` · Codex `:8780` · Companion Room · Conclave  
- StackForge Apex `:8771` · StackForge Codex `:8781`  
- ODS `:9300` · OpenHands `:3001` · free-cluely `:5180` · ComfyUI `:8001`  
- OpenMontage · Deep-Live-Cam · Godot project · Night Shift · Studio Tools  
- Living Game folder · Drive Map · AI File Sorter · Archive E:  

## Godot 3D slice

| Item | Status |
|------|--------|
| `D:\Mythos_Apex\godot_project` (4.7, `main_world.tscn`) | **Present** |
| Portable editor `D:\Mythos_Hearth\tools\Godot_v4.7\Godot_v4.7-stable_win64.exe` | **Seated** |
| `OPEN_GODOT.bat` prefers portable → launches `--path … --editor` | **Shipped** |
| Web village `:8790` | **Primary playable** |

See `GODOT_LINK.md`.

## Lore wings (honest gates)

| Wing | Why gated |
|------|-----------|
| **Q3 GLM Library Wing** | ~319GB GGUF; village lore & Districts `lore` — **not runnable** (not downloaded) |
| **VR lounge** | Imagination / future slice |

## APIs (`hearth_server.py` :8790)

- `GET /api/health` · `/api/world` · `/api/quest` · `/api/tools` · `/api/presence`  
- `GET /api/stories` · `/api/story/{name}` · `/api/gallery`  
- `POST /api/quest/action` `{action}`  
- `POST /api/launch` `{tool_id}` (allowlist only)  
- `POST /api/production` · `/api/open_living_game`

## How to play (2 minutes)

1. Double-click `START_HEARTH.bat`  
2. Enter the village → Herb Garden → pick rosemary/mint/thyme  
3. First Hearth → Craft tea → Gift to Apex or Codex  
4. Village awake celebration + Story Codex care beat  
5. Use Districts / Studio Tools to launch live studio tools  

Built as the village OS front door for the Mythos studio — Apex (cyan) and Codex (gold) stay distinct.
