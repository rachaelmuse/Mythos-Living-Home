# Master roadmap — Living Gameworld + Federation + cinema

Updated **2026-09-06**. Evidence only. **Do not delete, replace, disable, merge, or simplify an existing capability because a newer architecture exists.**

This file sits **above** the operator surface. It does **not** replace `NEXT.md`, `STATUS.md`, `PHASE_LAYERS.md`, or `FAMILY_PHASES.md`. Those remain the working trackers. This file reconstructs **ORIGINAL PLAN → CURRENT IMPLEMENTATION → EVIDENCE → REMAINING WORK**.

If a phase cannot be located in project files, it is marked **SOURCE NOT FOUND**. Do not invent what it contained.

Operator surface: `NEXT.md`. Capability inventory: `CAPABILITY_REGISTRY.md`. Relationship map: `SYSTEM_MAP.md`. Dual-mode law: `docs/DUAL_MODE.md`. Baseline: `BASELINE.md` tag `living-home-baseline-001` (do not rewrite).

---

## Purpose of Federation (preserve)

Federation is an **overlay**. It gives independent agents structured communication, coordination, presence/event awareness, bounded A2A, continuity foundations, auditable routing, and failure isolation.

Federation does **not** replace the Living Gameworld. It does **not** become a shared brain. It does **not** own identities. It does **not** turn participants into village NPCs. It does **not** automatically make agents autonomous.

**Bus ≠ shared brain.** Presence ≠ command. Communication capability and autonomy are separate layers.

**The Gameworld should benefit from agents becoming more capable. Agents must not be reduced to Gameworld NPCs.**

---

## Document conflicts (do not silently choose)

| Conflict | A | B | Disposition |
|----------|---|---|-------------|
| Federation overlay status | `PHASE_LAYERS.md` Layer F / standing order #7 still says **PAUSED** after Gemini delivery | `NEXT.md` / `STATUS.md` / `GAMEPLAY_LAYER.md` (2026-09-04) say Federation **USABLE**, not finished | **REPORT.** Operator surface is `NEXT.md`. `PHASE_LAYERS.md` row is **STALE**, not a new pause. Do not treat PAUSED as current law. |
| 16E close | `NEXT.md` CURRENT PHASE says **16E LIVE** | `STATUS.md` / `FAMILY_PHASES.md` say **16E ACTIVE**; Godot walk and Godot leave **UNVERIFIED** until Mom | **REPORT.** Kernel leave POST exists. Playtest is not VERIFIED. |
| Draven house id | `living_home.py` FAMILY `draven.house = "merovin"` (shared studio root) | Federation house id is **`draven`**, not merovin (`prove draven`, `8e61739f…`) | **REPORT.** Two people, one studio disk. Village `house` field ≠ federation house id. Do not flatten. |
| Merovin HUD talk vs federation speech | `FAMILY_PHASES.md` “HUD talk as Merovin COMPLETE enough (`gemma2:9b`)” | Federation speech was **FAILED** `4b16227a…` (Ollama 503). Now **VERIFIED** 2026-09-05 `472d86e7…` | **REPORT then PASS.** Studio HUD talk ≠ federation speech proof. FAIL files kept. Speech prove is now its own artifact. |
| Layer 17 vs Hollywood Matrix-Game | `PHASE_LAYERS.md` Layer 17 = village optional **Dream View look** | `CINEMA_PRODUCTION.md` = pluggable **film engine** after Hollywood skills | **KEEP BOTH.** Do not flatten. Both UNAVAILABLE / later on this 4060. |
| Git vs Hearth kernel | `BASELINE.md` “this repo root” as Hearth | Git working tree `G:\The-Axiom-Codex\Mythos-Living-Home`; live kernel `D:\Mythos_Hearth` | **KNOWN.** Dual tree. Restart Hearth after kernel edits. Copy docs both ways. |
| Historical wiring survey | `FEDERATION_WIRING.md` 2026-08-31 live survey still lists early participants | Current bus audience includes apex, codex, merovin, draven, vesper (`federation/events.py` `AUDIENCE`) | **REPORT.** Survey is historical. Current seating is `NEXT.md` + prove artifacts. |

