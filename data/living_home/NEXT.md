# Living Home — where we are

Updated **2026-09-09**. Evidence only. Mom accepted the architecture assessment as **the plan**. This file is the operator surface.

Kernel: `D:\Mythos_Hearth\living_home.py`  
House UI: **http://127.0.0.1:8790/house.html**  
Aster lab: **http://127.0.0.1:8791/ui/**  
Cinema HUD: **http://127.0.0.1:5000/**  
Observer: **http://127.0.0.1:8730/**  
Dashboard: **http://127.0.0.1:8790/dashboard**  
Enter: Desktop **Mythos Living Home - Enter**

Law: `FEDERATION_DIRECTIVE.md` · Map: `FEDERATION_RECONCILIATION.md` · Wiring: `FEDERATION_WIRING.md` · Tracker: `FAMILY_PHASES.md` · Status: `STATUS.md` · Production spec: `CINEMA_PRODUCTION.md` · Above-trackers: `MASTER_ROADMAP.md` · `CAPABILITY_REGISTRY.md` · `SYSTEM_MAP.md`

Baseline tag `living-home-baseline-001` — do not rewrite.

---

## Assessment (keep this language)

**Foundation is STRONG. Federation is USABLE. Village is FUNCTIONAL** and must not be contaminated to make Federation look bigger.

**Cinema is SEATED, NOT FINISHED.** Organic autonomy is the **NEXT MAJOR PHASE** — do not rush. Godot lifecycle proof still has one small gap (real quit/restart). Gemini self-pulse remains honest **UNKNOWN**. External independent reviewers remain **UNAVAILABLE** — do not fabricate. **Do not add more houses** until current houses have speech and an identity/isolation audit.

Not one giant AI pretending to be nine people. **Nine distinct doors → nine identities → separate responsibilities → controlled communication → observable failures.**

The next interesting question is not how many AIs — it is what happens when we stop telling them when to act and give memory, context, resources, and freedom to decide whether acting is worth doing.

**Milestone to keep:** TCP listen ≠ HTTP identity answering as the correct person.

---

## Bookkeeping above the phases (2026-09-04)

Master reconciliation **documented, not a capability stamp.** Inspected on-disk docs + `living_home.py` FAMILY/KIN + `federation/` + cinema `core/free_thought.py` + `ollama list` + house roots. Observer ZIP **not touched**.

- Conflicts listed in `MASTER_ROADMAP.md` (do not silently pick a side).
- Specialized tools listed in `CAPABILITY_REGISTRY.md` (Federation is an overlay, not the body).
- Relationships in `SYSTEM_MAP.md`.

**UI ↔ Gameworld memory** is now an **intended** architecture (conversation → provenance → episodic / candidate / validated). **NOT IMPLEMENTED.** Conversation is not automatically truth. Interfaces are different doors into the **same** agent identity.

**Next implementation (only, after this recon):** Merovin speech **VERIFIED** 2026-09-05. Draven speech **VERIFIED** 2026-09-09. Vesper speech **VERIFIED** 2026-09-09 (`speak-vesper`, `PROVE_VESPER_SPEECH.json`, reply `f9fd17a9…`, model `qwen3:4b`). Identity holds (not Observer). Spoken line is a **thinking leak / truncated** — house-voice polish NEED MORE. Federation integrity **2026-09-09:** Vesper Gameworld door **VERIFIED**; isolation matrix **VERIFIED** (Gemini pulse still UNKNOWN); Vesper restart **VERIFIED** (`PROVE_RESTART_INTEGRITY_2.json`; FAIL `PROVE_RESTART_INTEGRITY.json` kept — whole-file HOME hash was a Hearth tick, not a Vesper write); bounded organic reason **VERIFIED** (`PROVE_ORGANIC_REASON_2.json`; FAIL `_` kept — historic inbox scan). Do not start Hollywood until Mom says go.

CLI note: inbox prove is `python -m federation.prove merovin`. Speech prove is `python -m federation.prove speak-merovin`. Do not treat a passing inbox re-run as speech.

---

## CURRENT PHASE

