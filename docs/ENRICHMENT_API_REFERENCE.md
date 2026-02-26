# Enrichment API Reference

**Status**: Production Ready  
**Version**: 1.0  
**Date**: 2026-02-25

---

## Overview

The Connector Enrichment System provides REST API endpoints for enriching company data from multiple sources: SEC EDGAR, Companies House, and News Signals.

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints support optional Bearer token authentication via `Authorization` header.

---

## Health & Readiness Endpoints

### `GET /health`
Platform health check (liveness probe).

**Response**: 200 OK
```json
{
  "status": "healthy",
  "timestamp": "2026-02-25T21:00:00Z",
  "version": "1.0",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "connectors": {
      "sec_edgar": "healthy",
      "companies_house": "healthy",
      "news_signals": "healthy"
    }
  }
}
```

### `GET /ready`
Readiness probe for load balancers (checks if service is ready to receive traffic).

**Response**: 200 OK
```json
{
  "ready": true,
  "timestamp": "2026-02-25T21:00:00Z",
  "checks": {
    "configuration_loaded": true,
    "connectors_initialized": true,
    "cache_operational": true
  }
}
```

---

## Enrichment Endpoints

### `POST /companies/{id}/enrich`
Enrich a single company from available connectors.

**Parameters**:
- `id` (path, required): Company ID

**Request Body**:
```json
{
  "sources": ["SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS"],
  "dry_run": false
}
```

**Response**: 200 OK
```json
{
  "company_id": "001",
  "company_name": "Acme Corp",
  "status": "success",
  "enrichment": {
    "sources_used": ["SEC_EDGAR", "COMPANIES_HOUSE"],
    "fields_enriched": [
      "revenue",
      "employees",
      "profit_margin"
    ],
    "duration_ms": 1234
  },
  "data": {
    "revenue": 5000000,
    "employees": 150,
    "growth_rate": 0.15,
    "profit_margin": 0.12
  }
}
```

**Errors**:
- `400 Bad Request`: Invalid company ID format
- `404 Not Found`: Company not found
- `503 Service Unavailable`: Connectors unavailable

---

### `POST /companies/enrich/batch`
Batch enrich multiple companies with performance optimization.

**Request Body**:
```json
{
  "company_ids": ["001", "002", "003"],
  "batch_size": 10,
  "use_cache": true,
  "dry_run": false
}
```

**Response**: 200 OK
```json
{
  "status": "success",
  "batch_id": "batch_12345",
  "total_companies": 3,
  "enriched_count": 3,
  "failed_count": 0,
  "results": [
    {
      "company_id": "001",
      "status": "success",
      "duration_ms": 245,
      "source": "cache"
    },
    {
      "company_id": "002",
      "status": "success",
      "duration_ms": 1234,
      "source": "SEC_EDGAR"
    },
    {
      "company_id": "003",
      "status": "failed",
      "error": "No identifiers found",
      "duration_ms": 0
    }
  ],
  "metrics": {
    "total_duration_ms": 1479,
    "avg_duration_ms": 493,
    "cache_hits": 1,
    "cache_misses": 2,
    "success_rate": 66.7
  }
}
```

---

### `GET /companies/{id}/enrichment/audit`
Get enrichment audit trail for specific company.

**Parameters**:
- `id` (path, required): Company ID
- `limit` (query, optional): Max entries to return (default: 50)

**Response**: 200 OK
```json
{
  "company_id": "001",
  "company_name": "Acme Corp",
  "audit_entries": [
    {
      "timestamp": "2026-02-25T21:00:00Z",
      "operation": "enrich_success",
      "source": "SEC_EDGAR",
      "fields": ["revenue", "employees"],
      "duration_ms": 450,
      "user_id": "admin@example.com"
    },
    {
      "timestamp": "2026-02-25T20:55:00Z",
      "operation": "enrich_start",
      "source": "COMPANIES_HOUSE",
      "status": "in_progress"
    }
  ],
  "summary": {
    "total_enrichments": 5,
    "successful": 4,
    "failed": 1,
    "success_rate": 80.0
  }
}
```

---

## Metrics & Monitoring Endpoints

### `GET /metrics`
Get enrichment performance metrics.

**Response**: 200 OK
```json
{
  "timestamp": "2026-02-25T21:00:00Z",
  "enrichment": {
    "total": 156,
    "successful": 152,
    "failed": 4,
    "success_rate": 97.4,
    "avg_duration_ms": 892
  },
  "cache": {
    "size": 45,
    "ttl_hours": 24,
    "hits": 230,
    "misses": 152,
    "hit_rate": 60.2
  },
  "rate_limiting": {
    "requests_per_minute": 100,
    "current_requests": 45,
    "remaining": 55
  }
}
```

### `GET /companies/{id}/enrichment/cache`
Check if company is cached.

**Response**: 200 OK
```json
{
  "company_id": "001",
  "cached": true,
  "cache_key": "enriched_001_AAPL",
  "ttl_remaining_hours": 23.5,
  "cached_data": {
    "revenue": 5000000,
    "employees": 150
  }
}
```

---

## Cache Management Endpoints

### `POST /enrichment/cache/clear`
Clear all enrichment cache.

**Response**: 200 OK
```json
{
  "status": "success",
  "message": "Enrichment cache cleared",
  "entries_cleared": 47
}
```

### `POST /enrichment/cache/clear/{id}`
Clear cache for specific company.

**Parameters**:
- `id` (path, required): Company ID

**Response**: 200 OK
```json
{
  "status": "success",
  "company_id": "001",
  "message": "Cache cleared",
  "cache_key": "enriched_001_AAPL"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "invalid_input",
  "message": "Invalid ticker format: ticker must be 1-10 alphanumeric characters",
  "code": "VAL_001"
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded: 100 requests per minute",
  "retry_after_seconds": 35,
  "code": "RATELIMIT_001"
}
```

### 503 Service Unavailable
```json
{
  "error": "connector_unavailable",
  "message": "SEC EDGAR connector is currently unavailable",
  "affected_sources": ["SEC_EDGAR"],
  "code": "CONNECTOR_001"
}
```

---

## Common Patterns

### Enrich Single Company
```bash
curl -X POST http://localhost:8000/companies/001/enrich \
  -H "Content-Type: application/json" \
  -d '{"sources": ["SEC_EDGAR", "COMPANIES_HOUSE"]}'
```

### Batch Enrich with Caching
```bash
curl -X POST http://localhost:8000/companies/enrich/batch \
  -H "Content-Type: application/json" \
  -d '{
    "company_ids": ["001", "002", "003"],
    "batch_size": 10,
    "use_cache": true
  }'
```

### Check Audit Trail
```bash
curl -X GET "http://localhost:8000/companies/001/enrichment/audit?limit=20"
```

### Get Performance Metrics
```bash
curl -X GET http://localhost:8000/metrics
```

---

## Rate Limiting

All endpoints subject to rate limiting:
- **Default**: 100 requests per minute per client
- **Per-endpoint**: Consistent across all enrichment endpoints
- **Reset**: Automatic every minute
- **Headers Returned**:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1614033660
  ```

---

## Security Headers

All responses include security headers:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

---

## Versioning

API version: `1.0`  
Stable endpoints version: `/v1/*`

Future versions will be released as `/v2/*` with full backward compatibility maintained for `/v1/*`.
