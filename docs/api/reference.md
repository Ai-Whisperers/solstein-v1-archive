
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
| `/companies/{id}` | DELETE | Delete company profile | Optional |
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

CRUD endpoints for company profiles. Companies router has no prefix — paths are at the root level.

**Source**: `src/solstein/api/routers/companies.py`

---

#### `GET /companies`

List all profiled companies with optional filtering and pagination.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer (≥0) | `0` | Number of records to skip |
| `limit` | integer (1–1000) | `100` | Maximum number of records to return |
| `tier` | string | `null` | Filter by company tier (`Tier 1`, `Tier 2`, `Tier 3`, `Tier 4`) |
| `industry` | string | `null` | Filter by industry |
| `min_revenue` | float (≥0) | `null` | Minimum revenue in EUR millions |

**Response**: `200 OK` — Array of Company objects

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
    "composite_score": 7.8,
    "classification": "Phoenix",
    "geographic_presence": ["EU", "USA"],
    "financials": {
      "revenue": 12.5,
      "growth_rate": 34.0,
      "profit_margin": 18.0
    }
  }
]
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Success |
| `422` | Invalid query parameter type or range |
| `500` | Internal server error |

**Example:**

```bash
# List with pagination and tier filter
curl -X GET "http://localhost:8000/companies?skip=0&limit=10&tier=Phoenix" \
  -H "Authorization: Bearer {token}"

# Filter by industry and minimum revenue
curl -X GET "http://localhost:8000/companies?industry=SaaS&min_revenue=10" \
  -H "Authorization: Bearer {token}"
```

---

#### `POST /companies`

Create a new company profile. Scores are calculated automatically on creation.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Request Body**: `Company` object (JSON)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | **Yes** | Unique company identifier |
| `name` | string | **Yes** | Company name |
| `industry` | string | No | Industry classification (default: `"Energy Software"`) |
| `description` | string | No | Company description |
| `website` | string | No | Company website URL |
| `headquarters` | string | No | Headquarters location |
| `founded_year` | integer | No | Year founded |
| `tier` | string | No | Company tier (`Tier 1`–`Tier 4`, default: `Tier 3`) |
| `ai_maturity` | string | No | AI maturity level (`None`, `Low`, `Moderate`, `Strong`, `Very Strong`) |
| `saas_maturity` | integer (0–10) | No | SaaS maturity score (default: `1`) |
| `geographic_presence` | string[] | No | List of geographic regions |
| `financials` | object | No | Financial metrics (`revenue`, `growth_rate`, `profit_margin`, etc.) |

**Response**: `201 Created` — Scored Company object with all three dimension scores calculated

```json
{
  "id": "tech-corp-001",
  "name": "TechCorp",
  "industry": "SaaS",
  "tier": "Tier 3",
  "growth_score": 5.0,
  "financial_health_score": 5.0,
  "competitive_position_score": 5.0,
  "composite_score": 5.0,
  "classification": "Salt",
  "geographic_presence": ["USA", "EU"]
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `201` | Company created and scored successfully |
| `400` | Bad request — invalid company data or creation error |
| `422` | Schema validation failed (invalid field types/values) |

**Example:**

```bash
curl -X POST "http://localhost:8000/companies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "name": "TechCorp",
    "industry": "SaaS",
    "geographic_presence": ["USA", "EU"],
    "id": "tech-corp-001"
  }'
```

---

#### `GET /companies/{company_id}`

Retrieve a single company by ID.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Unique company identifier |

**Response**: `200 OK` — Single Company object

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Success |
| `404` | Company with specified ID not found |
| `500` | Internal server error |

**Example:**

```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

---

#### `DELETE /companies/{company_id}`

Delete a company profile permanently.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Unique company identifier |

**Response**: `204 No Content` — Empty response body on success

**Status Codes:**

| Code | Condition |
|------|-----------|
| `204` | Company deleted successfully |
| `404` | Company with specified ID not found |
| `500` | Internal server error |

**Example:**

