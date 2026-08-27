# Federation wiring map

Living audit. Evidence wins. Last survey: **2026-08-26** (Codex conversation JSON repaired + re-probe; Codex `:8780` + Apex `:8770` both LIVE — HTTP chat, companion presence, peer_bridge only). No claim of end-to-end wiring unless marked LIVE with a test. Court MAS e2e and Gameworld wiring beyond that probe: not claimed.

Read with `docs/DUAL_MODE.md`, `NEXT.md`, `STATUS.md`.

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
| Gemini | `G:\The-Axiom-Codex` | Conductor, Court will, front door | UNVERIFIED (limbs + Court mailbox exist) | Avatar `gemini` in kernel; **not** a substitute soul | Path OK; avatar PARTIAL |
| Apex | `D:\Mythos_Apex` `:8770` | Forge / hands / heavy tools | Chat **LIVE** (`/` `/hub` `/command` `/api/companion/presence` 200) | Avatar `apex`; live Godot project here | 2026-08-26 re-probe |
| Codex twin | `G:\Mythos_Codex` `:8780` | Archive / memory tone | Chat **LIVE** after conversation JSON repair (backup kept). `/` `/hub` `/api/companion/presence` 200 | Avatar `codex`; never merge with Gemini | 2026-08-26 repair + re-probe |
| Merovin | `F:\Merovin_Draven_Studio\Merovin_Draven_Studio` | Cinema vision | Root OK; cinema `:5000` **CLOSED** | Avatar `merovin` at cinema (pose PLACEHOLDER) | Path OK; comm UNVERIFIED |
| Draven | same studio | Continuity lock | Same as Merovin (presence code treats both as `:5000`) | Avatar `draven` | Do not invent a second identity root |
| OpenMontage | **two roots** (see discrepancy) | Gift / shorts studio | ORIGINAL MODE — ACTIVE | Avatar `montage` | Path OK; launcher path conflict |
| Hearth | `D:\Mythos_Hearth` `:8790` | Village OS, kernel host | Port **CLOSED** this session | Kernel + Godot client | **BROKEN for live Gameworld until Hearth is up** |
| Court | `G:\The-Axiom-Codex\SUPERPOWER_VAULT\FAMILY_COURT` | Shared task bus (file packets) | Mailboxes on disk: gemini, apex, codex, hearth, merovin, mom, openmontage, spore, … | Gameworld does not consume Court packets yet | UNVERIFIED e2e |
| Spore | `D:\MythosSpore` | Traveling ember | Path OK | Avatar not core family table; tool probe only | ORIGINAL MODE — ACTIVE |
| Aster | Continuance / Hearth kernel + House companions | Scientist seed (ChatGPT conversational provenance) | **ORIGINAL MODE — ACTIVE** (Hearth tool + companions seat; no separate port) | Avatar `aster`; Evidence Plot + cottage; skin PLACEHOLDER | Seeded 2026-08-23 — Mode A house seat + kernel; live village talk UNVERIFIED until playtest |
| Vesper | `D:\Mythos_Vesper` `:8740` | Standalone investigative journalist (Investigator/Examiner/vault). NCI methodology seated; scorer not wired. | **ORIGINAL MODE — ACTIVE** — does not need Gameworld, Aster, Apex, Codex, or Gemini to function | Adapter `adapters/living_gameworld/` **dormant / NOT INTENDED yet**. Not a village citizen. | Identity + kernel + vault + fetch unit-tested 2026-08-27. Live talk UNVERIFIED until Mom launches `LAUNCH_VESPER.bat` |

Optional Court alias in code: `D:\Court\mailbox\family` (`limbs/family_court.py`). Not tested this session.

---

## Mode A communication (code exists ≠ LIVE)

