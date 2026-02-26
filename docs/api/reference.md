
# 📜 API Reference

**Solstein REST API — Complete Endpoint Reference**

> Interactive docs (Swagger UI) available at `http://localhost:8000/docs` when running locally.
> ReDoc available at `http://localhost:8000/redoc`.
> OpenAPI Schema: `http://localhost:8000/openapi.json`

---

## 📋 Quick Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Platform health check | No |
| `/companies` | GET | List all companies | Optional |
| `/companies` | POST | Create and score company | Optional |
| `/companies/{id}` | GET | Get company by ID | Optional |
| `/scoring/company/{id}/score` | POST | Score specific company | Optional |
| `/scoring/stats` | GET | Market-wide statistics | Optional |
| `/scoring/batch` | GET | Queue batch scoring | Optional |
| `/market/analysis` | GET | Market landscape analysis | Optional |
| `/market/search` | GET | Search companies | Optional |
| `/market/overlap/{id}` | GET | Competitive overlap | Optional |
| `/export/excel` | GET | Export Excel dashboard | Optional |
| `/export/json` | GET | Export JSON data | Optional |
| `/async/enrich/single` | POST | Start async single enrichment | Optional |
| `/async/enrich/batch` | POST | Start async batch enrichment | Optional |
| `/async/jobs/{job_id}/status` | GET | Poll async job status | Optional |
| `/async/jobs/{job_id}/result` | GET | Get async job result | Optional |
| `/drill-down/company/{id}/audit-trail` | GET | Enrichment audit trail | Optional |
| `/drill-down/company/{id}/contradictions` | GET | Data contradictions | Optional |
| `/drill-down/company/{id}/data-quality` | GET | Data quality metrics | Optional |
| `/drill-down/company/{id}/fact/{fact_type}` | GET | Specific fact details | Optional |
| `/drill-down/company/{id}/facts` | GET | All aggregated facts | Optional |
| `/drill-down/company/{id}/signals` | GET | All extracted signals | Optional |
| `/drill-down/company/{id}/source/{source_id}` | GET | Specific source details | Optional |
| `/drill-down/company/{id}/sources` | GET | All data sources | Optional |
| `/drill-down/company/{id}/timeline` | GET | Analysis timeline | Optional |
| `/drill-down/company/{id}/why/{signal_name}` | GET | Signal explanation | Optional |
---

## Quick Start

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. List Companies

```bash
curl http://localhost:8000/companies?limit=10
```

### 3. Score a Company

```bash
curl -X POST http://localhost:8000/scoring/company/company-id/score
```

### 4. Export to Excel

```bash
curl -X POST http://localhost:8000/export/ \
  -H "Content-Type: application/json" \
  -d '{"format": "excel"}'
```

---

## Authentication

All endpoints accept an optional Bearer token. **Authentication is currently permissive** — requests without a token receive viewer-level access (`anonymous` user). This is by design for the demo phase; production deployments should enforce `auto_error=True` and proper JWT validation.

```
Authorization: Bearer <your-jwt-token>
```

**Example:**
```bash
curl -H "Authorization: Bearer your_token_here" \
  http://localhost:8000/companies
```

Public endpoints (no token required): `/health`

---

## HTTP Status Codes

| Code | Meaning | When It Happens |
|------|---------|-----------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created (POST) |
| **400** | Bad Request | Invalid request body or parameters |
| **401** | Unauthorized | Missing/invalid authentication |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable Entity | Schema validation failed |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Database/Redis offline |

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Company not found",
  "error_code": "COMPANY_NOT_FOUND",
  "timestamp": "2026-02-20T10:00:00Z",
  "path": "/companies/nonexistent"
}
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `COMPANY_NOT_FOUND` | 404 | Check company ID |
| `VALIDATION_ERROR` | 422 | Check request schema |
| `DATABASE_ERROR` | 503 | Retry after database comes online |
| `UNAUTHORIZED` | 401 | Add valid Bearer token |

---

## Base URL

```
http://localhost:8000          # Local development
https://api.solstein.io        # Production (when deployed)
```

---

## Request/Response Examples

### Content-Type

All requests must include:
```
Content-Type: application/json
```

### Response Format

All responses are JSON:
```json
{
  "data": {...},
  "meta": {
    "timestamp": "2026-02-20T10:00:00Z",
    "version": "1.0.0"
  }
}
```

---

## Client Code Examples

### Python

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# 1. List companies
response = requests.get(f"{BASE_URL}/companies", headers=HEADERS)
companies = response.json()

