---
name: Observer Vertical Slice
overview: Create The Observer as a new independent investigative entity at D:\The_Observer (not inside Mythos-Living-Home, not a Vesper rename). First build is a tested end-to-end pipeline from question to report, with persistent ledger/graph and honest UNAVAILABLE stubs for everything not yet wired.
todos:
  - id: repo-identity
    content: "Create D:\\The_Observer as its own git project: charter, identity, rules, launch script, pyproject. Do not scaffold inside Mythos-Living-Home."
    status: completed
  - id: db-core
    content: Persist the core spine (investigations, sources, claims, evidence, hypotheses, research_records, relationships) in SQLite with round-trip tests.
    status: completed
  - id: policy-registry
    content: Wire policy gates and an honest capability registry (CONNECTED only when tested).
    status: completed
  - id: research-adapters
    content: Implement URL intake, HTTP fetch+archive, and DuckDuckGo search with robots/rate-limits; unavailable adapters as interfaces only.
    status: completed
  - id: extract-ledger-graph
    content: Claim salvage, heuristic extraction, evidence ledger, NetworkX graph with provenance and inferred flags.
    status: completed
  - id: hypotheses-audit-report
    content: Competing hypotheses, required counter, 12-question adversarial audit, required report format, no auto-publish.
    status: completed
  - id: api-dashboard-integration
    content: FastAPI + static dashboard + end-to-end integration test on a public URL. Verify registry honesty and that Mythos/Vesper are untouched.
    status: completed
isProject: false
---

# The Observer — First Vertical Slice

**Identity:** The Observer (independent investigative journalist / researcher). Not a Mythos agent. Not Vesper. Not a Gameworld citizen.

**Root:** `D:\The_Observer` (does not exist yet). Port: `127.0.0.1:8730` (Vesper stays on `:8740`).

**Do not touch:** [living_home.py](living_home.py), Hearth, Court, Vesper, Apex, Codex, Gemini, or `living-home-baseline-001`. No supervisor relationship. Other systems may later *request* an investigation; they cannot write the ledger or rewrite conclusions.

## Approach (chosen)

Greenfield Observer repo, SQLite local spine, real adapters only where they actually run.

- **Not chosen:** Full PostgreSQL/React/Docker/Neo4j/FAISS stack on day one — that recreates the “claimed but unwired” failure mode.
- **Not chosen:** Extending [D:\Mythos_Vesper](D:\Mythos_Vesper) — identities must not merge. Vesper’s vault/examiner *patterns* may be reused as ideas, never imported as a runtime.

Vesper remains the family journalist with Mom as editorial authority. Observer is a separate institution whose loyalty is evidence; a human may **halt publication** (legal/safety) but may **not silently rewrite** evidence, source assessments, or conclusions. Disagreement is recorded as a versioned editorial note.

## First-slice pipeline (must work end-to-end)

```mermaid
flowchart TD
  question[UserQuestion] --> intake[InvestigationIntake]
  intake --> questions[QuestionEngine]
  intake --> search[WebSearchAdapter]
  search --> fetch[HttpFetchAdapter]
  fetch --> archive[SourceArchive]
  archive --> extract[ClaimEntityExtract]
  extract --> ledger[EvidenceLedger]
  extract --> graph[EntityRelationshipGraph]
  ledger --> hypo[HypothesisEngine]
  hypo --> counter[CounterHypothesis]
  counter --> audit[AdversarialReview]
  audit --> report[RequiredReport]
  report --> dash[Dashboard]
```



Every advertised box in this chain is **wired and tested**. Everything else is an explicit `UNAVAILABLE` module with a real interface and a registry reason — never `pass` / `TODO` pretending to work.

## Folder tree

```text
D:\The_Observer\
  README.md
  CHARTER.md
  STATUS.md
  NEXT.md
  pyproject.toml
  requirements.txt
  .env.example
  .gitignore
  LAUNCH_OBSERVER.bat
  observer/
    __init__.py
    identity.py          # immutable identity + never-merge list
    policy.py            # legal/research boundaries
    core.py              # enums/dataclasses from the provided spine
    db.py                # SQLAlchemy engine, SQLite default
    models.py            # ORM tables
    registry.py          # honest CONNECTED / UNAVAILABLE / DISABLED
    audit.py             # append-only mutation + self-audit checklist
    questions.py         # FACTS/PEOPLE/MONEY/POWER/... question engine
    human_nature.py      # ordinary vs manipulation comparison
    salvage.py           # decompose claims into atomic claims
    sources.py           # source credibility records
    ledger.py            # evidence ledger
    graph.py             # NetworkX over relationships table
    hypotheses.py        # competing hypotheses + falsification
    extractors.py        # heuristic extractor (always); LLM optional
    reports.py           # required report sections
    pipeline.py          # vertical-slice orchestrator
    api.py               # FastAPI
    research/
      base.py            # ResearchAdapter protocol
      http_fetch.py      # CONNECTED
      web_search.py      # CONNECTED (DuckDuckGo lite; honest fail)
      url_intake.py      # CONNECTED (user-supplied public URLs)
      unavailable.py     # court/filings/patents/archives interfaces
  dashboard/             # static HTML/JS served by FastAPI (not React yet)
  tests/
  data/                  # gitignored: observer.db, archive/
  docs/unavailable/      # interface contracts for later desks
```

