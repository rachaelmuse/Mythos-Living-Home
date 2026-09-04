# Federation build directive

Seated **2026-09-01** from Mom + DeepSeek + GPT concurrence. Evidence only. Mom `stop` wins.

This is the document to hand a builder. **Do not give them the zip Observer.**

Read with `FEDERATION_RECONCILIATION.md` (what exists on disk), `FEDERATION_WIRING.md` (tests), `docs/DUAL_MODE.md`.

**Name:** The Gameworld is **The Axiom Codex**. Federation `consume` is an action (authorized VERIFIED notice into `HOME.json`), not the world’s name. Gemini’s house `G:\The-Axiom-Codex` is Gemini, not the world.

**STOP:** Speech, Hearth coordination, presence-as-event, bounded choose-to-speak, and leave/return house memory are seated. Echo and Solace are **village kin only** — do not put them on the federation bus. Do not force a greeting chorus. Do not add a village A2A scheduler. A new Mode A house + UI still waits for Mom. External reviewer **UNAVAILABLE**. Full Aster Acceptance Test is **PASS** as of 2026-09-03.

---

## Convergence (keep)

| Voice | Principle |
|-------|-----------|
| Mom | Don't tell me it's wired. Make it actually work. |
| Cursor | Will not overwrite the live Observer with a conflicting system. |
| GPT / review | Separate Observer from the federation; verify every boundary. |
| DeepSeek | Diagnosis and architecture are correct; implement reconciliation, not a duplicate. |
| This directive | Prove one end-to-end chain, including refusal-to-lie, before scaling. |

Cursor's refusal of the zip was **correct**. That is Observer philosophy: *No. This does not match the evidence or the governing architecture.*

---

## Architecture (keep)

Observer is **beside** the family, not above it.

```text
                 OBSERVER :8730
                       │
                 independent audit
                       │
                       ▼
              FEDERATION INTERFACE
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       GEMINI        APEX         CODEX
          │            │            │
          └────────────┼────────────┘
                       │
                     ASTER
                       │
                     HEARTH
                       │
              THE AXIOM CODEX
                 (Gameworld)
```

Observer audits. She does not supervise, own, or merge identities.

Manifest path (no `create_all_mythos_agents()`):

```text
NEW AGENT → manifest → identity validation → capability discovery
        → tool inventory → permission negotiation → connection tests
        → registry → available
```

Any future agent (Aster today, Nova tomorrow, unknown next month) uses the **same protocol**. **No Observer rewrite.**

---

## Amendment 1 — Canonical source-of-truth / authority

| Domain | Authority |
|--------|-----------|
| Observer identity / mission / creed | **Observer** |
| Investigative ledger, evidence, conclusions, dissent, Observer audit history | **Observer** |
| Family federation identity, membership, registration, presence, federation communication, federation permissions | **Hearth / Federation** (not Observer) |
| Each agent's identity, memory, tools, internal state | **That agent / house** |
| Declared capabilities | **Declaring agent** (subject to federation verification) |
| Capability verification state | **Federation verification layer** (records; does **not** own the capability) |
| Tool ownership | **Owning agent / house** |
| The Axiom Codex / world state, citizens, locations, simulation, presentation | **Hearth / The Axiom Codex** |
| External reviewer identity | **External adapter** |
| Permissions to invoke | **Federation security layer** |

No system may silently become the authority for another system's identity or internal state. The capability registry is a **record**, not an owner.

---

## Amendment 2 — Versioned manifests

Track at minimum:

- `agent_id`
- `manifest_version`
- `agent_version`
- `capability_hash`
- `tool_hash`
- `timestamp`
- registration / update **event**

Capability or tool changes **must** produce an auditable event. Historical capability state **must** remain reconstructable. Do not erase old manifests.

Observer (later) should be able to ask: *What did this agent claim to be capable of at the time this action occurred?*

---

## Amendment 3 — Capability provenance

A capability marked **VERIFIED** must retain evidence:

