# EPIC-007: Domain-Driven Design Migration

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-023, STORY-024, STORY-025, STORY-026, STORY-027 |
| Created | 2026-02-28 |

---

## Summary

The domain model is an empty shell.

`domain/models.py` is 613 lines of Pydantic field definitions. It has 3 properties and zero business methods. `revenue` is a bare `float`. `employees` is a bare `int`. No currency. No bounds. No historical tracking. A `Company` entity that does not encapsulate any company logic is not a domain model — it is a database schema with a different name.

A competitive intelligence platform whose core `Company` entity has no intelligence is architecturally incoherent. Classification logic, scoring algorithms, threshold evaluation — all of this lives in router handlers and scattered service files rather than in the entity that represents the thing being classified, scored, and evaluated.

## The Problem

The codebase has a `domain/` directory. It has a `models.py` file. It looks like Domain-Driven Design. But the domain model is anemic: it defines data shapes without business behaviour. The 10+ `Any` type annotations in `domain/models.py` alone signal that the type system has been abandoned at the very boundary where it matters most.

This epic introduces the foundational DDD elements absent from the codebase:

### Value Objects
Revenue as a bare `float` is meaningless. A revenue of `1000000.0` contains no information about currency, reporting date, or data source. `EmployeeCount` as a bare `int` can be negative. `CompositeScore` carries no timestamp of when it was computed. Value Objects enforce invariants at construction time — invalid states become unrepresentable.

### Rich Entity Behaviour
The `Company` entity should know how to classify itself, determine if it has recent data, and validate its own state transitions. These are not application-layer concerns — they are intrinsic to what a Company is.

### Repository Interfaces
`infrastructure/company_repository.py` is a concrete implementation with no abstract interface. Application services call the concrete class directly. Testing requires the real database. A `Protocol`-based repository interface decouples the domain from infrastructure.

### Domain Events
The research pipeline writes directly to the database and outbox without any domain event mechanism. Adding a side effect (cache invalidation, notification, audit log) requires modifying the pipeline itself. Domain events decouple the pipeline from its side effects.

### Domain Services
Scoring logic, classification thresholds, and statistical calculations live in router handlers. They belong in domain services that can be tested independently of HTTP and reused by CLI and background tasks.

## Stories

| Story | Title | Priority | Severity |
|-------|-------|----------|----------|
| [STORY-023](STORIES/STORY-023-introduce-value-objects.md) | Introduce Value Objects for Primitive Domain Concepts | P1 | HIGH |
| [STORY-024](STORIES/STORY-024-migrate-company-rich-domain.md) | Migrate Company Entity to a Rich Domain Model | P1 | HIGH |
| [STORY-025](STORIES/STORY-025-abstract-repository-interfaces.md) | Define Abstract Repository Interfaces | P1 | MEDIUM |
| [STORY-026](STORIES/STORY-026-define-domain-events.md) | Define Domain Events for the Research Pipeline | P1 | MEDIUM |
| [STORY-027](STORIES/STORY-027-extract-domain-services.md) | Extract Domain Services from Router Handlers | P1 | HIGH |

## Definition of Done

- [ ] `Company` entity encapsulates business behaviour — classification, scoring readiness, data recency checks
- [ ] Value Objects replace primitive types for Revenue, EmployeeCount, and CompositeScore
- [ ] Protocol-based repository interfaces exist in the domain layer
- [ ] Domain events are defined for key state transitions (ResearchCompleted, CompanyTierChanged, EnrichmentFailed)
- [ ] Business logic is extracted from router handlers into testable domain services
- [ ] Zero `Any` type annotations remain in domain model files
- [ ] All new domain code has unit tests that run without HTTP or database context

## Ordering Notes

STORY-023 (Value Objects) should be completed before STORY-024 (rich domain model) because the entity methods will use Value Objects. STORY-025 (repository interfaces) is independent and can proceed in parallel. STORY-026 (domain events) depends on STORY-024 because events are emitted by entity state transitions. STORY-027 (domain services) depends on STORY-024 and STORY-025 because services use the rich entity and depend on repository interfaces.

Recommended execution order: STORY-023 → STORY-024 → STORY-027, with STORY-025 and STORY-026 in parallel after their dependencies are met.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
