# EPIC-088: Infrastructure Reliability & Observability

> **Priority**: P2 – Medium (silent failures undetectable today)
> **Stories**: 3 (STORY-357 through STORY-359)
> **Effort**: S (2–3 days total)
> **Dependencies**: None
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03

---

## Problem

Two infrastructure components fail silently with no detection mechanism:

1. **Celery health check is a placeholder** — `check_celery()` in `monitoring/health.py` returns a hardcoded "healthy" result with 0 actual worker introspection. A complete broker/worker outage appears healthy.

2. **No startup broker reachability check** — the FastAPI app boots successfully even if Redis (the Celery broker) is unreachable. Tasks submitted after boot queue silently and never execute.

3. **No task discovery test** — Beat scheduler has 12 scheduled tasks. There is no test that verifies all 12 task functions are importable and properly decorated. A renamed module silently breaks the entire schedule.

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| STORY-357 | Implement real Celery health check with worker introspection | P2 | S |
| STORY-358 | Add startup check: verify Celery broker reachable before app accepts traffic | P2 | S |
| STORY-359 | Add task discovery test: all Beat-scheduled tasks are importable and decorated | P2 | S |

---

## Definition of Done

- [ ] `check_celery()` in `monitoring/health.py` uses Celery Inspect API to verify active workers
- [ ] FastAPI startup event logs a clear warning (or fails fast) if Redis broker is unreachable
- [ ] A unit test verifies every task path in `celery_config.py` beat schedule is importable
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Key Files

| File | Role |
|------|------|
| `src/solstein/monitoring/health.py` | `check_celery()` placeholder at ~line 255 |
| `src/solstein/api/main.py` | FastAPI startup event — add broker check here |
| `src/solstein/celery_config.py` | Beat schedule with 12 task paths |
