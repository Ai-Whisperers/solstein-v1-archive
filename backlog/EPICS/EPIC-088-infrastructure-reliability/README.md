# EPIC-088: Infrastructure Reliability & Observability

> **Priority**: P2 – Medium (silent failures undetectable today)
> **Stories**: 3 ([STORY-357](STORIES/STORY-357.md) through [STORY-359](STORIES/STORY-359.md))
> **Effort**: S (2–3 days total)
> **Dependencies**: None
> **Status**: 🔴 Not Started
> **Created**: 2026-04-03
> **Updated**: 2026-04-03 (codebase audit corrected all line/function references)

---

## Problem

Two infrastructure components fail silently with no detection mechanism:

1. **Celery worker health check returns wrong HTTP code** — `worker_health()` at `src/solstein/monitoring/health.py:156–187` performs real Celery Inspect introspection but returns HTTP 200 even when `status == "unreachable"` or `status == "no_workers"`. A complete broker/worker outage appears healthy to upstreams.

2. **No startup broker reachability check** — the FastAPI lifespan at `main.py:77–141` runs cache warming but never pings Redis (the Celery broker). App boots successfully even if Redis is unreachable. Tasks submitted after boot queue silently and never execute.

3. **No task discovery test** — the Beat schedule at `celery_config.py:109–184` has **13 static tasks** (12 `refresh_*` + `refresh_all_sources`). There is no test verifying all 13 task functions are importable and decorated. A renamed module silently breaks the entire schedule. The re-export module is `src/solstein/worker_tasks.py`; task factory is `create_refresh_task()` at `worker/refresh_tasks.py:97`.

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| [STORY-357](STORIES/STORY-357.md) | Harden Celery health check — return HTTP 503 when workers unreachable | P2 | S | 🔴 READY |
| [STORY-358](STORIES/STORY-358.md) | Add startup check: broker reachable before accepting traffic | P2 | S | 🔴 READY |
| [STORY-359](STORIES/STORY-359.md) | Add task discovery test — all 13 Beat-scheduled tasks importable and decorated | P2 | S | 🔴 READY |

All three stories are independent and can be worked in any order.

---

## Definition of Done

- [ ] `worker_health()` in `health.py:156` raises `APIError(status_code=503)` for `"unreachable"` and `"no_workers"` states (not HTTP 200)
- [ ] FastAPI lifespan (`main.py:77`) pings Redis broker before accepting traffic; logs error or raises on failure
- [ ] A unit test verifies all 13 task paths in `celery_config.py` beat schedule are importable
- [ ] `pytest` passes at 0 failures, `ruff check` at 0 errors

---

## Key Files (Codebase-Verified 2026-04-03)

| File | Line | Role |
|------|------|------|
| `src/solstein/api/routers/health.py` | 156–187 | `worker_health()` — returns 200 even for "unreachable" (the bug) |
| `src/solstein/api/main.py` | 77–141 | FastAPI lifespan — add broker ping after line 128 (after cache warming) |
| `src/solstein/celery_config.py` | 109–184 | Beat schedule — 13 static task entries |
| `src/solstein/worker_tasks.py` | — | Re-export module for worker tasks |
| `src/solstein/worker/refresh_tasks.py` | 97–185 | `create_refresh_task()` factory |