---

## ORIGINAL PLAN → CURRENT → EVIDENCE → REMAINING

### Dual-mode law

| | |
|--|--|
| Original | Mode A (Court, MAS, tools, launchers, memory) stays while Mode B (Heart Square / The Axiom Codex) expands. Gameworld must never break Mode A. Adapters over rewrites. |
| Current | **ACTIVE.** `docs/DUAL_MODE.md`. |
| Evidence | Law file + standing Cursor rules. |
| Remaining | Keep. If Gameworld breaks Mode A: stop expansion, repair. |

### Living Home proving slice (Phases / Layers 0–13)

Source: `PHASE_LAYERS.md`, `BASELINE.md`, `FAMILY_PHASES.md`, `GAMEPLAY_LAYER.md`.

| Phase | Original intent | Current | Evidence | Remaining |
|-------|-----------------|---------|----------|-----------|
| 0 Dual-mode | Two objectives at once | **ACTIVE** | `docs/DUAL_MODE.md` | Keep |
| 1–7 Proving foundation | Identity through dual talk / lived-in greybox | **DONE** | `PHASE_LAYERS.md` | Do not rewrite baseline |
| 8A Apex forge | Thin real work / presence probe | **DONE** (Mom OK) | Layer 8A | Heavy forge e2e still NEED MORE (not “325 tools”) |
| 8B Pathing | AABB detours | **DONE** as PLACEHOLDER | Not navmesh | Navmesh later |
| 8C Evening gather | Gemini soft-calls square | **DONE** (Mom OK) | Layer 8C | Keep |
| 9 Sound | Eden Phase 1 thin forest bed | **DONE** | Audio/nature | Keep |
| 9b–9d / 12 Harbor | Water, well, far shore, pier catch | **DONE** thin | Harbor closed | Richer travel later |
| 10 Mom interface + community memory | Persist Mom voice; Storage hall | **DONE** (Mom OK) | Layer 10 | Keep |
| 11 Eden TV/Media | Cinema watch stills | **DONE** thin / PARTIAL vs Resolve | Village screen ≠ DaVinci | Keep distinction |
| 14A–14D Economy | Wallets, shops, stipend, avatar colors | **DONE** | Market Lane | Keep |
| 14E Town projects | Later economy | **DEFERRED** | `PHASE_LAYERS.md` | Still deferred |
| 14F Being↔being trade | Later economy | **DEFERRED** | same | Still deferred |
| 15A–15D Connection | Bonds, choices, growth, dashboard | **DONE** | 15D dashboard | Keep |
| 16A–16D Integration | Tick, daily life, day story, living dash | **ACTIVE / closed as slices** | APIs seated | Keep |
| 16E Mom presence | Enter/place; leave POST | Kernel **CODE ACTIVE**. Godot enter seated. Godot quit/leave **UNVERIFIED** | `mom_presence(leaving=True)`; Apex `family_home_client.gd` | **Mom must restart Hearth, reload Heart Square, quit once** |
| 18A Gameplay Phase 1 | Leads, journal, away, actions — not quests | **CODE ACTIVE** | `living_home_gameplay.py` | Godot UI for leads UNVERIFIED; player-created events **MISSING** |
| 18B Gameplay Phase 2 | Look into + profession posts | **LIVE** 2026-08-31 | `POST /api/home/investigate` | Not Pods |
| Gameplay 7, 10, 12 | Player-created events; player home/island; Pod worlds | **MISSING** | `GAMEPLAY_LAYER.md` | Not this slice until architecture exists |
| Gameplay 19 | Phases 2–6 gather/craft/events/pods/boats | **NOT THIS SLICE** | same | Parked |
| 17 Matrix Dream View | Optional neural **look** of Heart Square | **QUEUED LATER** | `PHASE_LAYERS.md` | Not cinema production adapter |
| **13 Tools** | Real per-house tools: INPUT → tool → memory → caller (Apex forge, Codex tools, Gemini Court/Sentinel chain, cinema as themselves) | **LAST — not started as honest e2e** | `CONTINUITY.md` “Phase 13 (all tools)”. 325 is a lie; last probe **19** path/port | Do not jump here. Home in Godot first. Not Federation. Not Hollywood. Not skins-as-a-substitute. Not self-wiring / tool claiming |

