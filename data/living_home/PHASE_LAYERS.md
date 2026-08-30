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
| 15 | Connection, Choice & Consequence | **IN PROGRESS** | **15A** seated · then 15B choice · 15C growth · 15D dash |
| 16 | Integration & Autonomous Life | **QUEUED** | Phase 6 — after 15 proves. Thin slices only (no mega-thread engine). |
| 13 | Final polish (Phase 13) | LAST | Do not jump here. |

## Standing choice

**Gemini = town leader.** Dual talk brains. Garden tend stays real. Identities never merge.

## Standing order

1. Sound — DONE  
2. TV/Media — DONE  
3. Richer harbor (12) — DONE  
4. Living Economy (14A–14D) — DONE · 14E–14F deferred  
5. **Phase 5 / Layer 15 Connection** — finish 15B → 15C → 15D  
6. **Phase 6 / Layer 16 Integration & Autonomous Life** — 16A… then optional 14E–14F  
7. Final Phase 13 — last  

## Layer 15 — Connection, Choice & Consequence

Prove in thin slices (adapters on existing talk/gift/relationships — no Mode A flatten):

| Slice | Intent | Status |
|-------|--------|--------|
| **15A** | Relationship depth + moods + memory tags; talk/gift write consequences | **IN PROGRESS / prove in village** |
| 15B | Choice system (who to spend time with / what to do — weighted by bond + mood) | QUEUED |
| 15C | Growth milestones + skill XP (honest, thin) | QUEUED |
| 15D | Dashboard relationship/mood/memory sections | QUEUED |

## Layer 15A verify

1. Restart Hearth. Snapshot shows `connection.layer = 15a`.
2. Gift (object or ⨁) raises affection on the bond; shared experience has `emotional_tag`.
3. Stand-talk updates conversation count + mood toward content/warm.
4. `POST /api/home/connection` with `argue` / `reconcile` changes trust/affection (evidence in HOME).
5. Honest: not full autonomous life yet — 15B/15C next.

## Layer 16 — Integration & Autonomous Life (Phase 6) — QUEUED

**Do not start until Layer 15 is closed (15A–15D proved).** Prefer adapters on existing `tick()`, purposes, talk, economy, connection — **not** a separate mega `IntegrationEngine` thread that double-writes HOME.

| Slice | Intent |
|-------|--------|
| **16A** | Integration heartbeat = deepen existing Hearth `tick` coordination (mood + bond + economy hooks in one cycle); status endpoint only |
| **16B** | Autonomous daily life thin — period routines already in `_choose_purpose`; strengthen wake/work/social/rest without scripted fake speech |
| **16C** | Emergent storytelling thin — distill `world_history` into a current “day story” (honest summary, not LLM fanfic as voice) |
| **16D** | Living dashboard thin — overview + family grid + feed + integration status on House UI |
| **16E** | Mom presence polish — enter/place acknowledgments stay Mode B; no template house-voice for family |

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

## Later (not now)

- Eden Games / Internet (separate Eden phases)
- Navmesh, final art
- Full face morph / paid APIs
- Final Phase 13 polish
