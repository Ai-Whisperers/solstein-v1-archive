# STORY-142: Delete Orphaned worker_tasks_v2.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-037: Dead Code Elimination Phase 2 |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> worker_tasks_v2.py — 713 lines, 13 task definitions, ZERO production callers. Only used by tests/unit/test_worker_tasks_v2.py.

## Problem Statement

There's an entire Celery task module — 713 lines — that nobody calls. It appears to be a refactored version of worker_tasks.py that was never integrated. The tests exist. The code is maintained (probably). But no production code ever schedules these tasks. It's a parallel universe where the tasks were refactored but the refactor was never completed. Meanwhile, the original worker_tasks.py continues to run in production.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 713 lines of dead code |
| **Confusion** | Which is canonical? |
| **Test Time** | Tests for unused code |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/worker_tasks_v2.py` | Orphaned task module |
| `tests/unit/test_worker_tasks_v2.py` | Tests for orphaned code |

## Architectural Requirements

- Confirm zero production callers (grep for .delay(), .apply_async(), send_task() with v2 task names)
- Archive or delete worker_tasks_v2.py
- Delete test_worker_tasks_v2.py (or archive)
- If any v2 tasks have better implementations, port to worker_tasks.py first (STORY-092 scope)
- Update any documentation referencing v2

## Acceptance Criteria

- [ ] worker_tasks_v2.py deleted
- [ ] test_worker_tasks_v2.py deleted
- [ ] No references to v2 tasks in codebase
- [ ] Celery worker starts without v2 tasks

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: None
- **Code Review Gate**: grep for "worker_tasks_v2" returns nothing

## Notes

Parallel universe code that was never integrated.

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