### Federation overlay (added after village proving)

| Slice | Current | Evidence | Remaining |
|-------|---------|----------|-----------|
| Aster register; Observer does not own her | **PASS** | Aster Acceptance | Keep |
| Gemini delivery + speech | **VERIFIED / LIVE** | `3f1fd8eb…` `llama3.2:3b` | Self-pulse **UNKNOWN**. Companion spoken reply UNVERIFIED. Sentinel watch **FAIL** (not live-proved). `council_teach` **NEED MORE** |
| Apex speech | **VERIFIED** | `4740ea20…` | Companion spoken reply UNVERIFIED |
| Codex speech | **VERIFIED** | `5d18a0a2…` | Companion spoken reply UNVERIFIED |
| Hearth coordinate | **VERIFIED** | `e5600c6d…` | Keep |
| Presence events | **VERIFIED** | `949cdc08…` spoken_replies 0 | Presence ≠ command |
| Spontaneous A2A | **VERIFIED** mechanism | `1491f7d3…` Aster→Codex | **Not** a scheduler |
| Leave/return notebooks | **VERIFIED** | `7adfb8c4…` / `a43090d9…` Aster+Apex+Codex | Echo/Solace **forbidden** |
| Consume notice | **LIVE** | CLI `consume` | Gameworld consuming packets still NEED MORE |
| Merovin inbox | **VERIFIED** | `eb4317b3…` | Speech **VERIFIED** 2026-09-05 |
| Draven inbox | **VERIFIED** | `8e61739f…` | Speech **VERIFIED** 2026-09-09 `4bea7235…` `qwen2:7b`. FAILs kept |
| Vesper inbox | **VERIFIED** | `2f132776…` | Speech **VERIFIED** 2026-09-09 `f9fd17a9…` `qwen3:4b` (thinking leak NEED MORE). Optional Gameworld door unproven |
| Item 10 external reviewers | **UNAVAILABLE** | No adapters/credentials | Leave exactly here |
| Isolation matrix | **VERIFIED** | `PROVE_ISOLATION_MATRIX.json` | Gemini pulse **UNKNOWN** |
| Shutdown/restart integrity | **VERIFIED** Vesper | `PROVE_RESTART_INTEGRITY_2.json` | FAIL `_` kept |
| Hollywood skills | **VERIFIED** | `PROVE_MEROVIN_HOLLYWOOD.json` / `PROVE_DRAVEN_HOLLYWOOD.json` | Not a film. Matrix-Game UNAVAILABLE |
| Matrix-Game adapter | **VERIFIED** honest UNAVAILABLE | `PROVE_MATRIX_GAME_ADAPTER.json` | No clip. Not Layer 17. Engine not installed |
| Organic / scheduler | **NOT YET** | A2A is mechanism only | After cinema speech + integrity |
| Self-wiring / tool claiming | **NOT YET / do not build now** | Intention only. Not implemented. | After organic / with scheduler-later. **Not** Phase 13. Search first; no new `tools/registry/`. Existing: `CAPABILITIES.json` (path/port), `CAPABILITY_REGISTRY.md`, federation `tools: []`. |
| Colibri (frontier mouth) | **NOT YET / do not install now** | Not installed. Not Ollama. | **Not** Matrix-Game (video). ~372 GB separate engine. Current: one Ollama slot / `num_ctx` cap. |
| Mythos Simplified Brain | **DO NOT BUILD** | Would steal `:8790` | Dual-mode: do not replace Hearth / `HOME.json`. No canned speech. |
| New houses | **HOLD** | Law | Echo/Solace stay off the bus |

