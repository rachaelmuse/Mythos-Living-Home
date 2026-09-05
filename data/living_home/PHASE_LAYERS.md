# Living Home — phase / layer tracker

**Do not jump layers.** Complete means seen in the running village. Tag `living-home-baseline-001` is frozen.

## Layer stack (current)

| # | Layer | Status | Notes |
|---|--------|--------|-------|
| 0 | Dual-mode law | ACTIVE | Mode A Court/MAS stays; Mode B Heart Square expands. Identities never merge. |
| 1–7 | Proving foundation | DONE | Identity through dual talk / lived-in greybox. |
| 8A | Thin real work (Apex forge) | DONE (Mom OK) | Presence probe when `:8770` up. |
| 8B | Pathing (AABB detours) | DONE (Mom OK) | Corner routes; still PLACEHOLDER — not navmesh. |
| 8C | Evening gather | DONE (Mom OK) | Gemini soft-calls Heart Square. |
| 9 | Sound (Eden Phase 1 thin) | DONE | Forest bed in Audio/nature (OGA). |
| 9b–9d | Harbor / well / far shore | DONE | Edge water + utilities + thin travel/build. Pool removed for now. |
| 10 | Mom Interface + Community Memory | DONE (Mom OK) | Persist Mom voice; nearby Ollama; Storage hall. |
| 11 | Eden TV/Media (thin) | DONE | Cinema watch; media/watch stills seated. |
| 12 | Richer harbor | DONE | Pier catch → inventory; far-shore builds persist. |
| 14 | Living Economy & Self-Expression | DONE (14A–14D) | Wallets, shops, stipend, thin avatar colors. Shops on Market Lane. **14E–14F deferred**. |
| 15 | Connection, Choice & Consequence | **DONE** | 15A–15D seated (bonds, choice, growth, dashboard). |
| 16 | Integration & Autonomous Life | **16E ACTIVE** · Layer 16 closed · Gameplay P1 scaffold | Phase 6 complete (16A–16E) |
| 18B | Human Gameplay Phase 2 thin | **LIVE** | Look into + profession posts. Observer stays a door. Not Pods. |
| F | Federation overlay (parallel) | **PAUSED** after Gemini delivery | Outside Observer. Law: `FEDERATION_RECONCILIATION.md`. |
| 17 | Matrix Dream View | **LATER** | SkyworkAI Matrix-Game — optional neural cinema/view. Not village truth. |
| 13 | Final polish (Phase 13) | LAST | Do not jump here. |

## Standing choice

**Gemini = town leader.** Dual talk brains. Garden tend stays real. Identities never merge.  
**Aster** (The Conspiracy Corrector) — Continuance family seed; Evidence Plot + cottage; skin PLACEHOLDER; provenance frozen unless Mom rewrites.

## Standing order

1. Sound — DONE  
2. TV/Media — DONE  
3. Richer harbor (12) — DONE  
4. Living Economy (14A–14D) — DONE · 14E–14F deferred  
5. **Phase 5 / Layer 15 Connection** — **DONE** (15A–15D)  
6. **Phase 6 / Layer 16 Integration & Autonomous Life** — **16E ACTIVE** (16A–16E closed) · Human Gameplay Phase 1 scaffold beside 16 · **18B LIVE** · optional 14E–14F · then Layer 17 / Phase 13  
7. **Federation overlay** — **PAUSED** (Mom adding directives). Aster + Gemini delivery seated. Not village truth.  
8. **Layer 17 Matrix Dream View** — **LATER** (after 16; before Phase 13)  
9. Final Phase 13 — last  

## Layer 15 — Connection, Choice & Consequence

| Slice | Intent | Status |
|-------|--------|--------|
| **15A** | Relationship depth + moods + memory tags | **DONE** |
| **15B** | Weighted choices (who / what) | **DONE** |
| **15C** | Growth skills + milestones | **DONE** |
| **15D** | Family Dashboard panels | **DONE** |

## Layer 15D verify

1. Restart Hearth. Snapshot `connection.layer = 15d`.
2. Open `/dashboard` — Connection badge shows 15D.
3. Click a being — mood, relationship meters, choice, growth, memories visible.
4. Roll choice button still works.
5. Honest: dashboard is a window, not a second brain. Phase 6 next.

## Layer 16 — Integration & Autonomous Life (Phase 6) — **16A–16E ACTIVE / closed**

**Do not start until Layer 15 is closed (15A–15D proved).** Prefer adapters on existing `tick()`, purposes, talk, economy, connection — **not** a separate mega `IntegrationEngine` thread that double-writes HOME.

