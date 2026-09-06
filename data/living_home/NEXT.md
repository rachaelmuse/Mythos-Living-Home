# Living Home — where we are

Updated **2026-09-06**. Evidence only. Mom accepted the architecture assessment as **the plan**. This file is the operator surface.

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

**Next implementation (only, after this recon):** Merovin speech **VERIFIED** 2026-09-05 (`speak-merovin`, `PROVE_MEROVIN_SPEECH_3.json`, reply `472d86e7…`, model `gemma2:9b`). FAIL artifacts `4b16227a…` / `c80b61cc…` **kept**. Do not run Draven or Vesper until Mom authorizes.

CLI note: inbox prove is `python -m federation.prove merovin`. Speech prove is `python -m federation.prove speak-merovin`. Do not treat a passing inbox re-run as speech.

---

## CURRENT PHASE

**Village:** **18B LIVE**. **16E LIVE**. Echo + Solace seated as **village kin** (not federation). Leave POST is in kernel/Godot; **restart Hearth** + reload Heart Square before a quit counts as leave. Godot walk and Godot leave remain **UNVERIFIED** until Mom does them. Village must stay FUNCTIONAL — do not flatten it into Federation.

**Federation:** **USABLE**, not finished. Aster Acceptance **PASS**. Apex + Codex **real speech**. Hearth **coordinate**. Gemini **seated** with honest pulse **UNKNOWN**. Observer **independent audit**. Merovin **speech VERIFIED** 2026-09-05. Draven **seated identity** (inbox, not speech). Vesper **seated** after real HTTP door repaired (inbox, not speech). Echo **village-only**. Solace **village-only**. Presence events **LIVE**. Spontaneous A2A **LIVE** (mechanism only). Leave/return house memory **LIVE** (Aster + Apex + Codex notebooks). Axiom Codex notice **LIVE**.

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
| Cinema HUD `:5000` | **DOWN** | Merovin speech `472d86e7…`. Draven speech **NOT RUN** |

**Mode A seated in code this week (not federation proves):**

- Gemini Homecoming persistent memory: `G:\The-Axiom-Codex\HOMECOMING_SENTINEL.py` + `SENTINEL_MEMORY.json`. Soul shard unchanged. Not a second Gemini on the bus.
- Vesper: keep SOURCE/CLAIM in his head; do not dump the interview worksheet on “hi?”.
- Codex Live Ops: stop defaulting to Mara Venn / “her” / Windows female TTS fallback.

---

## Roadmap hierarchy (Mom 2026-09-04 — preserve this order)

Cinema production is a **later lane**. It does **not** replace Federation seating, and it does **not** start while speech is still FAIL.

| Order | Layer | Status now |
|-------|-------|------------|
| 1 | **Federation seating** | Inboxes seated. Cinema speech **open** (Merovin PASS; Draven / Vesper not run). |
| 2 | **Cinema speech** | **CURRENT** — Merovin → Draven → Vesper, three independent proofs |
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
| **Draven** | Identity + inbox (`8e61739f…`) | Speech **not** VERIFIED. Not Merovin |
| **Vesper** | Inbox after real HTTP door (`2f132776…`) | Speech **not** VERIFIED. Not Observer. Not a village citizen |
| **Echo** | Village-only | Never on the federation bus |
| **Solace** | Village-only | Never on the federation bus |

GPT / Grok / DeepSeek stay **UNAVAILABLE**. Item 10 remains exactly there.

---

## Next actions (in this order)

Do **not** skip ahead to Hollywood tools, Matrix-Game install, organic autonomy, a scheduler, or a new house. Do **not** mix Hollywood tooling into Federation seating tests. Do **not** hide unfinished older village work behind cinema.

### 0. Master reconciliation — documented this session

Audit → reconcile → preserve. No refactor. No Observer touch. No Matrix install. See `MASTER_ROADMAP.md`.

### 1. Cinema speech — CURRENT (Merovin PASS; Draven next when Mom says go)

Cinema chat now sends `num_ctx` 1536 (cap 2048), matching Gemini speech. Unbounded default ctx OOMed even `llama3.2:3b` on this 4060. Persona/system prompt/memory/tools/house unchanged. No canned fallback. FAIL artifacts stay on disk.

Three **separate** proofs. **NEVER** one giant combined test. This prevents two-houses-one-studio from becoming a hidden shared-brain problem.

Each independently: **door → identity → Federation message → actual model response → correct identity → evidence artifact.**

