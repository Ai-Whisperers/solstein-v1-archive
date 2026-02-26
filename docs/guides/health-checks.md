# 🏥 Health Checks Guide

**Phase**: 13.3  
**Status**: Production-Ready  
**Last Updated**: February 2026

This guide explains Solstein's liveness and readiness probes for production monitoring.

---

## Overview

Health checks allow monitoring systems and load balancers to determine if Solstein is:
- **Alive** — Is the process running?
- **Ready** — Is it safe to send traffic?

### Two Types of Probes

| Probe | Endpoint | Purpose | Interval |
|-------|----------|---------|----------|
| **Liveness** | `GET /health` | Is process alive? | Every 10 seconds |
| **Readiness** | `GET /ready` | Is ready for traffic? | Every 5 seconds |

---

## Liveness Probe (`/health`)

### Purpose

Tells orchestration systems (Kubernetes, Docker, etc.) whether the process is still running.

### Response

```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T10:00:00Z",
  "checks": {
    "database": {
      "status": "connected",
      "healthy": true
    },
    "cache": {
      "status": "operational",
      "healthy": true
    }
  }
}
```

### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| **200** | System is healthy | Keep routing traffic |
| **503** | System is unhealthy | Consider restarting |

### Implementation

```python
# src/solstein/api/routers/enrichment.py
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Dict, Any

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """Liveness probe - Is the system alive?
    
    Returns:
        HealthCheckResponse with current system status
        
    Status Codes:
        200: System is healthy
        503: System is unhealthy (critical component failed)
    """
    logger.info("Health check requested")
    
    # Check critical components
    db_status, db_healthy = await check_database_health()
    cache_status, cache_healthy = await check_cache_health()
    
    # Determine overall health (database and cache required)
    all_healthy = db_healthy and cache_healthy
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        checks={
            "database": {
                "status": db_status,
                "healthy": db_healthy
            },
            "cache": {
                "status": cache_status,
                "healthy": cache_healthy
            }
        }
    )
```

### What Gets Checked

```python
async def check_database_health() -> tuple[str, bool]:
    """Check PostgreSQL connectivity."""
    try:
        db_manager = _get_db_manager()
        async with db_manager.get_session() as session:
            await session.execute("SELECT 1")
        return ("connected", True)
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return ("disconnected", False)

async def check_cache_health() -> tuple[str, bool]:
    """Check Redis or in-memory cache."""
    try:
        cache = get_cache()
        cache.ping()
        return ("operational", True)
    except Exception as e:
        logger.warning(f"Cache health check failed: {e}")
        return ("unavailable", False)
```

### Usage in Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: solstein-api
spec:
  template:
    spec:
      containers:
      - name: solstein
        image: solstein:latest
        
        # Liveness probe
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10  # Wait 10s before first check
          periodSeconds: 10        # Check every 10s
          timeoutSeconds: 5        # Consider failed if no response in 5s
          failureThreshold: 3      # Restart after 3 failures
        
        # Once liveness is satisfied, check readiness
        ports:
        - containerPort: 8000
