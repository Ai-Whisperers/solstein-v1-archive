# TypeScript Issue Mapping — 2026-03-26

## Purpose

This document maps the ordered audit fixes to the places where TypeScript can materially reduce recurrence.

The rule is simple:

- use Python to fix runtime orchestration, database, Celery, and core business logic
- use TypeScript for strict serialized contracts at boundaries where payload drift is the actual recurring bug

TypeScript is not a substitute for fixing broken Python control flow. It is a second contract gate where JSON-like payloads cross system boundaries.

---

## Ordered Issue Mapping

### ISSUE-11 — `enrich_batch()` silently substitutes original company on failure

**Current Python problem**

- `src/solstein/data/unified/enrichment.py`
- per-company failure appends the original `UnifiedCompany`
- callers receive a homogeneous list of `UnifiedCompany`
- failure semantics are implicit in `_enrichment_failed` and `enrichment_errors`

**Where TypeScript helps**

- batch enrichment result contract
- enrichment outcome envelope for external/UI/tooling consumers
- discriminated union for:
  - `success`
  - `partial`
  - `failure`

**Where TypeScript does not help directly**

- the Python loop still decides what object is returned
- rollback/orchestration semantics remain Python concerns

**Recommended implementation**

1. Fix Python first:
   - stop returning an untagged original company as if it were a normal enriched record
   - return an explicit typed outcome envelope or parallel result metadata
2. Then add TS contract:
   - `BatchEnrichmentCompanyOutcome`
   - discriminated by `status`
   - forbid a “success” payload without materialized enrichment data

**TS priority**

- very high

---

### ISSUE-06 / ISSUE-18 — DLQ durability and traceback retention

**Current Python problem**

- Celery retry exhaustion
- DLQ durability and monitoring

**Where TypeScript helps**

- post-failure audit consumption
- dashboards or tooling that read the DLQ JSONL records

**Where TypeScript does not help directly**

- retry behavior
- traceback capture
- persistence and monitoring emission

**Recommended implementation**

- Python owns the operational fix
- TS may validate the serialized DLQ record shape if a UI/admin tool starts consuming it

**TS priority**

- low for now

---

### ISSUE-04 — scoring silent degradation

**Current Python problem**

- scorer exceptions were converted into plausible numeric outputs

**Where TypeScript helps**

- only at exported score/report payload boundaries

**Where TypeScript does not help directly**

- sub-scorer exception handling
- composite score computation
- classification logic

**Recommended implementation**

- Python fail-fast logic first
- TS later for exported score envelopes if those are consumed outside Python

**TS priority**

- low to medium

---

### Connector Fact Boundary Issues

Examples:

- schema drift across refresh connectors
- fact envelope alias drift
- loose dict payloads

**Where TypeScript helps**

- strongly
- these are exactly the kinds of serialized payload boundaries where `zod` contracts are valuable

**Recommended implementation**

- Python validates live runtime ingestion/persistence
- TS mirrors the same envelope and per-family `value` contracts

**TS priority**

- very high

---

### External API / Heuristic Provider Drift

Examples:

- search fallbacks
- LinkedIn heuristics
- patent/news/fact payloads

**Where TypeScript helps**

- strongly
- these are externalized payloads with provenance and authority semantics

**Current status**

- already started in `tooling/contracts-ts/src/external/`

**TS priority**

- very high

---

## Recommended Next TypeScript Targets

### 1. Batch Enrichment Outcome Contracts

Add a schema family in `tooling/contracts-ts/src/pipeline/` for:

- `BatchEnrichmentCompanyOutcome`
- `BatchEnrichmentResponse`
- `EnrichmentFailureSummary`

Why first:

- directly supports `ISSUE-11`
- converts implicit `_enrichment_failed` semantics into an explicit discriminated union

### 2. Enriched Company Export Envelope

Add a contract for the serialized company shape used after enrichment and before reporting/export:

- identity
- enrichment status
- enrichment errors
- score presence/absence
- source provenance summary

Why:

- this is the main place where “looks successful but is structurally degraded” bugs survive

### 3. Per-Fact-Family Connector `value` Schemas

Build on the existing connector fact envelope contract and add:

