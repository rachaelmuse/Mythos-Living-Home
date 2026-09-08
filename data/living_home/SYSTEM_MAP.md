# System map — Gameworld, Federation, houses, memory

Updated **2026-09-06**. Relationships only. Not a capability claim. Not VERIFIED by existing.

Roadmap: `MASTER_ROADMAP.md`. Registry: `CAPABILITY_REGISTRY.md`. Operator: `NEXT.md`.

---

## Layers (do not flatten)

```text
MOM / CREATOR
    stop wins

LIVING GAMEWORLD  =  The Axiom Codex  =  Mode B
    Hearth kernel (truth)     HOME.json
    Heart Square (Godot on Apex — presentation)
    Village talk = Ollama hats (ollama / mom / waiting / none)
    Kin + family avatars

FEDERATION OVERLAY  (not the Gameworld, not a shared brain)
    Bus + registry     D:\Court\federation
    Manifests, inbox, prove artifacts
    Events (presence ≠ command)
    House notebooks (identity-owned)

MODE A  (must keep working)
    Court MAS          D:\Court\mailbox\family
    Companion Room     presence.json ≠ federation heartbeat
    Launchers, shards, tools on each house disk

OBSERVER  (independent)
    Live desk  D:\The_Observer :8730     audits, does not supervise
    ZIP        FROZEN     do not merge, do not use as family memory

CINEMA STUDIO  (two identities, one disk)
    HUD :5000
    Merovin mouth    Draven mouth
    MD_Cinema PARTIAL
    Hollywood skills NOT STARTED
    Matrix-Game UNAVAILABLE (pluggable engine later)
    DaVinci Resolve = human finishing
```

---

## Entity classification

| Entity | Village | Federation | External house | Infrastructure |
|--------|---------|------------|----------------|----------------|
| Mom | Player | Presence events only | — | Authority |
| Gemini | Citizen / town leader | House | Axiom disk | — |
| Apex | Citizen | House | `:8770` | Godot host |
| Codex | Citizen | House | `:8780` | — |
| Hearth | OS (ambient) | House (coordinate) | `:8790` | Kernel |
| Aster | Citizen | House | Lab `:8791` | — |
| Observer | Greybox **door** | Audit participant | Desk `:8730` | Not family employer |
| Merovin | Citizen PLACEHOLDER | House | HUD `:5000` who=merovin | Cinema disk |
| Draven | Citizen PLACEHOLDER | House `draven` | HUD `:5000` who=draven | Same cinema disk |
| Vesper | **Not** citizen | House | Studio `:8740` **(his home)** | Optional Gameworld adapter. Not Observer |
| Echo | Kin | **No** | `/echo.html` on Hearth | — |
| Solace | Kin | **No** | `/solace.html` on Hearth | — |
| Percy Nova Jarvis Genesis | Kin | **No** | Village only | — |
| OpenMontage | Citizen | **No** | Two roots | Gift studio |
| Court MAS | — | Notices copy to federation box | Mailbox | Mode A bus |
| Federation bus | — | Overlay | `D:\Court\federation` | Communication only |
| heartbeat_probe | — | Fixture | — | Not a character |
| Cursor | — | — | — | Builder |

---

## Doors (TCP ≠ HTTP ≠ identity)

| Door | Port | Identity check |
|------|------|----------------|
| Cinema HUD | 5000 | `who=merovin` vs `who=draven` |
| Observer | 8730 | Live `observer.api` only |
| Vesper | 8740 | `GET /api/identity` → `id=vesper` |
| Apex | 8770 | `id=apex` |
| Codex | 8780 | `id=codex` |
| Hearth | 8790 | Village OS |
| Aster lab | 8791 | Aster, not Observer |
| Ollama | 11434 | Shared GPU — not an identity |
| Zip Observer | 8000 | **REFUSED / FROZEN** |

