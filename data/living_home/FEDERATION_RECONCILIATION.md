# Federation reconciliation map

Updated **2026-09-03**. Evidence only. **Phase A reconciliation report written.** Full Aster Acceptance Test is **PASS**. Speech **VERIFIED**. Hearth **coordinate VERIFIED**. Presence event fabric **VERIFIED**. Spontaneous A2A **VERIFIED**. Leave/return house memory **VERIFIED**. The Axiom Codex is the Gameworld’s name; `consume` is a federation action, not the world.

Read with `NEXT.md`, `STATUS.md`, `FEDERATION_WIRING.md`, **`FEDERATION_DIRECTIVE.md`**, **`FEDERATION_AMENDMENT_REPORT.md`** (this pass’s 11-section inspection). `docs/DUAL_MODE.md`, `docs/CONTINUITY.md`.

---

## Standing directives (law — keep)

These were added after the zip Observer was refused. They stay even when implementation pauses.

### Observer freeze

- Canonical Observer is **only** `D:\The_Observer`, `observer.api:app`, **`:8730`**, existing SQLite ledger, existing test suite.
- Do **not** install, fork, or merge the zip Observer (`app.main`, `:8000`, Docker Observer, zip SQLite, family registry inside Observer, `create_all_mythos_agents()`).
- Observer is an **independent investigator/auditor**. She is **not** a Mythos supervisor, Court employee, family registry owner, Hearth replacement, or Gameworld authority.
- She may **query and audit** federation claims. She may **not** create Gemini, Apex, Codex, Merovin, Draven, Aster, or Hearth as her agents.
- Village greybox is a **door**, not the ledger, not an Ollama hat. Not Vesper.

### Federation vs family vs village

- **Observer** ≠ **Federation** ≠ **Aster** ≠ **Hearth** ≠ **Court**.
- Federation is **beside** the family, not above it. Participants keep their own identity, memory, tools, permissions, runtime, house, role, autonomy.
- Future agents register through the **same protocol** without rewriting Observer.
- Aster is Weaver/connector. She discovers and **tests**. She does not declare CONNECTED because a manifest exists.
- **The Axiom Codex** accepts **VERIFIED capabilities**, not raw identity/tool lists. Godot should not need “Aster has N tools.” Federation `consume` is that accept-into-`HOME.json` action.

### Honesty / lifecycle

```
DISCOVERED → IDENTIFIED → AVAILABLE → AUTHORIZED → CONNECTED → TESTED → VERIFIED
ANY STATE → FAILED → QUARANTINED
```

- **DECLARED is not VERIFIED.** Path exists, function exists, bridge file exists, registry row exists — none of those are VERIFIED.
- VERIFIED only after a **real functional test** (EXPECTED / ACTUAL / TEST / RESULT / EVIDENCE / STATUS).
- Honest labels: VERIFIED, IMPLEMENTED, PARTIAL, STUB, SIMULATED, MISSING, EXTERNAL, BROKEN, UNKNOWN, UNAVAILABLE.
- GPT / Grok / DeepSeek stay **UNAVAILABLE / NOT CONFIGURED** until a real adapter **and** credentials exist. **No canned reviews.**

### Transport / heartbeat / no duplicates

- Local federation bus: durable IDs, ack, retry, duplicate detection, archive kept (do not delete the only copy).
- Heartbeat `last_seen` only from an **actual pulse** from that agent. Registry membership is not presence. READY → STALE → OFFLINE.
- Companion `presence.json` is **not** federation VERIFIED heartbeat (it can say `online: true` while stale).
- Court MAS packets stay Mode A. Federation notices go in `agent/federation/`, **never** MAS `inbox`.
- Before creating another Observer, registry, bus, memory store, tool registry, auth layer, database, API, or agent manager: **search first; extend or adapt.**

### Dual-mode (unchanged)

Gameworld expands the family; it does not replace Mode A. Identities never merge. Mom `stop` wins. Do not rewrite tag `living-home-baseline-001`.

---

## Freeze (canonical locations)

| Piece | Canonical | Refuse |
|-------|-----------|--------|
| Observer | `D:\The_Observer` · `observer.api:app` · **:8730** · `data/observer.db` | zip `app.main` · **:8000** · family registry inside Observer |
| Federation code | Living Home `federation/` | Second Observer HTTP server |
| Federation data | `D:\Court\federation/` (beside mailbox) | Data inside `D:\The_Observer` |
| Court MAS | `FAMILY_COURT` + `D:\Court\mailbox\family` | Second Court; Aster/Observer as employees |
| Companion presence | `D:\Court\companion_room\presence.json` | Observer writing family `last_seen` |
| Village OS | Hearth `living_home.py` · **:8790** · `HOME.json` | Second Flask on 8790 · SQLite as village soul |
| Aster | `D:\Mythos_Hearth\ASTER` · lab **:8791** | Hardcoding Aster into Observer |