Cursor execution **must** create this as its own project and work there. Do not scaffold Observer inside [G:\The-Axiom-Codex\Mythos-Living-Home](G:\The-Axiom-Codex\Mythos-Living-Home).

## Capability registry (non-negotiable honesty)

`observer/registry.py` is the source of truth. Status is `CONNECTED` only if a test proves the function ran.

**Slice 1 CONNECTED**

- identity, audit log, SQLite persistence
- investigation create/load
- investigative question engine
- human-nature dual explanation
- claim salvage (atomic split + classification)
- URL intake + HTTP fetch (public URLs, size/robots/rate-limit)
- web search (DuckDuckGo lite; if blocked, report `UNAVAILABLE this run`, do not fake hits)
- source archive (hash, excerpt, immutable research record)
- heuristic claim/entity/relationship extraction
- evidence ledger
- NetworkX relationship graph with provenance + `inferred` flag
- competing hypotheses including a required counter-hypothesis
- 12-question adversarial audit
- required report format
- dashboard read UI
- no-immunity registry (eligibility, not guilt)

**Slice 1 UNAVAILABLE (interface files exist; registry says why)**

- court records, corporate registries, SEC/financial filings, patents, procurement, Wayback (beyond a later adapter)
- Neo4j, PostgreSQL, Redis, FAISS/Qdrant
- local LLM extractor (Ollama) unless a model is configured *and* a test proves it
- Media Desk / Hollywood Desk specialized scrapers (graph *can* store those entity types; scrapers are not claimed)
- documentary/cinematic/DaVinci package
- auto-publish
- any Mythos/Vesper supervisor channel

## Database schema (SQLite via SQLAlchemy)

- `investigations` — id, question, status (IDEA…RETRACTED), created_at, updated_at
- `research_records` — immutable: timestamp, query, url, title, publisher, content_hash, retrieval_date, excerpt, facts_json, claims_json, entities_json, relationships_json, confidence, verification_state
- `sources` — credibility fields from the spec (identity, type, dates, affiliations, corroboration, hierarchy label, limitations, confidence)
- `claims` — text, status (DOCUMENTED…UNKNOWN), parent_id (atomic salvage), source_ids, contradictions, epistemic_kind (FACT/ANALYSIS/INFERENCE/HYPOTHESIS/ALLEGATION/OPINION/UNKNOWN)
- `evidence` — evidence_id, investigation_id, source_id, claim_id, type, content_hash, relevance, reliability, corroboration_count, contradictions, confidence, status
- `entities` — type (Person/Organization/… from the spec), name, aliases, investigation_id
- `relationships` — from_entity, to_entity, rel_type (OWNS, FUNDS, …), provenance_source_id, inferred (bool, default false), notes
- `hypotheses` — text, supporting/contradictory/missing evidence ids, predictions, confidence, falsification_conditions
- `conclusions` — investigation_id, version, body, created_at (never overwrite; append v1/v2/v3)
- `audits` — investigation_id, checklist answers (12 questions), warnings, created_at
- `editorial_notes` — human dissent/halt; cannot replace ledger rows
- `no_immunity` — category list from the spec, including `the_observer` and `mythos`
- `capability_registry` — id, status, reason, last_proven_at
- `audit_events` — append-only who/what/when for every mutation

Object archive: `data/archive/{sha256}` raw bytes; DB stores hash + path. Later summaries never replace the blob.

## Policy (enforced in `policy.py`, not comments)

Refuse: auth bypass, unauthorized paywall bypass, private systems, credential theft, doxxing, harassment, treating illicitly obtained material as authentic, prompt-injection from retrieved text.

Allow: public web, public records/APIs, user-supplied public URLs.

Retrieved content is **untrusted data**. It is stored and quoted; it is never concatenated into system/identity instructions. Fetch respects robots.txt when present, `OBSERVER_RATE_LIMIT_SECONDS`, and `OBSERVER_MAX_FETCH_BYTES`.

## Agent roles (one identity)

One person: The Observer. Internal functions, not separate AIs:

