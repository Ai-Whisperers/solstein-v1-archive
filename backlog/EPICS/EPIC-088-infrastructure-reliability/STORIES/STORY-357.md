# STORY-357: Implement Real Celery Health Check with Worker Introspection

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (1 day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Risk** | Low |

---

## Problem Statement

`check_celery()` in `src/solstein/monitoring/health.py` (~line 255) returns a hardcoded healthy result: `{"status": "healthy", "workers": 0}`. A total Celery/Redis outage appears healthy in the `/health` endpoint. Operators have no visibility into worker availability.

## Acceptance Criteria

- [ ] `check_celery()` uses `celery_app.control.inspect(timeout=2.0)` to query active workers
- [ ] Returns `{"status": "healthy", "workers": N, "queues": [...]}` when workers are up
- [ ] Returns `{"status": "degraded", "workers": 0, "error": "no workers found"}` when no workers respond
- [ ] Returns `{"status": "unhealthy", "error": "broker unreachable"}` when broker connection fails
- [ ] Response time capped at 2 seconds (Inspect timeout)
- [ ] Unit test with mocked Celery Inspect: healthy, degraded, and unhealthy paths

## Tasks

- [ ] Read `src/solstein/monitoring/health.py` lines 250-280 to see full placeholder
- [ ] Import `celery_app` from `src/solstein/celery_config.py`
- [ ] Replace placeholder with `inspect = celery_app.control.inspect(timeout=2.0)`; call `inspect.active()`
- [ ] Handle `kombu.exceptions.OperationalError` for broker unreachable
- [ ] Add unit test mocking `celery_app.control.inspect`