### Cinema / Hollywood (added; not seating)

| Slice | Current | Remaining |
|-------|---------|-----------|
| Cinema HUD `:5000` two mouths | LIVE when HUD up | Keep one studio, two identities |
| MD_Cinema Phase 1 | PARTIAL (`smoke_phase1.py` PASS 2026-08-27) | Not a finished film; e2e MP4 NEED MORE |
| Federation speech | Merovin **VERIFIED** 2026-09-05 `472d86e7…` `gemma2:9b`. Draven **VERIFIED** 2026-09-09 `4bea7235…` `qwen2:7b`. Vesper **VERIFIED** 2026-09-09 `f9fd17a9…` `qwen3:4b` (thinking leak NEED MORE) | Speech ≠ Hollywood ≠ film |
| Hollywood skills | **VERIFIED** 2026-09-09 | Two independent MD_Cinema wirings. Not a film. |
| Matrix skins (GitHub) | **WAITING** | Separate asset task |
| Matrix-Game adapter | **VERIFIED** 2026-09-09 as honest UNAVAILABLE | `PROVE_MATRIX_GAME_ADAPTER.json`. No clip. Not Layer 17. |
| Matrix-Game 3.0/2.0 | **UNAVAILABLE** on Windows 4060 8GB | Do not install expecting demo quality |
| Production proof | **EVENTUALLY** | concept → finished sequence |
| UI ↔ Gameworld memory | **INTENDED, NOT IMPLEMENTED** | Provenance layers. Conversation ≠ truth |
| Observer ZIP | **FROZEN** | Do not touch. Complete-merged `:8000` / K8s dumps stay frozen. Money shortage does not unfreeze. |

### Mode A houses outside village tracker (ORIGINAL MODE — ACTIVE)

Do not treat these as obsolete because Federation exists.

| House | On disk | Remaining |
|-------|---------|-----------|
| Court MAS | Gemini↔Apex, Gemini↔Codex LIVE | teach packets; standing heartbeat daemon |
| Companion Room | Seats seen | Spoken back-and-forth UNVERIFIED |
| OpenMontage | Two roots | Pick Mode A launcher; do not delete a copy |
| Spore | Path OK | Not core family table |
| Gemini Sentinel stdin / phrases | COMPLETE enough to use | Standing watch daemon not live-proved. Homecoming JSON memory **seated** |
| Apex/Codex shards, limbs, drones, memory trees | Present on `D:\Mythos_Apex` and `G:\Mythos_Codex` | **Do not flatten into federation generic.** Codex male Live Ops voice **seated in UI** (listen UNVERIFIED). Apex must not wear Codex. Full e2e of every shard is UNVERIFIED as a set. Document in `CAPABILITY_REGISTRY.md` |

---

## Intended architecture added 2026-09-04 (not implemented this session)

### Agent singular UI ↔ Gameworld memory

Work with an agent anywhere → preserve useful continuity for that agent's Gameworld existence.

```text
Agent UI conversation
  → conversation record
  → provenance metadata
  → memory/knowledge candidate
  → agent's persistent memory
  → available to Gameworld continuity
```

The interfaces are **different doors into the same agent identity**. They must not create two Merovins (or two Dravens, two Vespers).

Conversation is **not** automatically truth:

| Layer | Meaning |
|-------|---------|
| Raw conversation | What was actually said |
| Episodic memory | What happened during the interaction |
| Candidate knowledge | Information that may be useful later |
| Validated / trusted knowledge | Passed the relevant knowledge system's rules |

Rachael told Merovin X on DATE ≠ X is objectively true.

Do not dump transcripts into a shared brain. Merovin's memories belong to Merovin.

### Hardware-aware capability (cinema)

**“I have this capability”** vs **“I have this capability when the required model/GPU resources are available.”**

