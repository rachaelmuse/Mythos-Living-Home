# Living Home — slice status

Kernel: `D:\Mythos_Hearth\living_home.py`  
Save: `D:\Mythos_Hearth\data\living_home\HOME.json`  
Godot live: `D:\Mythos_Apex\godot_project\scenes\heart_square_immersive.tscn`  
Git baseline: tag `living-home-baseline-001` (hash recorded after first push)

## CURRENT PHASE

**Living Home Proving Slice** — physical home + real interaction + life while Mom watches.

Do not treat roadmap phases 1–13 as permission to leave this slice.

## VERIFIED WORKING

- Godot 4.7 loaded Heart Square **headless** without script parse errors (2026-08-16).
- Hearth Python kernel compiles (`living_home.py`).
- Ollama can produce family JSON lines locally (`llama3.2:3b`) when context is small — **lab test**, not Creator playtest.
- Persist file `HOME.json` exists (tmp-replace save).
- Apex GitHub remote already exists (`Mythos_Apex`); it was **not** overwritten.

**Creator playtest of the proving slice is in progress.** Do not mark the home milestone complete until she confirms in the running village.

## PARTIAL

- Family choose purpose (work / rest / visit / company) in the kernel.
- NPC–NPC talk jobs via local Ollama (background thread).
- Mom type-to-talk API (`POST /api/home/talk` as Mom).
- World-space speech bubbles (code exists in Godot).
- Walk-in greybox homes including Mom's cottage (code exists).
- Visible work poses (hammer / sit).
- Tree-line world rim (code exists).
- Squirrel state machine (forage / eat / climb / follow / flee / hide / rest).

## PLACEHOLDER

- House architecture and furniture: greyboxes.
- Family pathing: straight lines; may clip walls.
- Squirrel E-chirp text (wildlife has no language model).
- Godot `godot_heart_square/` in git: snapshot copy of live Apex files.
- Capability count: probed paths/ports, **not** 325 seated tools.

## BROKEN

- Not independently re-verified after the last Godot write while Creator tests. Treat as **unconfirmed in play** until she reports.
- Hearth Python module cache: skipping restart after `living_home.py` edits serves old talk.

## NOT YET IMPLEMENTED

- True door pathfinding.
- Overhearing by distance / attention.
- Separate language model per inhabitant.
- Phase 13 in-world tool expansion.
- BitNet as talk backend (must be measured separately first).

## Honesty classes

| Thing | Class |
|-------|--------|
| Interiors | PLACEHOLDER |
| Speech when `source=ollama` | MODEL_GENERATED |
| Speech when writer misses | FALLBACK honesty / silence — never house quotes as their voice |
| Wildlife motion | AUTONOMOUS_DECISION (bounded) |
| Pathing | PLACEHOLDER |
| Identity (Gemini ≠ Codex, …) | REAL kernel law |

## Completed (this session, documentation/git)

- Continuity files + baseline docs.
- Private GitHub preservation planned as `Mythos-Living-Home`.

## In Progress

- Creator testing the proving slice.

## Blocked

- None for git preservation. Home **acceptance tests** wait on Creator play.

## Next

The single most important development task: **whatever the Creator reports broken from this playtest** — then remaining unfinished items on the home acceptance list. Do not start a new major system until then.

See `NEXT.md` and `BASELINE.md`.