```bash
curl -X DELETE "http://localhost:8000/companies/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

---

### Scoring

Scoring endpoints for calculating and retrieving company scores across three dimensions: growth, financial health, and competitive position. All scoring routes are prefixed with `/scoring`.

**Source**: `src/solstein/api/routers/scoring.py`

---

#### `POST /scoring/company/{company_id}/score`

Calculate growth and competitive scores for a specific company. Scores are persisted back to the database.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Unique company identifier |

**Response**: `200 OK` — Scoring result with full breakdown

```json
{
  "company_id": "tech-corp-001",
  "growth_score": 7.5,
  "financial_health_score": 6.8,
  "competitive_position_score": 7.2,
  "composite_score": 7.1,
  "classification": "Phoenix",
  "scoring_breakdown": {
    "growth": { "raw": 7.5, "weight": 0.4 },
    "financial_health": { "raw": 6.8, "weight": 0.3 },
    "competitive_position": { "raw": 7.2, "weight": 0.3 }
  },
  "calculated_at": "2026-02-26T10:30:00"
}
```

**Classification Thresholds** (based on `growth_score`):

| Classification | Condition | Meaning |
|----------------|-----------|---------|
| 🔥 **Phoenix** | `growth_score >= 7.0` | High-growth, act now |
| 🧂 **Salt** | `4.0 <= growth_score <= 6.9` | Stable, watch for signals |
| ⚖️ **Lead** | `growth_score <= 3.9` | Legacy weight, assess carefully |

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Scores calculated successfully |
| `404` | Company with specified ID not found |
| `500` | Internal server error |

**Example:**

```bash
curl -X POST "http://localhost:8000/scoring/company/tech-corp-001/score" \
  -H "Authorization: Bearer {token}"