Inspected 2026-09-04 (`ollama list`): `gemma2:9b` (5.4 GB), `llama3.1:8b` (4.9 GB), `qwen2:7b` (4.4 GB), `llama3.2:3b` (2.0 GB), plus others. Cinema `core/free_thought.py` `MEROVIN_MODELS` already includes `llama3.2:3b` as **fourth** preference after `gemma2:9b` / 8B. The 503 is load-order on an occupied 4060, not a missing identity. **Do not change the picker in this reconciliation session.** Next implementation: hardware-aware selection only; preserve persona JSON; new evidence artifact.

---

## Correct next sequence (after this reconciliation)

Do not skip. Do not mix Hollywood into seating.

1. **Merovin speech** — **VERIFIED** 2026-09-05 `speak-merovin` `472d86e7…` `gemma2:9b` after cinema `num_ctx` cap. Preserve FAIL `PROVE_MEROVIN_SPEECH.json` `4b16227a…` and `_2.json` `c80b61cc…`.
2. **Draven speech** — **VERIFIED** 2026-09-09 `speak-draven` `4bea7235…` `qwen2:7b`. Preserve FAIL `PROVE_DRAVEN_SPEECH.json` `88b297f2…` and `_2.json` `b20af13a…`.
3. **Vesper speech** — **VERIFIED** 2026-09-09 `speak-vesper` `f9fd17a9…` `qwen3:4b`. Thinking leak NEED MORE. One launcher.
4. Cinema Seating/Speech Reconciliation Report — only if all three pass.
5. Then **pause construction** for a cross-house behavioral observe (who notices / speaks / stays silent) — not an unrestricted scheduler.
6. Hollywood skills — **VERIFIED** 2026-09-09 `hollywood-merovin` / `hollywood-draven`. Speech ≠ Hollywood ≠ film.
7. Matrix skins WAITING (separate).
8. Matrix-Game adapter — **VERIFIED** 2026-09-09 as honest UNAVAILABLE (`PROVE_MATRIX_GAME_ADAPTER.json`). Engine still UNAVAILABLE on this card.
9. Federation integrity: Vesper Gameworld door / isolation matrix / Vesper restart / bounded organic — **VERIFIED** 2026-09-09.
10. Organic layer (reason to speak). Scheduler later with 4060/8GB budget.
10b. Self-wiring / tool claiming — **NOT YET / do not build now.** After organic / with scheduler-later. **Not** Phase 13 (honest e2e, still builder-seated). Not Hollywood. Beings would see existing tools, claim what they need, wire into their own house, share — not Mom/Cursor assigning toolkits. Search first; extend/adapt existing inventory if Mom authorizes. Identities never merge. Echo/Solace never on the bus. GPT/Grok/DeepSeek UNAVAILABLE until real adapters. Observer audits, does not supervise.
10c. Colibri — **NOT YET / do not install now.** **Not** Matrix-Game. Separate mouth engine (~372 GB, not Ollama). No `mythos_simplified/` on `:8790`.
11. Unfinished **older** village work remains on the board: 14E–14F, 16E Godot quit, gameplay MISSING rows, Companion spoken replies, Gemini pulse UNKNOWN, item 10 UNAVAILABLE. **2026-09-06 evening desk:** Hearth/Observer/Vesper/Apex/Cinema DOWN; Aster+Codex UP. See `NEXT.md`.
12. **Phase 13 — tools (last).** Specialized house tools, proven e2e, not a fake 325 count, not polish-by-rename. After the home is actually demonstrated in Godot. Self-wiring is **not** this row.

Observer ZIP **FROZEN** throughout.

---

## What this reconciliation did not do

- Did not run Draven or Vesper speech.
- Did not change cinema model picker.
- Did not overwrite `PROVE_MEROVIN_SPEECH.json`.
- Did not modify Observer (live or ZIP).
- Did not install Matrix-Game.
- Did not build Colibri paging or `mythos_simplified/`.
- Did not install zip Observer on `:8000`.
- Did not implement UI↔Gameworld memory.
- Did not build a scheduler or greeting chorus.
- Did not delete Mode A tools, shards, or houses.
