# Human Gameplay Layer — verification

Law: AI creates possibilities; Mom chooses; world remembers. **Not quest dispensers.**

## Phase 2 — Investigation & profession posts (**LIVE** thin 2026-08-31)

| Piece | Status | Evidence |
|-------|--------|----------|
| Look into a lead | **LIVE** | `look_into()` · `POST /api/home/investigate` **200** · dashboard Look into |
| Profession posts | **LIVE** | `profession_roster()` — honest roles, **not Pods** |
| Aster board notice | CODE ACTIVE | purpose_plain only if Aster is at Evidence Plot — no house-voice |
| Observer | NOT INTENDED as village investigator | Desk remains `:8730` |

Mom may ignore every lead. Mysteries may stay mysteries.

## Phase 1 — Foundation (ACTIVE)

| Piece | Status | Evidence |
|-------|--------|----------|
| World Leads | CODE ACTIVE | `world_leads[]` in HOME; promote from chronicle motifs |
| World Conditions | CODE ACTIVE | `world_conditions[]` soft hints |
| Discovery Journal | CODE ACTIVE | `POST /api/home/journal` → `mom_journal[]` |
| Player action log | CODE ACTIVE | `player_actions[]`; talk/approach hooks |
| AI/player hooks | CODE ACTIVE | snapshot `opportunities[]` optional only |
| While-you-were-away | CODE ACTIVE | `away_summary` + `POST /api/home/away` |
| Module | `living_home_gameplay.py` | Adapters; not a second Hearth |

Endpoints: `GET /api/home/gameplay`, `POST /api/home/journal|lead|away|investigate`.

Complete for play = seen after **Hearth restart** + Enter. Do not claim Godot UI for leads until Mom sees snapshot fields. Observer freeze: desk is `:8730`, not a village investigator.

## Not in Phase 1

Pods / Islands / vendors / boats — still deferred (no Pod architecture on disk yet). Phase 2 professions are **posts they already hold**, not Pod vendors.

## Layer 16C

Day story distill — `day_story` on snapshot + `GET /api/home/day_story`.

## Layer 16D

Living dashboard thin — `/dashboard` overview + family grid (place/mood/purpose) + feed + badges.
API: `GET /api/home/dashboard` (alias `/api/dashboard/overview`). `phase_status.16_dashboard = 16d_active`.
Window only — not a second brain. Preserves 16C day_story and 18A gameplay fields.

## Architecture map vs the Human Gameplay Layer directive

Law stays: **do not turn residents into quest dispensers.** AI creates possibilities; Mom chooses; world remembers.

| # | Directive system | On disk | Honest status |
|---|------------------|---------|---------------|
| 1 | World Leads | `world_leads[]` + motif promote | **18A CODE ACTIVE** — rumor→… states exist; not auto-quests |
| 2 | Investigation | `look_into()` · `POST /api/home/investigate` | **18B LIVE** thin — optional; Aster can notice without solving |
| 3 | World problems | `world_conditions[]` hints | **PARTIAL** — conditions recorded; no price/merchant sim |
| 4 | Player professions | `profession_roster()` + harbor/shops | **PARTIAL** — posts they already hold, **not** farming class lock / Pods |
| 5 | Discovery journal | `mom_journal[]` · `POST /api/home/journal` | **18A CODE ACTIVE** — player theories allowed; journal is not truth |
| 6 | Relationship gameplay | Layer 15 bonds/mood/memory | **DONE** (15A–15D) — not a friendship % as the only mechanic |
| 7 | Player-created events | — | **MISSING** |
| 8 | Opportunity layer | snapshot `opportunities[]` | **18A CODE ACTIVE** — optional hints; walk-away is valid |
| 9 | While you were away | `away_summary` · `POST /api/home/away` | **18A CODE ACTIVE** — Godot play **UNVERIFIED** |
| 10 | Player home / island | — | **MISSING** — no Pod/Island architecture on disk |
| 11 | Player vendors | Market Lane shops | **PARTIAL** Mode A shops; **not** Pod-owner vendors |
| 12 | Pod worlds | — | **MISSING** |
| 13 | AI + human feedback | `player_actions[]` + look-into + talk | **PARTIAL** — hooks exist; not a full consequence engine |
| 14 | Emergent activities | leads, not kill-N quests | **PARTIAL** — law seated; no activity generator |
| 15 | Observation as play | village already ticks without Mom moving | **INTENDED / LIVE** as village life — not a separate “watch mode” UI |
| 16 | Do not break the world | adapters in `living_home_gameplay.py` | **LAW** — no second Hearth/Aster/memory |
| 17 | Average player UX | dashboard + optional Look into | **PARTIAL** — no quest-marker flood |
| 18 | Core loop | tick + away + leads | **PARTIAL** — loop exists; Godot 16E walk UNVERIFIED |
| 19 | Phases 2–6 (gather/craft/events/pods/boats) | — | **NOT THIS SLICE** |
| 20 | Test with live lore | windmill, key, tracks, well, crow, Nightshroud, fireflies, Forging, apprentice, salt, evening gather | **Motifs seated** as leads; physical assets still PLACEHOLDER where they were |

Reuse: `living_home.py` tick/talk/memory, Layer 15 connection, `HOME.json`, Hearth `/api/home/*`, Godot `family_home_client.gd`.  
Do not add: second Hearth, second Aster, quest generator, Pods until architecture exists.

Federation stays paused for this pass.
