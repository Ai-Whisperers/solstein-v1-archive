# STORY-024: Migrate Company Entity to a Rich Domain Model

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-007: Domain-Driven Design Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-023](STORY-023-introduce-value-objects.md) |

---

## The Audit Verdict

> `domain/models.py` defines `Company` as 613 lines of Pydantic field definitions with 3 properties. Zero business methods. The entity that is the core of a competitive intelligence platform has no intelligence. Classification logic that should live on the entity lives in router handlers instead.

## Problem Statement

An anemic domain model moves business logic out of the domain and into every application layer that touches it. The `Company` entity — the central concept of a competitive intelligence platform — has no methods for classification, no methods for scoring readiness, no methods for data freshness evaluation. These operations are scattered across router handlers, analytics modules, and service files.

The consequences are predictable:
- Classification logic is duplicated wherever classification decisions are made
- Classification thresholds may differ between duplicated implementations
- Testing classification requires an HTTP context because it lives in a router handler
- The CLI and Celery background tasks cannot reuse classification logic without importing router code

A domain entity that does not encapsulate its own behaviour is a data transfer object with aspirational naming.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Architecture** | Business rules scattered across routers, services, and analytics modules |
| **Correctness** | Classification invariants enforced inconsistently across different call sites |
| **Testability** | Business logic requires full application context (HTTP, database) to test |
| **Reusability** | CLI commands and background tasks cannot access router-embedded business logic |
| **Onboarding** | New engineers cannot understand what a Company "does" by reading the Company class |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | Add business methods to `Company` entity |
| `src/solstein/api/routers/enrichment.py` | Modify | Extract classification logic to entity |
| `src/solstein/api/routers/scoring.py` | Modify | Extract scoring readiness logic to entity |
| `src/solstein/analytics/scoring.py` | Evaluate | Move scoring initiation to domain service |
| All callers that perform ad-hoc classification | Modify | Must call entity methods instead |

## Architectural Requirements

- **REQ-1**: The `Company` entity must expose methods for operations that constitute company-level business logic: `classify()` (return tier based on CompositeScore), `is_scored()` (whether scoring has been performed), `has_recent_data(as_of: date)` (whether data is fresh enough for analysis)
- **REQ-2**: State transitions must be controlled by the entity — external code must not directly set fields that have business meaning (e.g., tier, classification status) without going through entity methods
- **REQ-3**: The entity must reject invalid state at construction and at mutation — a Company cannot have a tier that contradicts its CompositeScore
- **REQ-4**: Business logic currently in router handlers that belongs in the domain must be extracted to entity methods or domain services — routers must only parse requests, call domain methods, and format responses

## Acceptance Criteria

- [ ] `Company.classify()` returns a tier based on its `CompositeScore` value
- [ ] `Company.is_scored()` returns whether the company has been scored
- [ ] `Company.has_recent_data(as_of)` returns whether the company's data is fresh enough for analysis
- [ ] Direct field mutation that violates business rules is rejected (e.g., setting tier without a supporting score)
- [ ] Router handlers contain no scoring or classification logic — only service/entity method calls
- [ ] Entity methods can be unit-tested without importing FastAPI or accessing a database

## Definition of Done

**Tests Required:**
- [ ] Unit tests for each new entity method (`classify`, `is_scored`, `has_recent_data`)
- [ ] Test: invalid state transitions are rejected (e.g., tier set without score)
- [ ] Test: classification logic produces the same results as the previously-router-embedded logic (regression test)
- [ ] Test: entity methods work with mock data — no database required

**Documentation Required:**
- [ ] Domain model design documented in code comments explaining the entity's responsibilities
- [ ] Docstrings on each business method explaining its purpose, parameters, and return value

**Code Review Gate:**
- [ ] Reviewer confirms zero business logic remains in router handlers for classification or scoring
- [ ] Reviewer confirms entity methods are independently testable
- [ ] Reviewer confirms regression: classification results match pre-refactoring behaviour

## Notes

This is the most impactful story in the DDD epic. A rich `Company` entity transforms the domain model from a data container into the authoritative source of business behaviour. Every subsequent architectural improvement benefits from a domain model that actually models the domain.

The dependency on STORY-023 (Value Objects) is important: entity methods like `classify()` will use `CompositeScore` as a Value Object with typed components, not a raw `float`. Complete Value Objects first.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
