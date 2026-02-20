
# 📜 API Reference

**Solstein REST API — Complete Endpoint Reference**

> Interactive docs (Swagger UI) available at `http://localhost:8000/docs` when running locally.
> ReDoc available at `http://localhost:8000/redoc`.

---

## Authentication

All endpoints accept an optional Bearer token. **Authentication is currently permissive** — requests without a token receive viewer-level access (`anonymous` user). This is by design for the demo phase; production deployments should enforce `auto_error=True` and proper JWT validation.

```
Authorization: Bearer <your-jwt-token>
```

Public endpoints (no token required): `/health`

---

## Base URL

```
http://localhost:8000          # Local development
https://api.solstein.io        # Production (when deployed)
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