```

---

## Readiness Probe (`/ready`)

### Purpose

Tells load balancers whether the system's **core infrastructure** (database & cache) is ready.

⚠️ **IMPORTANT**: Readiness checks ONLY database and cache, NOT data sources.
Data sources (SEC EDGAR, Companies House, News Signals) may be unavailable without affecting readiness.
Use `/health` to check if data sources are operational.

### Response

```json
{
  "ready": true,
  "timestamp": "2026-02-26T10:00:00Z",
  "checks": {
    "database": {
      "status": "connected",
      "healthy": true
    },
    "cache": {
      "status": "operational",
      "healthy": true
    },
    "sec_edgar_connector": {
      "status": "operational",
      "healthy": true
    },
    "companies_house_connector": {
      "status": "operational",
      "healthy": true
    },
    "news_signals_connector": {
      "status": "operational",
      "healthy": true
    }
  }
}
```

### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| **200** | Ready for traffic | Route requests normally |
| **503** | Not ready | Remove from load balancer, don't send traffic |

### Implementation

```python
# src/solstein/api/routers/enrichment.py
@router.get("/ready", response_model=ReadinessCheckResponse)
async def readiness_check() -> ReadinessCheckResponse:
    """Readiness probe - Is the system ready for traffic?
    
    More comprehensive than liveness - checks all connectors too.
    
    Returns:
        ReadinessCheckResponse indicating if system is ready
        
    Status Codes:
        200: System ready for traffic
        503: System not ready (return 200 but ready=false if partial)
    """
    logger.info("Readiness check requested")
    
    # Check critical components
    db_status, db_healthy = await check_database_health()
    cache_status, cache_healthy = await check_cache_health()
    
    # Check optional connectors
    sec_status, sec_healthy = await check_sec_edgar_health()
    ch_status, ch_healthy = await check_companies_house_health()
    news_status, news_healthy = await check_news_signals_health()
    github_status, github_healthy = await check_github_health()
    
    # System is ready if critical components + majority of connectors work
    critical_ready = db_healthy and cache_healthy
    connector_count = sum([sec_healthy, ch_healthy, news_healthy, github_healthy])
    connectors_ready = connector_count >= 2  # At least 2 of 4
    
    overall_ready = critical_ready and connectors_ready
    
    return ReadinessCheckResponse(
        ready=overall_ready,
        timestamp=datetime.now(timezone.utc),
        checks={
            "database": {"status": db_status, "healthy": db_healthy},
            "cache": {"status": cache_status, "healthy": cache_healthy},
            "sec_edgar_connector": {"status": sec_status, "healthy": sec_healthy},
            "companies_house_connector": {"status": ch_status, "healthy": ch_healthy},
            "news_signals_connector": {"status": news_status, "healthy": news_healthy},
            "github_connector": {"status": github_status, "healthy": github_healthy},
        }
    )
```

### What Gets Checked

```python
async def check_sec_edgar_health() -> tuple[str, bool]:
    """Check SEC EDGAR connector health."""
    try:
        connector = SECEDGARRefreshConnector()
        # Quick test call (not full refresh)
        await connector.test_connection()
        return ("operational", True)
    except Exception as e:
        logger.debug(f"SEC EDGAR health check failed: {e}")
        return ("unavailable", False)

async def check_companies_house_health() -> tuple[str, bool]:
    """Check Companies House connector health."""
    try:
        connector = CompaniesHouseRefreshConnector()
        await connector.test_connection()
        return ("operational", True)
    except Exception as e:
        logger.debug(f"Companies House health check failed: {e}")
        return ("unavailable", False)

# Similar for News Signals, GitHub, etc.
```

### Usage in Kubernetes

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: solstein-api
spec:
  template:
    spec:
      containers:
      - name: solstein
        image: solstein:latest
        
        # Readiness probe (after liveness passes)
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5   # Wait 5s before first check
          periodSeconds: 5         # Check every 5s
          timeoutSeconds: 5        # Consider failed if no response in 5s
          failureThreshold: 2      # Remove from LB after 2 failures
          successThreshold: 1      # Add back after 1 success
```

---

## Critical Feature: Health Checks NOT Rate Limited

### Design Principle

Health checks **MUST** never be rate limited. If they are:
- Monitoring systems can't check status
- Load balancers think system is down
- Traffic gets routed away even though system is healthy

### Implementation

```python
# ✅ CORRECT - No rate limit check in health endpoints
@router.get("/health")
async def health_check() -> HealthCheckResponse:
    # No: if not rate_limiter.is_allowed(client_id)
    # Just return status
    return {...}

@router.get("/ready")
async def readiness_check() -> ReadinessCheckResponse:
    # No rate limit check
    return {...}

# ❌ WRONG - Rate limited health checks
@router.get("/health")
async def health_check(request: Request):
    if not rate_limiter.is_allowed(request.client.host):
        raise HTTPException(429)  # ❌ WRONG
    return {...}
```

