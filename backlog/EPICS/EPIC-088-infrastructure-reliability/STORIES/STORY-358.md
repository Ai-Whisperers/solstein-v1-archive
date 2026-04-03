# STORY-358: Add Startup Check — Verify Celery Broker Reachable Before App Accepts Traffic

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (confirmed not implemented after codebase audit) |
| **Risk** | Low |

---

## Actual Codebase State (verified 2026-04-03)

**No startup broker check exists:**
- `src/solstein/api/main.py` lifespan handler (lines 70–141) initializes: tracing, profiling, cache warming, Supabase Realtime listener
- Celery app is created from config (`src/solstein/celery_config.py`) but never pinged or validated on startup
- Broker URL: `settings.celery_broker_url or "redis://localhost:6379/0"` — passively set, no connectivity check
- If Redis is down at startup, the app boots silently and only fails when a task is enqueued

---

## Problem Statement

The FastAPI application starts successfully even when the Celery broker (Redis) is unreachable. Any background task submitted while Redis is down silently fails. There is no warning at startup that background processing is unavailable.

---

## Acceptance Criteria

- [ ] During the lifespan `startup` phase, attempt a broker connectivity check using `celery_app.control.inspect(timeout=2.0).ping()`
- [ ] If the broker is unreachable: log `CRITICAL` but **do NOT raise** (app must still start — broker may come up after startup)
- [ ] Set a module-level `_broker_reachable: bool = False` flag; update to `True` if ping succeeds
- [ ] Expose `_broker_reachable` via the existing `GET /health` endpoint (add `broker_reachable` field to response)
- [ ] Test: mock `inspect().ping()` returning `None` → assert `_broker_reachable is False` and app still starts
- [ ] Test: mock `inspect().ping()` returning active worker dict → assert `_broker_reachable is True`

---

## Tasks

- [ ] Read `src/solstein/api/main.py:70` — identify the lifespan startup block
- [ ] Add broker reachability check at the end of the startup block (after existing initializations)
- [ ] Add `_broker_reachable` module-level flag to `src/solstein/api/main.py` or a dedicated health module
- [ ] Expose flag in `GET /health` response
- [ ] Write two unit tests as described above

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/api/main.py` | 70 | Lifespan startup block — add check here |
| `src/solstein/celery_config.py` | 28 | Broker URL — used by celery_app |
| `src/solstein/api/routers/health.py` | — | Add `broker_reachable` to response |