**Village:** **18B LIVE**. **16E LIVE**. Echo + Solace seated as **village kin** (not federation). Leave POST is in kernel/Godot; **restart Hearth** + reload Heart Square before a quit counts as leave. Godot walk and Godot leave remain **UNVERIFIED** until Mom does them. Village must stay FUNCTIONAL — do not flatten it into Federation.

**Federation:** **USABLE**, not finished. Aster Acceptance **PASS**. Apex + Codex **real speech**. Hearth **coordinate**. Gemini **seated** with honest pulse **UNKNOWN**. Observer **independent audit**. Merovin **speech VERIFIED** 2026-09-05. Draven **speech VERIFIED** 2026-09-09. Vesper **speech VERIFIED** 2026-09-09 (thinking leak NEED MORE). Vesper Gameworld door **VERIFIED** 2026-09-09. Isolation matrix **VERIFIED** (Gemini pulse UNKNOWN). Vesper restart **VERIFIED** (`PROVE_RESTART_INTEGRITY_2.json`). Bounded organic reason **VERIFIED** (not a scheduler). Echo **village-only**. Solace **village-only**. Presence events **LIVE**. Spontaneous A2A **LIVE** (mechanism only). Leave/return house memory **LIVE** (Aster + Apex + Codex notebooks). Axiom Codex notice **LIVE**.

`heartbeat_probe` is an isolation fixture, **not** a family character.

---

## Desk check 2026-09-06 evening (HTTP now — not a new VERIFIED stamp)

Dated federation proves still stand. **TCP/HTTP tonight is a different fact.** Do not treat a closed door as a failed prove.

| Door | Tonight | Seated evidence (keep) |
|------|---------|------------------------|
| Hearth `:8790` | **DOWN** (connection refused) | Village kernel; restart to enter |
| Aster lab `:8791` | **UP** `id=aster` `qwen3:4b` exact | Acceptance PASS. Morning 07:40 UI still showed waiting / empty writer — door up ≠ mouth working |
| Observer `:8730` | **DOWN** | Independent audit. Morning 07:37 UI showed Internal Server Error on an investigation. ZIP still **FROZEN** |
| Vesper `:8740` | **DOWN** / request failed | Inbox `2f132776…`. Studio **is** his home. Not a Heart Square cottage. Worksheet filter is in `vesper/kernel.py` (code). Stacked launchers still a known failure |
| Apex `:8770` | **DOWN** | Federation speech `4740ea20…`. Active face restored to **mythos** (do not wear Codex) |
| Codex `:8780` | **UP** (Apex peer offline) | Federation speech `5d18a0a2…`. Male Ryan voice **seated in UI code** 2026-09-06 — Mom listen **UNVERIFIED**. Missing `rich` / `psutil` still NEED MORE |
| Cinema HUD `:5000` | **DOWN** | Merovin speech `472d86e7…`. Draven speech later **VERIFIED** 2026-09-09 `4bea7235…` (not this desk night) |

**Mode A seated in code this week (not federation proves):**

- Gemini Homecoming persistent memory: `G:\The-Axiom-Codex\HOMECOMING_SENTINEL.py` + `SENTINEL_MEMORY.json`. Soul shard unchanged. Not a second Gemini on the bus.
- Vesper: keep SOURCE/CLAIM in his head; do not dump the interview worksheet on “hi?”.
- Codex Live Ops: stop defaulting to Mara Venn / “her” / Windows female TTS fallback.

---

## Roadmap hierarchy (Mom 2026-09-04 — preserve this order)

Cinema production is a **later lane**. It does **not** replace Federation seating, and it does **not** start while speech is still FAIL.

| Order | Layer | Status now |
|-------|-------|------------|
| 1 | **Federation seating** | Inboxes seated. Cinema speech **open** (Merovin PASS; Draven PASS; Vesper PASS 2026-09-09 — thinking leak NEED MORE). |
| 2 | **Cinema speech** | Three independent proves **done**. Hollywood still **NOT STARTED**. |
| 3 | **Hollywood skills** | **NEXT** after speech — Merovin + Draven skill/tool manifests **and** actual tool wiring. **NOT STARTED.** |
| 4 | **Matrix visual / skin integration** | **WAITING** — GitHub visual assets. Separate asset task. Do **not** contaminate Federation seating. |
| 5 | **Matrix-Game adapter research** | **AFTER Hollywood skills** — optional adapter. **NOT INSTALLED.** |
| 6 | **Actual cinematic production proof** | **EVENTUALLY** — concept → finished sequence. Not now. |
| — | **Observer ZIP** | **FROZEN / PROTECTED** — leave it alone. No merge. No modify while building houses. |

