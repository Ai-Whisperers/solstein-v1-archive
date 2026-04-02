# STORY-041: Eliminate `: Any` Type Annotations Across the Codebase

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-012: Type Safety & Code Quality](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-023: Define Value Objects](../../EPIC-007-ddd-migration/STORIES/STORY-023.md), [STORY-025: Repository Interfaces](../../EPIC-007-ddd-migration/STORIES/STORY-025.md) |

---

## The Audit Verdict
> 90 instances of `: Any` annotations appear across 32 files. `domain/models.py` alone has 10+. Each `Any` annotation is a hole in the type system — mypy cannot check code that interacts with an `Any`-typed value, meaning entire chains of logic are invisible to static analysis.

## Problem Statement
`Any` annotations defeat the purpose of having a type system. They propagate — a function that accepts `Any` causes every caller to also escape type checking. The domain model, which should be the most strictly typed part of the codebase, has the most `Any` annotations. This is precisely backwards: the domain layer is where type errors have the highest business impact.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Type Safety** | Entire chains of logic are invisible to mypy — type errors propagate silently through `Any`-typed values |
| **Refactoring Safety** | Cannot rely on mypy to catch breaking changes — renaming a field or changing a return type produces no warnings for `Any`-typed consumers |
| **Documentation** | `Any` types communicate no information about expected data shape — the type annotation is worse than absent because it suggests deliberate choice |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | 10+ `Any` annotations — replace with concrete domain types |
| 31 other files across the codebase | Modify | Run `grep -rn ": Any" src/` for the complete list |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: No `: Any` annotation may appear in the domain layer (`domain/`)
- **REQ-2**: No `: Any` annotation may appear in the application layer (`application/`)
- **REQ-3**: Infrastructure layer `Any` annotations must be justified with an inline comment explaining why a concrete type is not possible (e.g., third-party library returns untyped data)
- **REQ-4**: Each replacement type must be the most specific type that accurately describes the value — `Union[str, int]` is acceptable where accurate; `Any` is not
- **REQ-5**: After replacement, `mypy --strict` must report no new errors introduced by this change

## Acceptance Criteria
- [ ] `grep -rn ": Any" src/solstein/domain/` returns zero results
- [ ] `grep -rn ": Any" src/solstein/application/` returns zero results
- [ ] All remaining `: Any` in infrastructure layer have justification comments
- [ ] mypy passes on all modified files with no new errors

## Definition of Done

**Tests Required:**
- [ ] `mypy --strict` run on all changed files with zero new errors
- [ ] Existing tests continue to pass (type changes must not break runtime behaviour)

**Documentation Required:**
- [ ] Infrastructure layer `Any` justification comments serve as inline documentation

**Code Review Gate:**
- [ ] Reviewer confirms each replacement type is accurate — not just "not Any"
- [ ] Reviewer confirms no `Any` suppression via `# type: ignore` was introduced as a workaround

## Notes
This is a large-surface-area change that touches 32+ files. It should be broken into sub-PRs by layer: domain first, then application, then infrastructure. The domain layer must be completed before the application layer, because application layer types depend on domain types. STORY-023 (Value Objects) should be completed first so that domain model fields can use Value Object types rather than replacing `Any` with primitives that will themselves need replacement later.

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