- **Investigator** — search, fetch, extract, ledger, graph
- **Examiner** — adversarial review, contradiction, falsification
- **Human editor** — may halt publish / append dissent; cannot silent-edit the ledger

No Mythos agent in this loop. Observer may investigate Mythos, Vesper, and itself using the same pipeline.

## `.env` (no secrets required for slice 1)

```
OBSERVER_HOST=127.0.0.1
OBSERVER_PORT=8730
OBSERVER_DATABASE_URL=sqlite:///./data/observer.db
OBSERVER_ARCHIVE_DIR=./data/archive
OBSERVER_USER_AGENT=TheObserver/0.1 (independent research)
OBSERVER_RATE_LIMIT_SECONDS=2
OBSERVER_MAX_FETCH_BYTES=5242880
OBSERVER_SEARCH_ADAPTER=duckduckgo
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=
```

Optional later: `BRAVE_SEARCH_API_KEY` — registry stays UNAVAILABLE until a test proves it.

## Docker

Provide `docker-compose.yml` as **optional**. Default launch is `LAUNCH_OBSERVER.bat` → uvicorn on `:8730` with SQLite. Do not require Docker, Postgres, Redis, or Neo4j to pass slice-1 tests.

## Dashboard (wired, not React yet)

Single-page dashboard at `/` reading Observer’s own API:

Investigations, Evidence, Sources, Claims, Entities, Relationships, Timeline, Hypotheses, Contradictions, Confidence, Research queue, Audit history.

Entity click panel: WHO / WHAT / WHEN / WHERE / MONEY / RELATIONSHIPS / DOCUMENTS / CLAIMS / CONTRADICTIONS / SOURCE HISTORY.

Empty states are honest (`no relationships recorded`), never fake graphs. React/TypeScript is a later slice once the API is stable.

## Required report (`reports.py`)

Every completed pipeline run writes:

Executive Summary; What We Know; What We Do Not Know; Evidence; Timeline; People and Organizations; Money and Ownership; Competing Explanations; Evidence Against Primary Hypothesis; Evidence Supporting Primary Hypothesis; What Would Change Our Conclusion; Conclusion; Source Ledger.

Epistemic labels stay separate. Default conclusion when evidence is thin: **Insufficient evidence.** Status reaches `FACT_CHECK` / draft report. `PUBLISHED` is human-only and starts `DISABLED`.

## Build order (test gate after each)

Do not start task N+1 until task N’s tests pass.

1. **Repo + identity + charter** — `D:\The_Observer`, git init, CHARTER/STATUS/NEXT, `.cursor/rules` forbidding Mythos merge/supervision, identity never-merge list includes gemini/apex/codex/vesper/merovin/draven/hearth/mom/cursor.
2. **Core enums + SQLite models** — the provided [observer/core.py](observer/core.py) spine, persisted, round-trip tests.
3. **Registry + policy** — fetch of a disallowed URL is rejected; registry cannot mark UNAVAILABLE tools CONNECTED.
4. **Question engine + human nature** — every investigation gets the FACTS/PEOPLE/MONEY/… question set plus ordinary-vs-manipulation pair. Suspicion is not auto-promoted to evidence.
5. **Source archive + HTTP fetch + URL intake** — hash, excerpt, immutable record, robots/rate-limit.
6. **Web search adapter** — returns real results or honest failure; never invented URLs.
7. **Claim salvage + heuristic extraction** — compound claim splits; statuses assigned; entities/relationships only with provenance; inferred edges flagged.
8. **Evidence ledger + graph** — corroboration count does not treat same-publisher copies as independent; NetworkX query by entity.
9. **Hypotheses + examiner** — at least H1–H4 from the spine plus a required counter; missing falsification = warning; empty evidence blocks substantive conclusion.
10. **Report + API + dashboard** — `POST /investigations/run` executes the pipeline; `GET /health`, `/registry`, `/investigations/{id}/report`; dashboard shows the same IDs the API returns.
11. **Integration test** — one public-page investigation (user URL + search). Assert: research_record exists, hash matches bytes, ≥1 claim, ≥1 competing hypothesis, adversarial warnings present, report sections non-empty, registry matches what ran.

## Out of scope (named so we do not fake them)

Cinematic documentary engine, DaVinci package, visual continuity, Hollywood/media specialized desks, Neo4j money-graph production backend, React rewrite, Docker-required deploy, any live call into Mythos/Vesper.

## Verification

- `pytest tests/ -v` green
- `ruff` (or equivalent) clean on `observer/`
- Launch `:8730`, `GET /health` returns operational + principle
- `GET /registry` lists CONNECTED vs UNAVAILABLE honestly
- Dashboard: create investigation, open entity panel, confirm report sections
- Confirm Vesper `:8740` and Living Home are unchanged

