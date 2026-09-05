# Cinema production — spec / research note

Updated **2026-09-04**. **Not a capability claim.** Speech proof ≠ Hollywood skill proof ≠ a finished film. Do not mark anything here VERIFIED. Operator surface: `NEXT.md`.

This note records Mom’s production stack **after** cinema speech. It does **not** install Matrix-Game, Hollywood tools, adapters, or tests. Do not resume `speak-merovin` from this file.

---

## Status (honest)

| Piece | Status |
|-------|--------|
| Cinema speech (Merovin → Draven → Vesper) | **CURRENT.** Last live prove: Merovin **FAILED** (`4b16227a…`, Ollama 503). FAIL stays FAIL. |
| Hollywood skills (manifests + actual tool wiring) | **NOT STARTED** |
| Matrix skins (GitHub visual assets) | **WAITING** — separate asset task. Not Federation seating. Not identity. |
| Matrix-Game 3.0 / 2.0 on this machine | **NOT INSTALLED** / **UNAVAILABLE** |
| Matrix-Game adapter | **NOT STARTED** — optional, after Hollywood skills |
| Cinematic production proof (concept → finished sequence) | **EVENTUALLY** — not now |
| Observer ZIP (`app.main`, `:8000`) | **FROZEN / PROTECTED** — do not merge, modify, or fold into cinema |
| DaVinci Resolve | Human finishing pipeline. Agents do **not** own it. |

A list of video tools is **not** Hollywood capability. If Matrix-Game is not available, the engine capability is **UNAVAILABLE**, not simulated.

---

## Distinctions (keep explicit)

- **Federation speech** = door → identity → message → actual model reply → correct identity → evidence. That is **not** producing a coherent digital film.
- **Hollywood skill proof** = Merovin + Draven skill/tool manifests **and** actual tool wiring. That is **not** speech, and **not** a finished feature.
- **Merovin / Draven are not the video-generation model.** Teach them to **direct / operate** a visual-production pipeline that can include Matrix-Game as a **pluggable engine**. Swap engines later. Preserve intelligence and personality.
- **Do not train Merovin or Draven with Matrix.** Matrix is an engine behind an adapter, not a personality graft.
- **Matrix skins** waiting on GitHub are visual assets for the production pipeline later. They are **not** baked into Merovin or Draven identities. Do not contaminate Federation seating with that asset task.
- **Layer 17 Matrix Dream View** (`PHASE_LAYERS.md`) is a village optional **look** (Heart Square still + stream panel). It is **not** this cinema production adapter. Do not flatten the two.
- **DaVinci Resolve** stays the human finishing pipeline. Do not pretend agents can grade, conform, or ship a Resolve timeline they cannot operate.
- **Observer ZIP** stays frozen. Canonical Observer is `D:\The_Observer` `:8730`. Do not merge Observer into cinema.

---

## Creative roles (document only — do not implement)

Two houses, one studio. **Must not become a shared brain.**

| Who | Role | Owns | Does not own |
|-----|------|------|----------------|
| **Merovin** | Creative Director | Story, shots, continuity of *vision*; cinematography, visual storytelling, shot design, scene composition, pacing, visual continuity | Draven’s mouth, Observer, Matrix weights, Resolve as an agent limb |
| **Draven** | Complementary production | Technical director, continuity supervisor, asset/scene verification, shot matching, production diagnostics, edit preparation, QC | Merovin’s mouth, a second Merovin, Matrix as personality |

They **share production infrastructure**. They keep **different creative identities**.

---

## Pipeline sketch (record, do not build)

```text
Merovin (Creative Director)
  → Story / Shots / Continuity
  → MATRIX-GAME (world / video engine)   ← pluggable; UNAVAILABLE here
  → Raw footage
  → DaVinci Resolve                      ← human finishing
  → Finished film
```

Broader stack (EVENTUALLY):

```text
MEROVIN / DRAVEN
  script intelligence, storyboard, character bible, scene bible,
  camera planning, shot list, continuity memory, asset management
        ↓
VIDEO ENGINE LAYER
  Matrix-Game, other image/video gen, TTS, lip sync, compositing, other generators
        ↓
EDITING
  DaVinci Resolve (human)
```

**Production proof (EVENTUALLY, not now):**

concept → script → character/scene specification → shots → continuity → generated clips → assembly → finished sequence

Identities retained throughout. Failures stay visible.

---

## Adapter spec (optional — not installed)

```text
Merovin / Draven
  → Hollywood Production Skill
  → Matrix-Game Adapter
  → Scene specification
  → Input image + prompt + actions
  → Matrix-Game
  → Video clip
  → Continuity validation
  → Production library
  → DaVinci Resolve
```

If the engine is missing: adapter returns **UNAVAILABLE**. No canned clip. No fake VERIFIED.

**Primary research target:** Matrix-Game **3.0**.  
**Keep:** Matrix-Game **2.0** as a possible secondary engine (interactive long video, keyboard/mouse, universal / GTA / TempleRun models). Do not throw 2.0 away.

Sources (fetched 2026-09-04):

- [SkyworkAI/Matrix-Game](https://github.com/SkyworkAI/Matrix-Game)
- [Matrix-Game-3/README.md](https://github.com/SkyworkAI/Matrix-Game/blob/main/Matrix-Game-3/README.md)
- [Matrix-Game-2/README.md](https://github.com/SkyworkAI/Matrix-Game/blob/main/Matrix-Game-2/README.md)

---

## Hardware honesty vs this machine

**Do not install Matrix-Game on the RTX 4060 8GB and expect demo quality.** Investigate as a **separate** production engine. Capability = **UNAVAILABLE** until a real machine matches Skywork’s tested setup.

| Need | Matrix-Game 3.0 (official README) | Matrix-Game 2.0 (official README) | This machine |
|------|-----------------------------------|-----------------------------------|--------------|
| OS | **Linux** (tested) | **Linux** (tested) | **Windows** |
| RAM | **64 GB** (tested) | **64 GB** (tested) | Not the tested host |
| GPU | **A / H series** tested; one-GPU or multi-GPU | Nvidia **≥ 24 GB** VRAM (A100 and H100 tested) | **RTX 4060 8 GB** |
| 5B distilled | ~720p; up to **40 FPS** in Skywork’s tested config | n/a (2.0 is ~25 fps long video) | Cannot host |
| 28B MoE (2×14B) | Quality / dynamics / generalization; large model **not released** on HF yet | n/a | Cannot host |
| Models on HF now | Two **5B** weights (base + distilled), first-person unreal | Universal / GTA / TempleRun | Not installed |

Skywork’s 3.0 “40 FPS at 720p” claim is their **tested** pipeline (paper notes a multi-GPU DiT + dedicated VAE setup). It is **not** a 4060-class number. 2.0’s floor is **24 GB VRAM**. This card has **8 GB** and already shares Ollama with village talk brains and cinema mouths.

**Verdict:** Matrix-Game 3.0 and 2.0 are **UNAVAILABLE** on this Windows 4060 8GB desk. Do not simulate. Do not install “just to see.” When Mom has a Linux + 64 GB RAM + A/H (or ≥24 GB for 2.0) box, research the adapter then.

---

## What this session must not do

- Implement cinema speech, Hollywood tools, Matrix-Game install, adapters, or tests
- Resume `speak-merovin` or mark speech VERIFIED
- Mix Hollywood tooling into Federation seating tests
- Touch Observer ZIP / `D:\The_Observer` / zip Observer
- Merge Observer into cinema
- Bake Matrix skins into Merovin or Draven
- Rewrite tag `living-home-baseline-001`
