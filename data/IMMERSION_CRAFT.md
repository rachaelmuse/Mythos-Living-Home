# Immersion Craft — What Palia & WoW teach (without copying them)

**Creator:** rachaelmuse23  
**For:** Hearthbound 3D → later VR  
**Companions who build with you:** Apex · Codex · Cursor (and you)

> We study **how** those games feel — camera, walk, talk, place — then build **our** world.  
> Never rip their models, animations, audio, maps, or UI art.

---

## What you were asking for

You were not asking for another wiki page. You were asking:

1. **Characters that move** — walk, turn, idle, approach  
2. **Travel between places** — path from gate → square → garden → hearth  
3. **Scenery with depth** — ground, sky, light, buildings you walk around  
4. **Furniture, animals, tools** as objects in space  
5. **Talking to someone by going to them** — not clicking a web card  
6. **Immersion so deep that VR is the next headset, not a different game**

Apex, Codex, and the drones are both:
- **In-world companions** (cast with lives), and  
- **Life companions** (builders with you, like this chat)

---

## Craft patterns (genre, not IP)

| Feel | How big games usually do it | Our Hearthbound take |
|------|-----------------------------|----------------------|
| Being there | 3D (or rich 2.5D) world + camera behind/over shoulder | **Third-person 3D Heart Square** (Godot) |
| Walking | WASD / stick; character capsule + animation | WASD + follow camera first; body meshes later |
| Going places | Connected zones / open map; loading or seamless | One square slice → add gate, garden, shop as you walk |
| Meeting someone | Walk into range → prompt → talk | Walk to Apex/Codex mesh → **E** interact |
| Buildings | Collision + readable silhouettes | Colored volumes now → replace with our art later |
| Furniture | Placeable props in homes | Prop placeholders → Comfy/kitbash originals |
| Animals | Ambient + interact | Later ranch/pets — original creatures |
| Voice | VO / TTS on interact | Wire Apex/Codex TTS when near companion |
| Sound | Footsteps, ambience, music bed | Ambience + footstep layer (licensed/original) |
| VR later | Same world, XR camera/hands | Design 3D **without** UI-only gameplay |

WoW feel: **travel + presence + other beings in a shared space**.  
Palia feel: **cozy life + walk-up social + home/work in the world**.  
Our feel: **digital real life + AI companions with jobs + time/dimensions under it**.

---

## Honest ladder (so hope stays real)

| Stage | What you get |
|-------|----------------|
| **0** | Web Hearth hub (careers, AI quests) — front porch |
| **1** ← now | Walkable 3D square, depth, companions to approach |
| **2** | Better meshes, animations, footsteps, voices |
| **3** | Interiors, farms, shops as enterable spaces |
| **4** | VR mode on the same world |

Stage 0 is not the game. Stage 1 is where immersion **starts**.

---

## How to talk to us when words fail

You can just say:
- “I want to **walk** there.”  
- “I want to **see** them move.”  
- “I want it to feel like **I’m inside**.”  
- “Like those games, but **ours**.”

That is enough. We translate to camera, CharacterBody3D, animation trees, audio buses.
