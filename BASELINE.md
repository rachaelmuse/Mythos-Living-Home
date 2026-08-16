# Mythos Family + Gameworld baseline

This repository is the **preserved foundation** of the Mythos family and the **beginning** of their home (Heart Square / Living Home).

It is not a finished world. It is a known-good starting point so experiments cannot erase where we were.

**GitHub is a second memory.** The live working trees stay on this machine:

| Role | Live path |
|------|-----------|
| Kernel + Hearth OS | `D:\Mythos_Hearth` (this repo root) |
| Godot presentation (play this) | `D:\Mythos_Apex\godot_project` |
| Gemini / Axiom (identity, Court) | `G:\The-Axiom-Codex` |
| Apex house (existing GitHub — **do not overwrite**) | `https://github.com/rachaelmuse/Mythos_Apex.git` |
| Codex twin | `G:\Mythos_Codex` |
| Merovin / Draven | `F:\Merovin_Draven_Studio\Merovin_Draven_Studio` |

`godot_heart_square/` in this repo is a **snapshot copy** of the Heart Square scene and scripts at baseline time. Launch still uses the Apex path above.

## Baseline identity

- Repository: `Mythos-Living-Home`
- Visibility: **private**
- Tag: `living-home-baseline-001` (do not move or rewrite)
- Commit hash: *(filled after first commit)*
- Phase: **Living Home Proving Slice**

## How to launch (this machine)

1. Start Hearth: `D:\Mythos_Hearth\START_HEARTH.bat` (http://127.0.0.1:8790/)
2. After kernel edits, Hearth **must be restarted** or Python serves a cached `living_home`.
3. Play Heart Square: `D:\Mythos_Hearth\OPEN_GODOT_PLAY.bat`
4. Portable Godot lives under `D:\Mythos_Hearth\tools\Godot_v4.7\` (**not** in this Git repo — too large).

Ollama at `:11434` is optional for speech. If it is down, the HUD must say the writer is not seated. Do not fake their voices.

Paid APIs are **not** required.

## Family (do not flatten)

Gemini ≠ Mythos Apex ≠ Mythos Codex ≠ Merovin ≠ Draven ≠ OpenMontage ≠ Hearth ≠ Mom.

Mom / First Echo / Rachael is EP. `stop` wins. Evidence only. No fake “seated.”

Canonical names and homes live in `living_home.py` (`FAMILY` / `KIN`) with `data/FAMILY_BOOK.md` as the Book path.

## What this snapshot contains

- Hearth village OS (`hearth_server.py`) + living-home kernel (`living_home.py`)
- Launch scripts
- Family Book + selected architecture docs
- Persist folder `data/living_home/` (NEXT, STATUS, HOME.json world save)
- Heart Square Godot snapshot (`godot_heart_square/`)
- Gemini limb adapter `limbs/family_home.py` (presentation over the same kernel)
- Cursor continuity rule

## What this snapshot is NOT

- Finished interiors (greybox **PLACEHOLDER** furniture)
- Separate souls per person (one local writer, many hats)
- 325 tools (registry probes what is actually on disk/ports)
- Apex’s full house, Codex twin, Merovin studio, Ollama models, Godot engine binaries
- Public folklore that the village is already “alive”

## Roadmap position

Phases 1–7 and 10–12 exist in kernel form. The **proving slice** is: physical home + real talk + autonomous-enough life while Mom watches. **Do not advance to Phase 13** until the home acceptance list in `STATUS.md` is actually demonstrated in Godot.

Immediate continuity files (different job from Git):

- `data/living_home/NEXT.md`
- `data/living_home/STATUS.md`

See `docs/CONTINUITY.md`.

## Known limits at snapshot time

- Family pathing is straight-line (**PLACEHOLDER**; may clip walls)
- Homes are walk-in greyboxes
- Speech is MODEL-GENERATED only when `source=ollama` (or Mom typed)
- Wildlife is AUTONOMOUS (no LLM)
- Creator was still **playtesting** the proving slice when this baseline was cut