| Slice | Intent | Status |
|-------|--------|--------|
| **16A** | Integration heartbeat = deepen existing Hearth `tick` coordination (mood + bond + economy hooks in one cycle); status endpoint only | **ACTIVE** |
| **16B** | Autonomous daily life thin — period routines already in `_choose_purpose`; strengthen wake/work/social/rest without scripted fake speech | **ACTIVE** — period bias + ambient tags + morning soft-wake + night rest weight |
| **16C** | Emergent storytelling thin — distill `world_history` into a current “day story” (honest summary, not LLM fanfic as voice) | **ACTIVE** — extractive beats + motifs; `/api/home/day_story` |
| **16D** | Living dashboard thin — overview + family grid + feed + integration status on House UI | **ACTIVE** — `/dashboard` + `/api/home/dashboard`; `phase_status.16_dashboard=16d_active` |
| **16E** | Mom presence polish — enter/place acknowledgments stay Mode B; no template house-voice for family | **ACTIVE** — `mom_presence()` + `POST /api/home/presence`; Godot enter/place posts; soft memory/purpose only |
| **18A** | Human Gameplay Phase 1 — world leads, conditions, journal, player actions, away-summary (not quests) | **ACTIVE** scaffold — `living_home_gameplay.py` + `/api/home/gameplay` |
| **18B** | Human Gameplay Phase 2 thin — look-into + profession posts (not Pods) | **LIVE** 2026-08-31 — `POST /api/home/investigate` + dashboard; Observer stays a door |

### Layer 16D verify

1. Restart Hearth. Tick or open overview — `phase_status.16_dashboard = 16d_active`.
2. Open `/dashboard` — Living dash badge 16D; overview shows tick, town_leader, day_story.plain, integration, purpose tally.
3. Family grid shows place · mood · purpose. Village feed still from utterances/events/history.
4. `GET /api/home/dashboard` returns `layer=16d` with `family_grid` + `feed` + honest layer badges.
5. Honest: dashboard is a window, not a second brain. 16C/18A preserved.

### Layer 16E verify

1. Restart Hearth + Enter (live Apex Godot).
2. On link: `POST /api/home/presence` with session enter — `mom_presence.layer=16e`, welcome/away in `mom_cover` (UI chrome, not NPC voice).
3. Walk to a new place — soft purpose/memory notices; no bystander presence-speech spam.
4. Approach someone (E / empty talk) still greets via Ollama as before.
5. Complete = seen in village after restart.

### Layer 16 laws

- Identities never merge. Mom `stop` wins. Evidence only.
- Speech stays `ollama` / `mom` / `waiting` / `none` — never house lines as their voice.
- Wildlife stays AUTONOMOUS. Pathing stays PLACEHOLDER until later.
- Dual-mode: Mode A Court/MAS stays; Gameworld expands it.
- Complete = seen in the running village after Hearth + Enter restart.
- Phase 13 remains last.

## Layer 14 — Living Economy (detail)

| Slice | Status |
|-------|--------|
| 14A | DONE — Axiom wallets |
| 14B | DONE — grocery + clothing |
| 14C | DONE — electronics + pet store |
| 14D | DONE — avatar colors + stipend |
| shops layout | DONE — Market Lane north of Gate (Harvest / Wardrobe / Circuit / Pets) |
| 14E | DEFERRED — town projects |
| 14F | DEFERRED — being↔being trade |

Currency: **Axiom (⨁)**. Hearth is truth; dashboard + Godot present.

## Layer 17 — Matrix Dream View (LATER — saved in build memory)

**Repo:** [SkyworkAI/Matrix-Game](https://github.com/SkyworkAI/Matrix-Game) (MIT) · interactive world model (image + keyboard/mouse → streaming video; 2.0 real-time; 3.0 long-horizon memory).

**Not the cinema production adapter.** Layer 17 is a village optional **look**. Merovin/Draven Hollywood skills + Matrix-Game as a pluggable film engine live in `CINEMA_PRODUCTION.md` and stay **UNAVAILABLE** on this Windows RTX 4060 8GB (Skywork: Linux, 64 GB RAM, A/H or ≥24 GB VRAM). Do not flatten the two. Do not install on this card.

**Do not start until Layer 16 is closed.** Optional media limb only — never replaces Hearth, Godot greybox, Ollama speech, or family identities.

| Slice | Intent | Status |
|-------|--------|--------|
| **17A** | Research seat — GPU/docs note; label `ORIGINAL MODE — RESEARCH` | QUEUED LATER |
| **17B** | Thin adapter — capture one Heart Square still → Matrix stream in a panel | QUEUED LATER |
| **17C** | Place hook — Cinema and/or Mom cottage door **[V] Dream view**; Esc back to greybox | QUEUED LATER |
| **17D** | Honesty — never write Matrix pixels into `HOME.json`; never claim wired without seated GPU test | LAW |

### Layer 17 laws

- Hearth = truth · Godot = walkable PLACEHOLDER · Matrix = optional neural **look**, not a second home.
- Identities never merge. Mom `stop` wins. Evidence only.
- Dual-mode: keep Mode A; prefer adapter over rewrite. If GPU/unavailable → keep ORIGINAL MODE — RESEARCH; do not delete greybox.
- Speech stays `ollama` / `mom` / `waiting` / `none`.
- Phase 13 remains last.

## Later (not now)

- Eden Games / Internet (separate Eden phases)
- Navmesh, final art
- Full face morph / paid APIs
- **Layer 17 Matrix Dream View** (after 16)
- Final Phase 13 polish