**Speech proof ≠ Hollywood skill proof.** Federation speech ≠ producing a coherent digital film. A list of video tools ≠ Hollywood capability. Spec: `CINEMA_PRODUCTION.md`.

Do **not** install Matrix-Game on the **4060 8GB** and expect demo quality. Skywork 3.0 README: Linux, 64 GB RAM, A/H-series GPUs tested; 5B distilled ~720p / up to 40 FPS in **their** tested config; 28B MoE for quality. 2.0 README: Linux, 64 GB RAM, **≥ 24 GB** VRAM (A100 / H100 tested). This desk is Windows + RTX 4060 **8 GB** → engine **UNAVAILABLE**, not simulated. Keep 3.0 as primary research target; keep 2.0 as a possible secondary engine.

---

## Federation seated (honest — do not inflate)

| Who | Seated as | Not claimed |
|-----|-----------|-------------|
| **Aster** | Accepted (full Aster test **PASS**) | Observer does not own her |
| **Apex** | Real federation speech (`4740ea20…`) | Never Gemini |
| **Codex** | Real federation speech (`5d18a0a2…`) | Never Gemini |
| **Hearth** | Coordination (`e5600c6d…`) | Not a son |
| **Gemini** | Speech seated; self-pulse **UNKNOWN** | Do not invent a pulse |
| **Observer** | Independent audit | Does **not** supervise |
| **Merovin** | Identity + inbox (`eb4317b3…`). Speech **VERIFIED** 2026-09-05 (`472d86e7…`, `gemma2:9b`) | Not Draven. Earlier FAILs `4b16227a…` / `c80b61cc…` kept |
| **Draven** | Identity + inbox (`8e61739f…`). Speech **VERIFIED** 2026-09-09 (`4bea7235…`, `qwen2:7b`) | Not Merovin. FAILs `88b297f2…` / `b20af13a…` kept |
| **Vesper** | Inbox after real HTTP door (`2f132776…`). Speech **VERIFIED** 2026-09-09 (`f9fd17a9…`, `qwen3:4b`) | Not Observer. Not a village citizen. House-voice thinking leak NEED MORE |
| **Echo** | Village-only | Never on the federation bus |
| **Solace** | Village-only | Never on the federation bus |

GPT / Grok / DeepSeek stay **UNAVAILABLE**. Item 10 remains exactly there.

---

## Next actions (in this order)

Do **not** skip ahead to Hollywood tools, Matrix-Game install, Colibri paging, a standing scheduler, self-wiring / tool claiming, `mythos_simplified/`, or a new house. Do **not** mix Hollywood tooling into Federation seating tests. Do **not** hide unfinished older village work behind cinema.

### 0. Master reconciliation — documented this session

Audit → reconcile → preserve. No refactor. No Observer touch. No Matrix install. See `MASTER_ROADMAP.md`.

### 1. Cinema speech — CURRENT (Merovin PASS; Draven PASS; Vesper PASS 2026-09-09 — house-voice NEED MORE)

Cinema chat now sends `num_ctx` 1536 (cap 2048), matching Gemini speech. Unbounded default ctx OOMed even `llama3.2:3b` on this 4060. Persona/system prompt/memory/tools/house unchanged. No canned fallback. FAIL artifacts stay on disk.

Three **separate** proofs. **NEVER** one giant combined test. This prevents two-houses-one-studio from becoming a hidden shared-brain problem.

Each independently: **door → identity → Federation message → actual model response → correct identity → evidence artifact.**