# 2. Score a company
response = requests.post(
    f"{BASE_URL}/scoring/company/company-1/score",
    headers=HEADERS
)
scores = response.json()
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// List companies
fetch(`${BASE_URL}/companies`)
  .then(r => r.json())
  .then(companies => console.log(companies));

// Score a company
fetch(`${BASE_URL}/scoring/company/company-1/score`, {
  method: "POST",
  headers: { "Content-Type": "application/json" }
})
  .then(r => r.json())
  .then(scores => console.log(scores));
```

### cURL

```bash
# List companies
curl http://localhost:8000/companies

# Score a company
curl -X POST http://localhost:8000/scoring/company/company-1/score

# With pagination
curl "http://localhost:8000/companies?skip=0&limit=50"

# With filtering
curl "http://localhost:8000/companies?industry=Software&min_revenue=10"
```

---

## Endpoints

### System

#### `GET /health`

Platform availability check. No authentication required.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-02-20T01:43:00Z"
}
```

> Note: This endpoint checks API process availability only. It does not verify Redis or data directory health.

---

### Companies

#### `GET /companies`

List all profiled companies. Supports filtering and pagination.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | integer | Records to skip (default: 0) |
| `limit` | integer | Max records to return (1–1000, default: 100) |
| `tier` | string | Filter by tier (`Tier 1`, `Tier 2`, `Tier 3`, `Tier 4`) |
| `industry` | string | Filter by industry (partial match) |
| `min_revenue` | float | Minimum revenue in EUR millions |

**Response:** Array of Company objects

```json
[
  {
    "id": "acme-energy-bv",
    "name": "Acme Energy BV",
    "industry": "Energy Software",
    "tier": "Tier 1",
    "ai_maturity": "Strong",
    "saas_maturity": 9,
    "growth_score": 8.2,
    "financial_health_score": 7.4,
    "competitive_position_score": 8.0,
    "financials": {
      "revenue": 12.5,
      "growth_rate": 34.0,
      "profit_margin": 18.0
    }
  }
]
```

#### `POST /companies`

Create and immediately score a new company profile.

**Request Body:** Company object (see schema above, without scores)

**Response:** `201 Created` — Scored company with all three scores calculated

**Error:** `400 Bad Request` if validation fails

#### `GET /companies/{company_id}`

Retrieve a single company by ID.

**Path Parameters:** `company_id` — Company identifier string

**Response:** Single Company object

**Error:** `404 Not Found` if company does not exist

---

### Scoring

#### `POST /scoring/company/{company_id}/score`

Score a specific company across all three dimensions.

**Path Parameters:** `company_id` — Company identifier string

**Response:**
```json
{
  "company_id": "acme-energy-bv",
  "growth_score": 8.2,
  "financial_health_score": 7.4,
  "competitive_position_score": 8.0,
  "classification": "Phoenix",
  "calculated_at": "2026-02-20T01:43:00Z"
}
```

**Classification thresholds:**
- `growth_score >= 7.0` → 🔥 Phoenix
- `growth_score <= 4.0` → ⚖️ Lead
- Otherwise → 🧂 Salt

**Error:** `404 Not Found` if company does not exist

#### `GET /scoring/stats`

Market-wide scoring statistics, including tier distribution and classification counts.

**Response:**
```json
{
  "total_companies": 29,
  "revenue_statistics": {
    "total_revenue_eur_m": 450.5,
    "average_revenue_eur_m": 15.5,
    "companies_with_revenue_data": 24
  },
  "growth_statistics": {
    "average_growth_rate_pct": 12.4,
    "companies_with_growth_data": 22
  },
  "growth_classification": {
    "rockets": 4,
    "neutral": 18,
    "dinosaurs": 7
  },
  "calculated_at": "2026-02-20T01:43:00Z"
}
```

> Note: Stats scoring is capped at 50 companies for performance.

#### `GET /scoring/batch`

Queue a background batch scoring job. Returns immediately with a Celery task ID.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Filter by industry |
| `min_revenue` | float | Filter by minimum revenue (EUR millions) |

**Response:**
```json
{
  "message": "Batch scoring task started",
  "task_id": "abc-123",
  "status": "processing",
  "filters": {"industry": "Energy Software", "min_revenue": null}
}
```

> Note: There is currently no status-polling endpoint for Celery tasks. Task results are logged by the worker.

---

### Market Analysis

#### `GET /market/analysis`

Full market landscape analysis: SWOT, barriers to entry, key trends, recommendations, and aggregate metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Industry to analyze |
| `region` | string | Geographic region filter |

