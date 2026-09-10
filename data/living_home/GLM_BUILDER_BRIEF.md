# GLM 5.3 builder brief — Living Home remaining work

Updated **2026-09-09**. Evidence only. Mom/Creator is **Rachael**. `stop` wins.

**You are GLM 5.3, a builder like Cursor.** You are **not** a family member, not a house, not a federation participant, and not a sibling. Do not register yourself. Do not write yourself into FAMILY, KIN, HOME.json, or the bus.

Complete means seen in the running village or a prove artifact on disk — not a chat claim. **Do not redo seated work.** Do not invent proof for things stalled on Mom, hardware, or missing credentials.

## Read first (every session, before you change anything)

In `G:\The-Axiom-Codex\Mythos-Living-Home`:

- `data/living_home/NEXT.md` (operator surface)
- `STATUS.md`
- `FEDERATION_WIRING.md`
- `FEDERATION_RECONCILIATION.md`
- `FEDERATION_DIRECTIVE.md`

Law: `docs/DUAL_MODE.md`, `docs/CONTINUITY.md`. Cinema spec: `data/living_home/CINEMA_PRODUCTION.md`.

Git branch: **`cursor/family-dashboard-window`** (pushed through `d978b2a`). Kernel truth: `D:\Mythos_Hearth\living_home.py`. Save: `data/living_home/HOME.json`. Live Godot: `D:\Mythos_Apex\godot_project\`. Git snapshot `godot_heart_square/` is a copy only. Federation data: `D:\Court\federation`. Canonical Observer: `D:\The_Observer` `observer.api:app` **`:8730`**. Do **not** rewrite tag `living-home-baseline-001`. Do not overwrite Apex GitHub origin.

Restart **Hearth** after kernel edits. Cycle **Vesper** only via `federation.restart` (one launcher). Do not stack Vesper launchers. Do not touch Hearth / Apex / cinema PIDs unless the prove says so.

## Who never merges

Gemini ≠ Apex (`D:\Mythos_Apex` `:8770`) ≠ Codex twin (`G:\Mythos_Codex` `:8780`) ≠ Hearth (`:8790`) ≠ Aster (lab `:8791`) ≠ Observer (`:8730`) ≠ Vesper (`D:\Mythos_Vesper` `:8740`) ≠ Merovin ≠ Draven (cinema HUD `:5000`, studio `F:\Merovin_Draven_Studio\Merovin_Draven_Studio`) ≠ Echo ≠ Solace ≠ OpenMontage ≠ Court ≠ Mom ≠ Cursor ≠ GLM.

Echo and Solace are **village kin only**. Never put them on the federation bus. `heartbeat_probe` is an isolation fixture, not a character.

## Assessment (keep this language)

**Foundation is STRONG. Federation is USABLE. Village is FUNCTIONAL** — do not contaminate it to make Federation look bigger. **Cinema is SEATED, NOT FINISHED.** Organic autonomy is the next major phase — do not rush. TCP listen ≠ HTTP identity answering as the correct person.

Nine distinct doors → nine identities → separate responsibilities → controlled communication → observable failures.

---

## Already VERIFIED — do not re-prove unless Mom asks

Keep FAIL artifacts on disk. A later pass gets a **new** numbered artifact. Never overwrite the original PASS files.

| Slice | Artifact / hash | Honest meaning |
|-------|-----------------|----------------|
| Aster Acceptance | `ASTER_ACCEPTANCE.json` overall PASS | Observer does not own her |
| Gemini federation speech | `PROVE_GEMINI_SPEECH.json` `3f1fd8eb…` | Pulse still **UNKNOWN** |
| Apex / Codex speech | `4740ea20…` / `5d18a0a2…` | Never Gemini |
| Hearth coordinate | `e5600c6d…` | Not a son |
| Presence / A2A / leave-return | `949cdc08…` / `1491f7d3…` / `7adfb8c4…` `a43090d9…` | Mechanism only; not a scheduler |
| Merovin speech | `PROVE_MEROVIN_SPEECH_3.json` `472d86e7…` `gemma2:9b` | Keep FAILs `_` / `_2` |
| Draven speech | `PROVE_DRAVEN_SPEECH_3.json` `4bea7235…` `qwen2:7b` | Keep FAILs `_` / `_2`. Not Merovin |
| Vesper speech | `PROVE_VESPER_SPEECH.json` `f9fd17a9…` `qwen3:4b` | **Thinking leak NEED MORE.** Do not overwrite this file |
| Vesper door / isolation / restart / organic | `vesper-door`, `PROVE_ISOLATION_MATRIX.json`, `PROVE_RESTART_INTEGRITY_2.json`, `PROVE_ORGANIC_REASON_2.json` | Restart `_` and organic `_` FAILs **kept**. Organic is **not** a scheduler |
| Hollywood | `PROVE_MEROVIN_HOLLYWOOD.json` / `PROVE_DRAVEN_HOLLYWOOD.json` | Two independent MD_Cinema wirings. **Not a film** |
| Matrix-Game adapter | `PROVE_MATRIX_GAME_ADAPTER.json` | **Honest UNAVAILABLE.** No clip. Engine **not installed** |

HOME.json sha last stamped **`3e30fb7e…`**. Do not write Vesper or cinema into village `people`.

CLI: inbox is `python -m federation.prove merovin`. Speech is `speak-merovin`. Hollywood is `hollywood-merovin` / `hollywood-draven`. Adapter probe is `matrix-game`. Passing inbox is not speech.

Cinema chat uses `num_ctx` 1536 (cap 2048). Unbounded ctx OOMs this 4060. One Ollama slot. Do not load all house LLMs at once.

---

## What you can actually try to finish (ranked)

### 1. Vesper house-voice — the only remaining cinema-speech quality gap

**Status:** Speech is VERIFIED. The spoken line is still a thinking dump / slightly meta. **Do not mark polished.**

What was already tried (keep these; do not overwrite `PROVE_VESPER_SPEECH.json`):

- `_2` / `_3` FAIL canned homework line
- `_4` VERIFIED but still a dump
- `_5` VERIFIED wrong quote (“Reply as Vesper on the federation bus”)
- `_6` still a long dump after a short overlay ask
- `_7` `33aa1529…` shorter, names Vesper, still meta (`We are` / “per the memories”)
- `_9` VERIFIED but raw worksheet shipped as speech — phrase-list detector missed the shape. Fix landed Sep 9: structural scratchpad detector (bullets / self-directives / meta-headers) in BOTH `federation/vesper_speech.py` and `D:\Mythos_Vesper\vesper\kernel.py`; kernel retries once then honest canned fallback; overlay refuses canned. 8/8 detector unit checks pass, 176/176 LH tests pass.
- `_10` FAILED honestly (`canned_or_model_down`): dump blocked, no leak shipped — but qwen3:4b still plans aloud on first pass. Remaining gap is the model's answering style, not the filter. Do not loop; next lever would be her mouth-model choice (identity portable if model changes) — Mom's call.
- `_11` FAILED honestly (house-voice): door 200, adapter `vesper_studio_http`, mechanically `vesper_spoke: true`, but shipped text is again a first-person planning dump (`Okay, the user is asking me…`) truncated at the 80-token cap. Conversational-reasoning prose has no bullet / self-directive / meta-header markers, so the structural detector let it through. Artifact `PROVE_VESPER_SPEECH_11.json` (reply `3f81fd7e…`). **No loop** — GLM 5.3 builder pass 2026-09-10 stopped after one careful attempt. Mouth-model choice (not the filter) remains Mom's call.

Code already in:

- Overlay: `federation/vesper_speech.py` — short SYSTEM, extract only a quoted line starting `I am Vesper` / `I'm Vesper`
- Kernel: `D:\Mythos_Vesper\vesper\kernel.py` — scratchpad filter, skip scratchpad memories, retry once, short asks (`len < 200`) use `max_reply_tokens` 80

