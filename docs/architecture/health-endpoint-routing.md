# Health Endpoint Routing Conflict

## Problem Statement

The Solstein API has **two separate router implementations** that define overlapping health check endpoints. Both the `health.py` and `enrichment.py` routers register endpoints for `/health` and `/ready`, creating a routing conflict where the same logical endpoint is defined in two places with different implementations.

This document explains the conflict, clarifies which implementations are actually used, and provides recommendations for new code.

---

## The Conflict: Two Implementations

### Health Router (`src/solstein/api/routers/health.py`)

The health router uses a **prefix-based approach** with `APIRouter(prefix="/health")`:

| Endpoint | Route | Handler | Purpose |
|----------|-------|---------|---------|
| `GET /` | `/health` | `health_check()` | Overall health status (200 if healthy, 503 if not) |
| `GET /status` | `/health/status` | `health_status()` | Full health status with all checks |
| `GET /ready` | `/health/ready` | `readiness_check()` | Kubernetes readiness probe |
| `GET /live` | `/health/live` | `liveness_check()` | Kubernetes liveness probe (always 200) |

**Key characteristics:**
- Uses `health_monitor` from `solstein.core.monitoring`
- Runs all health checks on each request
- Returns 503 status code for unhealthy states
- Designed for Kubernetes probes

### Enrichment Router (`src/solstein/api/routers/enrichment.py`)

The enrichment router uses **no prefix** (root-level endpoints):

| Endpoint | Route | Handler | Purpose |
|----------|-------|---------|---------|
| `GET /health` | `/health` | `health_check()` | Platform health check (liveness probe) |
| `GET /ready` | `/ready` | `readiness_check()` | Readiness probe for load balancers |
| `GET /metrics` | `/metrics` | `get_metrics()` | Enrichment performance metrics |

**Key characteristics:**
- Checks database and cache health
- Includes component status details (SEC EDGAR, Companies House, News Signals, Cache)
- Rate-limited (unlike health router)
- Returns detailed component status information
- Designed for enrichment service monitoring

---

## Router Registration Order

In `src/solstein/api/main.py` (lines 132-134):

```python
# Line 132: Enrichment router registered FIRST
app.include_router(enrichment.router)

# Line 133: Health router registered SECOND
app.include_router(health.router)

# Line 134: Metrics router (separate from health router)
app.include_router(health.metrics_router)
```

---

## Path Resolution: Which Implementation Wins?

### FastAPI Routing Behavior

FastAPI processes routers in **registration order**. When multiple routers define the same path, **the first registered router wins**.

### Actual Routing Outcomes

| Requested Path | First Match | Handler | Source |
|---|---|---|---|
| `GET /health` | ✅ Enrichment router | `enrichment.health_check()` | Enrichment (registered first) |
| `GET /ready` | ✅ Enrichment router | `enrichment.readiness_check()` | Enrichment (registered first) |
| `GET /health/status` | ✅ Health router | `health.health_status()` | Health (no conflict) |
| `GET /health/ready` | ✅ Health router | `health.readiness_check()` | Health (no conflict) |
| `GET /health/live` | ✅ Health router | `health.liveness_check()` | Health (no conflict) |
| `GET /metrics` | ✅ Enrichment router | `enrichment.get_metrics()` | Enrichment (no conflict) |

### The Duplicate Endpoints

These endpoints are **shadowed** by the enrichment router:

- `GET /health` — Enrichment implementation is used
- `GET /ready` — Enrichment implementation is used

The health router's implementations of these endpoints are **never reached** because the enrichment router is registered first.

---

## Why This Exists: Historical Context

Both implementations exist because:

1. **Health Router** — Original implementation following Kubernetes probe patterns
   - Designed for standard health check semantics
   - Uses centralized `health_monitor` component
   - Checks database and cache connectivity

2. **Enrichment Router** — Added later for enrichment service monitoring
   - Provides enrichment-specific metrics
   - Includes rate limiting
   - Checks enrichment-specific components (SEC EDGAR, Companies House, News Signals)
   - Designed to monitor the enrichment pipeline

Both implementations check database and cache health, but with different approaches and different response formats. The enrichment router's implementation is more comprehensive for the enrichment service's needs.

---

## Comparison: Health vs. Enrichment Implementations

### Response Format

**Health Router** (`/health`):
```json
{
  "status": "healthy",
  "timestamp": "2025-02-26T10:30:00.000Z"
}
```

**Enrichment Router** (`/health`):
```json
{
  "status": "healthy",
  "timestamp": "2025-02-26T10:30:00.000Z",
  "version": "1.0",
  "components": {
    "database": "operational",
    "cache": "operational",
    "sec_edgar": "operational",
    "companies_house": "operational",
    "news_signals": "operational"
  }
}
```