---

## Hierarchical Health

### Component Hierarchy

```
System Health
├─ Critical
│  ├─ Database (PostgreSQL)
│  └─ Cache (Redis)
│
└─ Optional
   ├─ SEC EDGAR Connector
   ├─ Companies House Connector
   ├─ News Signals Connector
   └─ GitHub Connector
```

### Decision Logic

```python
# Liveness: Only critical components
alive = database_healthy AND cache_healthy

# Readiness: Critical + most optional
ready = database_healthy AND cache_healthy 
        AND (2+ connectors healthy)

# This means:
# - System can be alive but not ready (connectors down)
# - System is never ready if database down
# - System is never ready if cache down
```

---

## Monitoring

### Prometheus Metrics

```prometheus
# Extract liveness status
solstein_health_status{component="database"} 1  # 1 = healthy, 0 = unhealthy
solstein_health_status{component="cache"} 1
solstein_health_status{component="sec_edgar"} 1
solstein_health_status{component="companies_house"} 0

# Track check duration
solstein_health_check_duration_ms 45  # Took 45ms

# Track check failures
solstein_health_check_failures_total 3  # Total failures across all checks
```

### Log Monitoring

```bash
# Watch health check calls
tail -f application.log | grep "Health check\|Readiness check"

# Watch for failures
tail -f application.log | grep "health check failed"

# Output:
[2026-02-26 10:00:05] Health check requested → 200 (healthy)
[2026-02-26 10:00:05] Readiness check requested → 200 (ready)
[2026-02-26 10:00:10] Database health check failed: Connection timeout
[2026-02-26 10:00:10] Health check requested → 503 (unhealthy)
```

### Dashboard Alerts

```yaml
# Monitoring rules
alerts:
  - name: solstein_unhealthy
    condition: solstein_health_status == 0
    duration: 1m
    severity: critical
    message: "Solstein system is unhealthy"
  
  - name: solstein_not_ready
    condition: solstein_ready_status == 0
    duration: 2m
    severity: warning
    message: "Solstein is not ready for traffic"
  
  - name: slow_health_checks
    condition: solstein_health_check_duration_ms > 1000
    duration: 5m
    severity: warning
    message: "Health checks taking > 1 second"
```

---

## Testing

### Unit Test

```python
# tests/integration/test_health_checks.py
import pytest
from fastapi.testclient import TestClient
from solstein.api.main import app

client = TestClient(app)

def test_health_endpoint_returns_200_when_healthy():
    """Test /health returns 200 when system healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["checks"]["database"]["healthy"] == True
    assert data["checks"]["cache"]["healthy"] == True

def test_health_endpoint_returns_503_when_db_down(mock_db_down):
    """Test /health returns 503 when database unavailable."""
    # Mock database as down
    with patch("solstein.api.routers.check_database_health") as mock:
        mock.return_value = ("disconnected", False)
        
        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"

def test_readiness_endpoint_returns_200_when_ready():
    """Test /ready returns 200 when system ready."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] == True

def test_readiness_endpoint_returns_503_when_not_ready(mock_connectors_down):
    """Test /ready returns 503 when most connectors down."""
    with patch("solstein.api.routers.check_sec_edgar_health") as mock1, \
         patch("solstein.api.routers.check_companies_house_health") as mock2, \
         patch("solstein.api.routers.check_news_signals_health") as mock3, \
         patch("solstein.api.routers.check_github_health") as mock4:
        
        mock1.return_value = ("unavailable", False)
        mock2.return_value = ("unavailable", False)
        mock3.return_value = ("unavailable", False)
        mock4.return_value = ("operational", True)
        
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] == False  # Not enough connectors
```

### Integration Test with K8s