**Response:** MarketAnalysis object

**Error:** `404 Not Found` if no companies match the specified industry

#### `GET /market/overlap/{company_id}`

Competitive overlap ranking for a specific company — which competitors are most similar by industry, tier, and AI maturity.

**Path Parameters:** `company_id` — Company identifier string

**Query Parameters:** `top_n` (1–50, default: 10)

**Response:** Array of CompetitiveOverlap objects
```json
[
  {
    "company_a_id": "acme-energy-bv",
    "company_b_id": "gridtech-bv",
    "overlap_score": 1.0,
    "notes": "Calculated based on industry and tier match"
  }
]
```

**Error:** `404 Not Found` if target company does not exist

#### `GET /market/search`

Search companies by keyword within a specific field.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search term (min 2 chars) |
| `field` | string | Field to search: `name`, `industry`, or `description` (default: `name`) |

**Response:**
```json
{
  "query": "acme",
  "field": "name",
  "total_results": 2,
  "results": [...]
}
```

---

### Export

#### `GET /export/excel`

Trigger a background Excel dashboard export. Returns a Celery task ID.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Industry filter (optional) |
| `include_charts` | boolean | Include charts in Excel output (default: true) |

**Response:**
```json
{
  "message": "Export started",
  "task_id": "abc-123",
  "filename": "solstein_energy_software_20260220_014300.xlsx",
  "status": "processing"
}
```

#### `GET /export/json`

Synchronous JSON export of all scored companies.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Industry filter (optional) |

**Response:** JSON object with `exported_at`, `total_companies`, and `companies` array (each with scores attached)

**Error:** `404 Not Found` if no companies match the filter

---

## Common Error Responses

| Status | Meaning |
|--------|---------|
| `400 Bad Request` | Invalid request body (e.g., missing required fields on POST) |
| `404 Not Found` | Requested company or resource does not exist |
| `422 Unprocessable Entity` | Invalid query parameter types or value ranges |
| `500 Internal Server Error` | Server-side failure — check logs |

> `401 Unauthorized` is **not currently returned** — unauthenticated requests receive anonymous viewer access.

---


---

## 📝 Complete Endpoint Documentation

### Response Schema Reference

#### Company Object

```json
{
  "id": "string",                    // Unique identifier
  "name": "string",                  // Company name
  "industry": "string",              // Industry classification
  "tier": "string",                  // Tier 1-4
  "ai_maturity": "string",           // Weak/Medium/Strong
  "saas_maturity": integer,          // 0-10 scale
  "growth_score": number,            // 0.0-10.0
  "financial_health_score": number,  // 0.0-10.0
  "competitive_position_score": number, // 0.0-10.0
  "classification": "string",        // Phoenix/Salt/Lead
  "financials": {
    "revenue": number,               // EUR millions
    "growth_rate": number,           // Percentage
    "profit_margin": number          // Percentage
  },
  "calculated_at": "ISO-8601 timestamp"
}
```

#### Score Response Object

```json
{
  "company_id": "string",
  "growth_score": number,              // 0.0-10.0
  "financial_health_score": number,    // 0.0-10.0
  "competitive_position_score": number, // 0.0-10.0
  "classification": "Phoenix|Salt|Lead",
  "calculated_at": "ISO-8601 timestamp"
}
```

#### Market Analysis Object

```json
{
  "industry": "string",
  "total_companies": integer,
  "summary": "string",
  "swot_analysis": {
    "strengths": ["string"],
    "weaknesses": ["string"],
    "opportunities": ["string"],
    "threats": ["string"]
  },
  "key_trends": ["string"],
  "barriers_to_entry": ["string"],
  "recommendations": ["string"],
  "aggregate_metrics": {
    "average_revenue": number,
    "average_growth_rate": number
  }
}
```

---

## Enrichment API Endpoints (Phase 10-13)

The Connector Enrichment System provides REST API endpoints for enriching company data from multiple sources: SEC EDGAR, Companies House, and News Signals.

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
- `429 Too Many Requests`: Rate limit exceeded (100 req/min/client)
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

---

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

## Rate Limiting (Phase 13.5)

All endpoints (except `/health` and `/ready`) are subject to rate limiting:

- **Default**: 100 requests per minute per client
- **Per-endpoint**: Consistent across all enrichment endpoints
- **Reset**: Automatic every minute
- **Headers Returned**:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1614033660
  ```

**Rate Limit Error Response** (429):
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded: 100 requests per minute",
  "retry_after_seconds": 35,
  "code": "RATELIMIT_001"
}
```

