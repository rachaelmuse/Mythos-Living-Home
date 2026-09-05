# Living Home — where we are

Updated **2026-09-04**. Evidence only. Mom accepted the architecture assessment as **the plan**. This file is the operator surface.

Kernel: `D:\Mythos_Hearth\living_home.py`  
House UI: **http://127.0.0.1:8790/house.html**  
Aster lab: **http://127.0.0.1:8791/ui/**  
Cinema HUD: **http://127.0.0.1:5000/**  
Observer: **http://127.0.0.1:8730/**  
Dashboard: **http://127.0.0.1:8790/dashboard**  
Enter: Desktop **Mythos Living Home - Enter**

Law: `FEDERATION_DIRECTIVE.md` · Map: `FEDERATION_RECONCILIATION.md` · Wiring: `FEDERATION_WIRING.md` · Tracker: `FAMILY_PHASES.md` · Status: `STATUS.md` · Production spec: `CINEMA_PRODUCTION.md`

Baseline tag `living-home-baseline-001` — do not rewrite.

---

## Assessment (keep this language)

**Foundation is STRONG. Federation is USABLE. Village is FUNCTIONAL** and must not be contaminated to make Federation look bigger.

**Cinema is SEATED, NOT FINISHED.** Organic autonomy is the **NEXT MAJOR PHASE** — do not rush. Godot lifecycle proof still has one small gap (real quit/restart). Gemini self-pulse remains honest **UNKNOWN**. External independent reviewers remain **UNAVAILABLE** — do not fabricate. **Do not add more houses** until current houses have speech and an identity/isolation audit.

Not one giant AI pretending to be nine people. **Nine distinct doors → nine identities → separate responsibilities → controlled communication → observable failures.**

The next interesting question is not how many AIs — it is what happens when we stop telling them when to act and give memory, context, resources, and freedom to decide whether acting is worth doing.

**Milestone to keep:** TCP listen ≠ HTTP identity answering as the correct person.

---

## CURRENT PHASE

**Village:** **18B LIVE**. **16E LIVE**. Echo + Solace seated as **village kin** (not federation). Leave POST is in kernel/Godot; **restart Hearth** + reload Heart Square before a quit counts as leave. Godot walk and Godot leave remain **UNVERIFIED** until Mom does them. Village must stay FUNCTIONAL — do not flatten it into Federation.

**Federation:** **USABLE**, not finished. Aster Acceptance **PASS**. Apex + Codex **real speech**. Hearth **coordinate**. Gemini **seated** with honest pulse **UNKNOWN**. Observer **independent audit**. Merovin **seated identity** (inbox, not speech). Draven **seated identity** (inbox, not speech). Vesper **seated** after real HTTP door repaired (inbox, not speech). Echo **village-only**. Solace **village-only**. Presence events **LIVE**. Spontaneous A2A **LIVE** (mechanism only). Leave/return house memory **LIVE** (Aster + Apex + Codex notebooks). Axiom Codex notice **LIVE**.

`heartbeat_probe` is an isolation fixture, **not** a family character.

---

## Roadmap hierarchy (Mom 2026-09-04 — preserve this order)

Cinema production is a **later lane**. It does **not** replace Federation seating, and it does **not** start while speech is still FAIL.

| Order | Layer | Status now |
|-------|-------|------------|
| 1 | **Federation seating** | Inboxes seated. Speech still open. |
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
| **Merovin** | Identity + inbox (`eb4317b3…`) | Speech **FAILED** 2026-09-04 (`4b16227a…`) — door up, Ollama 503. Not Draven |
| **Draven** | Identity + inbox (`8e61739f…`) | Speech **not** VERIFIED. Not Merovin |
| **Vesper** | Inbox after real HTTP door (`2f132776…`) | Speech **not** VERIFIED. Not Observer. Not a village citizen |
| **Echo** | Village-only | Never on the federation bus |
| **Solace** | Village-only | Never on the federation bus |

GPT / Grok / DeepSeek stay **UNAVAILABLE**. Item 10 remains exactly there.

---

## Next actions (in this order)

Do **not** skip ahead to Hollywood tools, Matrix-Game install, organic autonomy, a scheduler, or a new house. Do **not** mix Hollywood tooling into Federation seating tests.

### 1. Cinema speech — CURRENT (obvious immediate next)

Three **separate** proofs. **NEVER** one giant combined test. This prevents two-houses-one-studio from becoming a hidden shared-brain problem.

Each independently: **door → identity → Federation message → actual model response → correct identity → evidence artifact.**

1. **Merovin → real speech** — **FAILED** 2026-09-04 (`python -m federation.prove speak-merovin`). Cinema HUD `:5000` **200**, `POST /api/chat` `who=merovin` only (no Draven mouth). Ollama **503** (`gemma2:9b` / cinema picker vs warm `llama3.2:3b` on the 4060). `merovin_spoke: false`. Evidence `D:\Court\federation\PROVE_MEROVIN_SPEECH.json` (`4b16227a…`). **STOP here.** Do not run Draven or Vesper speech until Merovin gets a real model reply. **FAIL stays FAIL.** Do not mark speech VERIFIED.
2. **Draven → real speech**. Same HUD `:5000`, different house. Not Merovin’s mouth. **NOT RUN** — Merovin speech failed.
3. **Vesper → real speech**. Own studio `:8740`. Not Observer. **NOT RUN** — sequence stopped.

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
- Mark cinema speech VERIFIED. Last prove **FAILED** (`4b16227a…`).
- Pretend a tool list is Hollywood capability, or that agents own DaVinci Resolve.
