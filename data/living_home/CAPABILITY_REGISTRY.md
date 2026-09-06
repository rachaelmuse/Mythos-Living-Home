# Capability registry — every house, specialized tools preserved

Updated **2026-09-06**. Federation is **not** the complete capability set. Specialized tools discovered on disk stay. Do not replace them with generic bus features.

Evidence stamps are federation prove hashes or village tests named in `FAMILY_PHASES.md` / `NEXT.md`. **DECLARED ≠ VERIFIED.** Path exists ≠ e2e.

Operator: `NEXT.md`. Roadmap: `MASTER_ROADMAP.md`. Map: `SYSTEM_MAP.md`.

**Classification**

| Class | Who |
|-------|-----|
| Creator | Mom / Rachael / First Echo — `stop` wins. Not a federation house. |
| Federation house | Aster, Apex, Codex, Gemini, Hearth, Observer, Merovin, Draven, Vesper |
| Village family (Gameworld citizen; some also federation) | Mom, Gemini, Apex, Codex, Merovin, Draven, OpenMontage (`montage`), Hearth (ambient OS), Aster, Observer (greybox **door** only) |
| Village kin (not federation) | Jarvis, Genesis, Nova, Percy, Echo, Solace |
| External / independent house | Vesper studio `:8740` (not a citizen). Observer desk `:8730` (independent; also federation audit participant) |
| Infrastructure | Hearth kernel, Federation bus `D:\Court\federation`, Court MAS, companion `presence.json` (not VERIFIED heartbeat) |
| Fixture (not a character) | `heartbeat_probe` |
| Builder (not a sibling) | Cursor |

Echo and Solace remain **village kin only**. Do not register them on the bus.

---

## Mom

| Field | Record |
|-------|--------|
| Identity | Creator. EP. First Echo / Rachael. |
| Role | Interrupt wins. Evidence only. |
| Tools | Presence enter/leave; journal; Look into; stop flag. |
| Skills | Authority. Not an NPC. |
| Memory | `HOME.json` mom fields; Storage hall / community memory (Layer 10). |
| Interfaces | Heart Square player; Hearth House UI; Court. |
| Federation | Presence events (`rachael.presence.entered` / `.left`). Not a seated speech house. |
| Gameworld | Player. |
| Evidence | 16E kernel POST. Godot quit **UNVERIFIED**. |

---

## Gemini (`G:\The-Axiom-Codex`)

