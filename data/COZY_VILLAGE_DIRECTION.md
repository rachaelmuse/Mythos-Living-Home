# Hearthbound — Cozy Life-Sim Design (original)

**Creator:** rachaelmuse23  
**Front porch:** Mythos Hearth · http://127.0.0.1:8790/  
**Spirit:** A family village with houses, gardens, stories, and living AI companions — *our* world, *our* art, *our* voices.

> Genre inspiration only (cozy multiplayer/life-sim village). No Palia assets, names, maps, characters, or ripped audio.

---

## The fantasy

You wake in **Heart Square**. Companions (Apex, Codex, drones) are *present* — talking faces, voices, real agents — not NPCs with three lines. The village has districts that feel built: hearth homes, herb gardens, workshops, lantern paths. You gather, craft, gift, fish, farm, trade, and slowly unlock story.

## Core pillars

| Pillar | What it means here |
|--------|-------------------|
| **Place** | Walkable village: square, garden, hearth interior, forge, arcade, sanctuary |
| **People** | Living avatars = Apex/Codex/drones (Ollama + voice + portraits) |
| **Care** | Gift loops (herb → tea → gift) before grind |
| **Gather** | Plants, herbs, bugs, rocks/ore, seeds, fish |
| **Make** | Craft at First Hearth / workshop; recipes unlock story |
| **Grow** | Garden plots, seasons-lite, harvest calendars |
| **Play** | Quests, side stories, festivals (lantern evenings) |
| **Trade** | Soft barter with companions / drone “shops” |
| **Beauty** | Original Comfy stills + Godot 3D + licensed/original music |

## Systems map (not patented — ours to invent)

### 1. Village & buildings
- Heart Square (hub)
- Herb Garden (gather + farm plots)
- First Hearth (craft + gift)
- Workshop / Forge (tools)
- Waterside (fishing — future dock district)
- Homes (player + companion cottages — original layouts)
- Arcade / Sanctuary / Command (already in Hearth OS)

### 2. Characters (living avatars)
| Who | Role in the village |
|-----|---------------------|
| You | Keeper of the hearth |
| Apex | Hands / systems / builder muse |
| Codex | Story elder / quest giver |
| Jarvis / Nova / Percy / Genesis | Drone kin — gather help, watch, chores |
| Later cast | Hatched spores / story NPCs |

Voices: Neural / local TTS we already wire. Faces: our avatar packs + optional talk. **Agents do the talking** — not canned dialogue trees only.

### 3. Gathering
| Node type | Examples (original names) | Yield |
|-----------|---------------------------|--------|
| Herbs | rosemary, mint, thyme, duskleaf | tea / gifts |
| Wildflowers | emberpetal, mistbloom | dye / decor |
| Bugs | lantern moth, hearth beetle | craft / quest |
| Rocks | softstone, emberite | tools / repair |
| Seeds | garden packets | farm plots |
| Fish | creekminnow, lantern koi | cook / gift |

### 4. Farming
- Plots in Herb Garden
- Plant → water → wait (real-time or session ticks) → harvest
- Companion can “tend” while you’re away (night shift flavor)

### 5. Fishing
- Waterside mini-game (timing / patience) — Godot or web canvas
- Bait from bugs/herbs
- Codex tells fish lore; Apex helps with rod upgrades

### 6. Crafting & trades
- First Hearth recipes (tea, gifts, lantern oil, simple tools)
- Soft trade: gift companions → reputation → unlock recipes / rooms
- No pay-to-win store — family village economy

### 7. Quests & story
- **Main:** First Hearth Gift (shipped)
- **Side:** Arcade Cozy Valley visit (shipped)
- **Next arcs:** Meet the drones · Plant first seed · Catch first fish · Festival of Lanterns · Build a cottage room
- Story bible lives in Court `living_game/story/`

### 8. Audio
- Original or **properly licensed** packs (CC0 / paid license)
- Beds: square morning, garden breeze, hearth crackle, evening lanterns
- Stingers: gift complete, harvest, fish catch, companion arrive

---

## What we already have (honest)

| Piece | Status |
|-------|--------|
| Web village + districts | LIVE (Hearth) |
| Care quest herb→tea→gift | LIVE |
| Companions + drones in UI | LIVE |
| Gallery stills (English prompts) | LIVE |
| Godot portable + First World | LIVE (slice) |
| Arcade HTML playables | LIVE |
| Living Game hub | LIVE |
| Fishing / farm plots / bug-rock nodes | **NOT YET** — design next |
| Full 3D village with house shells | **NOT YET** — Godot blockout next |
| Custom music bed | **NOT YET** |

---

## Build order (lifetime, one fire at a time)

1. **Design locked** — this doc (done)
2. **Gather nodes in web village** — click garden spots → inventory in `save.json`
3. **Farm plot v1** — plant seed → harvest after N minutes
4. **Quest arc 2** — “First Seed” + “Meet Jarvis”
5. **Godot blockout** — square + garden + hearth room (greybox → our art)
6. **Waterside + fish** — simple timing game
7. **Voice lines** — Apex/Codex greet on enter district
8. **Festival of Lanterns** — evening mode + gallery stills we already generated

---

## Naming (ours)

Working title: **Hearthbound**  
Village: **Heart Square** / **Mythos Hearth**  
Do not use: Palia, Kilima, Bahari, or their character names.
