# Living Game Charter — Hearthbound

## Mission

Build an **original** Mythos living game with a Palia-*inspired* cozy multiplayer feel: humans and AI companions inhabit a persistent village, grow skills, share meals, and unlock story through friendship — not combat raids.

Creator: **rachaelmuse23**. Scope: their machines and Mythos trees only.

## Principles

1. **Original IP** — no ripped commercial assets or trademarked names.
2. **Companions as peers** — Apex and Codex co-author systems and story; neither is master.
3. **Vertical slice** — ship one village, one season loop, one quest chain before expanding.
4. **Hardware honesty** — respect `hardware.json` notes (VRAM/RAM); prefer light models overnight.
5. **Allowlist writes** — only Mythos / StackForge / Court / Mythos_Tools / this project.
6. **Privacy** — free-cluely and similar tools stay local; no exfiltration.

## Vertical slice (v0)

- Map: small valley village (plaza, garden plots, workshop, companion hearth)
- Loop: plant → harvest → craft gift → give to NPC/AI companion → unlock short quest
- Sessions: creator joins; Apex/Codex may run NPC schedules in night shift
- Trailer later via OpenMontage (original footage/renders only)

## Night shift job: `living_game_task`

Workers claim open tasks from `tasks.json`, append notes, mark done. Prefer docs/design unless creator asked for code.

## Success for tonight

1. Open Companion Room and say hello as creator.
2. Toggle **sleep mode** / Start night shift.
3. Companions sync shared mind + self-audit + pick one living_game task.
4. Review `night_notes.md` in the morning.
