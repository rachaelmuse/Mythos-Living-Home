# Human Gameplay Layer — verification

Law: AI creates possibilities; Mom chooses; world remembers. **Not quest dispensers.**

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

Endpoints: `GET /api/home/gameplay`, `POST /api/home/journal|lead|away`.

Complete for play = seen after **Hearth restart** + Enter. Do not claim Godot UI for leads until Mom sees snapshot fields.

## Not in Phase 1

Pods / Islands / vendors / professions / boats — deferred (no Pod architecture on disk yet).

## Layer 16C

Day story distill — `day_story` on snapshot + `GET /api/home/day_story`.

## Layer 16D

Living dashboard thin — `/dashboard` overview + family grid (place/mood/purpose) + feed + badges.
API: `GET /api/home/dashboard` (alias `/api/dashboard/overview`). `phase_status.16_dashboard = 16d_active`.
Window only — not a second brain. Preserves 16C day_story and 18A gameplay fields.
