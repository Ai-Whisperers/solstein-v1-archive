# EPIC-025: Worker Reliability

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

The Celery worker system is the backbone of the research pipeline — 12+ Beat-scheduled tasks collecting data from SEC EDGAR, Crunchbase, Companies House, GitHub, Yahoo Finance, NewsAPI, and more. These tasks run every hour to every 24 hours and are the only mechanism for keeping competitive intelligence data fresh.

The problem: the worker system is a reliability liability. The custom `DeadLetterQueue` class is in-memory and evaporates on every worker restart. `task_acks_late` is not configured, meaning a worker crash between task receipt and completion silently drops the task forever. No idempotency means Beat double-fires on restart and tasks execute twice. Results accumulate in Redis indefinitely because `result_expires` is unset. And a half-finished refactor left two parallel task files (`worker_tasks.py` + `worker_tasks_v2.py`) whose canonical state is anyone's guess.

This epic hardens the worker system so that task failures are durable, task execution is safe, and operational state is observable.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-088 | Fix In-Memory DLQ — Persist to PostgreSQL | P1 |
| STORY-089 | Set task_acks_late and task_reject_on_worker_lost | P1 |
| STORY-090 | Implement Task Idempotency via Deduplication Lock | P1 |
| STORY-091 | Set Result Expiry TTL to Prevent Redis Bloat | P1 |
| STORY-092 | Merge worker_tasks_v2.py — Eliminate Duplicate Task Files | P1 |

## Dependencies
- EPIC-002 (Configuration Integrity) — environment-driven config must be stable first
- STORY-087 (Celery DLQ — gap story in EPIC-018) — this epic supersedes that gap story for the persistence requirement; STORY-087 addresses the DLQ concept, EPIC-025 delivers the full implementation

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
