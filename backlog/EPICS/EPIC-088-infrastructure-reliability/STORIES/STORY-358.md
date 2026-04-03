# STORY-358: Add Startup Check — Verify Celery Broker Reachable Before App Accepts Traffic

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Risk** | Low |

---

## Problem Statement

The FastAPI application boots and accepts HTTP traffic even when Redis (the Celery broker) is unreachable. Tasks submitted to Celery silently queue and never execute. There is no startup warning or failure that signals this condition to operators.

## Acceptance Criteria

- [ ] FastAPI `@app.on_event("startup")` (or `lifespan`) includes a broker reachability check
- [ ] If broker unreachable: logs a `CRITICAL` level warning — app still boots (degraded mode, not hard fail)
- [ ] `/health` endpoint reflects `celery.broker_reachable: false` when broker is down
- [ ] Unit test: mock Redis unavailable, confirm startup log message and health flag

## Tasks

- [ ] Add `check_broker_reachable()` function: attempt `redis.ping()` using the configured broker URL
- [ ] Call it in the FastAPI `lifespan` startup block in `src/solstein/api/main.py`
- [ ] Set a module-level flag `_broker_reachable: bool` consumed by `check_celery()`
- [ ] Add the flag to the `/health` response under `celery.broker_reachable`