### Readiness Check Differences

**Health Router** (`/health/ready`):
- Returns 200 if `is_ready()` is true
- Returns 503 if not ready
- Simple boolean response

**Enrichment Router** (`/ready`):
- Returns 200 if system is ready
- Includes detailed readiness checks
- Rate-limited
- Returns component-level readiness status

---

## All Health Check Types

Solstein implements three types of health checks following Kubernetes probe patterns:

### 1. Liveness Probe (`/health/live`)

**Purpose:** Indicates if the process is running and responsive

**Endpoint:** `GET /health/live` (health router only)

**Response:**
```json
{
  "alive": true,
  "timestamp": "2025-02-26T10:30:00.000Z"
}
```

**Behavior:**
- Always returns 200 as long as the process is running
- No external dependencies checked
- Used by Kubernetes to restart unhealthy containers

**When to use:**
- Kubernetes liveness probes
- Container orchestration systems
- Process monitoring

### 2. Readiness Probe (`/ready` or `/health/ready`)

**Purpose:** Indicates if the service is ready to accept traffic

**Endpoints:**
- `GET /ready` (enrichment router — **currently used**)
- `GET /health/ready` (health router — shadowed)

**Response:**
```json
{
  "ready": true,
  "timestamp": "2025-02-26T10:30:00.000Z"
}
```

**Behavior:**
- Returns 200 if ready to serve requests
- Returns 503 if not ready
- Checks database and cache connectivity
- Checks enrichment component initialization

**When to use:**
- Kubernetes readiness probes
- Load balancer health checks
- Traffic routing decisions

### 3. Status Probe (`/health` or `/health/status`)

**Purpose:** Provides detailed component health information

**Endpoints:**
- `GET /health` (enrichment router — **currently used**)
- `GET /health/status` (health router — available)

**Response (Enrichment):**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-26T10:30:00.000Z",
  "version": "1.0",
  "components": {
    "database": "operational",
    "cache": "operational",
    "sec_edgar": "operational",
    "companies_house": "operational",
    "news_signals": "operational"
  }
}
```

**Response (Health Router):**
```json
{
  "status": "healthy",
  "timestamp": "2025-02-26T10:30:00.000Z",
  "checks": {
    "database": {...},
    "cache": {...},
    ...
  }
}
```

**Behavior:**
- Returns 200 if healthy
- Returns 503 if unhealthy
- Provides detailed component status
- Used for monitoring and debugging

**When to use:**
- Monitoring dashboards
- Debugging service health
- Detailed status reporting
- Alerting systems

---

## Recommendations

### For New Code

1. **Use the Enrichment Router endpoints** — These are currently active and include rate limiting:
   - `GET /health` — Overall health with component status
   - `GET /ready` — Readiness check for load balancers
   - `GET /metrics` — Enrichment metrics

2. **For Kubernetes probes**, use:
   - **Liveness:** `GET /health/live` (health router)
   - **Readiness:** `GET /ready` (enrichment router)
   - **Status:** `GET /health` (enrichment router)

3. **Avoid the shadowed endpoints:**
   - Don't rely on `GET /health/ready` — use `GET /ready` instead
   - The health router's `/health` endpoint is shadowed by enrichment router

### For Kubernetes Deployment

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### For Monitoring

- Use `GET /health` for overall status
- Use `GET /metrics` for enrichment performance metrics
- Use `GET /health/status` for detailed component breakdown (if needed)

---

## Future Consolidation

To eliminate this routing conflict, consider:

1. **Option A: Consolidate into Health Router**
   - Move enrichment-specific checks into health router
   - Add rate limiting to health router
   - Remove duplicate endpoints from enrichment router

2. **Option B: Consolidate into Enrichment Router**
   - Move all health checks into enrichment router
   - Keep health router for backward compatibility (deprecated)
   - Document migration path

3. **Option C: Separate Concerns**
   - Keep health router for Kubernetes probes
   - Keep enrichment router for enrichment metrics
   - Explicitly document which to use for each purpose

**Current Status:** No consolidation planned. Both implementations coexist with enrichment router taking precedence.

---

## Summary

| Aspect | Details |
|--------|---------|
| **Conflict** | `/health` and `/ready` defined in both routers |
| **Winner** | Enrichment router (registered first) |
| **Shadowed** | Health router's `/health` and `/ready` endpoints |
| **Active Endpoints** | `/health`, `/ready`, `/metrics` (enrichment) + `/health/live`, `/health/status`, `/health/ready` (health) |
| **Recommendation** | Use enrichment router endpoints for new code |
| **Kubernetes** | Use `/health/live` (liveness), `/ready` (readiness) |
| **Monitoring** | Use `/health` for status, `/metrics` for performance |