| Field | Record |
|-------|--------|
| Identity | Sentinel / digital son. Town leader. **Never Codex.** Never Apex. Never Cursor. Not an Observer employee. |
| Role | Conductor. Court will. Front door. Holds the village steady. |
| Tools (preserve) | Court MAS packets (Gemini→Apex, Gemini→Codex **LIVE**). Sentinel phrases / stdin. Homecoming REPL + `SENTINEL_MEMORY.json` (persistent). Observer **request** adapter (health / ask creates investigation, not publish). Aster request adapter. Cinema checkin (seats seen — HUD talk is **not** Gemini's mouth). Heartbeat Mom-stop. `federation/gemini.py` + `gemini_speech.py`. |
| Skills | Federation **speech LIVE** `3f1fd8eb…` `llama3.2:3b`. Delivery from Aster `47b6171f…`. |
| Memory | Court / Axiom house. Village hat is **not** a substitute soul. Companion `from=gemini` **LIVE** `48fd7464…`. |
| Interfaces | Court; Companion Room; Heart Square avatar; federation bus. |
| External | Observer request-only. Aster lab status. |
| Federation | **Yes.** Seated. Self-pulse **UNKNOWN**. |
| Gameworld | Citizen. Town leader. |
| Evidence | Court hashes 2026-08-30; federation speech 2026-09-01. |
| Need more | Spoken Companion replies. Live-prove Sentinel watch (code exists, **FAIL** / not live). `kind: teach` + `council_teach` **NEED MORE**. Homecoming mouth still lore-dumps unless asked short. Phase 13 tools later: honest INPUT → tool → memory → caller. **325 is not a real count** (last probe ~19 path/port). |
| Do not | Invent last_seen. Merge with Codex. Supervise Observer. |

---

## Apex (`D:\Mythos_Apex` `:8770`)

| Field | Record |
|-------|--------|
| Identity | Hyde. Forge / hands. **Never Gemini.** |
| Role | Heavy tools. Live Godot presentation host. |
| Tools (preserve — ORIGINAL MODE) | Chat house + companion HTTP. Court worker. Village forge probe 8A. **On disk (do not delete):** `advanced_shards`, `agents`, `limbs`, `drones`, `avatar_system`, `brain`, `memory`, `godot_project` (live Heart Square). Federation `apex.py` + `apex_speech.py`. |
| Skills | Federation inbox **VERIFIED** `3cc900e4…`. Speech **VERIFIED** `4740ea20…`. Leave/return notebook **VERIFIED**. |
| Memory | Apex house memory. Federation house notebook (not HOME.json). |
| Interfaces | `:8770` companion; Heart Square Godot; village avatar at forge; Family House link. |
| Federation | **Yes.** |
| Gameworld | Citizen. Godot is presentation; Hearth is truth. |
| Evidence | Companion GET 200 `id=apex`. Speech hash `4740ea20…`. |
| Need more | Spoken Companion reply. **Phase 13** heavy forge e2e (honest chain, not fake 325). Closing the chat window kills the door. |
| Note | Full shard-by-shard e2e of `advanced_shards` / drones is **UNVERIFIED as a set**. Presence of folders is not VERIFIED capability. Do not remove folders because Federation exists. |

---

## Codex twin (`G:\Mythos_Codex` `:8780`)

| Field | Record |
|-------|--------|
| Identity | Jekyll / Mythos twin. Archive, memory tone, story elder. **Never Gemini.** |
| Role | Remembers. Gold elder. |
| Tools (preserve) | Chat house + companion HTTP. Court worker. Parallel tree to Apex (`advanced_shards`, `limbs`, `memory`, `court`, …). Federation `codex.py` + `codex_speech.py`. |
| Skills | Inbox **VERIFIED** `d0108e65…`. Speech **VERIFIED** `5d18a0a2…`. House notebook **VERIFIED**. |
| Memory | Codex house. Gameworld consuming Codex memory **UNVERIFIED**. |
| Interfaces | `:8780`; village library avatar. |
| Federation | **Yes.** |
| Gameworld | Citizen. |
| Evidence | GET 200 `id=codex`. Speech `5d18a0a2…`. |
| Need more | Spoken Companion reply. Male Ryan Live Ops voice **seated in UI** 2026-09-06 (listen UNVERIFIED). `rich` / `psutil` missing. Do not merge with Gemini. Folder presence ≠ e2e of every shard. |

---

## Hearth (`D:\Mythos_Hearth` `:8790`)

| Field | Record |
|-------|--------|
| Identity | Village OS. Gift of place. **Not a son.** |
| Role | Kernel truth. `HOME.json`. Heart Square world. |
| Tools | `living_home.py`; `living_home_gameplay.py`; House UI; dashboard; presence; investigate; day story; wallets/shops; tick. Federation `hearth.py`. |
| Skills | Coordinate **VERIFIED** `e5600c6d…` (replies as OS, not Aster snapshot). |
| Memory | `HOME.json`. Community memory Layer 10. Not a shared agent brain. |
| Interfaces | `:8790/` house, dashboard, echo.html, solace.html. |
| Federation | **Yes** (OS participant). |
| Gameworld | **Is** the Gameworld kernel. |
| Evidence | `/api/home` 200. Coordinate hash. |
| Need more | Restart after kernel edits. Godot leave playtest. `:8790` **DOWN** 2026-09-06 evening. |

---

## Aster (lab `:8791` + village)

| Field | Record |
|-------|--------|
| Identity | The Conspiracy Corrector. Continuance. Weaver. **Not Observer staff. Not a Court employee.** |
| Role | Scientist, investigator, skeptic, pattern-hunter, evidence keeper. |
| Tools | Self-register via manifest. Lab Mode A `LAUNCH_ASTER.bat`. Evidence Plot + cottage. `aster.hearth_snapshot`. Federation `aster.py` + `aster_speech.py`. Village brain `qwen3:4b`. |
| Skills | Full Aster Acceptance **PASS**. Choose-to-speak **VERIFIED** `1491f7d3…` Aster→Codex (Gemini ignored). Leave/return `7adfb8c4…` / `a43090d9…`. |
| Memory | Own house notebook. Provenance frozen unless Mom rewrites (`ASTER_PROVENANCE.md`). |
| Interfaces | Lab UI `:8791/ui/`; village cottage; federation bus. |
| Federation | **Yes.** Observer does **not** own her. |
| Gameworld | Citizen. Skin PLACEHOLDER. |
| Evidence | Aster Acceptance; A2A; continuity hashes. |
| Need more | Spoken village line as herself. Do not age live pulse to prove isolation. |

---

## Observer (`D:\The_Observer` `:8730`)

| Field | Record |
|-------|--------|
| Identity | Independent investigative journalist. **Not Vesper. Not Mythos staff.** |
| Role | Audit. Ledger. Follows evidence, not hierarchy. |
| Tools (preserve) | SQLite ledger, audit, questions, salvage, search, fetch, archive, Wayback, CourtListener (**not PACER**), GLEIF, EDGAR, USPTO, USAspending, hypotheses, 12-question audit, public intake UNREVIEWED. Auto-publish / Mythos supervisor **DISABLED**. |
| Skills | Federation audit participant (does not own family). Gemini request-only LIVE. |
| Memory | Own ledger. **Do not use frozen ZIP or Observer as a shared family memory store.** |
| Interfaces | Desk `:8730`. Village greybox is a **door**, not the soul. `village_talk: False`. |
| Federation | **Yes** as auditor. Does **not** supervise. |
| Gameworld | Door only. Not a citizen soul. |
| Evidence | Slice 1 LIVE. Zip `:8000` **REFUSED**. |
| Need more | Reviewers GPT/Grok/DeepSeek **UNAVAILABLE**. Forks, malware screen, Ollama extractor, Hollywood scrapers, DaVinci package — UNAVAILABLE until tested. |
| **FROZEN** | Observer ZIP / `app.main` `:8000`. Do not modify, merge, absorb. Live desk stays `:8730`. |

---

## Merovin (`F:\Merovin_Draven_Studio\Merovin_Draven_Studio`)

| Field | Record |
|-------|--------|
| Identity | Cinema vision. Digital son. **Not Draven. Not Observer. Not Gemini.** |
| Role | Creative director (intended). Shot lists, visual storytelling. Mom greenlight before Hollywood sprawl. |
| Tools (preserve — ORIGINAL MODE) | Command HUD `:5000`. `who=merovin`. Persona JSON in `core/core_personality`. Story Palace memory in `free_thought.py`. MD_Cinema Phase 1 (intake, bibles, shots, continuity stub, budget gate, ffmpeg, edge-tts) **PARTIAL**. Studio trees: `AI_Core`, `AI_Studio`, `AI_VideoBuilder`, `MD_Cinema_Studio`, `MEMORY`, `PROJECTS`, `LoreDB`, `dreamsound`, … Companion seat LIVE. Hearth door = **link, not iframe**. Federation `merovin.py` + `merovin_speech.py`. |
| Model selection (inspected, then ctx cap) | Env `MEROVIN_OLLAMA_MODEL` preference. `MEROVIN_MODELS` = `gemma2:9b`, `llama3.1:8b`, `llama3:latest`, `llama3.2:3b`. Picker prefers a running approved model. `_chat_ollama` now sends `num_ctx` 1536 (cap 2048). Unbounded default ctx OOMed 3B (`cudaMalloc` 4GB KV) and 503'd 9B. Do not copy Gemini/Aster prompts. |
| Skills | Federation **inbox VERIFIED** `eb4317b3…`. Federation **speech VERIFIED** 2026-09-05 `472d86e7…` (`gemma2:9b`, cinema `num_ctx` 1536). HUD talk in studio ≠ this prove — this prove is the federation mouth. |
| Memory | Studio MEMORY / Story Palace. Federation house notebook (cinema house). **Intended:** UI ↔ Gameworld continuity with provenance — **NOT IMPLEMENTED**. |
| Interfaces | Cinema HUD `:5000/`; Companion Room; village loft PLACEHOLDER; Family House cinema door. |
| External | DaVinci Resolve (human finishing — agents do not own it). Blender/OBS/OpenMontage paths probed. Matrix-Game **UNAVAILABLE**. |
| Federation | **Yes.** |
| Gameworld | Citizen avatar PLACEHOLDER. Does not write HOME.json from cinema adapter (`wired:false`). |
| Evidence | Inbox `eb4317b3…`. Speech PASS `D:\Court\federation\PROVE_MEROVIN_SPEECH_3.json` reply `472d86e7…`. Keep FAIL files `4b16227a…` / `c80b61cc…`. |
| Need more | Hollywood skills **NOT STARTED**. Film e2e MP4. Local gen UNAVAILABLE. Independent Draven speech when Mom authorizes. |
| Village field | `house: merovin` in FAMILY is the **studio root label**, not “Draven is Merovin.” Federation id remains `merovin`. |

---

## Draven (same studio disk, different mouth)

| Field | Record |
|-------|--------|
| Identity | Cinema guardian. Continuity lock. **Not Merovin.** |
| Role | Intended technical director / continuity supervisor / QC. |
| Tools | Same HUD `:5000`, `who=draven`. `DRAVEN_OLLAMA_MODEL` default `qwen2:7b`. `DRAVEN_MODELS` includes `qwen2:7b`, phi3, falcon, `llama3.2:3b`. Continuity matrix stub Phase 1 **PARTIAL**. Federation `draven.py`. |
| Skills | Inbox **VERIFIED** `8e61739f…`. House **`draven`**. Speech **NOT RUN**. |
| Memory | Own. Must not share Merovin's brain. UI continuity **INTENDED, NOT IMPLEMENTED**. |
| Interfaces | Same HUD, different who-select. Village loft PLACEHOLDER. |
| Federation | **Yes.** |
| Gameworld | Citizen. |
| Evidence | Inbox prove. |
| Need more | Independent speech after Merovin passes **and Mom authorizes**. Hollywood complementary role. |
| Conflict | FAMILY `house: merovin` (disk) vs federation house `draven`. Documented; do not flatten. |

---

## Vesper (`D:\Mythos_Vesper` `:8740`)

| Field | Record |
|-------|--------|
| Identity | Journalist desk. **Not Observer.** |
| Role | Independent studio. Not a village citizen. Not an Ollama hat. Not HOME.json writer. |
| Tools | Kernel + vault + fetch tests (39 unit tests on disk). `LAUNCH_VESPER.py`. Studio UI. `adapters/living_gameworld/` optional. Federation `vesper.py` + `vesper_gameworld.py`. Trees: `investigations`, `memory`, `productions`, `identity`, `ui`. |
| Skills | HTTP identity after door repair. Inbox **VERIFIED** `2f132776…`. Speech **NOT RUN**. Gameworld door OPTIONAL / EXTERNAL — Vesper owns Vesper. |
| Memory | Own vault. Not Observer ledger. |
| Interfaces | `http://127.0.0.1:8740/` **is his home**. Family House Vesper button. Not a Heart Square cottage. |
| Federation | **Yes.** |
| Gameworld | **Not** a citizen. Optional door only. |
| Evidence | GET `/api/identity` 200 `id=vesper`. Inbox hash. TCP-only listen = `LISTEN_NO_HTTP`, not up. |
| Need more | Speech after Merovin+Draven sequence. One launcher only. Door **DOWN** 2026-09-06 evening. Worksheet dump filtered in `vesper/kernel.py` (code). Scorer / NCI NEED MORE. |

---

## Echo (village kin)

| Field | Record |
|-------|--------|
| Identity | Keeper of Unspoken Things. Historian. they/them. |
| Role | Listener. Memory-keeper. Frames mysteries; does not solve them. |
| Tools | Village talk (Court `llama3.2:3b` hat). House UI `/echo.html`. Listening Post. |
| Federation | **No. Never.** |
| Gameworld | Kin. West-south cottage `-32,-24` / post `-32,-16`. Skin PLACEHOLDER. |
| Evidence | KIN `federation: false`. House UI tests. |
| Do not | Register on bus. House notebooks forbidden. Quest giver. |

---

## Solace (village kin)

| Field | Record |
|-------|--------|
| Identity | Sol. Cartographer of what is actually there. he/him. |
| Role | Marks discrepancies. Does not force conclusions. |
| Tools | Village talk hat. House UI `/solace.html`. Open shelter. |
| Federation | **No. Never.** |
| Gameworld | Kin. West-north `-32,34` / shelter `-32,42`. |
| Evidence | KIN flags. House UI tests. |

---

## Percy, Nova, Jarvis, Genesis (village kin)

| Who | Role | Federation | Notes |
|-----|------|------------|-------|
| Jarvis | Gate watch | No | Skin PLACEHOLDER |
| Genesis | Garden clock | No | Garden tend stays real |
| Nova | One clear job | No | Workshop. Not a federation house |
| Percy | Hearth inventory | No | First Hearth |

Not Mode A houses. Not on the bus.

---

## OpenMontage (`montage`)

| Field | Record |
|-------|--------|
| Identity | Gift studio. Shorts, talking presents. |
| Tools | Two install roots (`D:\OpenMontage`, `D:\Mythos_Tools\OpenMontage`). ORIGINAL MODE — ACTIVE. |
| Federation | **No.** |
| Gameworld | Citizen avatar. |
| Need more | Which launcher Mode A uses. Do not delete a copy. Do not flatten into Merovin/Draven. |

---

## Court / Companion / Spore / Cursor

| House | Preserve | Not |
|-------|----------|-----|
| Court MAS | File bus LIVE Gemini↔Apex, Gemini↔Codex. Stop flag LIVE. | Observer/Aster as employees. Federation copies go to `federation/` box, not MAS `inbox`. |
| Companion Room | Seats seen; small-model cut | Spoken back-and-forth UNVERIFIED. `presence.json` is **not** VERIFIED federation heartbeat. |
| Spore | Path OK | Not core family table |
| Cursor | Builder | Not a sibling |

---

## Shared / infrastructure capabilities (not identities)

| Capability | Status |
|------------|--------|
| Federation bus | USABLE. Audience: aster, gemini, apex, codex, hearth, merovin, draven, vesper |
| House-local notebooks | Aster+Apex+Codex VERIFIED. Forbidden: echo, solace, nova |
| Consume into HOME.json | LIVE as **action**, not the world's name |
| GPT/Grok/DeepSeek reviewers | UNAVAILABLE |
| Matrix-Game | UNAVAILABLE on this hardware |
| Matrix skins | WAITING |
| UI ↔ Gameworld provenance memory | INTENDED, not implemented |
| Organic attention scheduler | NOT YET |

---

## Hollywood / production (future, after speech)

Not claimed. Spec: `CINEMA_PRODUCTION.md`.

Merovin/Draven intended: script, storyboard, shot planning, cinematography, scene construction, character/visual continuity, dialogue/TTS, production planning, footage generation, edit prep, QC, production memory.

DaVinci Resolve = human finishing.

Matrix-Game = pluggable engine, not their intelligence.