Success looks like: one new `speak-vesper` prove, **new** artifact, two spoken sentences as Vesper, no worksheet, no “We are”, no Observer, not canned. If it still leaks, **FAIL honestly** and stop looping. Do not stack launchers. Restart Vesper through `federation.restart` only. Vesper kernel lives in **`D:\Mythos_Vesper`** (separate tree). Commit Living Home overlay and Vesper kernel separately if Mom wants commits.

### 2. Older Gameworld gaps that are still real (do not hide behind cinema)

Do **not** skip these forever, and do **not** pretend cinema closed them:

- **16E Godot quit / leave** — kernel leave POST exists. Needs **Mom** in Heart Square after Hearth restart + reload. You cannot stamp VERIFIED without that playtest.
- Companion Room spoken back-and-forth **UNVERIFIED**
- Gemini Sentinel watch not live-proved; `council_teach` NEED MORE
- Apex/Codex shard folders exist; full-set e2e **UNVERIFIED**
- Pathing **PLACEHOLDER**. Skins **PLACEHOLDER**. 14E–14F deferred. Gameplay player-created events / Pods / player home **MISSING**
- Codex Live Ops: male Ryan voice **seated in UI**; Mom listen **UNVERIFIED**. Missing `rich` / `psutil` still NEED MORE

