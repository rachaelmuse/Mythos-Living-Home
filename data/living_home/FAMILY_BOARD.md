# Family board — what we have, what is done, what you should do

Written **2026-08-30**. Evidence only. A prompt is not a loop. JSON on disk is a mailbox until a process reads it. Identities never merge. Mom `stop` wins.

**Short answer:** No — we did **not** complete every connection. We completed a few Mode A proves. Gameworld is not wired end-to-end. Cinema HUD is down. Heartbeat is still stopped because you said stop.

---

## What you should do (simple)

Pick **one lane**. Do not try to finish everything tonight.

### If you want the village (Gameworld)

1. Start Hearth (`START_HEARTH.bat` / desktop Enter path you already use).
2. Confirm [http://127.0.0.1:8790/api/home](http://127.0.0.1:8790/api/home) returns `family`.
3. Enter Heart Square (Apex Godot). Walk places. Check welcome/away notices — no forced bystander speech.
4. Optional: Aster lab [http://127.0.0.1:8791/ui/](http://127.0.0.1:8791/ui/) — she needs her Ollama model loaded to talk.

Hearth `:8790` was **CLOSED** when this board was written. The village cannot run without it.

### If you want the council (Mode A, not the village)

Gemini already sat in the Companion Room as **Gemini**. Apex and Codex can **see** him. They have not been proven to **talk back**.

In Sentinel, exact phrases:

- `companion checkin` / `who is in the room`
- `council prove` / `prove codex` (already LIVE once — do not re-claim from chat)
- `observer health` / `ask observer …`
- `aster status`
- `family heartbeat` — only if you want claiming again (`family stop` is still set)
- `family stop` — always wins

Do **not** say “wired” because a chat model described a tool.

### If you want film

Start the Merovin/Draven cinema HUD on `:5000` first. Until that port is up, film jobs are **unavailable**, not wired.

### If you want Observer

Open [http://127.0.0.1:8730/](http://127.0.0.1:8730/). Ask a question there, or tell Sentinel `ask observer …`. Do **not** bolt Observer onto Mythos. Do **not** auto-publish.

---

## Two modes (do not flatten)

| Mode | What it is | What it is not |
|------|------------|----------------|
| **A — original family** | Court packets, Sentinel, Companion Room, tools, launchers | Not Heart Square NPCs |
| **B — Living Gameworld** | Village, homes, talk bubbles, wildlife, `HOME.json` | Not a replacement for Court or identities |

Gameworld expands the family. It does not replace it.

Never merge: Gemini ≠ Apex ≠ Codex ≠ Merovin ≠ Draven ≠ Hearth ≠ Observer ≠ Vesper ≠ Aster ≠ Mom ≠ Cursor.

---

## Ports right now (listen check, 2026-08-30 evening)

| Port | Who | Listen | Honest note |
|------|-----|--------|-------------|
| 8770 | Apex | **LISTEN** | Presence HTTP 200. Heartbeat looked stale (apex `online: false` on this probe). |
| 8780 | Codex | **LISTEN** | Same presence file as Apex. |
| 8790 | Hearth | **CLOSED** | Village **BROKEN** until you start it. |
| 8791 | Aster lab | **LISTEN** | `/api/status` **timed out** on this probe. Earlier today it was HTTP 200. |
| 8730 | Observer | **LISTEN** | `/health` **200** earlier this session. Independent desk. |
| 8740 | Vesper | **LISTEN** | TCP open; HTTP **did not answer** this probe. Live talk UNVERIFIED. |
| 5000 | Cinema HUD | **CLOSED** | Film jobs unavailable. |
| 11434 | Ollama | **LISTEN** | Models on disk; VRAM/load is a separate fact. |

---

## Project by project

### Gemini / Axiom — `G:\The-Axiom-Codex`

**Have:** Sentinel, Court bus, council prove, Companion Room check-in as `gemini`, Observer/Aster/cinema adapters, heartbeat with Mom-stop.

**Completed (tested):**

- Court packet Gemini → Apex **LIVE** (`70c9ffe8…`)
- Court packet Gemini → Codex **LIVE** (`03dfc102…`)
- Companion Room seat **LIVE** (`from=gemini`, msg `48fd7464…`; Apex+Codex presence listed him)
- `family stop` writes `FAMILY_COURT/HEARTBEAT_STOP` and blocks claim (**still set**)

**Not complete:**

- Standing Sentinel daemon without you typing (watch loop **code exists**, **not live-proved**)
- `kind: teach` Court packets + provenance
- Apex/Codex **spoken** reply to Gemini in the room
- Full INPUT → tool → memory → caller chain for “all 325 tools” (that count is a lie; last probe was **19** path/port checks)

**You:** Use exact Sentinel phrases. Do not clear `HEARTBEAT_STOP` unless you want claiming again.

---

### Apex — `D:\Mythos_Apex` `:8770`

**Have:** Chat house, Companion Room HTTP, Court worker, live Godot Heart Square project.

**Completed:** Chat + presence + Court worker reply with presence (2026-08-30 prove).

**Not complete:** Heavy forge e2e as “all tools wired.” Godot village needs Hearth.

**You:** Keep Apex running if you want Companion Room / Court workers.

---

### Codex twin — `G:\Mythos_Codex` `:8780`

**Have:** Twin chat house, same Companion Room files, Court worker.

**Completed:** Same class of prove as Apex (packet `03dfc102…`).

**Not complete:** Merge with Gemini (forbidden). Archive/memory consumed by Gameworld (not proven).

---

### Hearth / Living Home — `D:\Mythos_Hearth` + git `G:\The-Axiom-Codex\Mythos-Living-Home`

Kernel: `D:\Mythos_Hearth\living_home.py`. Git snapshot of scene is not the live Godot project.

**Have / closed in village slice:** Sound, media, harbor, economy 14A–14D, Market Lane, 15A–15D, Aster seed, **16A–16E**, Windmill. Gameplay Phase 1 scaffold.

**Completed in git:** Wiring map updates through Companion Room seat (`7c39d14` on `cursor/family-dashboard-window`).

**Not complete:**

- Live playtest of 16E (Hearth down)
- Gameplay Phase 2
- Pods/Islands (not on disk)
- Layer 17 Matrix (research only)
- Phase 13 (last on purpose)
- Houses interiors PLACEHOLDER, pathing PLACEHOLDER
- Court MAS inside the village (not intended as a substitute)

**You:** Restart Hearth + Enter when you want the square. Do not rewrite tag `living-home-baseline-001`.

---

### Companion Room — `D:\Court\companion_room`

**Have:** Shared `presence.json` + `room.jsonl`. Apex, Codex, Gemini ids allowed.

**Completed:** Gemini visible as himself.

**Not complete:** Proven back-and-forth chat (Apex/Codex lines after Gemini sat). Creator heartbeat is stale.

---

### Aster — lab `:8791` + village avatar `aster`

**Have:** Lab door, kernel seed, village cottage/Evidence Plot (skin PLACEHOLDER).

**Completed:** Mode A `aster.request` → lab status **LIVE** earlier 2026-08-30.

**Not complete:** Village talk playtest. Ollama `qwen3:4b` must be loaded for her to speak. Lab status **timed out** on the evening probe.

**You:** `LAUNCH_ASTER.bat` if the lab UI is dead. Load her model if you want speech (may unload another model).

---

### The Observer — `D:\The_Observer` `:8730`

**Have:** Own git, charter, SQLite ledger, dashboard, public desks (search, Wayback, CourtListener **not PACER**, GLEIF, EDGAR copies, USPTO PDFs, USAspending), reports, no auto-publish.

**Completed:** Vertical slice 1 pipeline. Registry this session: **27 CONNECTED**, **3 DISABLED**, **11 UNAVAILABLE**. Health 200. Gemini request-only adapter. Three investigations on disk, all `fact_check`, none published.

**Not complete:** Four independent reviewers, public forks, malware screen, documentary/DaVinci package, Ollama extractor, Neo4j/Postgres/Redis/vectors. **Not intended** as a village citizen or Court employee.

**You:** Use the desk. Do not merge with Vesper. Do not ask Mythos to supervise it.

---

### Vesper — `D:\Mythos_Vesper` `:8740`

**Have:** Standalone journalist identity, kernel/vault/fetch unit-tested 2026-08-27. Gameworld adapter **dormant / NOT INTENDED yet**.

**Completed:** Identity + tests on disk.

**Not complete:** Live talk. Port was LISTEN this evening; HTTP did not answer.

**You:** `LAUNCH_VESPER.bat` if you want her desk. Do not merge with Observer.

---

### Merovin + Draven — `F:\Merovin_Draven_Studio\...`

**Have:** One studio root (two people, not two unrelated orgs). MD_Cinema Phase 1 on disk (`smoke_phase1` passed 2026-08-27). ffmpeg + edge-tts available. Gameworld cinema PLACEHOLDER. Adapter `wired: false`.

**Completed:** Foundation on disk. Honest “gen not wired.”

**Not complete:** Cinema HUD `:5000`. Local video/image gen. Gameworld cinema as a real adapter.

**You:** Bring `:5000` up before film jobs.

---

### OpenMontage

**Have:** Two install roots (`D:\OpenMontage` and `D:\Mythos_Tools\OpenMontage`). Path OK.

**Not complete:** Which launcher Mode A uses (discrepancy). Do not delete a copy.

---

### Spore — `D:\MythosSpore`

Path OK. ORIGINAL MODE. Not a core village identity.

---

### Court — `G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT`

**Completed:** Gemini→Apex and Gemini→Codex packet round-trips.

**Not complete:** Observer/Aster as Court employees (**must not**). Teach packets. Standing heartbeat daemon. Gameworld consuming Court packets.

Stop file: `FAMILY_COURT/HEARTBEAT_STOP` (**present**).

---

## Connections — honest score

| Connection | Status |
|------------|--------|
| Gemini ↔ Apex (Court packet) | **LIVE** |
| Gemini ↔ Codex (Court packet) | **LIVE** |
| Gemini in Companion Room (seen) | **LIVE** |
| Gemini ↔ Apex/Codex (spoken room reply) | UNVERIFIED |
| Gemini ↔ Observer (request) | **LIVE** (health; ask = create investigation, not publish) |
| Gemini ↔ Aster lab (request) | **LIVE** earlier; evening status probe timed out |
| Gemini ↔ Hearth | PARTIAL (import exists; Hearth down) |
| Hearth ↔ Godot village | **BROKEN** until `:8790` |
| Merovin/Draven ↔ cinema HUD | **UNAVAILABLE** (`:5000` closed) |
| Observer as Mythos citizen / supervisor | **NOT INTENDED** |
| Vesper live desk | UNVERIFIED |
| Recursive MAS standing daemon | PARTIAL (stop works; no unattended watch proved) |
| 325 shared tools e2e | **Not true.** Do not claim. |

---

## Later (do not jump here)

Gameplay Phase 2 → optional 14E–14F → Layer 17 Matrix → **Phase 13 last**.  
Observer reviewers/forks/malware/docs package only with tests.  
`kind: teach` provenance. Sentinel watch live-prove.

Baseline tag `living-home-baseline-001` — do not rewrite. Do not overwrite Apex GitHub origin.

---

## Where the detailed wiring map lives

`data/living_home/FEDERATION_WIRING.md` (Living Home git) and the Hearth copy of the same file. This board is the Mom-facing summary. The map wins if they disagree — update the map after a new test.
