# Health Endpoint Reference

## Endpoints

### GET /health

Primary health check endpoint for load balancers and monitoring.

Returns HTTP 200 with per-component status for healthy or degraded states.
Returns HTTP 503 only when critical components (database, configuration) are unhealthy.

**Response (200):**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-27T17:00:00.000000+00:00",
  "components": {
    "database": "healthy",
    "api": "healthy",
    "redis": "healthy",
    "configuration": "healthy",
    "llm_services": "healthy"
  }
}
```

**Response (200 — degraded):**

```json
{
  "status": "degraded",
  "timestamp": "2026-03-27T17:00:00.000000+00:00",
  "components": {
    "database": "healthy",
    "api": "healthy",
    "redis": "unhealthy",
    "configuration": "healthy",
    "llm_services": "degraded"
  }
}
```

**Response (503 — unhealthy):**

Returned only when a critical component (database, configuration) is down.

```json
{
  "status": "unhealthy",
  "components": {
    "database": "unhealthy",
    "api": "healthy",
    "redis": "healthy",
    "configuration": "healthy",
    "llm_services": "healthy"
  }
}
```

### GET /health/status

Full health status with all checks, durations, and details. Intended for operators and dashboards.

### GET /health/ready

Kubernetes readiness probe. Returns 200 if database, API, and configuration are healthy. Returns 503 otherwise.

### GET /health/live

Kubernetes liveness probe. Always returns 200 if the process is running.

### GET /health/workers

Celery worker health check. Returns worker online/offline status. Always returns 200 (worker failures are non-fatal for the API).

## Component Criticality

| Component | Critical | Effect of Failure |
|-----------|----------|-------------------|
| database | Yes | Overall status = unhealthy (503) |
| configuration | Yes | Overall status = unhealthy (503) |
| api | No | Overall status = degraded (200) |
| redis | No | Overall status = degraded (200) |
| llm_services | No | Overall status = degraded (200) |

## Probe Timeouts

Each health check probe has an implicit timeout governed by the underlying connection settings. No `asyncio.sleep` is used in any probe.

- **Database**: Uses SQLAlchemy async engine with configured pool timeout
- **Redis**: Uses redis-py async client with default timeout
- **LLM providers**: Uses the enhanced health checker from `llm/health_checker.py`
- **Configuration**: In-process validation (sub-millisecond)
- **API**: Implicit (if this code runs, API is responsive)