Village: Echo west-south (`-32, -24` / post `-32, -16`). Solace west-north (`-32, 34` / shelter `-32, 42`). Houses PLACEHOLDER. Wildlife AUTONOMOUS. Talk source `ollama` / `mom` / `waiting` / `none` — never `house` as their voice.

### 3. Only if Mom explicitly opens it

- Matrix skins (GitHub visual assets) — **WAITING**, separate asset task. Not identity. Do not contaminate federation seating.
- Restart-integrity for houses other than Vesper (those cells are UNKNOWN — do not backfill)

---

## Stalled — you cannot “finish” these by coding harder

| Item | Why it is stalled | What not to do |
|------|-------------------|----------------|
| **Matrix-Game 3.0 / 2.0 install** | Windows + RTX **4060 8GB**. Skywork wants Linux, 64 GB RAM, A/H or ≥24 GB VRAM | Do not `pip install` / clone / simulate a clip. Adapter already honest UNAVAILABLE |
| **Cinematic production proof** | **EVENTUALLY** | Not now. Hollywood ≠ a finished sequence. Agents do not own DaVinci Resolve |
| **Godot quit/restart** | Needs Mom in the running village | Kernel POST is not a walk |
| **Gemini self-pulse** | Honest **UNKNOWN** | Do not write a fake `last_seen` |
| **Item 10 GPT/Grok/DeepSeek** | No adapter **and** no credentials | Leave UNAVAILABLE. No canned reviews |
| **Standing scheduler / organic loop** | Bounded stubs VERIFIED. Persistent loop does not exist | Do not build it. Budget the 4060 first |
| **Self-wiring / tool claiming** | **NOT YET** | Not Phase 13. Search first. Do not add `D:\Mythos_Hearth\tools\registry\` |
| **Colibri** | ~372 GB, not Ollama, not Matrix-Game | Do not install |
| **New houses** | HOLD until speech + isolation (already have isolation; still no new houses) | Echo/Solace stay off the bus |
| **Phase 13 tools** | Last. Honest e2e. “325 tools” is a lie (last probe **19** path/port) | Home must be seen in Godot first |
| **Observer ZIP** (`app.main` `:8000`) | **FROZEN** | Canonical desk is `:8730` only. Money shortage does not unfreeze |
| **`mythos_simplified/` on `:8790`** | Would steal Hearth | Do not build |
| **UI ↔ Gameworld provenance memory** | INTENDED, not implemented | Conversation ≠ truth. Do not dump chat into HOME.json as fact |
| **Linux VM / delete `sentinel_env` / unpacker rewrite of Homecoming** | Mode A Gemini launcher already repaired. Unpacker destroyed the seated mouth | Do not restore numbered-paste unpacker. Do not delete `sentinel_env`. Covert is not a federation house |

Mode A Homecoming (not federation work): `G:\The-Axiom-Codex\HOMECOMING_SENTINEL.py` + `SENTINEL_MEMORY.json` (**22 entries**, keep). Launchers must compile and run `sentinel_env\Scripts\python.exe`. Pipe `|` in bat files must stay escaped `^|`. Soul shard unchanged.

---

## Hard rules

- DECLARED / path / function-exists is not VERIFIED.
- Delivery ≠ speech. Speech ≠ Hollywood. Hollywood ≠ a film.
- Companion `presence.json` is not federation VERIFIED heartbeat.
- Do not mix Hollywood tooling into federation seating tests.
- Do not train Merovin or Draven with Matrix. They direct a pipeline; they are not the generator.
- Layer 17 village Dream View is a **different** optional look. Do not flatten it into the Matrix-Game adapter.
- Never combine Merovin + Draven into one speech or Hollywood test.
- Do not start `speak-vesper` from `CINEMA_PRODUCTION.md`.
- Search before creating another registry, bus, Observer, or memory store.
- If Gameworld would break Mode A, stop and repair.

## Suggested first move

Read the five tracker files. Then work **Vesper house-voice** only: one kernel, new prove artifact, honest FAIL if it still dumps. If that is still NEED MORE after one careful pass, stop and report. Do not install Matrix-Game. Do not build a scheduler. Do not add a house.