- `funding_summary`
- `market_signal`
- `hiring_signals`
- `company_profile`

Why:

- this is the highest-return schema-hardening path after the envelope gate already added in Python

---

## Non-Goals

Do not use TypeScript for:

- Celery task implementations
- SQLAlchemy/DB writes
- internal Python-only scoring algorithms
- retry/backoff orchestration

Those should stay in Python and be hardened with tests plus Pydantic/domain validation.

---

## Recommended Next Combined Move

For the next ordered issue (`ISSUE-11`):

1. change Python batch enrichment to return explicit failure-aware outcome data
2. add matching TypeScript schemas for batch enrichment outcomes
3. validate the API/export boundary against that contract

That is the first place where the Python fix and the TypeScript contract layer should be advanced together.

---

## Solstein-Specific Agentic Engineering Guardrails

These are the best-practice rules that matter most for Solstein specifically, based on the current repo shape:

- `pyrightconfig.json` already exists, but `typeCheckingMode` is still `basic`
- `mypy` is present, but `strict = false` and many error codes are disabled
- MkDocs exists, but API docs are still mostly manual
- the repo already has many local AST-style guard scripts under `scripts/ci/`
- the recurring failures are mostly boundary drift, weak typed handoffs, and stale tests, not syntax mistakes

The implication is:

- do not add more free-form agent text and “smart summaries” as the main safety layer
- add more deterministic, tokenless, syntax-aware, schema-aware enforcement

### 1. Python Boundary Models Must Become Strict Where Drift Actually Hurts

Use Pydantic strictness at critical boundaries instead of relying on coercion.

Why this matters for Solstein:

- many bugs came from loose dicts and shape assumptions
- Pydantic’s default coercion is useful in some intake paths, but harmful in critical business boundaries

Recommended Solstein rule:

- connector outputs, enrichment outcomes, export envelopes, and worker failure records should prefer strict or field-level strict validation
- keep lax parsing only at true external ingestion edges, then normalize immediately into strict internal models

Relevant source:

- Pydantic strict mode supports validation-call, field-level, and config-level strictness

### 2. Replace “Brittle Python Typing by Convention” With Stricter Typed Gates

For Solstein, TypeScript is not the first answer to brittle Python typing. The first answer is:

- stricter Python boundary types
- stricter static analysis
- narrower typed interfaces between pipeline stages

Recommended move:

- adopt `basedpyright` alongside or instead of current CLI `pyright` for high-risk folders first
- use its baseline mode to ratchet strictness without blocking the whole repo

Why this fits Solstein:

- the repo already has `pyrightconfig.json`
- basedpyright provides stricter defaults and baseline support, which is useful for a large messy codebase

### 3. Prefer AST Rules Over Natural-Language Review For Recurring Bug Classes

When a bug class repeats, the fix should become an AST rule or codemod, not just another audit note.

Recommended split:

- use local Python `ast` scripts for lightweight custom checks
- use `ast-grep` for structural search/lint/rewrite across Python and TypeScript
- use `LibCST` codemods for safe Python refactors that must preserve formatting and comments

Why this matters for Solstein:

- the repo already uses custom AST-like lint gates such as `check_async_boundaries.py`
- there are many recurring anti-patterns that are syntax-shaped:
  - `or 0.0` masking score failures
  - direct fallback to original objects in error paths
  - sync helpers called directly in async code
  - dict alias drift like `type` vs `fact_type`

### 4. Docs Should Be Generated From AST And Type Metadata Where Possible

Manual docs are too easy to drift in this repo.

Best-fit tools for Solstein:

- `mkdocstrings-python`
- `Griffe`

Why:

- MkDocs already exists in the repo
- mkdocstrings-python uses Griffe to collect Python object trees and type annotations from source
- Griffe can also serialize API data and detect breaking changes

This is the right “tokenless docs” direction for Solstein:

- generate API/module reference from code
- stop hand-maintaining object signatures and parameter docs when the code already knows them
- use generated reference docs as input material for later AI tooling, not the other way around

### 5. Anti-Slop Rule: Agents Should Edit Under Machine-Checkable Contracts

For this repo, “AI slop” usually means one of these:

