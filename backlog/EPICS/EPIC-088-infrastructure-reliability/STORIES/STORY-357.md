# STORY-357: Verify and Harden Celery Health Check Endpoint

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | XS (2 hours) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (rewritten after codebase audit) |
| **Risk** | Low |

---

## Actual Codebase State (verified 2026-04-03)

**The Celery health check IS implemented:**
- File: `src/solstein/api/routers/health.py:156`
- Endpoint: `GET /workers` — `worker_health()` function
- Implementation calls `celery_app.control.inspect(timeout=_ht.health_celery_inspect).ping()`
- Returns: `{timestamp, workers: [{name, status}], status}` where status ∈ `{"healthy", "degraded", "no_workers", "unreachable"}`
- **Always returns HTTP 200** — "degraded doesn't block Kubernetes readiness"

**Gaps found:**
1. The endpoint always returns HTTP 200, even when all workers are unreachable. Kubernetes `readinessProbe` and monitoring systems can't distinguish "no workers" from "healthy".
2. No test verifies the response shape or status transitions.

---

## Problem Statement

The Celery health check exists and calls `control.inspect().ping()` correctly, but it always returns HTTP 200 regardless of worker availability. Kubernetes and external monitors cannot use this to detect worker outages.

This story is a hardening task — the core implementation exists but needs response code semantics fixed and tests added.

---

## Acceptance Criteria

- [ ] `GET /workers` returns HTTP 200 when ≥1 worker responds to ping
- [ ] `GET /workers` returns HTTP 503 (Service Unavailable) when `status == "no_workers"` or `status == "unreachable"`
- [ ] `GET /workers` returns HTTP 200 with `status: "degraded"` when some but not all workers are healthy (degraded is non-fatal)
- [ ] Test: mock `celery_app.control.inspect().ping()` returning `None` → assert HTTP 503
- [ ] Test: mock returning `{"worker@host": {"ok": "pong"}}` → assert HTTP 200 and `status: "healthy"`
- [ ] `ruff check` passes at 0 errors

---

## Tasks

- [ ] Read `src/solstein/api/routers/health.py:156` — confirm current implementation
- [ ] Change `worker_health()` to return HTTP 503 when `status in ("no_workers", "unreachable")`
- [ ] Add unit tests in `tests/unit/test_health_endpoints.py` (or equivalent) for both scenarios
- [ ] Verify the change doesn't break any existing health check test

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/api/routers/health.py` | 156 | `worker_health()` — change HTTP status here |