1. Who declared it  
2. Manifest version  
3. Capability version / hash  
4. Adapter / implementation used  
5. Connection test performed  
6. Functional test performed  
7. When verification occurred  
8. What result was returned  
9. Verification artifact / evidence reference  

```
DECLARED ≠ AVAILABLE ≠ CONNECTED ≠ TESTED ≠ VERIFIED
```

If evidence is missing, **downgrade** — do not assume success.

Lifecycle:

```
DISCOVERED → IDENTIFIED → AVAILABLE → AUTHORIZED → CONNECTED → TESTED → VERIFIED
ANY / ACTIVE → DEGRADED → FAILED → QUARANTINED
```

---

## Amendment 4 — Failure isolation

Agent, adapter, tool, or external-service failure **must not** terminate unrelated systems.

```
agent failure → mark unavailable → quarantine affected capability → federation continues
```

Not: agent failure → everything dies.

Support: **ACTIVE → DEGRADED → FAILED → QUARANTINED**. Unaffected agents keep running. Add tests that demonstrate this.

---

## Amendment 5 — Communication ≠ collaboration

Separate layers. Test them separately.

| Layer | Question |
|-------|----------|
| 1. COMMUNICATION | Can I reach you? |
| 2. CAPABILITY | What can you actually do? |
| 3. AUTHORIZATION | Am I permitted to ask you to do it? |
| 4. COLLABORATION | Can we execute this task together? |
| 5. VERIFICATION | Did it actually happen and return the expected result? |

**Successful message delivery must not be reported as successful collaboration.** Aster→Gemini ack is COMMUNICATION, not Gemini speech, not collaboration, not The Axiom Codex taking a notice.

---

## Amendment 6 — No duplicate systems

Before adding any subsystem, search first. Do not create a second Observer, ledger, database, registry, message bus, memory system, tool registry, authentication layer, orchestration system, or API. Extend verified infrastructure or add a thin adapter.

Zip Observer remains **research only**.

---

## Amendment 7 — Two-phase build discipline

### Phase A — Reconciliation (no destructive changes)

Inventory: existing systems, duplicates, canonical owners, dependencies, APIs, registries, transports, databases, auth, identities, tool ownership, stubs, simulations, placeholders, untested claims.

Produce a reconciliation report. **Do not destroy working code for style.**

### Phase B — Implementation (one boundary at a time)

After each boundary: existing tests, new functional tests, **failure** tests, preserve evidence, update status. Do not proceed to the next major integration until the current boundary passes acceptance.

Objective is not maximum code generation. Objective is a federation whose claimed connections can be independently tested.

---

## Amendment 8 — Aster Acceptance Test (first measurable milestone)

**Foundation already on disk is not this full test.** Distinguish:

| Piece | On disk 2026-09-01 | Full test |
|-------|--------------------|-----------|
| Aster registers without Observer owning her | **VERIFIED** | required |
| Real heartbeat (Aster pulse; Observer not faked) | **VERIFIED** | required |
| Aster → Hearth message + ack + persist | **VERIFIED** | required |
| Aster → Hearth snapshot capability | **VERIFIED** (`aster.hearth_snapshot`) | required |
| Aster → Gemini **delivery** (Gemini did not speak) | **VERIFIED** (communication only) | COMMUNICATION yes; collaboration **no** |
| Gemini **responds as Gemini** | **PASS** live 2026-09-01 | required for full test |
| Authorized Gameworld invocation + world state change | **PASS** live 2026-09-01 | required |
| Independent Observer audit of evidence | **PASS** live 2026-09-01 | required |
| Negative / refusal-to-lie tests | **PASS** live 2026-09-02/03 (fail / unauth / merge / throwaway heartbeat isolation) | required |

### Happy path (must all be true)

Prerequisites: Observer `:8730` running, Hearth running, Gameworld running (for steps 5–6), Aster **not** pre-owned by Observer.

