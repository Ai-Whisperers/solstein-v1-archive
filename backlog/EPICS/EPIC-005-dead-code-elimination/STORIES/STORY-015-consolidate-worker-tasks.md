# STORY-015: Consolidate Competing Worker Task Files

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-005: Dead Code Elimination](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `worker_tasks.py` and `worker_tasks_v2.py` both exist in the codebase with overlapping task definitions and no documentation explaining which is canonical or whether both are in use. Celery workers configured to load one will silently miss tasks defined only in the other.

## Problem Statement

Two worker task files with overlapping definitions create ambiguity about which tasks are actually registered with the Celery worker. This is not a minor style issue — missing task registration means work silently disappears. A task defined in `worker_tasks.py` but not in `worker_tasks_v2.py` (or vice versa) will execute or not depending entirely on which file the Celery worker was configured to import. There is no error, no warning, no log entry. The task simply never runs.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Tasks defined in the non-canonical file may never execute — silently |
| **Maintainability** | Every task change must be evaluated against an unknown number of task files |
| **Debugging** | "Why didn't this task run?" is unanswerable without knowing which file the worker loaded |
| **Onboarding** | New engineers cannot determine which file to modify for task changes |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/worker_tasks.py` | Evaluate | May be canonical or may be legacy |
| `src/solstein/worker_tasks_v2.py` | Evaluate | May be canonical or may be the migration target |
| Celery worker configuration | Modify | Must explicitly register the canonical file |
| Final consolidated file | Create/Modify | Single source of truth for all worker tasks |

## Architectural Requirements

- **REQ-1**: A single worker tasks file must contain all active task definitions
- **REQ-2**: The canonical file must be explicitly registered in the Celery worker configuration
- **REQ-3**: The retired file must be deleted, not commented out or renamed to `.bak`
- **REQ-4**: Any tasks unique to either file must be explicitly evaluated — retained in the canonical file or deleted with documented justification

## Acceptance Criteria

- [ ] One worker tasks file exists in the codebase
- [ ] All active Celery tasks are registered and discoverable by the Celery worker
- [ ] `grep -r "worker_tasks_v2" .` returns zero results
- [ ] The Celery worker configuration references the canonical file explicitly

## Definition of Done

**Tests Required:**
- [ ] Each task in the canonical file is discoverable by the Celery worker (test task registration)
- [ ] A task submitted to Celery executes successfully (smoke test)

**Documentation Required:**
- [ ] Comment in the canonical worker tasks file noting the consolidation date and the fact that `worker_tasks_v2.py` was retired

**Code Review Gate:**
- [ ] Reviewer confirms that all tasks from both files have been accounted for — either retained or explicitly removed with justification

## Notes

The first step is an audit: diff the two files to identify which tasks exist in which file and whether any tasks are unique to one file. Do not merge blindly — understand what each file contains before choosing the canonical version. The file with the superset of active, tested tasks is the canonical file.