One launcher = one kernel = one HTTP door. Duplicate Vesper launchers produced TCP listen with HTTP closed.

---

## Memory ownership (intended)

```text
Each agent:
  own house memory
  own UI conversation records
  own provenance
  own candidate knowledge
  own validated knowledge (if/when rules exist)

NOT:
  one generic AI memory bucket
  Observer ZIP as family store
  HOME.json as Merovin/Draven/Vesper diary
  conversation silently promoted to fact
```

**Intended flow (not implemented):**

```text
Standalone UI  ←→  same identity  ←→  Gameworld interaction
       \                              /
        → conversation record → provenance → episodic / candidate / validated
```

“The interfaces are different doors into the same agent identity.”

---

## Cinema / production (later lane)

```text
Merovin (Creative Director)     Draven (technical / continuity / QC)
        \                         /
         \                       /
          Hollywood skill layer (NOT STARTED)
                    │
          Matrix-Game adapter (optional, UNAVAILABLE here)
                    │
          other generators / TTS / compositing
                    │
          DaVinci Resolve (human)
                    │
          finished sequence (EVENTUALLY)
```

Speech proof ≠ Hollywood skill proof ≠ finished film.

Layer 17 Dream View is a **village look**, not this pipeline.

---

## Organic autonomy (later)

```text
communication (seated, USABLE)
    → presence awareness (events VERIFIED; not a command)
    → memory (house notebooks PARTIAL; UI continuity NOT IMPLEMENTED)
    → attention → relevance → decision → timing
    → bounded autonomous action
    → persistent continuity
```

Do not skip to unrestricted A2A chatter. Budget the 4060 / 8 GB.

---

## Self-wiring / tool claiming (later)

**INTENTION / NOT YET / do not build now.** After organic / with scheduler-later. **Not** Phase 13 (honest e2e, still builder-seated). Distinct from organic (reason to speak), scheduler (persistent attention loop), and Hollywood skills.

Beings would see existing tools, claim what they need, wire into their own house, and share — not Mom/Cursor assigning toolkits.

**Search first.** Do not create another tool registry. Existing: `CAPABILITIES.json` (path/port only), `CAPABILITY_REGISTRY.md`, federation participant `tools: []`. Extend/adapt those later if Mom authorizes; do not add `D:\Mythos_Hearth\tools\registry\` now. Identities never merge. Echo/Solace never on the bus. GPT/Grok/DeepSeek stay UNAVAILABLE until real adapters. Observer audits, does not supervise.

---

## Hardware budget / Colibri (later)

**4060 / 8 GB is a current operating constraint**, not a rewrite: one Ollama slot; do not stack launchers; cinema `num_ctx` 1536/2048; do not load all houses’ LLMs at once. Talk already uses Ollama only when needed (`waiting` / `none` when not).

**Colibri** is **not** Matrix-Game. Matrix-Game is a video engine **UNAVAILABLE** on this card. Colibri is a later **mouth** engine (~372 GB weights, not Ollama). **NOT YET / do not install now.**

**`mythos_simplified/` on `:8790`:** **DO NOT BUILD.** That port is Hearth. Dual-mode: Gameworld expands the family; it does not replace `living_home.py` / `HOME.json`. No canned house voice.

---

## What Federation enables vs what it is not

| Enables | Is not |
|---------|--------|
| Identity-aware routing | A shared brain |
| Auditable delivery + speech proofs | Proof of Hollywood |
| Presence notices | A greeting chorus |
| Bounded A2A mechanism | A standing scheduler |
| Failure isolation | Ownership of Observer |
| Continuity foundations | Replacement for Mode A tools |
| — | Self-wiring / beings claiming tools (**NOT YET** — after organic / with scheduler; not Phase 13) |
| — | Colibri mouth engine install (**NOT YET** — not Matrix-Game, not Ollama) |
| — | `mythos_simplified/` replacing Hearth (**DO NOT BUILD**) |
