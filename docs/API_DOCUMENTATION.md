# Solstein API Documentation

> **Version**: 2026-03-01  
> **Base URL**: `http://localhost:8000`  
> **Source of truth**: `src/solstein/api/routers/`  
> **Interactive docs**: `GET /docs` (Swagger) · `GET /redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting & Tenancy](#rate-limiting--tenancy)
3. [Error Format](#error-format)
4. [Endpoints](#endpoints)
   - [Health](#health)
   - [Metrics](#metrics)
   - [Auth](#auth)
   - [Companies](#companies)
   - [Scoring](#scoring)
   - [Market](#market)
   - [Enrichment](#enrichment)
   - [Export](#export)
   - [Simulation](#simulation)
   - [Dashboard](#dashboard)
   - [Drill-Down](#drill-down)
   - [Async Operations](#async-operations)
   - [Jobs](#jobs)
5. [WebSocket](#websocket)
6. [Domain Enums](#domain-enums)

---

## Authentication

Solstein uses a two-layer auth model:

### 1. Tenant API Key (Header)

All requests (except `/health/*` and `/docs`) require a tenant API key:

```http
X-API-Key: <your-api-key>
```

API keys are SHA-256 hashed before storage in the `tenants` table. The raw key is only shown at tenant creation.

### 2. JWT Bearer Token (Login flow)

For user-level operations, obtain a JWT via `POST /auth/login` then pass it as:

```http
Authorization: Bearer <jwt_token>
```

### Token Expiry

| Token Type | Default Lifetime |
|------------|-----------------|
| Access token | Configurable via `SECRET_KEY` + settings |
| Refresh token | Obtained via `POST /auth/refresh` |

---

## Rate Limiting & Tenancy

Rate limits are stored per tenant in the `tenants` table (`rate_limit_per_min`, default: **60 req/min**).

| Plan | Default Limit |
|------|--------------|
| `free` | 60 req/min |
| `standard` | 60 req/min (configurable) |
| `enterprise` | 60 req/min (configurable) |

Rate limit exceeded returns:
```json
HTTP 429 Too Many Requests
{"detail": "Rate limit exceeded"}
```

---

## Error Format

All errors follow a consistent JSON structure:

```json
{
  "detail": "Human-readable description of the error",
  "code": "OPTIONAL_ERROR_CODE",
  "field": "optional_field_name"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `400` | Bad request / validation error |
| `401` | Missing or invalid credentials |
| `403` | Forbidden (insufficient permissions) |
| `404` | Resource not found |
| `422` | Unprocessable entity (Pydantic validation) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
| `501` | Not implemented (endpoint disabled) |
| `503` | Service unavailable (Celery/Redis not available) |

---

## Endpoints

---

### Health

No authentication required for health endpoints.

#### `GET /health`

Returns overall system health.

**Response `200`:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-01T12:00:00Z"
}
```

#### `GET /health/status`

Detailed health check including database, Redis, and LLM providers.

**Response `200`:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "llm_providers": {
    "ollama": "healthy",
    "groq": "healthy",
    "openai": "healthy"
  }
}
```

#### `GET /health/ready`

Kubernetes readiness probe. Returns `200` when the service is ready to serve traffic.

#### `GET /health/live`

Kubernetes liveness probe. Returns `200` when the process is alive.

#### `GET /healthz`

Alias for `/health`. Provided for Kubernetes compatibility.

#### `GET /health/workers`

Returns Celery worker health status.

**Response `200`:**
```json
{
  "workers": ["celery@hostname"],
  "active_tasks": 3,
  "reserved_tasks": 0
}
```

---

### Metrics

#### `GET /metrics`

Returns Prometheus-compatible metrics for scraping.

**Response `200` (text/plain):**
```
# HELP solstein_requests_total Total HTTP requests
# TYPE solstein_requests_total counter
solstein_requests_total{method="GET",endpoint="/companies"} 142
...
```

#### `GET /metrics/data-quality`

Returns data quality metrics across the company dataset.

**Response `200`:**
```json
{
  "total_companies": 250,
  "avg_data_completeness": 0.73,
  "companies_with_revenue": 180,
  "companies_with_employees": 220,
  "companies_scored_last_24h": 15
}
```

---

### Auth

#### `POST /auth/login`

Authenticate and obtain JWT tokens.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "secret"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### `POST /auth/logout`

Invalidate the current session.

**Headers:** `Authorization: Bearer <token>`

**Response `200`:**
```json
{"message": "Logged out successfully"}
```

#### `POST /auth/refresh`

Obtain a new access token using a refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGci..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### `GET /auth/me`

Get the currently authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response `200`:**
```json
{
  "id": "user-id",
  "username": "user@example.com",
  "plan": "standard",
  "rate_limit_per_min": 60
}
```

---

### Companies

#### `GET /companies`

List companies with optional filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `50` | Max records (max: 200) |
| `tier` | string | — | Filter by tier: `TIER_1`, `TIER_2`, `TIER_3`, `TIER_4` |
| `industry` | string | — | Filter by industry name (partial match) |
| `min_revenue` | float | — | Minimum revenue in EUR millions |
| `classification` | string | — | Filter by classification (Phoenix, Salt, Lead) |
| `min_score` | float | — | Minimum composite score |
| `max_score` | float | — | Maximum composite score |

**Response `200`:**
```json
{
  "companies": [
    {
      "id": 42,
      "company_id": "acme-corp",
      "name": "Acme Corp",
      "industry": "Energy Software",
      "tier": "TIER_1",
      "threat_level": "HIGH",
      "classification": "Phoenix",
      "ai_score": 0.82,
      "composite_score": 0.76,
      "revenue_eur_m": 45.5,
      "growth_rate_pct": 28.0,
      "employee_count": 320,
      "last_updated": "2026-03-01T10:00:00Z"
    }
  ],
  "total": 250,
  "skip": 0,
  "limit": 50
}
```

#### `GET /companies/{id}`

Get a single company by integer `id` or string `company_id`.

**Path Parameters:**
- `id` — Integer primary key or string `company_id` (e.g. `acme-corp`)

**Response `200`:**
```json
{
  "id": 42,
  "company_id": "acme-corp",
  "name": "Acme Corp",
  "industry": "Energy Software",
  "hq": "Berlin",
  "website": "https://acme.example.com",
  "description": "...",
  "tier": "TIER_1",
  "threat_level": "HIGH",
  "classification": "Phoenix",
  "ai_maturity": "STRONG",
  "ai_score": 0.82,
  "ai_key_capabilities": ["NLP", "Computer Vision"],
  "ai_in_production": true,
  "revenue_eur_m": 45.5,
  "revenue_confidence": "ESTIMATED",
  "growth_rate_pct": 28.0,
  "profit_margin_pct": 12.5,
  "ebitda_margin_pct": 18.0,
  "employee_count": 320,
  "growth_score": 0.81,
  "financial_health_score": 0.70,
  "competitive_position_score": 0.78,
  "composite_score": 0.76,
  "last_updated": "2026-03-01T10:00:00Z",
  "created_at": "2025-01-15T08:00:00Z"
}
```

**Response `404`:**
```json
{"detail": "Company not found"}
```

#### `POST /companies/{id}/score`

Trigger immediate re-scoring for a company.

**Response `200`:**
```json
{
  "company_id": "acme-corp",
  "growth_score": 0.81,
  "financial_health_score": 0.70,
  "competitive_position_score": 0.78,
  "overall_score": 0.76,
  "classification": "Phoenix",
  "scored_at": "2026-03-01T12:00:00Z"
}
```

#### `POST /companies/{id}/enrich`

Trigger synchronous enrichment for a single company. Requires Celery worker.

**Request (optional body):**
```json
{
  "sources": ["GITHUB", "SEC_EDGAR", "LINKEDIN"],
  "force_refresh": false
}
```

**Response `200`:**
```json
{
  "company_id": "acme-corp",
  "fields_enriched": ["employee_count", "funding_rounds", "open_positions"],
  "sources_used": ["GITHUB", "SEC_EDGAR"],
  "duration_ms": 3420
}
```

**Response `503`:** Redis/Celery not available.

#### `POST /companies/enrich/batch`

Trigger enrichment for multiple companies. Requires Celery worker.

**Request:**
```json
{
  "company_ids": ["acme-corp", "beta-ltd", "gamma-inc"],
  "sources": ["GITHUB", "NEWS"],
  "force_refresh": false
}
```

**Response `202`:**
```json
{
  "job_id": "a1b2c3d4-e5f6-...",
  "status": "PENDING",
  "company_count": 3
}
```

#### `GET /companies/{id}/enrichment/audit`

Get enrichment audit trail for a company.

**Query Parameters:**
- `limit` (int, default: 50)
- `operation` (string, optional) — filter by operation type

**Response `200`:**
```json
{
  "records": [
    {
      "id": 101,
      "operation": "enrich_success",
      "source": "GITHUB",
      "status": "SUCCESS",
      "duration_ms": 820,
      "fields_enriched": ["open_positions", "employee_count"],
      "timestamp": "2026-03-01T09:30:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /companies/{id}/enrichment/cache`

Inspect the enrichment cache entry for a company.

**Response `200`:**
```json
{
  "company_id": "acme-corp",
  "cached_at": "2026-03-01T08:00:00Z",
  "expires_at": "2026-03-02T08:00:00Z",
  "ttl_seconds": 86400,
  "hits": 4,
  "sources_used": ["GITHUB", "SEC_EDGAR"],
  "fields_enriched": ["employee_count", "funding_rounds"]
}
```

**Response `404`:** No cache entry for this company.

---

### Scoring

#### `POST /scoring/company/{id}/score`

Score a specific company and persist the result to `scoring_records`.

> **Note**: This is a `POST`, not `GET`. Scoring is a write operation.

**Path Parameters:**
- `id` — Company integer id or string `company_id`

**Response `200`:**
```json
{
  "company_id": "acme-corp",
  "company_name": "Acme Corp",
  "growth_score": 0.81,
  "financial_health_score": 0.70,
  "competitive_position_score": 0.78,
  "overall_score": 0.76,
  "classification": "Phoenix",
  "scored_at": "2026-03-01T12:00:00Z",
  "data_sources_used": ["GITHUB", "SEC_EDGAR", "NEWS"]
}
```

#### `GET /scoring/stats`

Aggregate scoring statistics across all companies.

**Response `200`:**
```json
{
  "total_scored": 250,
  "avg_growth_score": 0.52,
  "avg_financial_health_score": 0.48,
  "avg_competitive_position_score": 0.55,
  "avg_overall_score": 0.51,
  "classification_breakdown": {
    "Phoenix": 38,
    "Salt": 142,
    "Lead": 70
  },
  "last_scored_at": "2026-03-01T11:45:00Z"
}
```

---

### Market

#### `GET /market/analysis`

Analyze market-level trends across all companies.

**Query Parameters:**
- `industry` (string, optional) — Filter to specific industry
- `tier` (string, optional) — Filter to tier

**Response `200`:**
```json
{
  "market_overview": {
    "total_companies": 250,
    "avg_ai_score": 0.42,
    "avg_revenue_eur_m": 38.5,
    "avg_growth_rate_pct": 14.2
  },
  "competitive_intensity": "HIGH",
  "top_threats": ["acme-corp", "beta-ltd"],
  "emerging_trends": ["LLM adoption", "Edge AI"],
  "market_metadata": {}
}
```

#### `GET /market/search`

Search companies by name, description, or industry.

**Query Parameters:**
- `q` (string, required) — Search query
- `limit` (int, default: 20) — Max results

**Response `200`:**
```json
{
  "results": [
    {
      "company_id": "acme-corp",
      "name": "Acme Corp",
      "industry": "Energy Software",
      "relevance_score": 0.92
    }
  ],
  "total": 3,
  "query": "energy ai"
}
```

#### `GET /market/overlap/{id}`

Analyze competitive overlap between a company and all other tracked companies.

**Path Parameters:**
- `id` — Target company id

**Response `200`:**
```json
{
  "company": "acme-corp",
  "overlapping_companies": [
    {
      "company_id": "beta-ltd",
      "overlap_score": 0.78,
      "shared_capabilities": ["NLP", "Predictive Analytics"],
      "shared_markets": ["Energy", "Utilities"]
    }
  ],
  "total_overlap_count": 12
}
```

---

### Enrichment

Enrichment endpoints require Celery + Redis. Without them, endpoints return `503`.

#### `GET /enrichment/status/{job_id}`

Get the status of an enrichment job.

**Path Parameters:**
- `job_id` — Celery task UUID (from `POST /companies/enrich/batch`)

**Response `200`:**
```json
{
  "job_id": "a1b2c3d4-...",
  "company_id": "acme-corp",
  "status": "SUCCESS",
  "progress": 100,
  "sources": ["GITHUB", "SEC_EDGAR"],
  "result_data": {},
  "duration_ms": 4200,
  "completed_at": "2026-03-01T12:00:00Z"
}
```

---

### Export

#### `GET /export`

Export company data in the specified format.

> **Note**: This is a `GET` endpoint with query parameters, not `POST /export/`.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | string | `excel` | Export format: `excel`, `csv`, `pdf`, `markdown`, `llm` |
| `tier` | string | — | Filter by tier |
| `industry` | string | — | Filter by industry |
| `limit` | int | `100` | Max companies to export |
| `include_signals` | bool | `false` | Include signal details |
| `include_audit` | bool | `false` | Include audit trail |

**Response `200`:**
- `excel` → `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `csv` → `text/csv`
- `pdf` → `application/pdf`
- `markdown` → `text/markdown`
- `llm` → `application/json` (LLM-optimized structured data)

**Example:**
```bash
curl -H "X-API-Key: <key>" \
  "http://localhost:8000/export?format=excel&tier=TIER_1&limit=50" \
  -o companies.xlsx
```

---

### Simulation

#### `POST /simulation/run`

Run a market simulation scenario.

> **Note**: This is a `POST` endpoint at `/simulation/run`, not `GET /simulation`.

**Request:**
```json
{
  "scenario": "aggressive_growth",
  "companies": ["acme-corp", "beta-ltd"],
  "time_horizon_years": 3,
  "parameters": {
    "market_growth_rate": 0.15,
    "competitive_pressure": "HIGH"
  }
}
```

**Response `200`:**
```json
{
  "simulation_id": "sim-abc123",
  "scenario": "aggressive_growth",
  "time_horizon_years": 3,
  "results": {
    "acme-corp": {
      "projected_revenue_eur_m": 78.5,
      "projected_market_share": 0.12,
      "threat_trajectory": "INCREASING"
    }
  },
  "run_at": "2026-03-01T12:00:00Z"
}
```

---

### Dashboard

> **Note**: These endpoints are fully implemented but not documented elsewhere. They aggregate pre-computed data for quick dashboard rendering.

#### `GET /dashboard/summary`

High-level summary statistics for dashboard rendering.

**Response `200`:**
```json
{
  "total_companies": 250,
  "phoenix_count": 38,
  "salt_count": 142,
  "lead_count": 70,
  "avg_composite_score": 0.51,
  "high_threat_count": 23,
  "last_analysis_at": "2026-03-01T11:45:00Z"
}
```

#### `GET /dashboard/sectors`

Company distribution and scoring by industry sector.

**Response `200`:**
```json
{
  "sectors": [
    {
      "industry": "Energy Software",
      "company_count": 85,
      "avg_ai_score": 0.48,
      "avg_growth_score": 0.55,
      "phoenix_ratio": 0.18
    }
  ]
}
```

#### `GET /dashboard/top`

Top companies by composite score.

**Query Parameters:**
- `limit` (int, default: 10)
- `tier` (string, optional)

**Response `200`:**
```json
{
  "companies": [
    {
      "rank": 1,
      "company_id": "acme-corp",
      "name": "Acme Corp",
      "composite_score": 0.91,
      "classification": "Phoenix",
      "threat_level": "CRITICAL"
    }
  ]
}
```

#### `GET /dashboard/trends`

Historical score trends for market monitoring.

**Query Parameters:**
- `days` (int, default: 30)
- `industry` (string, optional)

**Response `200`:**
```json
{
  "period_days": 30,
  "data_points": [
    {
      "date": "2026-02-01",
      "avg_ai_score": 0.41,
      "avg_composite_score": 0.50,
      "phoenix_count": 35
    }
  ]
}
```

---

### Drill-Down

#### `GET /drill-down/company/{id}/why/{signal_name}`

Explain why a company received a specific signal score. Returns supporting evidence and contributing data points.

**Path Parameters:**
- `id` — Company id
- `signal_name` — Signal identifier (e.g. `ai_adoption`, `revenue_growth`, `market_expansion`)

**Response `200`:**
```json
{
  "company_id": "acme-corp",
  "signal_name": "ai_adoption",
  "signal_value": 0.82,
  "signal_category": "technology",
  "explanation": "Company has 3 production ML models, 12 AI-related job postings, and recent patent filings...",
  "evidence": [
    {
      "source": "GITHUB",
      "evidence_text": "Repository 'acme/ml-pipeline' with 142 stars, active development",
      "confidence": 0.9
    },
    {
      "source": "LINKEDIN",
      "evidence_text": "12 open positions for ML Engineers",
      "confidence": 0.85
    }
  ],
  "contributing_signals": ["github_ml_repos", "ai_job_postings", "ai_patents"]
}
```

---

### Async Operations

Long-running operations are executed asynchronously via Celery. These endpoints return `503` if Redis/Celery is unavailable.

#### `GET /async/status/{task_id}`

Check status of any async operation.

**Response `200`:**
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "SUCCESS",
  "progress": 100,
  "result": {},
  "created_at": "2026-03-01T12:00:00Z",
  "completed_at": "2026-03-01T12:01:30Z"
}
```

**`status` values:** `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`

---

### Jobs

> **⚠️ DISABLED**: The jobs system (Temporal workflow engine) has been removed. This endpoint returns `501 Not Implemented`.

#### `GET /jobs/{workflow_id}`

**Response `501`:**
```json
{"detail": "Jobs endpoint not implemented"}
```

---

## WebSocket

Real-time updates are available via WebSocket at:

```
ws://localhost:8000/ws
```

Requires `X-API-Key` header or token in query string: `?token=<jwt>`.

**Event types:**
- `scoring_update` — New score computed for a company
- `enrichment_progress` — Enrichment job progress update
- `market_alert` — Market-level alert triggered

---

## Domain Enums

| Enum | Values |
|------|--------|
| `ThreatLevel` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `CompanyTier` | `TIER_1`, `TIER_2`, `TIER_3`, `TIER_4` |
| `AIMaturity` | `NONE`, `LOW`, `MODERATE`, `STRONG`, `VERY_STRONG` |
| `ConfidenceLevel` | `CONFIRMED`, `ESTIMATED`, `UNKNOWN`, `SYNTHETIC` |
| `DataSourceType` | `GITHUB`, `COMPANY_FILINGS`, `NEWS`, `CRUNCHBASE`, `LINKEDIN`, `PATENTS`, `WEBSITE`, `PRESS_RELEASE`, `YAHOO_FINANCE`, `EXA_SEARCH`, `GOOGLE_SEARCH`, `USPTO`, `GOOGLE_PATENTS`, `NEWSAPI`, `COMPETITOR_JSON`, `STATIC_CATALOG` |

---

## Quick Reference

```bash
# Auth
curl -X POST /auth/login -d '{"username": "user", "password": "pass"}'

# List companies
curl -H "X-API-Key: $KEY" "/companies?tier=TIER_1&limit=20"

# Get company
curl -H "X-API-Key: $KEY" "/companies/acme-corp"

# Score a company
curl -X POST -H "X-API-Key: $KEY" "/scoring/company/acme-corp/score"

# Export to Excel
curl -H "X-API-Key: $KEY" "/export?format=excel&tier=TIER_1" -o report.xlsx

# Run simulation
curl -X POST -H "X-API-Key: $KEY" "/simulation/run" \
  -H "Content-Type: application/json" \
  -d '{"scenario": "base", "time_horizon_years": 2}'

# Dashboard
curl -H "X-API-Key: $KEY" "/dashboard/summary"
```

---

*Source of truth: `src/solstein/api/routers/`*  
*Interactive docs: `GET /docs` or `GET /redoc` when server is running*  
*Last verified: 2026-03-01*
