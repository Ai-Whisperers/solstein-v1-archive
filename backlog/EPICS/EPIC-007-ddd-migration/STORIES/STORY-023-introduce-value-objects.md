# STORY-023: Introduce Value Objects for Primitive Domain Concepts

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-007: Domain-Driven Design Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | STORY-041 (Any type elimination) preferred first |

---

## The Audit Verdict

> `domain/models.py` represents revenue as a bare `float`, employees as a bare `int`. A revenue of `1000000.0` contains no information about currency, reporting date, or data source. A `Company` with `revenue: float` can accept `revenue = -5.0` without complaint.

## Problem Statement

Primitive types carrying domain meaning without domain constraints allow invalid states to be represented and prevent the type system from enforcing business invariants. Every piece of code dealing with revenue must independently handle currency, bounds checking, and source attribution. Every consumer of employee count must independently validate that the number is positive. Every user of a composite score must independently determine when it was computed and whether it is still fresh.

This is not a theoretical concern. A revenue of `-5.0` can propagate through the scoring pipeline and produce nonsensical competitive rankings. An employee count of `0` can trigger division-by-zero in per-employee metrics. A composite score with no timestamp cannot be evaluated for staleness.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Negative revenues, zero headcounts, currency-less financial figures are all representable and undetected |
| **Maintainability** | Currency handling, bounds checking, and source attribution duplicated across every consumer |
| **Type Safety** | `float` and `int` carry no domain meaning — the type system cannot distinguish revenue from temperature |
| **Data Quality** | Invalid values propagate through the pipeline undetected until they produce visible anomalies |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | Replace `float` revenue, `int` employees, and raw score fields with Value Objects |
| `src/solstein/domain/value_objects.py` | Add | New module for `Revenue`, `EmployeeCount`, `CompositeScore` Value Objects |
| All files that construct or consume these fields | Modify | Must use Value Object constructors instead of raw primitives |
| `src/solstein/domain/exceptions.py` | Add/Modify | Domain exceptions for invariant violations |

## Architectural Requirements

- **REQ-1**: `Revenue` must be a Value Object encapsulating amount (`Decimal`), currency (ISO 4217 string), and as-of date (`date`)
- **REQ-2**: `EmployeeCount` must be a Value Object with a positive integer constraint and optional data source attribution
- **REQ-3**: `CompositeScore` must be a Value Object encapsulating the overall score value, component scores (dict), and a `scored_at` timestamp (`datetime`)
- **REQ-4**: All Value Objects must be immutable — once constructed, their values cannot be changed
- **REQ-5**: All Value Objects must validate their invariants at construction time — invalid construction must raise a domain exception, not return a default or silently clamp

## Acceptance Criteria

- [ ] Constructing `Revenue` with a negative amount raises a domain exception
- [ ] Constructing `Revenue` without a currency raises a domain exception
- [ ] Constructing `EmployeeCount` with zero or negative value raises a domain exception
- [ ] `Revenue` carries currency denomination (e.g., `"USD"`, `"EUR"`)
- [ ] `CompositeScore` carries its computation timestamp (`scored_at`)
- [ ] All Value Objects are immutable (frozen Pydantic models or `@dataclass(frozen=True)`)
- [ ] Existing code that constructs `Company` objects is updated to use Value Objects

## Definition of Done

**Tests Required:**
- [ ] Unit tests for each Value Object's invariant enforcement (negative revenue, zero employees, missing currency)
- [ ] Test: currency-less revenue construction rejected
- [ ] Test: Value Object equality is value-based, not identity-based (`Revenue(100, "USD") == Revenue(100, "USD")`)
- [ ] Test: Value Objects are immutable (attribute assignment raises error)

**Documentation Required:**
- [ ] Docstrings on each Value Object explaining its invariants and why they matter
- [ ] Domain model documentation updated to reflect the new Value Object types

**Code Review Gate:**
- [ ] Reviewer confirms all Value Objects validate invariants at construction
- [ ] Reviewer confirms immutability is enforced
- [ ] Reviewer confirms no raw `float`/`int` remains for revenue, employees, or composite score in the domain model

## Notes

Value Objects are the foundation for STORY-024 (rich domain model). The entity methods introduced in STORY-024 will depend on these Value Objects for type safety and invariant enforcement. Complete this story first.

If STORY-041 (Any type elimination) has been completed, the domain model will already have stronger typing, making Value Object integration smoother. If STORY-041 is not yet complete, this story can still proceed — the Value Objects replace specific primitive types, not `Any` types.

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