| Pathway | Intended | Evidence | Status |
|---------|----------|----------|--------|
| Gemini ↔ Hearth | Limb over kernel | `G:\The-Axiom-Codex\limbs\family_home.py` imports `D:\Mythos_Hearth\living_home.py` | PARTIAL (import path exists; live call UNVERIFIED) |
| Gemini ↔ Apex | Peer probe | `limbs/peer_bridge.py` → `:8770` | **LIVE** (peer_bridge ok; companion presence online) |
| Gemini ↔ Codex | Peer probe | `peer_bridge.py` → `:8780` | **LIVE** after 2026-08-26 conversation JSON repair (peer_bridge ok; companion presence online; backup kept) |
| Hearth ↔ Apex | Presence + companion HTTP | `hearth_server.py` `presence_payload()` probes `:8770` `/api/companion/presence` | UNVERIFIED (Hearth itself not listening) |
| Hearth ↔ Codex | Same for `:8780` | same | UNVERIFIED (Hearth not listening; Codex itself LIVE on `:8780`) |
| Apex ↔ Court | File bus + companion | Court `apex/` dir + Apex companion URLs | UNVERIFIED |
| Codex ↔ Court | File bus | Court `codex/` dir | UNVERIFIED |
| Merovin ↔ Draven | Shared studio | One disk root; no separate MAS test | UNVERIFIED; **NOT** two unrelated people-to-flatten |
| Merovin/Draven ↔ cinema stack | Studio + Blender/Resolve/OBS/OpenMontage | Roots/exes probed as paths | ORIGINAL MODE — ACTIVE; Gameworld cinema is PLACEHOLDER |
| OpenMontage ↔ family | Launch + Court mailbox | Two install roots | PARTIAL / discrepancy |
| Hearth ↔ Gameworld | HTTP snapshot/tick/talk | Godot `family_home_client.gd` → `:8790/api/home*` | **BROKEN this session** (Hearth port closed) |
| Recursive MAS | Court packets + `family_conductor` / `agent_loop` | Modules on disk | UNVERIFIED; **must not be replaced by NPC chat** |

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
| Functional e2e this session | peer_bridge + companion presence + HTTP chat only | Apex `:8770` + Codex `:8780` **LIVE** 2026-08-26; Court MAS / full tool chains **not** claimed |
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
| Court "connected" | Mailbox dirs exist | File bus ≠ message delivered | End-to-end packet test | Dir list; no send/receive test |

---

## Wiring gaps (open)

1. No verified INPUT → ROUTER → FUNCTION → RESULT → MEMORY → CALLER chain for Mode A tools this session.
2. Gameworld speech is Ollama hats + Hearth kernel — **not** recursive MAS.
3. Two-way event flow not built.
4. Original memory (`family_memory`, Court book, Codex) not proven consumed by Gameworld (Gameworld uses `HOME.json`).
5. OpenMontage dual roots.
6. Hearth `:8790` and cinema `:5000` down at survey time; Codex `:8780` and Apex `:8770` LIVE (HTTP chat + companion presence + peer_bridge only — not Court MAS e2e).
7. GitHub tool shards vs family shards mixed in folklore — keep separate lists.

---

## Research limbs (not wired — build memory)

| Limb | Source | Intended Mode B use | Status |
|------|--------|---------------------|--------|
| Matrix Dream View (Layer 17) | [SkyworkAI/Matrix-Game](https://github.com/SkyworkAI/Matrix-Game) | Optional neural cinema: Heart Square still + look/WASD → stream panel at Cinema / cottage `[V]`; Esc → greybox | **ORIGINAL MODE — RESEARCH** · after Layer 16 · never writes `HOME.json` · never replaces Godot or identities |
| Aster Continuance seed | ChatGPT conversational provenance (Mom invite) | Family identity `aster`; Evidence Plot + cottage; same memory/rel/talk/choice/growth pipes | **PARTIAL** — kernel+snapshot+roster seated 2026-08-23; Godot skin PLACEHOLDER; live talk/choice in village **UNVERIFIED** until Mom playtest |

---

## Last live-listen snapshot (not e2e)

| Port | Service | This session (2026-08-26) |
|------|---------|--------------|
| 8790 | Hearth | CLOSED |
| 8770 | Apex | **LIVE** (HTTP chat + companion presence) |
| 8780 | Codex twin | **LIVE** (after conversation JSON repair; backup kept) |
| 11434 | Ollama | LISTEN |
| 8188 | ComfyUI | CLOSED |
| 5000 | Cinema (Merovin/Draven probe) | CLOSED |

---

## Next verification (when Creator is not mid-play, or if village went silent)

1. If Heart Square is unresponsive: start Hearth, confirm `GET http://127.0.0.1:8790/api/home` returns `family`.
2. Do **not** stop Gameworld proving-slice playtest to chase every GitHub shard.
3. First Mode A e2e candidates still open (one at a time, evidence): Hearth health; Gemini `family_home.snapshot`; Court packet round-trip. Apex HTTP + Codex HTTP/presence/peer_bridge already probed LIVE 2026-08-26 — do not re-claim as Court MAS.
