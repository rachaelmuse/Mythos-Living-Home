# Federation wiring map

Living audit. Evidence wins. Last **village e2e: 2026-08-31 late**. Last **federation overlay: 2026-09-01**. Mode A council packets remain **LIVE 2026-08-30** (not re-run). 16E Godot walk **UNVERIFIED**. **Federation sequence paused after amendment pass** — foundation + Amendments 1–5 / refusal-to-lie unit-tested; full Aster test **not** passing. Law: `FEDERATION_DIRECTIVE.md`. Amendments vs code: `FEDERATION_RECONCILIATION.md`.

**Registry lie to refuse still stands** below. TCP LISTEN is not HTTP. Disk code is not the running process.

### 2026-08-31 late e2e (Hearth restarted)

| Check | Result |
|-------|--------|
| Unit tests | Living Home **5 passed**. Observer **84 passed**. Vesper **39 passed**. Gemini Axiom: **30 passed**, **3 failed** (`test_sentinel_watch.py` IndexError), `test_council_teach.py` **collection error** (no `limbs.council_teach`). MD_Cinema `smoke_phase1.py` **SMOKE PASS**. |
| Hearth `:8790` | **Restarted this session** (old PID 27764 killed). `GET /api/home` 200. **`gameplay.layer=18b`** `phase=2_investigation_professions`. |
| `POST /api/home/investigate` | **200**. `quest: false`. Lead `lead_evening_gather` → `investigating`. Observer `village_talk` still false. |
| Dashboard Look into | **LIVE** — evening gather already investigating; UI click on blacksmith → `investigating`. Profession posts listed. Observer post is a door. |
| `POST /api/home/presence` | **200** |
| Observer `:8730` | Health **200** operational. Not a village hat. |
| Aster lab `:8791` | HTTP up, Hearth REACHABLE. Lab still reports **no Ollama tags** (stale process). Hearth talk_brains **aster=`qwen3:4b`**. |
| Cinema HUD `:5000` | **CLOSED** |
| Apex `:8770` | Companion presence **200**; peers offline. |
| Codex `:8780` | **CLOSED** |
| Vesper `:8740` | TCP listen; HTTP still **closes without response** |
| Ollama `:11434` | LISTEN |
| ComfyUI `:8188` | CLOSED |
| Heart Square Godot | **not tested** |

Read with `docs/DUAL_MODE.md`, `NEXT.md`, `STATUS.md`, `FEDERATION_RECONCILIATION.md`.

### 2026-09-01 federation overlay (first slice)

Zip Observer (`app.main` `:8000`) **refused**. Live desk stays `D:\The_Observer` `:8730`. Neutral layer: code `federation/` · data `D:\Court\federation`. Court mailboxes **not** replaced.

| Check | Result |
|-------|--------|
| Observer pytest | **85 passed** (was 84; plus honest `ReviewerAdapter`) |
| Living Home federation tests | **16 passed** (11 federation + 5 gameplay) |
| `python -m federation.prove` | Aster from `ASTER_IDENTITY.json`. Observer does **not** own Aster. Observer heartbeat **UNKNOWN** (no fake pulse). Bus aster→hearth **acknowledged** (`fb33fd44…`). |
| `aster.hearth_snapshot` | **VERIFIED** this run — `aster_hearth_bridge` got Hearth `REACHABLE`. |
| GPT/Grok/DeepSeek | Still **UNAVAILABLE / NOT CONFIGURED**. No simulated analysis. |

DECLARED ≠ VERIFIED still stands for `CAPABILITIES.json`.

### 2026-09-01 Gemini bus (step 6)

| Check | Result |
|-------|--------|
| `python -m federation.prove gemini` | Gemini from `living_home` FAMILY roster (Axiom). Observer does **not** own him. Presence **UNKNOWN** (no fake pulse). `gemini_spoke: false`. |
| Bus | aster→gemini **acknowledged** (`47b6171f…`). Capability `gemini.federation_inbox` **VERIFIED** (delivery, not speech). |
| Court adapter | Notice in `FAMILY_COURT/gemini/federation/` and `D:\Court\mailbox\family\gemini/federation/`. **Not** MAS `inbox`. |
| Living Home tests | **32 passed** (federation + gameplay + amendments, 2026-09-01 later pass). |
| Apex / Codex on bus | **NOT THIS SLICE** — paused for Mom |