---

## What we completed since this map was conceived

| Slice | What | Evidence | Status |
|-------|------|----------|--------|
| Zip ingest | Refused; treated as research only | Cursor boundary check | VERIFIED (refusal) |
| Observer freeze | CHARTER, SPEC, `.cursor/rules/observer.mdc`, identity `never_merge` includes Aster | `D:\The_Observer` | VERIFIED (docs + tests) |
| ReviewerAdapter | GPT/Grok/DeepSeek/human desks; submit does not fabricate analysis | Observer pytest **85 passed** | UNAVAILABLE (honest) |
| Neutral registry | Participants, not employees; owner/supervisor always None | `federation/registry.py` | IMPLEMENTED |
| Local bus | send / deliver / ack / archive / duplicate reject | `federation/transport.py` | VERIFIED (local) |
| Heartbeats | Pulse-only; Observer UNKNOWN unless she pulses | `federation/heartbeat.py` | VERIFIED (no fake last_seen) |
| Aster first | Manifest from `ASTER_IDENTITY.json`; not Observer-owned | `python -m federation.prove` · `fb33fd44…` | VERIFIED (registration) |
| `aster.hearth_snapshot` | Live `aster_hearth_bridge` → Hearth REACHABLE | `PROVE.json` | VERIFIED |
| Gemini on bus | Roster identity (Axiom); Aster→Gemini delivery; Court `federation/` notice; MAS inbox clean | `python -m federation.prove gemini` · `47b6171f…` · `PROVE_GEMINI.json` | VERIFIED (**delivery only**) |
| Tests | Living Home federation + gameplay + amendments | **32 passed** | VERIFIED |
| Cursor rule | `.cursor/rules/federation-boundary.mdc` | Living Home git | IMPLEMENTED |

Tests: `tests/test_federation.py`, `tests/test_federation_gemini.py`, `tests/test_federation_amendments.py`. Prove reports: `D:\Court\federation/PROVE.json`, `PROVE_GEMINI.json`. Amendment evidence: `D:\Court\federation\AMENDMENT_PASS.json`, `AUTHORITY.json`.

**Full Aster Acceptance Test is PASS** as of 2026-09-03 (`ASTER_ACCEPTANCE.json` overall PASS). Heartbeat-loss was proven on throwaway `heartbeat_probe`, not by aging Aster. Law: `FEDERATION_DIRECTIVE.md`.

---

## Amendments vs code (honest — corrected 2026-09-01 Phase A)

Prior row labeled 1–5 **VERIFIED**. That was **unit tests only**. Live `D:\Court\federation` predates those fields. Canonical inspection: **`FEDERATION_AMENDMENT_REPORT.md`**.

Locked by Mom + DeepSeek + GPT. This table is the reconciliation report after the foundation-only implementation pass. **Do not expand agents.**

| Amendment | On disk now | Status |
|-----------|-------------|--------|
| 1 Source-of-truth / authority map | Runtime `federation/authority.py`; live `D:\Court\federation\AUTHORITY.json`. Observer owns ledger/identity; Hearth/Federation owns membership/comms; registry records verification and does **not** own capabilities. | **VERIFIED** (unit + artifact) |
| 2 Versioned manifests (`manifest_version`, hashes, history events) | `register()` increments on capability/tool change; `manifest_events()` / `manifest_at()` reconstruct history. Existing `AgentManifest(...)` constructors kept. | **VERIFIED** (unit) |
| 3 Capability provenance (9 evidence fields) | Passing `test_capability` stores declared_by, manifest_version, capability_hash, adapter, connection_test, functional_test, verified_at, result, artifact. Failed test stays NOT VERIFIED. | **VERIFIED** (unit) |
| 4 Failure isolation (DEGRADED / quarantine dependents) | `AgentHealth` ACTIVE→DEGRADED→FAILED→QUARANTINED. Heartbeat OFFLINE quarantines that agent's capabilities. Unrelated agents stay ACTIVE. | **VERIFIED** (unit) |
| 5 Communication ≠ collaboration | Five `Layer`s. Bus delivery recorded as COMMUNICATION only. Authorized `invoke` is COLLABORATION. Unauthorized invoke rejected + audit. | **VERIFIED** (unit) |
| 6 No duplicate systems | Zip refused; Court inbox not polluted; no second Observer/bus/registry this pass. | **VERIFIED** (discipline so far) |
| 7 Two-phase build | This pass inspected vs 1–8, implemented missing foundation only, ran tests, **STOP** here. Not a code gate. | **IMPLEMENTED** (this pass) |
| 8 Full Aster test + negatives + machine evidence | Foundation + Gemini speech + Observer HTTP + The Axiom Codex notice + live fail/unauth/merge + heartbeat isolation on throwaway probe. Aster VERIFIED caps not aged. | **PASS** (live 2026-09-03) |