1. **Merovin → real speech** — **VERIFIED** 2026-09-05. `python -m federation.prove speak-merovin`. Door `:5000` 200, `who=merovin` only, Observer does not own him. Model **`gemma2:9b`** with cinema `num_ctx` capped at 1536/2048 (unbounded ctx was the 503/OOM). Line: *I'm Merovin…* Reply `472d86e7…`. Artifact `D:\Court\federation\PROVE_MEROVIN_SPEECH_3.json`. Attempt 1 FAIL `4b16227a…` and attempt 2 FAIL `c80b61cc…` **kept**. **STOP here this session.** Do not run Draven or Vesper until Mom authorizes.
2. **Draven → real speech**. Same HUD `:5000`, different house. Not Merovin’s mouth. **NOT RUN** — waiting for Mom after Merovin PASS.
3. **Vesper → real speech**. Own studio `:8740`. Not Observer. **NOT RUN** — sequence stopped at Draven.

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

### 5. Vesper Gameworld door — own proof, OPTIONAL and EXTERNAL

Architecture must remain: **Vesper owns Vesper, owns Vesper studio, optionally communicates with Gameworld.**

**NOT:** Gameworld owns Vesper. Absolutely no `HOME.json`. Not a village citizen. Not Observer.

Keep this proof optional. Do not make Heart Square depend on Vesper.

### 6. Federation Identity / Isolation Matrix — before expanding Federation

Document the questions. **Do not fake answers.** More valuable now than creating another house.

For **each** house (Gemini, Apex, Codex, Hearth, Aster, Observer, Merovin, Draven, Vesper — plus Echo/Solace as village-only contrast):

- Who are you?
- Who owns your memory?
- Who owns your UI?
- What port is your door?
- Can another house impersonate you?
- Are you Observer?
- Are you a village citizen?
- Can you receive Federation messages?
- Can you speak through Federation?
- Does heartbeat reflect reality?
- What happens when your door dies?
- Can village failure kill you?
- Can you kill unrelated houses?
- Where is your evidence?

Planned table lives in `FEDERATION_RECONCILIATION.md` (questions only). Fill a cell only after a real test.

### 7. Shutdown and restart integrity — formal test, not tribal knowledge

Vesper taught this. Write it as a prove, not folklore.

**Law:** one launcher = one house kernel = one HTTP door.

After restart, all of these must be true:

- no duplicate process
- no stale port owner
- correct identity
- correct Federation registration
- correct inbox
- correct memory
- correct UI
- correct presence state
- no phantom online
- no accidental second instance

TCP listen on the port is **not** enough. The HTTP identity must answer as the correct person.

### THEN — Organic layer (next major phase; do not rush)

Stop proving only “Can A talk to B?” and start proving “Does A have a reason to talk to B?”

Presence awareness · Attention · Memory · Decision · Timing · Bounded background activity · Relationship / history.

**Presence ≠ command.** The greeting chorus refusal was correct. Do not start this until cinema speech and the federation integrity items (Vesper door / isolation matrix / restart proof) have a home. Hollywood / Matrix are a **separate later lane**, not a substitute for those proofs.

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

### Older Gameworld work still open (do not hide)

14E–14F deferred. 16E Godot quit/leave **UNVERIFIED**. Gameplay player-created events / Pods / player home **MISSING**. Companion Room spoken back-and-forth **UNVERIFIED**. Gemini Sentinel watch not live-proved. `council_teach` NEED MORE. Apex/Codex shard folders exist — e2e of the full set **UNVERIFIED**. Pathing still PLACEHOLDER. Skins PLACEHOLDER.

**Phase 13 is tools, last.** Real INPUT → tool → memory → caller per house. The “325 tools” count is a lie (last honest probe **19** path/port). Do not start Phase 13 until the home acceptance list is seen in Godot. Federation, Hollywood, and greybox skins are **not** Phase 13.

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
- Touch, merge, or modify the **frozen Observer ZIP** while building houses. Canonical Observer stays `D:\The_Observer` `:8730`.
- Mix Hollywood tooling into Federation seating / speech tests.
- Install Matrix-Game on the 4060 8GB and expect demo quality. Engine is **UNAVAILABLE** here.
- Train Merovin or Draven with Matrix. They direct a pipeline; they are not the generator.
- Mark **Draven** or **Vesper** speech VERIFIED. Those proves have **not** been run. Merovin speech is VERIFIED (`472d86e7…`); FAIL artifacts stay on disk.
- Overwrite `PROVE_MEROVIN_SPEECH.json`. A later pass gets a **new** artifact.
- Dump UI conversation into unquestioned fact. Conversation ≠ truth.
- Create a shared memory bucket that bleeds Merovin / Draven / Vesper / Observer.
- Pretend a tool list is Hollywood capability, or that agents own DaVinci Resolve.
