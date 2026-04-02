# STORY-117: Fix Circular Import Risk — Introduce shared/ Package

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-031: Shared Library & Architecture |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `src/solstein/core/` — imported by both `api/` and `domain/`. `domain/` models imported by `api/` AND `infrastructure/`. Layering violations create circular import risk that will manifest as `ImportError` or silent module-level side effects as the codebase grows.

## Problem Statement

The current layer hierarchy is undefined in practice. `core/` is supposed to be foundational, but it imports from `domain/` in some places. `domain/` is supposed to be business logic, but it's imported by `infrastructure/` which is supposed to be outbound adapters. `api/` imports from everywhere. This is not domain-driven design; it is "import what you need and hope Python's import system doesn't notice the cycle." It hasn't noticed yet. It will. The fix is a strict `shared/` package that has zero imports from any domain layer — pure utilities — and a documented import graph that is enforced by a lint rule.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Circular imports cause unpredictable initialization order |
| **Reliability** | Import errors in production are total outages |
| **Developer Experience** | Adding a new import requires circular dependency archaeology |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/core/` | Imports from domain, creates circular risk |
| `src/solstein/domain/` | Imported by infrastructure (layer violation) |
| `src/solstein/api/` | Imports from everywhere |

## Architectural Requirements

- New `shared/` package: contains only pure utilities — retry, logging config, exceptions base classes, constants, datetime utils — zero imports from `api/`, `domain/`, `infrastructure/`, `application/`
- Modules from `core/` that import domain types are moved to `application/` or `domain/services/` instead
- `core/` either becomes an alias for `shared/` or is deprecated and emptied
- Documented import graph: `shared/ → (nothing)`, `domain/ → shared/`, `infrastructure/ → shared/ + domain/`, `application/ → domain/ + infrastructure/`, `api/ → application/ + shared/`
- A lint rule (custom ruff plugin or import-linter config) enforces the documented import graph in CI
- No circular imports verified: `python -c "import solstein"` must complete without circular import warnings

## Acceptance Criteria

- [ ] `shared/` package exists with zero imports from application layers
- [ ] `import-linter` or equivalent configured and passing in CI
- [ ] `python -c "import solstein"` completes with no circular import warnings or errors
- [ ] Layer documentation (import graph) committed to `docs/architecture/`

## Definition of Done

- **Tests Required**: CI lint rule catches deliberately introduced circular import
- **Documentation Required**: Import graph architecture doc
- **Code Review Gate**: Reviewer verifies `shared/` has zero domain imports

## Notes

This establishes clean architecture boundaries.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `READY`.

### Next Agent Action

- Remove measured boundary risk with the smallest viable shared-layer introduction.
- Do not combine this with unrelated retry, CLI, or timezone work.

### Required Working Style

- Prefer explicit import-boundary cleanup and machine-checkable enforcement over large package moves.
- Keep the resulting import graph auditable.

### Minimum Verification For Future Agents

- Prove the cycle/boundary problem is reduced by code shape, not by weakening checks.
- Run the maintained structural gates after the change.