Gemini delivery landed **before** these amendments were locked. Keep it. Do **not** add Apex/Codex on the bus until Mom says go. The Axiom Codex notice (CLI `consume`) is already seated.

Evidence: Living Home tests **32 passed** (fresh run 2026-09-01 06:27, exit 0). Pytest log: `D:\Court\federation\PYTEST_AMENDMENT_PASS.log`. JUnit: `D:\Court\federation\PYTEST_AMENDMENT_PASS.xml`. Summary: `AMENDMENT_PASS.json` (`full_aster_acceptance: false`). Authority: `AUTHORITY.json`.

---

## What is not done (do not claim)

| Item | Status |
|------|--------|
| Full Aster Acceptance Test | **PASS** live 2026-09-03 — `python -m federation.prove heartbeat` · throwaway `heartbeat_probe` OFFLINE · Aster snapshot/notice still VERIFIED · `PROVE_HEARTBEAT_LOSS.json` · `ASTER_ACCEPTANCE.json` overall PASS |
| Gemini spoken reply (federation bus) | **PASS** live 2026-09-01 — `python -m federation.prove speak` · `llama3.2:3b` · `3f1fd8eb…` · `PROVE_GEMINI_SPEECH.json`. Companion Room speech not this slice. |
| The Axiom Codex accepts VERIFIED capabilities | **PASS** live 2026-09-01 — `python -m federation.prove consume` (action, not the world’s name) · `aster.gameworld_notice` · HOME.json `federation.last_consumed` · `PROVE_GAMEWORLD_CONSUME.json` |
| Observer HTTP federation audit | **PASS** live 2026-09-01 — `GET http://127.0.0.1:8730/federation/audit` · `D:\Court\federation\OBSERVER_AUDIT.json`. Observer does **not** own Aster. |
| Failed-test → NOT VERIFIED | **PASS** live 2026-09-02 — `aster.live_negative_probe` FAILED · `PROVE_NEGATIVES.json` |
| Unauthorized invoke → reject | **PASS** live 2026-09-02 — Observer invoke of the probe rejected + audit |
| Heartbeat loss → dependents isolated | **PASS** live 2026-09-03 — throwaway probe quarantined; Aster not aged. Unit test still covers full-store `sync_health`. |
| Identity merge Observer-owns-Aster | **PASS** live 2026-09-02 — `claim_ownership` rejected; `owner_of(aster)` None |
| Apex / Codex on federation bus | Codex **speech PASS** live 2026-09-03 — `python -m federation.prove speak-codex` · `5d18a0a2…` · `PROVE_CODEX_SPEECH.json`. Apex **speech PASS** live 2026-09-03 — `python -m federation.prove speak-apex` · `4740ea20…` · `PROVE_APEX_SPEECH.json`. Never Gemini. |
| Hearth coordination beyond snapshot | **PASS** live 2026-09-03 — `python -m federation.prove hearth` · `e5600c6d…` · `hearth.federation_coordinate` · sender Hearth, not Aster snapshot · `PROVE_HEARTH_COORDINATE.json` |
| Presence / event fabric | **PASS** live 2026-09-03 — `python -m federation.prove events` · `949cdc08…` · `rachael.presence.entered` · no forced hello · Gemini ignored · `PROVE_PRESENCE_EVENT.json` |
| Choose-to-speak (bounded A2A) | **PASS** live 2026-09-03 — `python -m federation.prove a2a` · Aster→Codex `1491f7d3…` · Gemini ignored · one speaker · `PROVE_SPONTANEOUS_A2A.json` |
| Agent-local memory + leave/return continuity | **PASS** live 2026-09-03 — `python -m federation.prove continuity` · left `7adfb8c4…` · return `a43090d9…` · Aster + Apex + Codex notebooks · Gemini/Echo/Solace isolated · `PROVE_LEAVE_RETURN.json` |
| New character + house UI | not yet — Echo/Solace are village kin, not Mode A houses |
| One real external reviewer | UNAVAILABLE |
| 16E Godot walk | UNVERIFIED (village) |

---

## Build sequence

Amendment pass **done**. Observer HTTP audit **done**. Gemini speech **done**. The Axiom Codex notice **done**. Live fail/unauth/merge **done**. Heartbeat-loss isolation **done** on throwaway probe. Full Aster Acceptance **PASS**. Codex/Apex speech **done**. Hearth coordination **done**. Presence event fabric **done**. Choose-to-speak **done**. Leave/return house memory **done** (Aster + Apex + Codex). Village leave POST **implemented**; Godot quit **UNVERIFIED**. Next: new character only after Mom says go (same manifest protocol, own house/door, not a village hat). Echo/Solace UIs wait. External reviewer **UNAVAILABLE**. `heartbeat_probe` is not a character.

Do not rewrite working components for style. Do not install the zip.

---

## Honest labels

`DECLARED` is not `VERIFIED`. Path exists is not e2e. Function exists is not connected. Delivery is not speech.