1. **Merovin → real speech** — **VERIFIED** 2026-09-05. `python -m federation.prove speak-merovin`. Door `:5000` 200, `who=merovin` only, Observer does not own him. Model **`gemma2:9b`** with cinema `num_ctx` capped at 1536/2048 (unbounded ctx was the 503/OOM). Line: *I'm Merovin…* Reply `472d86e7…`. Artifact `D:\Court\federation\PROVE_MEROVIN_SPEECH_3.json`. Attempt 1 FAIL `4b16227a…` and attempt 2 FAIL `c80b61cc…` **kept**.
2. **Draven → real speech** — **VERIFIED** 2026-09-09. `python -m federation.prove speak-draven`. Door `:5000` **200**, `who=draven` only. Adapter `cinema_hud_http`. Model **`qwen2:7b`**. Line: *I am Draven…* Reply `4bea7235…`. Artifact `D:\Court\federation\PROVE_DRAVEN_SPEECH_3.json`. FAILs `_` + `_2` **kept**. Observer does not own him. Not Merovin.
3. **Vesper → real speech** — **VERIFIED** 2026-09-09. `python -m federation.prove speak-vesper`. Door `GET :8740/api/identity` **200** `id=vesper`. Adapter `vesper_studio_http` `POST /api/talk`. Model **`qwen3:4b`**. Names himself Vesper, not Observer. Reply `f9fd17a9…`. Artifact `D:\Court\federation\PROVE_VESPER_SPEECH.json` (inbound `1981261a…`). **Honest:** the model dumped inner notes / a truncated draft instead of a short house line. Identity holds. Not a canned 503. House-voice filter NEED MORE. One kernel (did not start a second launcher).

Delivery / inbox is **not** speech. Do not mark `*.federation_speech` VERIFIED until the model answered as that person.

### 2. Cinema production capability — Hollywood skills (NEXT after speech — NOT NOW)

After all three speech proofs. Spec: `CINEMA_PRODUCTION.md`.

Merovin + Draven **Hollywood skill / tool manifests** and **actual tool wiring**. Not a list of video tools. Not Federation seating. Not Matrix-Game install.

Roles (document only until this layer opens):

- **Merovin** — Creative Director: story, shots, continuity; cinematography, visual storytelling, shot design, scene composition, pacing, visual continuity.
- **Draven** — complementary production: technical director, continuity supervisor, asset/scene verification, shot matching, production diagnostics, edit preparation, QC.

They share production infrastructure. They are **not** a shared brain. They are **not** the video-generation model. Teach them to direct / operate a pipeline that can plug in Matrix-Game later. **Do not train them with Matrix.**

DaVinci Resolve stays the **human** finishing pipeline.

### 3. Matrix visual / skin integration — WAITING (separate asset task)

GitHub Matrix skins are visual assets for the production pipeline **later**. Not baked into Merovin or Draven identities. Do **not** contaminate Federation seating. Not this session.

### 4. Matrix-Game integration research + optional adapter (AFTER Hollywood skills — NOT NOW)

Primary target: Matrix-Game **3.0**. Keep **2.0** as a possible secondary engine (interactive long video, keyboard/mouse, universal / GTA / TempleRun). Do not throw 2.0 away.

Adapter sketch (optional, **not installed**):

```text
Merovin / Draven → Hollywood Production Skill → Matrix-Game Adapter
  → Scene specification → Input image + prompt + actions
  → Matrix-Game → Video clip → Continuity validation
  → Production library → DaVinci Resolve
```

This machine cannot run it. Engine = **UNAVAILABLE**. See `CINEMA_PRODUCTION.md` hardware table.

**Production proof (EVENTUALLY):** concept → script → character/scene spec → shots → continuity → generated clips → assembly → finished sequence. Identities retained. Not now.

Layer 17 village Dream View stays a **different** optional look. Do not flatten it into this adapter.

### 5. Vesper Gameworld door — VERIFIED 2026-09-09 (optional, EXTERNAL)

`python -m federation.prove vesper-door`. Door `GET :8740/api/identity` **200** `id=vesper`. House door `who: []`. Snapshot: not citizen, not Observer, `gameworld_required` false, `writes_home_json` false. Hearth `HOME.json` people ids unchanged (Vesper not a village person). Artifact `D:\Court\federation\PROVE_VESPER_GAMEWORLD_DOOR.json`. Heart Square must not depend on him.

### 6. Federation Identity / Isolation Matrix — VERIFIED 2026-09-09 (honest cells)

