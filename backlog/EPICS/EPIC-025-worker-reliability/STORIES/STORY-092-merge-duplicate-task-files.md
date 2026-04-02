# STORY-092: Merge worker_tasks_v2.py — Eliminate Duplicate Task Files

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-025: Worker Reliability |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-088 (persistent DLQ), STORY-089 (acks_late) — the canonical file must incorporate both |

## The Audit Verdict
> `src/solstein/worker_tasks.py` (original) and `src/solstein/worker_tasks_v2.py` (refactored) coexist. Which is authoritative is undocumented. Both are imported in different parts of the codebase.

## Problem Statement

Someone started refactoring the worker task module and didn't finish. Now there are two files defining overlapping task names, with different dependency injection patterns, different error handling strategies, and no clear winner. Callers import from whichever file happened to be convenient at the time — a decision driven by proximity in the file tree rather than architectural intent.

This is a maintenance trap: fixing a bug in one file doesn't fix it in the other, adding a task requires choosing the "right" file (a choice with no documented answer), and every new developer has to deduce canonical state from import archaeology. The longer this coexists, the more the files diverge, and the harder the eventual merge becomes.

The v2 file uses a cleaner dependency injection pattern. The v1 file has the production-tested task definitions. Neither is complete on its own. The merge is overdue.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Bug fixes applied to the wrong file leave the production code path unfixed |
| **Operational** | Ambiguous task registration — overlapping `@shared_task` definitions create silent shadowing |
| **Data Integrity** | No impact if both files define identical logic — but they don't, and the divergence grows |
| **Developer Experience** | New contributors cannot determine which file is canonical without reading both and tracing imports |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/worker_tasks.py` | Original task file — production-tested but uses global reference DI pattern |
| `src/solstein/worker_tasks_v2.py` | Refactored file — cleaner DI pattern but incomplete migration |

## Architectural Requirements
- A single canonical `worker_tasks.py` that merges the best patterns from both files
- `worker_tasks_v2.py` must be deleted from the codebase entirely
- All imports across the codebase must be updated to reference the canonical module only
- The canonical file must use the dependency injection pattern from v2 (parameter-based injection, not module-level global references)
- STORY-088 (persistent DLQ) and STORY-089 (acks_late) must be implemented in the canonical file — do not merge first and refactor second
- The canonical file must have a module-level docstring listing all registered tasks with their schedules and queue assignments
- All 12 Beat-scheduled tasks must be present and functional in the merged file
- No duplicate `@shared_task` definitions for the same task name may exist anywhere in the codebase

## Acceptance Criteria
- [ ] `worker_tasks_v2.py` does not exist in the codebase
- [ ] All task imports reference a single module
- [ ] All 12 Beat-scheduled tasks are present and functional in the merged file
- [ ] No duplicate `@shared_task` definitions for the same task name
- [ ] Module-level docstring lists all tasks with schedules and queues
- [ ] DI pattern from v2 is used throughout the canonical file

## Definition of Done
- **Tests Required**: `grep -r "worker_tasks_v2" .` returns zero results. All existing task integration tests pass against the merged file. No new test gaps introduced.
- **Documentation Required**: Update any developer onboarding docs that reference task file locations. Module-level docstring serves as inline documentation.
- **Code Review Gate**: Reviewer verifies no tasks were lost in the merge by comparing task registrations before and after. Reviewer confirms all imports are updated.

## Notes
- This is the capstone story of EPIC-025. It should be implemented last, after STORY-088 and STORY-089 are complete, since those changes must be incorporated into the canonical file.
- The merge strategy should be: (1) inventory all tasks in both files, (2) identify divergences in logic, (3) resolve each divergence in favor of the correct behavior (not necessarily the newer code), (4) write the canonical file with v2's DI pattern, (5) update all imports, (6) delete v2.
- Beware of Celery task name collisions during the transition. If both files register a task with the same name, Celery uses the last-imported definition. The merge must ensure exactly one definition per task name.

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