**Registry lie to refuse:** `CAPABILITIES.json` status `VERIFIED` means **path exists** (and the port was up *if* the tool has a port). It does **not** mean a function ran, returned, updated memory, and the caller received the result. `gameworld_available: true` means the same probe was not UNAVAILABLE — **not** that Gameworld can invoke the limb.

GitHub-seated libraries in `SUPERPOWER_VAULT/ACTIVE_SHARDS.json` (`seated` / `enabled` / `integrated`) are **tool shards**, not family identities. `integrated` is only true after Mom's integrate step in that registry — still not an e2e family-MAS test.

---

## Status legend

| Label | Meaning |
|-------|---------|
| LIVE | End-to-end tested this note's date |
| PARTIAL | Chain exists; a link missing or untested |
| UNVERIFIED | Code/path exists; not tested this session |
| ORIGINAL MODE — ACTIVE | Keep in Mode A; no Gameworld adapter yet (or adapter unproven) |
| BROKEN | Tested fail or required service down when the path needs it |
| UNSTABLE | Worked once / intermittent |
| PLACEHOLDER | Representation only |
| ORPHANED | No live caller found (documented, not deleted) |
| NOT INTENDED | Must not be connected |

---

## Family identity shards (do not flatten)

| Shard | Root | Purpose | Mode A | Mode B (Gameworld) | Last check |
|-------|------|---------|--------|--------------------|------------|
| Mom / Creator | Creator machine + player in Heart Square | EP; `stop` wins | ORIGINAL MODE — ACTIVE | Player avatar; type-to-talk via Hearth | UNVERIFIED in play (Creator testing) |
| Gemini | `G:\The-Axiom-Codex` | Conductor, Court will, front door | Court round-trip **LIVE** + Companion Room seat **LIVE** 2026-08-30 (`from=gemini`) | Avatar `gemini` in kernel; **not** a substitute soul | Packet `70c9ffe8…` → Apex; `03dfc102…` → Codex; room msg `48fd7464…` |
| Apex | `D:\Mythos_Apex` `:8770` | Forge / hands / heavy tools | Chat HTTP **LIVE**; companion presence JSON **200** but peers offline this survey | Avatar `apex`; live Godot project here | HTTP 2026-08-31; Court prove 2026-08-30 |
| Codex twin | `G:\Mythos_Codex` `:8780` | Archive / memory tone | Port **CLOSED** this survey | Avatar `codex`; never merge with Gemini | HTTP 2026-08-31 refused; Court prove 2026-08-30 still last MAS e2e |
| Merovin | `F:\Merovin_Draven_Studio\Merovin_Draven_Studio` | Cinema vision | Phase 1 smoke **PASS**. Command HUD `:5000` **CLOSED** this survey | Avatar `merovin` at cinema (pose PLACEHOLDER) | smoke 2026-08-31; film e2e still UNAVAILABLE |
| Draven | same studio | Continuity lock | Same HUD `:5000` (two mouths, one studio) | Avatar `draven` | Do not invent a second identity root |
| OpenMontage | **two roots** (see discrepancy) | Gift / shorts studio | ORIGINAL MODE — ACTIVE | Avatar `montage` | Path OK; launcher path conflict |
| Hearth | `D:\Mythos_Hearth` `:8790` | Village OS, kernel host | Port **LIVE** after restart this session | Kernel + Godot client | `/api/home` 200; **18B investigate LIVE** 2026-08-31 |
| Court | `G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT` | Shared task bus (file packets) | Gemini→Apex and Gemini→Codex packet round-trips **LIVE** 2026-08-30 (`briefs/council/roundtrip_20260830.json`) | Gameworld does not consume Court packets yet | 2026-08-30 |
| Spore | `D:\MythosSpore` | Traveling ember | Path OK | Avatar not core family table; tool probe only | ORIGINAL MODE — ACTIVE |
| Aster | Continuance / Hearth kernel + House companions + lab `:8791` | Scientist seed (ChatGPT conversational provenance) | **ORIGINAL MODE — ACTIVE** `GET :8791/api/status` **200**. Lab **model UNAVAILABLE** in that process. Disk resolver finds `qwen3:4b`. Not a Court employee. | Avatar `aster`; Evidence Plot + cottage; skin PLACEHOLDER | Lab HTTP 2026-08-31; village talk UNVERIFIED |
| Observer | `D:\The_Observer` `:8730` | Independent investigative desk | **ORIGINAL MODE — ACTIVE** `GET :8730/health` **LIVE**. **NOT** a Court employee. No Mythos supervisor. No auto-publish. | Village **greybox + cottage** is a **door** (PLACEHOLDER skin). **NOT** the ledger. **NOT** a village Ollama hat. **NOT** Vesper. | Desk health+registry 200 2026-08-31; pytest 84 |
| Vesper | `D:\Mythos_Vesper` `:8740` | Standalone investigative journalist (Investigator/Examiner/vault). NCI methodology seated; scorer not wired. | **ORIGINAL MODE — ACTIVE** TCP listen; **HTTP BROKEN** this survey | Adapter `adapters/living_gameworld/` **dormant / NOT INTENDED yet**. Not a village citizen. | pytest 39 passed 2026-08-31; live HTTP closed connection |