- implicit semantics with no schema
- error handling that looks graceful but hides failure
- broad edits with no structural verification
- docs that are not derived from code

Recommended enforcement:

- every fixed issue should add one of:
  - regression test
  - schema gate
  - AST gate
  - codemod
  - generated doc/reference update

If a fix adds none of those, it is probably incomplete.

---

## Tokenless Tooling To Add Next

### A. `ast-grep` Rule Pack For Solstein Anti-Patterns

Use for:

- blocking known bad syntax patterns in CI
- repository-wide structural rewrites
- complementing existing Python-only AST scripts with polyglot structural checks

Immediate candidate rules:

- forbid `growth_score or 0.0` and similar score masking
- forbid appending original company objects in `enrich_batch()` failure paths
- forbid direct creation of “success” batch results when failure markers are present
- forbid writing new connector fact payloads without canonical `fact_type`

### B. `LibCST` Codemods For Python Refactors

Use for:

- safe mass edits where comments/formatting matter
- migrating old field aliases
- replacing stale error-handling patterns
- updating repetitive imports or deprecated interfaces

Immediate candidate codemods:

- normalize score-failure handling sites
- migrate old enrichment result shapes to explicit outcome wrappers
- migrate legacy connector fact aliases or metadata fields

### C. `mkdocstrings` + `Griffe` For Generated Reference Docs

Use for:

- API/module reference pages generated directly from code
- keeping docs synchronized with signatures and annotations
- later API breakage comparisons

Immediate candidate docs:

- `src/solstein/analytics/scoring.py`
- `src/solstein/data/unified/enrichment.py`
- `src/solstein/infrastructure/refresh.py`
- `src/solstein/worker/base.py`
- `src/solstein/worker/enrichment_tasks.py`

### D. `basedpyright` Baseline Rollout

Use for:

- incremental hardening of high-risk folders
- catching optional misuse, unreachable assumptions, and shape drift earlier than runtime

Immediate candidate scope:

- `src/solstein/data/unified`
- `src/solstein/analytics`
- `src/solstein/worker`
- `src/solstein/infrastructure/connectors`

### E. TypeScript Pipeline Contracts

Use for:

- serialized result boundaries
- admin/dashboard/tooling consumers
- regression fixtures validated outside Python

Immediate candidate schemas:

- batch enrichment outcome union
- enriched company export envelope
- DLQ record envelope
- per-fact-family connector values

---

## Issue-Fixing Rule From Now On

Each ordered issue fix should be used as a trigger to add one or more of these:

1. Python runtime fix
2. nearest regression test
3. AST rule or codemod if the bug class is syntactic and repeatable
4. strict boundary schema in Python
5. matching TypeScript schema if the payload crosses a serialized boundary
6. generated or AST-derived docs if the fix changes a public or high-churn interface

That is the only sustainable way to reduce drift in Solstein without replacing the repo with more agent-written prose.

---

## Practical Next Step After ISSUE-11

When implementing `ISSUE-11`, do all of the following together:

1. change Python batch enrichment to emit explicit failure-aware outcome structures
2. add a TypeScript discriminated union for batch enrichment outcomes
3. add an AST guard that forbids reintroducing `enriched_companies.append(company)` in batch error paths
4. add generated or semi-generated docs for the batch enrichment response contract

That gives one issue fix four durable guardrails instead of one temporary patch.

### Status Update

`ISSUE-11` has now been implemented following that exact pattern:

1. Python batch enrichment emits explicit per-company outcomes
2. TypeScript has a matching `batch-enrichment` contract schema
3. AST rule `no-batch-enrichment-fallback-company` blocks the old fallback pattern
4. A dedicated audit record documents the nested cache-contract issue found during implementation

---

## Primary References

- Pydantic strict mode: `https://docs.pydantic.dev/latest/concepts/strict_mode/`
- basedpyright: `https://docs.basedpyright.com/latest/`
- Python `ast`: `https://docs.python.org/3/library/ast.html`
- ast-grep: `https://ast-grep.github.io/`
- LibCST codemods: `https://libcst.readthedocs.io/en/latest/codemods.html`
- mkdocstrings-python: `https://mkdocstrings.github.io/python/`
- Griffe: `https://mkdocstrings.github.io/griffe/`