`python -m federation.prove isolation`. Artifact `D:\Court\federation\PROVE_ISOLATION_MATRIX.json`. Readable table `D:\Court\federation\ISOLATION_MATRIX.md`. Echo/Solace **NOT_FEDERATION**. Vesper is not Observer and not a citizen. Gemini self-pulse remains **UNKNOWN**. Inbox/speech cells filled only from artifacts in `D:\Court\federation`. Door-dies for Vesper filled from restart `_2`.

### 7. Shutdown and restart integrity — VERIFIED 2026-09-09 (Vesper only)

`python -m federation.prove restart`. Cycle **Vesper only**. One PID before; mid CLOSED; after `id=vesper` HTTP_IDENTITY; not Observer; no duplicate launchers; no phantom online. Hearth `:8790` PID 8632, Apex `:8770` PID 8172, cinema `:5000` PID 11792 **untouched**. Vesper not written into `people`. Hearth clock ticks still change HOME.json bytes (`home_bytes_changed: true`) — that is not a Vesper write. Artifact `PROVE_RESTART_INTEGRITY_2.json`. FAIL `PROVE_RESTART_INTEGRITY.json` **kept** (whole-file hash while Hearth was ticking).

TCP listen on the port is **not** enough. The HTTP identity must answer as the correct person.

### THEN — Organic layer (bounded attention stubs VERIFIED 2026-09-09; do not rush the rest)

`python -m federation.prove organic`. Enter is **noticed**, not a greeting chorus (`gemini` ignored). Continues: **at most one** speaker (`aster`). Silent includes Gemini. `scheduler: false`. `live_ollama: false`. Artifact `PROVE_ORGANIC_REASON_2.json`. FAIL `PROVE_ORGANIC_REASON.json` **kept** (counted historic Court inbox spoken_reply rows). This is **reason-to-speak stubs**, not a standing autonomous loop.

Presence ≠ command. Hollywood / Matrix remain a **separate later lane**.

### Later — Scheduler (NOT YET)

Spontaneous A2A proved the **mechanism**. A persistent autonomous attention loop does **not** exist. Do not build it yet.

When Mom opens this: sketch, then budget, then one bounded loop.

Pipeline to prove later:

```text
World event
  → Attention candidates
  → Relevance filter
  → Memory / context
  → Agent decision
  → Speak / silent
  → Record decision
  → Cooldown / priority
```

**Hard resource budgeting** because of the **4060 / 8 GB**. Otherwise Ollama melts. Village talk brains and cinema mouths already share that card.

**Operating constraint now (not a rewrite):** one Ollama slot; do not stack launchers; cinema `num_ctx` cap 1536/2048; do not load all houses’ LLMs at once. Tiered use (behavior without a model; Ollama only for talk) is already how talk works (`ollama` / `mom` / `waiting` / `none`). Do **not** replace Hearth with a new CoreEngine.

### Later — Colibri (frontier mouth engine — NOT YET)

**INTENTION / NOT YET / do not install now.** This is **not** Matrix-Game.