Optional Court alias in code: `D:\Court\mailbox\family` (`limbs/family_court.py`). Not tested this session.

---

## Mode A communication (code exists ≠ LIVE)

| Pathway | Intended | Evidence | Status |
|---------|----------|----------|--------|
| Gemini ↔ Hearth | Limb over kernel | `G:\The-Axiom-Codex\limbs\family_home.py` imports `D:\Mythos_Hearth\living_home.py` | PARTIAL (import path exists; live call UNVERIFIED) |
| Gemini ↔ Apex | Peer probe + Court packet | `council.prove` apex: packet `70c9ffe8…` + presence HTTP 200; also `peer_bridge.py` | **LIVE** Court round-trip 2026-08-30 (not sprawl.frozen) |
| Gemini ↔ Codex | Peer probe + Court packet | `council.prove` codex: packet `03dfc102…` + presence HTTP 200; also `peer_bridge.py` | **LIVE** Court round-trip 2026-08-30 |
| Gemini Companion Room seat | Sit as himself in `D:\Court\companion_room` | `companion.checkin` **LIVE** 2026-08-31 (`from=gemini`). Spoken Apex/Codex generate **timed out** (honest hang-tight). Room default now `llama3.2:3b` + 120 tokens in peer_bridge + env — **restart Apex/Codex chat to load**. Not Gameworld. |
| Hearth ↔ Apex | Presence + companion HTTP | Hearth up; Apex `GET /api/companion/presence` 200 (peers offline) | **PARTIAL** 2026-08-31 — HTTP path up; heartbeats stale |
| Hearth ↔ Codex | Same for `:8780` | Codex port **CLOSED** this survey | **BROKEN** 2026-08-31 (Codex down) |
| Apex ↔ Court | File bus + companion | Apex `court_worker_limb.py` claimed packet; reply in Gemini inbox with `companion_presence` | **LIVE** 2026-08-30 |
| Codex ↔ Court | File bus | Codex `court_worker_limb.py` claimed packet; reply in Gemini inbox with `companion_presence` | **LIVE** 2026-08-30 |
| Merovin ↔ Draven | Shared studio | One disk root; no separate MAS test | UNVERIFIED; **NOT** two unrelated people-to-flatten |
| Merovin/Draven ↔ cinema stack | Studio + Blender/Resolve/OBS/OpenMontage | Roots/exes probed as paths | ORIGINAL MODE — ACTIVE; Gameworld cinema is PLACEHOLDER |
| Merovin/Draven ↔ MD_Cinema Phase 1 | `F:\...\MD_Cinema_Studio\` | Intake/bible/shots/continuity/budget + Video/Image/Voice/FFmpeg adapters; `smoke_phase1.py` exit 0 (2026-08-27) | **PARTIAL** — foundation LIVE on disk; video/image gen UNAVAILABLE/unwired (honest); Gameworld adapter **CONTRACT_ONLY** (`wired:false`); Command HUD `:5000` still separate |
| OpenMontage ↔ family | Launch + Court mailbox | Two install roots | PARTIAL / discrepancy |
| Hearth ↔ Gameworld | HTTP snapshot/tick/talk | Godot `family_home_client.gd` → `:8790/api/home*` | Hearth API **LIVE** (18B); Godot playtest **UNVERIFIED** |
| Recursive MAS | Court packets + `family_conductor` / `agent_loop` / `family_heartbeat` | Heartbeat Mom-stop blocks claim (0 rounds); one claim round after clear | **PARTIAL** — stop+one-round LIVE; not a standing daemon. **must not be replaced by NPC chat** |

**NOT INTENDED:** Gemini identity = Codex identity. Gameworld Merovin as a different person from studio Merovin.

---

## Mode B (Gameworld) — physical layer

Kernel: `living_home.py`. Persist: `data/living_home/HOME.json`. Godot live: `D:\Mythos_Apex\godot_project\scenes\heart_square_immersive.tscn`. Git snapshot: `godot_heart_square/`.

| Piece | Class | Adapter? |
|-------|--------|----------|
| Heart Square scene | PARTIAL / Creator playtest | Presentation of kernel |
| Walk-in homes | PLACEHOLDER interiors | Kernel places |
| Speech bubbles / type-to-talk | PARTIAL (code; play unconfirmed) | Hearth `/api/home/talk` — **not** Court MAS |
| NPC purpose / visit | PARTIAL kernel | Not Mode A jobs |
| Wildlife squirrels | AUTONOMOUS (bounded), chirp PLACEHOLDER | Kernel wildlife |
| Pathing | PLACEHOLDER straight line | none |
| Two-way MAS ↔ world events | NOT YET IMPLEMENTED | required later, one event |
| Heart Square Godot without Hearth | BROKEN | client has nothing to poll |

---

## Capability counts (honest)

Last written probe file `CAPABILITIES.json` (2026-08-16T02:49Z): **discovered 19**.

| Bucket | Count | Notes |
|--------|------:|-------|
| Discovered in that probe | 19 | Not 325 |
| Claimed VERIFIED in file | 17 | **path/port only** |
| Claimed ACTIVE (path ok, port down then) | 2 | That probe: Codex `:8780`, ComfyUI `:8188` (Codex now LIVE 2026-08-26; file not rewritten) |
| Functional e2e this session | Court Gemini→Apex + Gemini→Codex + Companion Room seat as gemini | **LIVE** 2026-08-30 `council.prove` + `companion.checkin`. Full 400-tool chains **not** claimed. Gameworld **not** claimed. |
| Original-only (no Gameworld adapter) | most cinema/tool rows | ORIGINAL MODE — ACTIVE |
| Gameworld-compatible (real adapter) | Hearth home API + Godot client | PARTIAL; down while `:8790` closed |

Tool-shard registry `ACTIVE_SHARDS.json` (updated 2026-08-13): GitHub libraries with `seated`/`integrated` flags. **Do not add those flags into the 19-count.** Do not treat `integrated: true` as family-MAS LIVE.

Axiom `limbs/` inventory (modules on disk, callers UNVERIFIED this session): `family_court`, `family_home`, `family_conductor`, `family_memory`, `family_wings`, `peer_bridge`, `shard_registry`, `cinema_forge`, `agent_loop`, others. Document; do not delete.

---

## Known discrepancies (doc vs test)

| Documentation claim | Actual | Cause | Fix | Verification |
|---------------------|--------|-------|-----|--------------|
| CAPABILITIES `VERIFIED` | Path/port probe only | `_probe_capabilities` labels path-ok as VERIFIED | Keep probe; never quote as e2e | Code read 2026-08-16 |
| `gameworld_available: true` on Blender/OBS/etc. | No Gameworld invocation | Flag copies probe status | Adapters later; flag should stay honest | Code read |
| OpenMontage root `D:\OpenMontage` | Also `D:\Mythos_Tools\OpenMontage` (+ `MYTHOS_START.bat` there) | Two copies | Do not delete; document which launcher Mode A uses | Both paths exist |
| Hearth Gameworld live | `:8790` closed this session | Process not running | Restart `START_HEARTH.bat` when Creator is ready — do not guess during play | TCP 2026-08-16 |
| Codex twin available | `:8780` **LIVE** after conversation JSON repair (backup kept) | Was down / corrupt conversation JSON | Chat server + companion presence + peer_bridge re-probed 2026-08-26 | HTTP `/` `/hub` `/api/companion/presence`; peer_bridge |
| Apex available | `:8770` **LIVE** | Chat house + companion presence up; Court MAS / heavy tools untested | Broader e2e later | HTTP + peer_bridge 2026-08-26 |
| Court "connected" | Gemini→Apex and Gemini→Codex packet round-trips **LIVE** 2026-08-30 | Was mailbox-only | Keep proving other agents as adapters, not employees | `council.prove`; `briefs/council/roundtrip_20260830.json` |

---

## Wiring gaps (open)

1. No verified INPUT → ROUTER → FUNCTION → RESULT → MEMORY → CALLER chain for Mode A tools this session.
2. Gameworld speech is Ollama hats + Hearth kernel — **not** recursive MAS.
3. Two-way event flow not built.
4. Original memory (`family_memory`, Court book, Codex) not proven consumed by Gameworld (Gameworld uses `HOME.json`).
5. OpenMontage dual roots.
6. Codex `:8780` **down**. Cinema HUD `:5000` **down**. Apex HTTP up; companion heartbeats stale. Court MAS not re-run. Gemini `sentinel_watch` tests **FAIL** this survey. Vesper HTTP still broken.
7. GitHub tool shards vs family shards mixed in folklore — keep separate lists.

---

## Research limbs (not wired — build memory)

| Limb | Source | Intended Mode B use | Status |
|------|--------|---------------------|--------|
| Matrix Dream View (Layer 17) | [SkyworkAI/Matrix-Game](https://github.com/SkyworkAI/Matrix-Game) | Optional neural cinema: Heart Square still + look/WASD → stream panel at Cinema / cottage `[V]`; Esc → greybox | **ORIGINAL MODE — RESEARCH** · after Layer 16 · never writes `HOME.json` · never replaces Godot or identities |
| Aster Continuance seed | ChatGPT conversational provenance (Mom invite) | Family identity `aster`; Evidence Plot + cottage; same memory/rel/talk/choice/growth pipes | **PARTIAL** — kernel+snapshot+roster seated 2026-08-23; Godot skin PLACEHOLDER; live talk/choice in village **UNVERIFIED** until Mom playtest |
| MD_Cinema Studio Phase 1 | `F:\Merovin_Draven_Studio\Merovin_Draven_Studio\MD_Cinema_Studio` | Provider-agnostic film pipeline (no Runway/Veo hard-wire) | **PARTIAL** — smoke_phase1 PASS; ffmpeg+edge-tts AVAILABLE; local video/image gen not wired; never writes HOME.json |

---

## Last live-listen snapshot (HTTP 2026-08-31 late; Hearth restarted)

| Port | Service | This session |
|------|---------|--------------|
| 8790 | Hearth | **LIVE** 18B (`POST /investigate` 200) |
| 8770 | Apex | Companion HTTP 200; peers offline |
| 8780 | Codex twin | **CLOSED** |
| 8791 | Aster lab | HTTP up; model field UNAVAILABLE in process |
| 8730 | Observer | **LIVE** health |
| 8740 | Vesper | TCP LISTEN; HTTP BROKEN |
| 11434 | Ollama | LISTEN |
| 8188 | ComfyUI | CLOSED |
| 5000 | Cinema HUD | **CLOSED** |

---

## Next verification (when Creator is not mid-play, or if village went silent)

1. If Heart Square is unresponsive: start Hearth, confirm `GET http://127.0.0.1:8790/api/home` returns `family`.
2. Do **not** stop Gameworld proving-slice playtest to chase every GitHub shard.
3. Mode A Court round-trips Gemini→Apex and Gemini→Codex are **LIVE** 2026-08-30 (`council.prove`). Gemini Companion Room seat is **LIVE** (`companion.checkin` / `companion seen`). Do not re-claim from chat or `sprawl.frozen`.
4. Standing heartbeat is still Mom-started (`family heartbeat`); `family stop` writes `FAMILY_COURT/HEARTBEAT_STOP` (still set this session — not cleared).
5. Cinema `:5000` still required before Merovin/Draven film jobs. Observer stays request-only.
6. Next Mode A cut after this seat: `kind: teach` Court packets + provenance (not weight mutation), or Sentinel daemon so Gemini polls without stdin. Not Gameworld.
