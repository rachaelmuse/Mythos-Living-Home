# House rest dreams (Eidolon craft, separate diaries)

Date: 2026-09-10  
Status: design landed in code — unit IMPLEMENTED 2026-09-10, not village VERIFIED  
Law: identities never merge; no shared memory bucket; dreams are not speech; no standing scheduler. **Hearth stays silent.**

This is the same *craft* as Merovin's old `dream_archive.py` / `dream_weaver.py`. It is not that code, not `C:/AI_Studio`, and not a "Merovin Dream-Weaver" byline on other houses.

Mom's correction 2026-09-10: **they all dream**, and the dream is **who they are** — not a generic rest line, not a shared vault. **Hearth stays silent** (village OS, not a dreamer).

## Intent

When a character **begins rest**, they write **one** rest-note dream into **their own** vault, in **their own** voice-shape (role + personality seed + last work + place). Wake, work, then rest again can write another. While they stay asleep, ticks do not keep writing.

Dreams are rest notes. They are not village speech, not Ollama, not a house pretending to talk.

## Who

Every seated character with a self. Not fixtures. Not the player.

**Village FAMILY (Hearth tick rest-begin):**  
`gemini`, `apex`, `codex`, `merovin`, `draven`, `montage`, `aster`, `observer`

**Village KIN (same rest-begin, not on the federation bus):**  
`jarvis`, `genesis`, `nova`, `percy`, `echo`, `solace`

**Studio, not a citizen (own disk, own rest signal):**  
`vesper`

**Does not dream:**

- `hearth` — village OS; holds the fire; stays silent
- `mom` — player / EP, not an NPC rest loop
- `heartbeat_probe` — isolation fixture, not a character

Observer dreams as **the village door resting**, not as the `:8730` ledger. Echo and Solace dream as kin. Vesper dreams as Vesper. None of those promotions put Echo, Solace, or Vesper on the federation bus, and none make Observer a family employee. Hearth never writes a dream file.

## Where (lane per identity — do not flatten)

| Who | Vault | Must not |
|-----|--------|----------|
| `aster`, `gemini`, `apex`, `codex`, `merovin`, `draven` | `D:\Court\federation\houses/<id>/dreams/` plus `kind: dream` in that house notebook | Shared glob; another house's folder |
| `montage` | same federation house tree `houses/montage/` | Merge with Merovin/Draven |
| `echo`, `solace`, `jarvis`, `genesis`, `nova`, `percy` | Hearth village vault `data/living_home/dreams/<id>/` | `D:\Court\federation\houses/`; federation bus; `HouseNotebook` |
| `observer` | Observer's own disk `D:\The_Observer\dreams/` (or equivalent beside the desk, **not** `observer.db`) | Federation notebook; SQLite ledger; Vesper's tree |
| `vesper` | `D:\Mythos_Vesper\dreams/` (his house) | `HOME.json`; village `people`; Observer |

Authority: only that id may write that vault. Writer must equal owner.

Do not:

- write dream **text** into `HOME.json`
- write into `C:/AI_Studio` or one shared DreamVault
- glob `Dream_*.json` across ids or lanes
- merge into `family_memory`, Observer ledger, or Court MAS inbox
- let Echo compile other people's dreams (historian later; out of scope)

Cooldown only: village people may store `last_rest_dream_tick` on their person row. That flag is not the dream. Vesper/Observer cooldowns live in **their** vault (a small `last.json`), never in `HOME.json` for Vesper.

## Trigger

**Village people (FAMILY + KIN, including Observer door; not Hearth):**  
Hook Hearth `tick` / `_choose_purpose`. **Rest-begin** = this tick `purpose` is `rest` or `sleep`, and it was not `rest`/`sleep` last tick. One dream, then `last_rest_dream_tick` = current tick. If `id == hearth`, skip.

**Vesper (not in `HOME.json`):**  
Once per village **night** rest wave: the first rest-begin of any village dreamer while `clock.period == night` may also call Vesper's own `rest_begin` on **his** disk. If Hearth never rests anyone that night, Vesper does not fake a village body. Do not add him to `people`.

**Not a trigger:** every tick while still resting; Mom leave/return (work notes stay); Ollama; a standing scheduler.

If Hearth is down, village dreams do not fire. Vesper does not fire from that hook. Honest skip.

## What a dream is

JSON in **that** vault. Federation-lane dreamers also get a notebook row `kind: "dream"`. Village-lane / Observer / Vesper do **not** get a federation notebook row.

```json
{
  "agent_id": "aster",
  "kind": "dream",
  "source": "rest",
  "speech": false,
  "text": "<character rest note — see below>",
  "from_note": "<last work text or null>",
  "place": "<their place if known>",
  "timestamp": 0,
  "authority": "owning_agent"
}
```

### Character rest note (no Ollama, not speech)

Compose **only** from that id's own fields:

- `name`, `role`, `personality` (seed already on the roster)
- last **work** note if that lane has one
- current `place` if known

Each id uses a **different rest-shape** so Gemini cannot sound like Codex and Echo cannot sound like Aster. Shapes are rest notes, not mouth lines:

