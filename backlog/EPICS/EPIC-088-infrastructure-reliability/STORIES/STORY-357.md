# STORY-357: Harden Celery Health Check — Return HTTP 503 When Workers Unreachable

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P2 |
| **Size** | S (half day) |
| **Epic** | EPIC-088 Infrastructure Reliability |
| **Created** | 2026-04-03 |
| **Updated** | 2026-04-03 (deep wiring audit) |
| **Risk** | Low |

---

## Exact Codebase Wiring (deep audit 2026-04-03)

### Current Implementation (`src/solstein/api/routers/health.py:156–187`)

```python
@router.get("/workers", name="worker_health")
async def worker_health() -> dict:
    """...Returns degraded (HTTP 200) rather than 503 so it never blocks
    Kubernetes readiness — worker failures are non-fatal for the API."""
    import datetime as _dt
    from ...celery_config import celery_app

    result: dict = {
        "timestamp": _dt.datetime.now(timezone.utc).isoformat(),
        "workers": [],
        "status": "degraded",
    }
    try:
        from solstein.config import get_settings as _get_settings
        _ht = _get_settings().http_timeouts
        inspect = celery_app.control.inspect(timeout=_ht.health_celery_inspect)
        ping_result: dict | None = inspect.ping()
        if ping_result:
            result["workers"] = [{"name": w, "status": "online"} for w in ping_result]
            result["status"] = "healthy"
        else:
            result["status"] = "no_workers"     # line 183 — returns HTTP 200 ← GAP
    except Exception as exc:
        result["error"] = str(exc)
        result["status"] = "unreachable"        # line 186 — returns HTTP 200 ← GAP
    return result
```

**All endpoints in health.py**:

| Endpoint | Handler | HTTP on failure | Line |
|----------|---------|-----------------|------|
| `GET /health` | `health_check()` | 503 when component unhealthy | 22–55 |
| `GET /health/status` | `health_status()` | 200 always | 58–63 |
| `GET /health/ready` | `readiness_check()` | 503 when not ready | 66–95 |
| `GET /health/live` | `liveness_check()` | 200 always | 98–107 |
| `GET /metrics` | `get_metrics()` | 200 | 113–135 |
| `GET /health/workers` | `worker_health()` | **200 always — bug** | 156–187 |

**Call chain**: `GET /health/workers` → `celery_app.control.inspect(timeout=N)` → `inspect.ping()`
- `ping()` returns `{worker_name: {"ok": "pong"}, ...}` when workers online
- `ping()` returns `None` on timeout or no workers
- `ping()` raises `Exception` when broker unreachable (connection refused, etc.)

**Current HTTP response for each scenario**:

| Scenario | `status` field | HTTP code | Correct? |
|----------|----------------|-----------|---------|
| Workers healthy | `"healthy"` | 200 | ✅ |
| No workers (idle broker) | `"no_workers"` | 200 | debatable |
| Broker exception/timeout | `"unreachable"` | 200 | ❌ |

### APIError pattern used elsewhere (`health.py:66`)

```python
from ..exceptions import APIError
raise APIError(
    code="SERVICE_UNAVAILABLE",
    message="...",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
)
```

---

## Problem Statement

`GET /health/workers` returns HTTP 200 even when the Celery broker is completely unreachable (`status: "unreachable"`). Monitoring systems, load balancers, and Kubernetes readiness probes all treat 200 as healthy — they cannot distinguish between a working worker pool and a completely dead one.

The endpoint docstring explicitly says "never blocks Kubernetes readiness", but this is now the wrong policy — infrastructure monitoring needs an accurate 503.

---

## Acceptance Criteria

- [ ] `GET /health/workers` returns **HTTP 503** when `status == "unreachable"` (broker exception or timeout)
- [ ] `GET /health/workers` returns **HTTP 503** when `status == "no_workers"` (broker reachable but no workers connected — this is a degraded state that should page on-call)
- [ ] `GET /health/workers` returns HTTP 200 only when `status == "healthy"` (at least one worker responded to ping)
- [ ] Response body is unchanged — still includes `timestamp`, `workers`, `status`, and optional `error` fields
- [ ] Docstring updated to remove "never blocks Kubernetes readiness" claim
- [ ] Test: mock `inspect.ping()` returning `None` → assert HTTP 503
- [ ] Test: mock `inspect.ping()` raising exception → assert HTTP 503
- [ ] Test: mock `inspect.ping()` returning valid dict → assert HTTP 200

---

## Tasks

- [ ] Modify `health.py:156–187`:
  ```python
  if ping_result:
      result["workers"] = [{"name": w, "status": "online"} for w in ping_result]
      result["status"] = "healthy"
      return result                          # HTTP 200
  else:
      result["status"] = "no_workers"

  # Fall through to 503 for no_workers or unreachable
  except Exception as exc:
      result["error"] = str(exc)
      result["status"] = "unreachable"

  raise APIError(
      code="WORKER_UNAVAILABLE",
      message=f"Celery workers unavailable: {result['status']}",
      status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
      details=result,
  )
  ```
- [ ] Update docstring to remove "never blocks Kubernetes readiness" claim
- [ ] Write tests in `tests/unit/test_health_worker_check.py`

## Key Files

| File | Line | Note |
|------|------|------|
| `src/solstein/api/routers/health.py` | 156–187 | `worker_health()` — the full function to modify |
| `src/solstein/api/routers/health.py` | 66–95 | `readiness_check()` — example of correct 503 pattern |
| `src/solstein/api/exceptions.py` | — | `APIError` class to raise |
| `src/solstein/celery_config.py` | 26 | `celery_app` — imported inside function |
