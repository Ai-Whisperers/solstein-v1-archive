# STORY-043: Resolve Primitive Obsession in Domain Types

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-012: Type Safety & Code Quality](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-023: Define Value Objects](../../EPIC-007-ddd-migration/STORIES/STORY-023.md) |

---

## The Audit Verdict
> `domain/models.py` uses `revenue: float`, `employees: int`, `score: float` throughout. These primitives carry domain meaning — revenue is not merely a float, it is a monetary amount in a specific currency at a specific point in time. The type system cannot enforce this. Nothing prevents `revenue = -999999.0` from being stored.

## Problem Statement
Primitive obsession — using basic types where domain-specific types are appropriate — allows invalid domain states to be constructed and propagated silently. A `float` that represents revenue has no currency, no point-in-time reference, and no positivity constraint. The type system provides no assistance in enforcing business invariants. A negative employee count, a revenue figure in the wrong currency, or a score exceeding the ceiling are all representable and will propagate through the entire pipeline without error.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Invalid values (negative revenue, negative employees, scores beyond ceiling) are representable and storable without error |
| **Type Safety** | mypy cannot enforce currency denomination or positivity constraints on `float` fields — `revenue` and `temperature` are the same type |
| **Domain Integrity** | Domain rules must be re-enforced at every call site rather than once at construction — a rule enforced everywhere is enforced nowhere |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | Replace primitive field types with Value Objects |
| All files constructing domain objects with raw primitives | Modify | Update construction sites to use Value Objects |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Once STORY-023 Value Objects are implemented, all domain model fields that represent domain concepts must use Value Objects rather than primitives
- **REQ-2**: Construction of domain objects with invalid primitives must raise a domain exception, not silently accept the value
- **REQ-3**: Serialisation to/from database and API must handle Value Object ↔ primitive conversion at the infrastructure boundary only — domain code must never interact with raw primitives for domain concepts
- **REQ-4**: mypy must be able to distinguish `Revenue` from `float` — accidental assignment must be a type error

## Acceptance Criteria
- [ ] `Company.revenue` is of type `Revenue`, not `float`
- [ ] `Company.employees` is of type `EmployeeCount`, not `int`
- [ ] Constructing `Revenue` with a negative amount raises a domain exception
- [ ] mypy catches assignment of `float` to `Revenue` field
- [ ] Constructing `EmployeeCount` with a negative value raises a domain exception

## Definition of Done

**Tests Required:**
- [ ] Unit tests: Value Object invariant enforcement (negative values, out-of-range values rejected)
- [ ] Type test: mypy catches incorrect primitive assignment to Value Object fields

**Documentation Required:**
- [ ] Value Object usage patterns documented in `docs/contributing.md`

**Code Review Gate:**
- [ ] Reviewer confirms no domain model field uses a primitive type for a domain concept
- [ ] Reviewer confirms Value Object ↔ primitive conversion occurs only at infrastructure boundaries

## Notes
This story depends on STORY-023 (Value Objects) being completed first. The Value Objects defined there become the types used here. The migration should proceed model-by-model: start with the `Company` entity, then expand to other domain objects. Each model migration can be a separate PR to keep review scope manageable. Infrastructure boundary conversion (database mappers, API serializers) must be updated simultaneously to prevent runtime errors.

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