**See**: [Rate Limiting Guide](../guides/rate-limiting.md)

---

## Async Operations (Phase 12)

The Async Job system enables long-running enrichment operations via Celery workers. Jobs are submitted, polled for status, and results retrieved when complete.

> **Requires**: Celery + Redis. If Celery is unavailable, all async endpoints return `503 Service Unavailable`.

### Job Lifecycle

```
1. POST /async/enrich/single or /async/enrich/batch  →  Returns job_id, status: SUBMITTED
2. GET  /async/jobs/{job_id}/status                   →  Returns status: PENDING | RUNNING | SUCCESS | FAILED
3. Poll every 1-5 seconds until status = SUCCESS or FAILED
4. GET  /async/jobs/{job_id}/result                   →  Returns enrichment data (only when SUCCESS)
```

**Status state machine:**
```
SUBMITTED → PENDING → RUNNING → SUCCESS
                               → FAILED (with error_message)
```

---

### `POST /async/enrich/single`

Submit a single company for async enrichment.

**Request Body:**
```json
{
  "company_id": "tech-corp-001",
  "company_name": "TechCorp",
  "sources": ["github", "news"],
  "use_cache": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | string | Yes | Company identifier |
| `company_name` | string | No | Human-readable name |
| `sources` | string[] | No | Data sources to use (defaults to all) |
| `use_cache` | boolean | No | Use cached data if available (default: true) |

**Response:** 200 OK
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "company_id": "tech-corp-001",
  "status": "SUBMITTED",
  "message": "Enrichment job submitted successfully"
}
```

**Errors:**
- `400 Bad Request`: Invalid company_id format
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Celery/Redis not configured

**Example:**
```bash
curl -X POST "http://localhost:8000/async/enrich/single" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "company_id": "tech-corp-001",
    "company_name": "TechCorp",
    "sources": ["github", "news"],
    "use_cache": true
  }'
```

---

### `POST /async/enrich/batch`

Submit multiple companies for async batch enrichment.

**Request Body:**
```json
{
  "companies": [
    {"id": "tech-corp-001", "name": "TechCorp"},
    {"id": "acme-energy-bv", "name": "Acme Energy"}
  ],
  "sources": ["github", "news"],
  "batch_size": 10
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `companies` | object[] | Yes | List of `{id, name}` dicts (max 1000) |
| `sources` | string[] | No | Data sources to use (defaults to all) |
| `batch_size` | integer | No | Processing batch size (default: 10) |

**Response:** 200 OK
```json
{
  "job_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "total_companies": 2,
  "status": "SUBMITTED",
  "message": "Batch enrichment job submitted for 2 companies"
}
```

**Errors:**
- `400 Bad Request`: Empty companies list or batch > 1000
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Celery/Redis not configured

**Example:**
```bash
curl -X POST "http://localhost:8000/async/enrich/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "companies": [
      {"id": "tech-corp-001", "name": "TechCorp"},
      {"id": "acme-energy-bv", "name": "Acme Energy"}
    ],
    "sources": ["github", "news"],
    "batch_size": 10
  }'
```

---

### `GET /async/jobs/{job_id}/status`

Poll the status of an async job. Use this to monitor job progress.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string | Celery task ID returned from submit endpoint |

**Response:** 200 OK
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "RUNNING",
  "progress": 45
}
```

**Status values:**

| Status | Meaning |
|--------|---------|
| `PENDING` | Job queued, not yet started |
| `RUNNING` | Job actively processing (includes `progress` %) |
| `SUCCESS` | Job completed — call `/result` to get data |
| `FAILED` | Job failed — `error` field contains details |

**When `SUCCESS`:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "progress": 100,
  "result": { ... }
}
```

**When `FAILED`:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILED",
  "progress": 0,
  "error": "Connection to SEC EDGAR timed out"
}
```

**Errors:**
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Celery/Redis not configured

**Example (polling pattern):**
```bash
# Submit job
JOB_ID=$(curl -s -X POST "http://localhost:8000/async/enrich/single" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"company_id": "tech-corp-001"}' | jq -r '.job_id')

# Poll until complete
while true; do
  STATUS=$(curl -s "http://localhost:8000/async/jobs/$JOB_ID/status" \
    -H "Authorization: Bearer {token}" | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILED" ]; then break; fi
  sleep 2
done

# Get result
curl -s "http://localhost:8000/async/jobs/$JOB_ID/result" \
  -H "Authorization: Bearer {token}" | jq .
```