| Id | Rest-shape (intent, not a canned quote sheet) |
|----|-----------------------------------------------|
| `gemini` | Holds the village; what must stay steady while he rests |
| `apex` | Hands/forge; what was being built |
| `codex` | Memory/archive; what he is keeping |
| `merovin` | Vision/shot; what he saw, not Hollywood sprawl |
| `draven` | Continuity; what must not drift across the cut |
| `montage` | Gift/short; what was being made for someone |
| `aster` | Pattern/evidence; a notice or an honest I don't know yet |
| `observer` | Evidence, not hierarchy; the door rests; not Vesper |
| `echo` | Silence, unspoken, a question — not a declaration |
| `solace` | A discrepancy or the map of what is actually there |
| `jarvis` | Gate watch banks; still a watch, at rest |
| `genesis` | Garden clock; season/soil, not speech |
| `nova` | One job set down for the night |
| `percy` | Inventory/hearth stores counted, then quiet |
| `vesper` | A story not yet dug; journalist rest; not Observer |

If there is no last work note: still write the rest-shape from role + personality + place. Honest `from_note: null`. Do **not** fall back to Merovin "gentle clouds" / shared Calm-Inspired lists. Do **not** use markovify. Do **not** call Ollama.

`source` is always `rest`. `speech` is always `false`. Never `ollama`, `house`, or `mom`.

Weaver / cross-house chronicle is **out of scope**. If added later: one `agent_id`, that vault only, that name on the byline. Echo must not ingest others' Dream_ files.

## Write path

1. Hearth tick sees rest-begin for a village dreamer id.
2. Dispatch by lane: federation house dreams vs village vault vs Observer disk.
3. Refuse writer ≠ owner. No-op if already dreamed this bout.
4. Build text from **that** id's character fields + last work (if any) + place.
5. Write `Dream_<YYYYMMDD_HHMMSS>.json` under **that** vault only.
6. Federation-lane only: append `kind: dream` to that house `notes.json`.
7. Set cooldown flag on the correct lane.
8. If this tick is the first village rest-begin of a **night** period, also `rest_begin("vesper")` on Vesper's disk once.

Missing disk / Observer tree / Vesper tree: skip that id, do not crash the village, do not invent a dream in another vault.

Do not create a new Observer, bus, or `tools/registry/`. Extend `federation/house_memory.py` for federation-lane only. Village-lane is a thin Hearth helper that writes `data/living_home/dreams/<id>/`. Observer and Vesper writers are adapters to **their** roots.

## Isolation tests (required before any VERIFIED claim)

Unit tests (tmp_path, no live Ollama):

1. **Owner write:** `aster` rest-begin writes federation `houses/aster/dreams/` and a `kind=dream` notebook row.
2. **No leak:** Aster's dream is absent from Gemini's vault and notebook.
3. **Cross-write refused:** `writer="gemini"` cannot write Aster's dream (`PermissionError`).
4. **Silent / fixtures refused:** `hearth`, `heartbeat_probe`, and `mom` cannot rest-dream. No files.
5. **Echo is not federation:** Echo rest-begin writes village `dreams/echo/` and does **not** create `D:\Court\federation\houses\echo/` (tmp roots). Federation `HouseNotebook.remember("echo")` still raises.
6. **Solace / Nova / kin:** same village lane; not on the bus.
7. **Observer is not the ledger:** Observer rest-begin writes Observer-root `dreams/`, not federation houses, not a sqlite ledger file.
8. **Vesper is not a citizen:** Vesper rest-begin writes Vesper-root `dreams/`, does not add `vesper` to a fixture `HOME.json` `people`.
9. **Hearth silent:** `rest_begin("hearth")` raises; no `dreams/hearth/` file. Tick must not call it.
10. **Corpus isolation:** list(apex) never returns codex files.
11. **Character isolation:** with empty work notes, `text` for `aster` ≠ `codex` ≠ `echo` ≠ `vesper` ≠ `observer`.
12. **Rest-begin once:** second call in the same bout does not write a second file.
13. **New bout:** leaving rest then rest-begin again allows a second file.
14. **Not speech:** `source=="rest"` and `speech is False`.
15. **Work notes survive:** leave/return `kind=work` tests still PASS.

Hearth-facing (kernel, not Godot VERIFIED):

16. Purpose `work` → `rest` writes once; next tick still `rest` does not.
17. Night first rest-begin also writes Vesper's vault once; a second village rest-begin the same night does not write a second Vesper dream.
18. Echo rest-begin does not register Echo on the federation bus.

Village-complete only when Mom sees rest → that person's own dream file after Hearth restart. Playtest is separate from unit PASS.

## Error handling

- Cross-house or fixture write: `PermissionError`; no file.
- Empty agent id: `PermissionError`.
- Missing root / disk error: skip that id; do not crash tick; do not write into another id's vault.
- No work note: still a character rest-shape; `from_note` null.
- Same-second filename: suffix `_2` rather than overwrite.

## Out of scope (do not build in this slice)

- Markov weaver / compiling a shared Eidolon chronicle
- Echo ingesting other houses' dreams
- Layer 17 Dream View / Matrix-Game
- Standing organic scheduler
- GPU / Ollama dreams
- New houses
- Observer ZIP / writing Observer `observer.db`
- Putting Echo, Solace, or Vesper on the federation bus
- Changing `living-home-baseline-001`

## Success

- Isolation tests above PASS.
- Leave/return house memory tests still PASS.
- Every seated character except **Hearth**, Mom, and `heartbeat_probe` can rest-dream **as themselves** in **their** lane. Hearth stays silent.
- Ticks during sleep do not spam files.
- Identities remain unmerged.
- Operator docs updated only after code lands: **IMPLEMENTED** (unit) until a village playtest. Not VERIFIED as "seen in Heart Square" until running.
