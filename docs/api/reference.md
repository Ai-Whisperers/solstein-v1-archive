
# 📜 API Reference

**Solstein REST API — Complete Endpoint Reference**

> Interactive docs (Swagger UI) available at `http://localhost:8000/docs` when running locally.
> ReDoc available at `http://localhost:8000/redoc`.
> OpenAPI Schema: `http://localhost:8000/openapi.json`

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
  "classification": "Rocket",
  "calculated_at": "2026-02-20T01:43:00Z"
}
```

**Classification thresholds:**
- `growth_score >= 7.0` → 🚀 Rocket
- `growth_score <= 4.0` → 🦕 Dinosaur
- Otherwise → ⚖️ Neutral

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