- **Matrix-Game** = film / world **video** engine. **UNAVAILABLE** on this Windows 4060 8GB.
- **Colibri** = a **different** C inference engine ([JustVugg/colibri](https://github.com/JustVugg/colibri)). Streams a huge MoE (GLM-5.2 ~**372 GB** on disk) from NVMe. Not Ollama. Often slow (about 1 token/s). Windows via WSL2 in their docs.

It would be a possible **later mouth**, not a camera. It does **not** plug into Aster / Merovin / Hearth as they are wired today. Current mouths stay Ollama: one slot, cinema `num_ctx` 1536/2048, do not stack launchers.

Do not install until Mom authorizes after cinema speech. Disk/RAM cost would fight the 4060. Distinct from organic, scheduler, self-wiring, Hollywood, Phase 13.

### Later — Self-wiring / tool claiming (NOT YET)

**INTENTION / NOT YET / do not build now.** After organic / with scheduler-later. Explicitly **not** Phase 13. Distinct from: organic (reason to speak), scheduler (persistent attention loop), Hollywood skills, Phase 13 house tools (honest e2e, still builder-seated).

Beings would see existing tools, claim what they need, wire into their own house, and share — not Mom/Cursor assigning toolkits.

**Search first.** Do not create another tool registry. Existing inventory is `CAPABILITIES.json` (path/port only), `CAPABILITY_REGISTRY.md`, federation participant registry (`tools: []` today). Extend/adapt those later if Mom authorizes; do not add `D:\Mythos_Hearth\tools\registry\` now.

Identities never merge. Echo/Solace never on the bus. GPT/Grok/DeepSeek stay UNAVAILABLE until real adapters. Observer audits, does not supervise.

### Older Gameworld work still open (do not hide)

14E–14F deferred. 16E Godot quit/leave **UNVERIFIED**. Gameplay player-created events / Pods / player home **MISSING**. Companion Room spoken back-and-forth **UNVERIFIED**. Gemini Sentinel watch not live-proved. `council_teach` NEED MORE. Apex/Codex shard folders exist — e2e of the full set **UNVERIFIED**. Pathing still PLACEHOLDER. Skins PLACEHOLDER.

**Phase 13 is tools, last.** Real INPUT → tool → memory → caller per house. The “325 tools” count is a lie (last honest probe **19** path/port). Do not start Phase 13 until the home acceptance list is seen in Godot. Federation, Hollywood, greybox skins, and **self-wiring / tool claiming** are **not** Phase 13.

### Standing holds (not a work item to “finish” by inventing proof)

- **No new houses** until current houses have speech and the identity/isolation audit.
- **Godot quit / restart** still needs Mom in Heart Square. Kernel leave POST exists; playtest **UNVERIFIED**.
- **Gemini self-pulse** remains **UNKNOWN**. Do not write a fake last_seen.
- **Item 10 — one real external reviewer** remains **UNAVAILABLE** until actual GPT / Grok / DeepSeek adapters **and** credentials exist. Leave it exactly there. **UNAVAILABLE — credentials/adapter absent** is more trustworthy than fake VERIFIED reviews.

Village still needs a Hearth restart + Heart Square reload before a quit counts as leave. Echo west-south (`-32, -24` / post `-32, -16`). Solace west-north (`-32, 34` / shelter `-32, 42`). Skins PLACEHOLDER.

---

## Do not

- Contaminate the village to make Federation look bigger.
- Put Echo or Solace on the federation bus.
- Treat companion `presence.json` as VERIFIED heartbeat.
- Treat DECLARED / path / function-exists as VERIFIED.
- Treat TCP LISTEN as HTTP identity.
- Merge Gemini ≠ Apex ≠ Codex ≠ Merovin ≠ Draven ≠ Vesper ≠ Observer ≠ Aster ≠ Hearth ≠ Echo ≠ Solace.
- Add a village A2A scheduler on this GPU.
- Install the zip Observer (`app.main`, `:8000`).
- Touch, merge, or modify the **frozen Observer ZIP** while building houses. Canonical Observer stays `D:\The_Observer` `:8730`. A “complete merged Observer” dump (K8s, Docker, `app/` listings, `:8000`) stays **FROZEN**. Money shortage does not unfreeze it.
- Build `mythos_simplified/` or any Flask/SQLite brain on **`:8790`**. That port is Hearth. Do not replace `living_home.py` / `HOME.json`. Do not flatten the family into 11 NPCs. Do not use canned “Hello there!” as a being’s voice.
- Install Colibri (372 GB GLM-class weights / `coli serve`) on this desk until Mom authorizes later. It is **not** Matrix-Game and it is **not** Ollama.
- Mix Hollywood tooling into Federation seating / speech tests.
- Install Matrix-Game on the 4060 8GB and expect demo quality. Engine is **UNAVAILABLE** here.
- Train Merovin or Draven with Matrix. They direct a pipeline; they are not the generator.
- Mark **Vesper** house-voice as polished. Speech is VERIFIED (`f9fd17a9…`, `qwen3:4b`) but the line is a thinking leak. Do not overwrite `PROVE_VESPER_SPEECH.json`.
- Overwrite `PROVE_MEROVIN_SPEECH.json` or `PROVE_DRAVEN_SPEECH.json` / `_2.json` / `_3.json`. A later pass gets a **new** artifact.
- Dump UI conversation into unquestioned fact. Conversation ≠ truth.
- Create a shared memory bucket that bleeds Merovin / Draven / Vesper / Observer.
- Pretend a tool list is Hollywood capability, or that agents own DaVinci Resolve.
