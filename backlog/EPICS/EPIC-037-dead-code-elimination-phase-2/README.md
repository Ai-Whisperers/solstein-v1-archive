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