1. Aster presents manifest → registry accepts → **DISCOVERED** (identity isolated).  
2. Aster → Hearth real message → ack → persist → **CONNECTED**.  
3. Aster → Gemini real message → Gemini **responds** → persist → **COMMUNICATING**.  
4. Aster declares a capability → functional test **passes** → **VERIFIED** with provenance.  
5. Gameworld **authorized** request → Aster performs it → result returned → **world state updates**.  
6. Observer independently queries: who exists, what is VERIFIED, what communications occurred, what evidence supports VERIFIED — and produces an audit **without owning Aster**.

No system owns another.

### Refusal-to-lie (must all be true)

- Failed capability test → remains **NOT VERIFIED**.  
- Unauthorized invocation → **REJECTED** + audit event.  
- Heartbeat loss → Aster **OFFLINE**; dependent capability **DEGRADED / UNAVAILABLE**.  
- Identity merge attempt (Observer owns Aster, or `create_all_mythos_agents`) → **REJECTED**.  
- Dependent failure → isolated; Observer / Hearth / Gemini / Gameworld do not die.

### Machine-readable evidence (required)

Not “all tests passed” in chat. A record Observer can inspect, e.g. `D:\Court\federation\ASTER_ACCEPTANCE.json`:

```text
ASTER FEDERATION ACCEPTANCE TEST
Registration: …
Identity isolation: …
Hearth connection: …
Gemini communication: …
Heartbeat: …
Capability declaration: …
Capability functional test: …
Gameworld invocation: …
Gameworld state change: …
Observer audit: …
Negative:
  Failed capability → correctly rejected
  Unauthorized invocation → correctly rejected
  Heartbeat loss → correctly detected
  Identity merge attempt → correctly rejected
Evidence: test IDs / timestamps / agent IDs / message IDs / hashes / artifacts
Overall: PASS | FAIL
```

Every PASS/FAIL has: test ID, timestamp, agent IDs, message IDs, hashes where appropriate, result, artifact reference.

---

## Build sequence (after amendment pass)

1. Protect Observer — **done**  
2. Extract interfaces — **amendment pass done** (authority, versions, provenance, isolation, layers **unit-tested**)  
3. Neutral registry — **foundation done**  
4. Real local transport — **foundation done**  
5. Connect Aster — **foundation done**; full acceptance **PASS** 2026-09-03  
6. Connect Gemini — **delivery + speech done**  
6b. Connect Codex — **delivery + speech done** 2026-09-03  
6c. Connect Apex — **delivery + speech done** 2026-09-03  
7. Hearth coordination beyond snapshot — **done** 2026-09-03 (`python -m federation.prove hearth`)  
7b. Presence / event fabric — **done** 2026-09-03 (`python -m federation.prove events`) — awareness, not a greeting order  
8. The Axiom Codex accepts VERIFIED capabilities — **done** (CLI `consume`)  
9. Observer as audit participant (HTTP) — **done**  
10. One real external reviewer — later (UNAVAILABLE until adapter + credentials)  
11. House-local attention that may speak — **choose-to-speak done** 2026-09-03 (`python -m federation.prove a2a`); leave/return continuity — **done** 2026-09-03 (`python -m federation.prove continuity`, Aster + Apex + Codex notebooks `7adfb8c4…` / `a43090d9…`)  
12. New character + own UI — after 7b and 11, same manifest protocol, own house/door. Not a village hat. Echo/Solace are **village kin**, not this item. Wait for Mom.

---

## What Cursor must do next (when Mom says go)

Heartbeat-loss isolation **2026-09-03**. Presence event fabric **2026-09-03**. Spontaneous A2A **2026-09-03**. Leave/return **2026-09-03** (Aster + Apex + Codex). Evidence: `D:\Court\federation\PROVE_LEAVE_RETURN.json` (`7adfb8c4…` / `a43090d9…` VERIFIED). Village leave POST needs a Hearth restart; Godot quit still UNVERIFIED.

**Do not** add a new character until Mom says go. Do not order everyone to hello. Do not start an unbounded A2A scheduler on the village GPU. Codex is not Gemini. Apex is not Gemini. External reviewer later (no adapter, no keys).

Do not rewrite working components for style. Do not install the zip.
