# EPIC-037: Dead Code Elimination Phase 2

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

Forensic audit found DISCONNECTED ROUTER (api/routes/refresh.py — 200+ lines, never included in main.py), ORPHANED CELERY TASKS (worker_tasks_v2.py — 713 lines, 13 tasks, ZERO production callers), and 21 ORPHANED FILES (~2,500 lines) used only by tests or not at all.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-141 | Delete Disconnected Refresh Router | P2 |
| STORY-142 | Delete Orphaned worker_tasks_v2.py | P2 |
| STORY-143 | Audit and Delete Orphaned Data Layer Files | P2 |
| STORY-144 | Create Dead Code Detection CI Job | P2 |

## Dependencies

- EPIC-005 (Dead Code Elimination)
- STORY-124 (delete old adapters)

## Notes

This is not dead code in the traditional sense — it's code that looks alive, has tests probably, but is unreachable from any HTTP request.