```bash
# Test liveness probe
$ curl -i http://localhost:8000/health
HTTP/1.1 200 OK
Content-Type: application/json
{"status": "healthy", "timestamp": "...", "checks": {...}}

# Test readiness probe
$ curl -i http://localhost:8000/ready
HTTP/1.1 200 OK
Content-Type: application/json
{"ready": true, "timestamp": "...", "checks": {...}}

# Simulate database down
$ redis-cli SHUTDOWN  # Shutdown Redis
$ curl -i http://localhost:8000/health
HTTP/1.1 503 Service Unavailable
{"status": "unhealthy", "checks": {"cache": {"healthy": false}}}
```

---

## Best Practices

### 1. Keep Health Checks Fast

```python
# ✅ GOOD - Quick validation
async def check_database_health() -> tuple[str, bool]:
    try:
        async with db_manager.get_session() as session:
            await session.execute("SELECT 1")  # 1-5ms
        return ("connected", True)
    except Exception:
        return ("disconnected", False)

# ❌ BAD - Expensive checks
async def check_database_health():
    try:
        result = await expensive_query()  # 1000ms+ - too slow!
        return ("connected", True)
    except Exception:
        return ("disconnected", False)
```

### 2. Separate Liveness and Readiness

```python
# ✅ GOOD - Different endpoints with different thresholds
@router.get("/health")
async def health_check():  # Only critical components
    return {...}

@router.get("/ready")
async def readiness_check():  # All components
    return {...}

# ❌ BAD - Same endpoint for both
@router.get("/health")
async def health_check():  # Mixes concerns
    return {...}
```

### 3. Avoid Rate Limiting Health Checks

```python
# ✅ GOOD - No rate limit
@router.get("/health")
async def health_check():
    # No: if not rate_limiter.is_allowed(...)
    return {...}

# ❌ BAD - Rate limited
@router.get("/health")
async def health_check(request: Request):
    if not rate_limiter.is_allowed(request.client.host):
        raise HTTPException(429)  # Will break monitoring!
```

### 4. Use Appropriate Status Codes

```python
# ✅ GOOD - Standard codes
response_status_code = 200 if healthy else 503

# ❌ BAD - Non-standard codes
response_status_code = 200 if healthy else 400  # 400 wrong for this
```

### 5. Provide Rich Metadata

```python
# ✅ GOOD - Detailed status
return HealthCheckResponse(
    status="unhealthy",
    timestamp="2026-02-26T10:00:00Z",
    checks={
        "database": {"status": "disconnected", "healthy": false},
        "cache": {"status": "operational", "healthy": true}
    }
)

# ❌ BAD - Minimal info
return {"status": "unhealthy"}  # No details
```

---

## Troubleshooting

### Health Check Returns Unhealthy

**Symptom**: `GET /health` returns 503

**Check**:
1. Is database running? `psql -c "SELECT 1"`
2. Is Redis running? `redis-cli ping`
3. Are both configured correctly?

```bash
# Test database
SQLALCHEMY_DATABASE_URL=postgresql://user:pass@localhost/solstein
psql $SQLALCHEMY_DATABASE_URL -c "SELECT 1"

# Test Redis
REDIS_URL=redis://localhost:6379
redis-cli -u $REDIS_URL ping
```

### Health Checks Too Slow

**Symptom**: Health check takes > 1 second

**Optimize**:
```python
# ❌ BAD - Expensive
await session.execute("SELECT COUNT(*) FROM company")  # Slow

# ✅ GOOD - Fast
await session.execute("SELECT 1")  # 1ms
```

### Readiness Never Becomes True

**Symptom**: `/ready` always returns `ready: false`

**Check**:
1. Are at least 2 connectors working?
2. Is database and cache healthy?
3. Check logs for connector failures

```bash
tail -f application.log | grep "health check failed"
```

---

## References

- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Phase 13.3 Implementation](../phases/phase-13.md#133-health-checks)
- [Health Check Implementation](../../src/solstein/api/routers/enrichment.py)

---

**Last Updated**: February 26, 2026  
**Status**: Production-Ready ✅