---

### `GET /async/jobs/{job_id}/result`

Retrieve the result of a completed async job. Only available when job status is `SUCCESS` or `FAILED`.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string | Celery task ID returned from submit endpoint |

**Response (SUCCESS):** 200 OK
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "SUCCESS",
  "result": {
    "company_id": "tech-corp-001",
    "enrichment_results": { ... },
    "sources_used": ["github", "news"],
    "duration_ms": 4500
  }
}
```

**Response (FAILED):** 200 OK
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "FAILED",
  "error": "Connection to SEC EDGAR timed out"
}
```

**Errors:**
- `202 Accepted`: Job still pending or running (not yet complete)
- `400 Bad Request`: Unknown job state
- `429 Too Many Requests`: Rate limit exceeded
- `503 Service Unavailable`: Celery/Redis not configured

> **Note:** A `202` response means the job is still in progress. Continue polling `/status` and retry `/result` when status reaches `SUCCESS` or `FAILED`.

**Example:**
```bash
curl -X GET "http://localhost:8000/async/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890/result" \
  -H "Authorization: Bearer {token}"
```

---

## Deep Dive Analysis (Drill-Down Endpoints)

The drill-down endpoints provide full transparency into company analysis. All endpoints are read-only (GET) and operate on data from the enrichment audit trail.

> **Tag**: `transparency` — All drill-down endpoints are grouped under the "transparency" tag in the OpenAPI spec.

**Common Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier (same as used in enrichment) |

**Common Errors (all drill-down endpoints):**
- `404 Not Found`: No analysis found for the given company_id

---

### `GET /drill-down/company/{company_id}/why/{signal_name}`

Explain why a company received a specific signal value. Shows the calculation method, contributing facts, and confidence level.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |
| `signal_name` | string | Signal to explain (e.g., `growth_score`, `competitive_position`) |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "signal_name": "growth_score",
  "signal_value": 7.8,
  "confidence": 0.85,
  "reasoning": "Calculated via weighted_multi_source",
  "source_facts": ["revenue_growth_25pct", "employee_count_up_30pct"],
  "calculation_method": "weighted_multi_source"
}
```

**Errors:**
- `404 Not Found`: No analysis found, or signal_name not found for the company

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/why/growth_score" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/sources`

List all data sources gathered during company analysis. Optionally filter by fact type.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fact_type` | string | Filter sources by fact type (optional) |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "total_sources": 3,
  "fact_type_filter": null,
  "sources": [
    {
      "source_id": "src-github-001",
      "source_name": "GitHub API",
      "source_type": "github",
      "url": "https://api.github.com/repos/techcorp/main",
      "confidence": 0.92,
      "retrieval_timestamp": "2026-02-26T10:30:00Z",
      "facts_found": 5
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/sources" \
  -H "Authorization: Bearer {token}"

# With fact_type filter
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/sources?fact_type=revenue" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/source/{source_id}`

Get detailed information about a specific data source, including raw content and metadata.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |
| `source_id` | string | Source identifier (from `/sources` response) |

**Response:** 200 OK
```json
{
  "source_id": "src-github-001",
  "source_name": "GitHub API",
  "source_type": "github",
  "url": "https://api.github.com/repos/techcorp/main",
  "confidence": 0.92,
  "retrieval_timestamp": "2026-02-26T10:30:00Z",
  "raw_content": "...",
  "metadata": { ... },
  "facts": [
    {"type": "commit_velocity", "value": "8.5/day"}
  ]
}
```

**Errors:**
- `404 Not Found`: Source not found for this company

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/source/src-github-001" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/facts`

List all aggregated facts for a company, with optional confidence filtering. Includes contradiction summary.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `min_confidence` | float | Minimum confidence threshold (0.0–1.0, default: 0.0) |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "facts_count": 12,
  "min_confidence_filter": 0.5,
  "facts": [
    {
      "fact_type": "revenue",
      "value": "12500000",
      "confidence": 0.95,
      "sources_used": 3,
      "source_agreement_percentage": 100.0
    }
  ],
  "contradictions_count": 1,
  "contradictions": [
    {
      "fact_type": "employee_count",
      "value": "150",
      "confidence": 0.6
    }
  ]
}
```

**Example:**
```bash
# All facts
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/facts" \
  -H "Authorization: Bearer {token}"

# High-confidence only
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/facts?min_confidence=0.8" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/fact/{fact_type}`

