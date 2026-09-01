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