```

---

#### `GET /scoring/batch`

Start a batch scoring job for multiple companies. Attempts to run via Temporal workflow; falls back to synchronous scoring if Temporal is unavailable.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `industry` | string | `null` | Filter companies by industry |
| `min_revenue` | float (≥0) | `null` | Filter by minimum revenue (EUR millions) |

**Response**: `200 OK` — Job status (format depends on execution path)

*Temporal workflow response:*
```json
{
  "status": "running",
  "workflow_id": "batch-abc123",
  "message": "Batch scoring workflow started via Temporal",
  "filters": { "industry": "Energy Software" }
}
```

*Synchronous fallback response:*
```json
{
  "processed_count": 15,
  "status": "completed",
  "message": "Batch scoring completed synchronously (Local Fallback)",
  "filters": { "industry": "Energy Software" }
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Batch job started or completed |
| `500` | Both Temporal and fallback scoring failed |

**Example:**

```bash
curl -X GET "http://localhost:8000/scoring/batch?industry=SaaS" \
  -H "Authorization: Bearer {token}"
```

> **Note**: There is currently no status-polling endpoint for Temporal workflow results. Task results are logged by the worker.

---

#### `GET /scoring/stats`

Get platform-wide scoring statistics including revenue aggregates, growth rates, tier distribution, and classification counts.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Query Parameters**: None

**Response**: `200 OK` — Market-wide statistics

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
  "tier_distribution": {
    "Tier 1": 4,
    "Tier 2": 8,
    "Tier 3": 12,
    "Tier 4": 5
  },
  "growth_classification": {
    "Phoenix": 4,
    "Salt": 18,
    "Lead": 7
  },
  "calculated_at": "2026-02-26T10:30:00"
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Statistics calculated successfully |
| `500` | Internal server error |

**Example:**

```bash
curl -X GET "http://localhost:8000/scoring/stats" \
  -H "Authorization: Bearer {token}"
```

---

### Market Analysis

Market landscape analysis, competitive overlap, and company search. All market routes are prefixed with `/market`.

**Source**: `src/solstein/api/routers/market.py`

---

#### `GET /market/analysis`

Perform full market landscape analysis including SWOT, barriers to entry, key trends, recommendations, and aggregate metrics.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `industry` | string | `null` | Industry to analyze |
| `region` | string | `null` | Geographic region filter (matches against company `geographic_presence`) |

**Response**: `200 OK` — `MarketAnalysis` object

```json
{
  "market_name": "SaaS",
  "analysis_date": "2026-02-26T10:30:00Z",
  "companies": [ "...Company objects..." ],
  "total_market_size": null,
  "growth_rate": null,
  "concentration_ratio": null,
  "barriers_to_entry": ["High capital requirements", "Regulatory compliance"],
  "key_trends": ["AI adoption accelerating", "Consolidation in mid-market"],
  "regulatory_environment": [],
  "swot_analysis": {
    "strengths": ["Strong recurring revenue"],
    "weaknesses": ["Limited geographic reach"],
    "opportunities": ["AI-driven automation"],
    "threats": ["Increasing competition"]
  },
  "recommendations": ["Focus on AI capabilities", "Expand geographic presence"]
}
```

Returns an empty `MarketAnalysis` (with `companies: []`) if no companies match the filters.

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Analysis completed (may be empty if no matching companies) |
| `500` | Internal server error |

**Example:**

```bash
curl -X GET "http://localhost:8000/market/analysis?industry=SaaS" \
  -H "Authorization: Bearer {token}"
```

---

#### `GET /market/overlap/{company_id}`

Calculate competitive overlap for a specific company against all peers in the same industry. Returns the top 10 most similar competitors ranked by overlap score.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Unique company identifier |

**Response**: `200 OK` — Array of `CompetitiveOverlap` objects (max 10, sorted by overlap score descending)

```json
[
  {
    "company_a_id": "acme-energy-bv",
    "company_b_id": "gridtech-bv",
    "overlap_score": 0.85,
    "overlap_areas": ["Energy Software"],
    "competitive_intensity": "Medium",
    "notes": null
  }
]
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Overlap calculated successfully |
| `404` | Target company not found |
| `500` | Internal server error |

**Example:**

```bash
curl -X GET "http://localhost:8000/market/overlap/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

---

#### `GET /market/search`

Search companies by keyword within a specific field. Returns up to 100 matching results.

**Authentication**: Bearer token (optional — anonymous gets viewer access)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string (min 2 chars) | **Required** | Search term |
| `field` | string | `"name"` | Field to search: `name`, `industry`, or `description` |

**Response**: `200 OK` — Search results

```json
{
  "query": "acme",
  "field": "name",
  "total_results": 2,
  "results": [
    {
      "id": "acme-energy-bv",
      "name": "Acme Energy BV",
      "industry": "Energy Software"
    }
  ]
}
```

**Status Codes:**

| Code | Condition |
|------|-----------|
| `200` | Search completed |
| `422` | Query too short (< 2 characters) |
| `500` | Internal server error |

**Example:**

```bash
curl -X GET "http://localhost:8000/market/search?query=acme&field=name" \
  -H "Authorization: Bearer {token}"
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

## Enrichment Operations

The Enrichment API provides endpoints for enriching company data from multiple sources (SEC EDGAR, Companies House, News Signals), managing the enrichment cache, viewing audit trails, and monitoring platform health.

> **Router**: `src/solstein/api/routers/enrichment.py` — Registered **without prefix** in `main.py`.
>
> **Routing Note**: The enrichment router is registered *first* in `main.py` (before `health.py`). This means `/health` is served by `enrichment.py`, not `health.py`. The health router provides separate endpoints at `/health/live`, `/health/ready`, and `/health/status` (see [Health Checks (Phase 13.3)](#health-checks-phase-133)).

---

### `POST /companies/{company_id}/enrich`

Enrich a single company from available data connectors.

**Authentication**: Optional Bearer token

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier (required) |

**Request Body** (`EnrichmentRequest`):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sources` | array[string] | `["SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS"]` | Data sources to use |
| `dry_run` | boolean | `false` | If true, don't persist results |

```json
{
  "sources": ["SEC_EDGAR", "COMPANIES_HOUSE", "NEWS_SIGNALS"],
  "dry_run": false
}
```

**Response** (`EnrichmentResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | string | Company identifier |
| `company_name` | string | Company name |
| `status` | string | `"success"` or `"failure"` |
| `enrichment` | object | Enrichment metadata |
| `enrichment.sources_used` | array[string] | Sources that were queried |
| `enrichment.fields_enriched` | array[string] | Fields that were updated |
| `enrichment.duration_ms` | integer | Processing time in milliseconds |
| `data` | EnrichmentResultData \| null | Enriched financial data |
| `data.revenue` | float \| null | Company revenue |
| `data.employees` | integer \| null | Number of employees |
| `data.growth_rate` | float \| null | Revenue growth rate |
| `data.profit_margin` | float \| null | Profit margin |
| `data.funding_raised` | float \| null | Total funding raised |
| `data.valuation` | float \| null | Company valuation |

```json
{
  "company_id": "tech-corp-001",
  "company_name": "TechCorp",
  "status": "success",
  "enrichment": {
    "sources_used": ["SEC_EDGAR", "COMPANIES_HOUSE"],
    "fields_enriched": ["revenue", "employees", "profit_margin"],
    "duration_ms": 1234
  },
  "data": {
    "revenue": 5000000,
    "employees": 150,
    "growth_rate": 0.15,
    "profit_margin": 0.12,
    "funding_raised": 2000000,
    "valuation": 50000000
  }
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Enrichment completed (success or partial) |
| `400` | Invalid company ID or parameters |
| `401` | Unauthorized |
| `404` | Company not found |
| `429` | Rate limit exceeded |
| `503` | Connector unavailable |

**Example**:
```bash
curl -X POST "http://localhost:8000/companies/tech-corp-001/enrich" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"sources": ["SEC_EDGAR", "NEWS_SIGNALS"], "dry_run": false}'
```

---

### `POST /companies/enrich/batch`

Batch enrich multiple companies with caching and optimization.

**Authentication**: Optional Bearer token

**Request Body** (`BatchEnrichmentRequest`):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `company_ids` | array[string] | *(required)* | Company IDs to enrich (1–1000) |
| `batch_size` | integer | `10` | Companies per batch (1–100) |
| `use_cache` | boolean | `true` | Whether to use cached results |
| `dry_run` | boolean | `false` | If true, don't persist results |

```json
{
  "company_ids": ["tech-corp-001", "saas-inc-002", "fintech-003"],
  "batch_size": 10,
  "use_cache": true,
  "dry_run": false
}
```

**Response** (`BatchEnrichmentResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall batch status |
| `batch_id` | string | Unique batch identifier |
| `total_companies` | integer | Total companies requested |
| `enriched_count` | integer | Successfully enriched count |
| `failed_count` | integer | Failed enrichment count |
| `results` | array[BatchEnrichmentResult] | Per-company results |
| `results[].company_id` | string | Company identifier |
| `results[].status` | string | `"success"` or `"failed"` |
| `results[].duration_ms` | float | Processing time in ms |
| `results[].source` | string \| null | Data source used |
| `results[].error` | string \| null | Error message if failed |
| `metrics` | object | Batch processing metrics |
| `metrics.total_duration_ms` | integer | Total batch processing time |
| `metrics.avg_duration_ms` | integer | Average per-company time |
| `metrics.cache_hits` | integer | Number of cache hits |
| `metrics.cache_misses` | integer | Number of cache misses |
| `metrics.success_rate` | float | Percentage of successful enrichments |

```json
{
  "status": "success",
  "batch_id": "batch_1740000000.0",
  "total_companies": 3,
  "enriched_count": 3,
  "failed_count": 0,
  "results": [
    {"company_id": "tech-corp-001", "status": "success", "duration_ms": 245, "source": "batch_enrichment"},
    {"company_id": "saas-inc-002", "status": "success", "duration_ms": 245, "source": "batch_enrichment"},
    {"company_id": "fintech-003", "status": "success", "duration_ms": 245, "source": "batch_enrichment"}
  ],
  "metrics": {
    "total_duration_ms": 735,
    "avg_duration_ms": 245,
    "cache_hits": 0,
    "cache_misses": 3,
    "success_rate": 100.0
  }
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Batch processing completed |
| `400` | Invalid request (bad company ID format) |
| `401` | Unauthorized |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X POST "http://localhost:8000/companies/enrich/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "company_ids": ["tech-corp-001", "saas-inc-002"],
    "batch_size": 2,
    "use_cache": true
  }'
```

---

### `GET /companies/{company_id}/enrichment/audit`

Retrieve the enrichment audit trail for a specific company. Returns a chronological log of all enrichment operations (starts, successes, failures, cache hits).

**Authentication**: Optional Bearer token

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier (required) |

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | `50` | Max entries to return (1–1000) |
| `offset` | integer | `0` | Entries to skip (for pagination) |

**Response** (`AuditTrailResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | string | Company identifier |
| `company_name` | string \| null | Company name |
| `audit_entries` | array[AuditEntry] | Audit log entries |
| `audit_entries[].timestamp` | datetime | Operation timestamp (ISO 8601) |
| `audit_entries[].operation` | string | Operation type (`enrich_start`, `enrich_success`, `enrich_failure`, `cache_hit`) |
| `audit_entries[].source` | string \| null | Data source used |
| `audit_entries[].status` | string \| null | Operation status |
| `audit_entries[].fields` | array[string] \| null | Fields enriched |
| `audit_entries[].duration_ms` | float \| null | Operation duration in ms |
| `audit_entries[].user_id` | string \| null | User who triggered the operation |
| `summary` | object | Audit statistics |

```json
{
  "company_id": "tech-corp-001",
  "company_name": null,
  "audit_entries": [
    {
      "timestamp": "2026-02-26T10:30:00Z",
      "operation": "enrich_success",
      "source": "SEC_EDGAR",
      "status": "SUCCESS",
      "fields": ["revenue", "employees"],
      "duration_ms": 450,
      "user_id": null
    },
    {
      "timestamp": "2026-02-26T10:29:55Z",
      "operation": "enrich_start",
      "source": "SEC_EDGAR,COMPANIES_HOUSE",
      "status": "IN_PROGRESS",
      "fields": null,
      "duration_ms": null,
      "user_id": null
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

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Audit trail retrieved |
| `404` | Company not found (invalid ID format) |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001/enrichment/audit?limit=10" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /companies/{company_id}/enrichment/cache`

Check whether enrichment data is cached for a specific company, and retrieve cache metadata.

**Authentication**: Optional Bearer token

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier (required) |

**Response** (`CacheCheckResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | string | Company identifier |
| `cached` | boolean | Whether data is cached |
| `cache_key` | string \| null | Cache key used |
| `ttl_remaining_hours` | float \| null | Remaining TTL in hours |
| `cached_data` | object \| null | Cached enrichment data (if available) |

```json
{
  "company_id": "tech-corp-001",
  "cached": true,
  "cache_key": "company_tech-corp-001",
  "ttl_remaining_hours": 23.5,
  "cached_data": {
    "revenue": 5000000,
    "employees": 150
  }
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Cache status retrieved (cached or not) |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001/enrichment/cache" \
  -H "Authorization: Bearer {token}"
```

---

### `POST /enrichment/cache/clear`

Clear all enrichment cache entries. Clears both database-backed and in-memory caches.

**Authentication**: Optional Bearer token

**Request Body**: None

**Response** (`CacheClearResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Operation status (`"success"`) |
| `message` | string | Status message |
| `entries_cleared` | integer | Number of cache entries cleared |

```json
{
  "status": "success",
  "message": "Enrichment cache cleared",
  "entries_cleared": 47
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Cache cleared successfully |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X POST "http://localhost:8000/enrichment/cache/clear" \
  -H "Authorization: Bearer {token}"
```

---

### `POST /enrichment/cache/clear/{company_id}`

Clear cached enrichment data for a specific company.

**Authentication**: Optional Bearer token

**Path Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | string | Company identifier (required) |

**Request Body**: None

**Response** (`CacheClearResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Operation status (`"success"`) |
| `message` | string | Status message (includes company ID) |
| `entries_cleared` | integer | Number of cache entries cleared |

```json
{
  "status": "success",
  "message": "Cache cleared for tech-corp-001",
  "entries_cleared": 1
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Cache cleared for company |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X POST "http://localhost:8000/enrichment/cache/clear/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

---

### `GET /health`

Platform health check (liveness probe). Checks database and cache connectivity, plus status of all data connectors (SEC EDGAR, Companies House, News Signals).

> **⚠️ Routing Note**: This endpoint is served by `enrichment.py` (registered first in `main.py`), not by `health.py`. The health router serves `/health/live`, `/health/ready`, and `/health/status` at prefixed paths. See [Health Checks (Phase 13.3)](#health-checks-phase-133) for the `health.py` endpoints.

**Authentication**: Not required

**Rate Limited**: No — health probes are always accessible

**Response** (`HealthCheckResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"healthy"` or `"unhealthy"` |
| `timestamp` | datetime | Health check timestamp (ISO 8601) |
| `version` | string | API version (currently `"1.0"`) |
| `components` | object | Per-component health statuses |
| `components.database` | string | `"operational"`, `"not_initialized"`, or `"unavailable"` |
| `components.cache` | string | Cache status |
| `components.sec_edgar` | string | SEC EDGAR connector status |
| `components.companies_house` | string | Companies House connector status |
| `components.news_signals` | string | News Signals connector status |

```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T10:30:00Z",
  "version": "1.0",
  "components": {
    "database": "operational",
    "cache": "operational",
    "sec_edgar": "operational",
    "companies_house": "not_initialized",
    "news_signals": "operational"
  }
}
```

**Health Logic**: Overall status is `"healthy"` only when **both** database and cache are healthy. Individual connector failures do not affect overall health.

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | System is healthy (or unhealthy — check `status` field) |

> **Note**: The current implementation returns HTTP 200 even when unhealthy, with `status: "unhealthy"` in the body. Callers should check the `status` field. Production deployments should use middleware to convert unhealthy responses to HTTP 503.

**Example**:
```bash
curl -X GET "http://localhost:8000/health"
```

---

### `GET /ready`

Readiness probe for load balancers. Checks whether the system is ready to serve traffic by verifying configuration, connectors, cache, and database.

> **⚠️ Routing Note**: This endpoint is at `/ready` (from `enrichment.py`). The health router provides a separate readiness endpoint at `/health/ready`. Both perform similar checks but return different response models.

**Authentication**: Not required (but rate limited)

**Rate Limited**: Yes

**Response** (`ReadinessCheckResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `ready` | boolean | Whether service is ready to serve traffic |
| `timestamp` | datetime | Readiness check timestamp (ISO 8601) |
| `checks` | object | Individual readiness checks (all boolean) |
| `checks.configuration_loaded` | boolean | Configuration is loaded |
| `checks.connectors_initialized` | boolean | At least one data connector is healthy |
| `checks.cache_operational` | boolean | Cache subsystem is operational |
| `checks.enrichment_enabled` | boolean | Enrichment pipeline is enabled |
| `checks.database_ready` | boolean | Database is accessible |

```json
{
  "ready": true,
  "timestamp": "2026-02-26T10:30:00Z",
  "checks": {
    "configuration_loaded": true,
    "connectors_initialized": true,
    "cache_operational": true,
    "enrichment_enabled": true,
    "database_ready": true
  }
}
```

**Readiness Logic**: System is `ready` when database status is `"operational"` or `"not_initialized"` AND cache status is `"operational"` or `"not_initialized"`. A system with `not_initialized` components can still serve traffic (graceful degradation).

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | System is ready |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X GET "http://localhost:8000/ready"
```

---

### `GET /metrics`

Retrieve enrichment performance metrics including enrichment counts, cache statistics, and rate limiting state.

> **⚠️ Routing Note**: This endpoint is at `/metrics` (from `enrichment.py`). The health router provides a separate data quality metrics endpoint at `/metrics/data-quality`.

**Authentication**: Not required (but rate limited)

**Rate Limited**: Yes

**Response** (`MetricsResponse`): `200 OK`

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | Metrics collection timestamp (ISO 8601) |
| `enrichment` | object | Enrichment processing metrics |
| `enrichment.total` | integer | Total enrichment requests processed |
| `enrichment.successful` | integer | Successful enrichments |
| `enrichment.failed` | integer | Failed enrichments |
| `enrichment.success_rate` | float | Success rate (0–100) |
| `enrichment.avg_duration_ms` | float | Average enrichment duration in ms |
| `enrichment.total_duration_ms` | float | Total cumulative processing time |
| `cache` | object | Cache performance metrics |
| `cache.size` | integer | Current cache size (entries) |
| `cache.ttl_hours` | integer | Cache TTL in hours |
| `cache.hits` | integer | Total cache hits |
| `cache.misses` | integer | Total cache misses |
| `cache.hit_rate` | float | Cache hit rate (0.0–1.0) |
| `rate_limiting` | object | Rate limiting state for current client |
| `rate_limiting.requests_per_minute` | integer | Configured rate limit |
| `rate_limiting.current_requests` | integer | Requests made in current window |
| `rate_limiting.remaining` | integer | Remaining requests in current window |

```json
{
  "timestamp": "2026-02-26T10:30:00Z",
  "enrichment": {
    "total": 156,
    "successful": 152,
    "failed": 4,
    "success_rate": 97.4,
    "avg_duration_ms": 892,
    "total_duration_ms": 139232
  },
  "cache": {
    "size": 45,
    "ttl_hours": 24,
    "hits": 230,
    "misses": 152,
    "hit_rate": 0.0
  },
  "rate_limiting": {
    "requests_per_minute": 100,
    "current_requests": 1,
    "remaining": 99
  }
}
```

**Status Codes**:

| Code | Meaning |
|------|---------|
| `200` | Metrics retrieved |
| `429` | Rate limit exceeded |

**Example**:
```bash
curl -X GET "http://localhost:8000/metrics"
```

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

> **Note**: The primary `/health`, `/ready`, and `/metrics` endpoints are served by the enrichment router and documented above in [Enrichment Operations](#enrichment-operations). The endpoints below are from the **health router** (`health.py`) and serve at prefixed paths.

### `GET /health/live`

Kubernetes liveness probe (from `health.py`). Returns basic health status.

**Authentication**: Not required

### `GET /health/ready`

Kubernetes readiness probe (from `health.py`). Checks database and all connectors.

**Authentication**: Not required

### `GET /health/status`

Full health status with detailed component checks (from `health.py`).

**Authentication**: Not required

### `GET /metrics/data-quality`

Data quality metrics for the market intelligence pipeline (from `health.py`).

**Authentication**: Not required

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