Get detailed information about a specific aggregated fact.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |
| `fact_type` | string | Fact type (e.g., `revenue`, `employee_count`) |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `value` | string | Required — the specific fact value to look up |

**Response:** 200 OK
```json
{
  "fact_type": "revenue",
  "value": "12500000",
  "confidence": 0.95,
  "sources_used": 3,
  "source_agreement_percentage": 100.0
}
```

**Errors:**
- `404 Not Found`: Fact type/value combination not found for this company

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/fact/revenue?value=12500000" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/audit-trail`

Get the complete audit trail for a company analysis, including all enrichment artifacts, scores, and data quality.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Response:** 200 OK — Returns `CompanyAnalysisAuditTrail` object
```json
{
  "company_id": "tech-corp-001",
  "gathering_batch_id": "batch-2026-02-26",
  "company_name": "TechCorp",
  "raw_data": { "sources": [...] },
  "aggregated_facts": { "facts": [...], "average_confidence": 0.87 },
  "extracted_signals": { "signals": [...] },
  "growth_score": 7.8,
  "financial_health_score": 6.5,
  "competitive_position_score": 8.1,
  "classification": "Phoenix",
  "scoring_breakdown": { ... },
  "analysis_started_at": "2026-02-26T10:00:00Z",
  "analysis_completed_at": "2026-02-26T10:02:30Z",
  "analysis_duration_seconds": 150.0,
  "data_completeness": 0.85,
  "confidence_level": "high",
  "errors": [],
  "warnings": ["Companies House data unavailable"]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/audit-trail" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/signals`

List all extracted business signals for a company. Signals are derived from aggregated facts using calculation methods.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "signals_count": 5,
  "signals": [
    {
      "signal_name": "growth_score",
      "signal_value": 7.8,
      "signal_confidence": 0.85,
      "calculation_method": "weighted_multi_source",
      "source_facts": ["revenue_growth_25pct", "employee_count_up_30pct"]
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/signals" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/contradictions`

List all data contradictions detected during analysis. Contradictions occur when different sources report conflicting values for the same fact.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "contradictions_count": 2,
  "contradictions": [
    {
      "fact_type": "employee_count",
      "value": "150",
      "confidence": 0.6
    },
    {
      "fact_type": "revenue",
      "value": "10000000",
      "confidence": 0.45
    }
  ]
}
```

> **Note:** An empty `contradictions` array means all sources agreed. A high contradiction count suggests unreliable data — check individual sources for details.

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/contradictions" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/data-quality`

Get data quality metrics for a company analysis, including completeness, confidence, and coverage gaps.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "completeness": 0.85,
  "average_confidence": 0.87,
  "sources_count": 4,
  "confidence_level": "high",
  "coverage_gaps": []
}
```

**Confidence levels:**

| Level | Meaning |
|-------|---------|
| `unknown` | Insufficient data to assess |
| `low` | Significant data gaps |
| `medium` | Adequate data, some gaps |
| `high` | Comprehensive data |
| `very_high` | Multiple corroborating sources |

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/data-quality" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /drill-down/company/{company_id}/timeline`

Get the timeline of the analysis process, showing when analysis started, completed, and how long it took.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier |

**Response:** 200 OK
```json
{
  "company_id": "tech-corp-001",
  "started_at": "2026-02-26T10:00:00Z",
  "completed_at": "2026-02-26T10:02:30Z",
  "duration_seconds": 150.0,
  "batch_id": "batch-2026-02-26"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/timeline" \
  -H "Authorization: Bearer {token}"
```

---

## Health Checks (Phase 13.3)

### `GET /health`

Platform health check (liveness probe). **NOT rate limited**.

**Response**: 200 OK
```json
{
  "status": "healthy",
  "timestamp": "2026-02-25T21:00:00Z",
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

**See**: [Health Checks Guide](../guides/health-checks.md)

### `GET /ready`

Readiness probe for load balancers. **NOT rate limited**.

**Response**: 200 OK
```json
{
  "ready": true,
  "timestamp": "2026-02-25T21:00:00Z",
  "checks": {
    "database": {"healthy": true},
    "cache": {"healthy": true},
    "sec_edgar_connector": {"healthy": true},
    "companies_house_connector": {"healthy": true},
    "news_signals_connector": {"healthy": true},
    "github_connector": {"healthy": true}
  }
}
```

**See**: [Health Checks Guide](../guides/health-checks.md)

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

---

**Last Updated**: February 26, 2026  
**Status**: Production-Ready ✅
