# Solstein — API Reference

> REST API for the Solstein Competitive Intelligence Platform.
>
> **Base URL**: `http://localhost:8000`  
> **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)  
> **ReDoc**: `http://localhost:8000/redoc`  
> **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

## Authentication

Solstein uses **JWT Bearer tokens** (HS256).

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token

```http
GET /companies
Authorization: Bearer eyJ...
```

---

## Endpoints

### Health

#### `GET /health`
Platform health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### `GET /health/metrics`
Prometheus-compatible metrics endpoint.

#### `GET /healthz`
Kubernetes liveness probe alias. Returns `{"status": "healthy"}`.

---

### Companies

#### `GET /companies`
List all profiled companies.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `industry` | string | Filter by industry |
| `classification` | string | Filter by Phoenix/Salt/Lead |
| `min_score` | float | Minimum growth score |
| `max_score` | float | Maximum growth score |
| `limit` | int | Max results (default: 50) |
| `offset` | int | Pagination offset |

**Response:**
```json
{
  "companies": [
    {
      "id": "uuid",
      "name": "Acme Corp",
      "industry": "Energy Software",
      "classification": "Phoenix",
      "growth_score": 7.8,
      "financial_health_score": 6.5,
      "competitive_position_score": 8.1
    }
  ],
  "total": 101,
  "limit": 50,
  "offset": 0
}
```

#### `GET /companies/{id}`
Retrieve a single company profile with full scoring detail.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Company identifier |

**Response:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "industry": "Energy Software",
  "headquarters": "London, UK",
  "founded_year": 2015,
  "classification": "Phoenix",
  "scores": {
    "growth": 7.8,
    "financial_health": 6.5,
    "competitive_position": 8.1,
    "composite": 7.5
  },
  "signals": [...],
  "last_updated": "2026-03-01T12:00:00Z"
}
```

---

### Scoring

#### `POST /scoring/company/{id}/score`
Trigger scoring for a specific company.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Company identifier |

**Response:**
```json
{
  "company_id": "uuid",
  "classification": "Phoenix",
  "scores": {
    "growth": 7.8,
    "financial_health": 6.5,
    "competitive_position": 8.1
  },
  "scored_at": "2026-03-01T12:00:00Z"
}
```

#### `GET /scoring/stats`
Market-wide scoring statistics.

**Response:**
```json
{
  "total_companies": 101,
  "classification_breakdown": {
    "Phoenix": 23,
    "Salt": 54,
    "Lead": 24
  },
  "score_distribution": {
    "mean": 5.4,
    "median": 5.1,
    "std_dev": 1.8
  }
}
```

---

### Market

#### `GET /market/analysis`
Full market landscape analysis.

**Response:**
```json
{
  "market_summary": "...",
  "top_companies": [...],
  "classification_breakdown": {...},
  "trends": [...]
}
```

#### `GET /market/search`
Search companies by query string.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `limit` | int | Max results (default: 20) |

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Acme Corp",
      "relevance_score": 0.95
    }
  ],
  "total": 5
}
```

#### `GET /market/overlap/{id}`
Competitive overlap analysis for a company.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Company identifier |

**Response:**
```json
{
  "company_id": "uuid",
  "competitors": [
    {
      "id": "uuid",
      "name": "Rival Corp",
      "overlap_score": 0.78,
      "shared_segments": ["Energy Management", "SaaS"]
    }
  ]
}
```

---

### Export

#### `POST /export/`
Generate an Excel intelligence report.

**Request Body:**
```json
{
  "company_ids": ["uuid1", "uuid2"],
  "format": "excel",
  "include_signals": true,
  "include_scoring_detail": true
}
```

**Response:** Binary Excel file (`.xlsx`) download.

---

### Jobs

#### `GET /jobs`
List background jobs.

**Response:**
```json
{
  "jobs": [
    {
      "id": "job-uuid",
      "type": "research_run",
      "status": "completed",
      "created_at": "2026-03-01T10:00:00Z",
      "completed_at": "2026-03-01T10:05:00Z"
    }
  ]
}
```

---

### Enrichment

#### `POST /enrichment/company/{id}`
Trigger data enrichment for a company.

---

### Simulation

#### `GET /simulation`
Run market simulation scenarios.

---

### Drill-Down

Detailed drill-down endpoints for individual company signal chains.

---

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "not_found",
  "message": "Company with id 'uuid' not found",
  "status_code": 404,
  "timestamp": "2026-03-01T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request — invalid input |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient permissions |
| `404` | Not Found |
| `422` | Unprocessable Entity — validation error |
| `429` | Too Many Requests — rate limited |
| `500` | Internal Server Error |

---

## Rate Limiting

API endpoints are rate-limited. When exceeded, you receive:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

---

## CORS

Allowed origins are configured via `API__CORS_ORIGINS` environment variable. Default:
- `http://localhost:3000`
- `http://localhost:8000`

---

## Code Examples

### Python

```python
import httpx

BASE_URL = "http://localhost:8000"

# Authenticate
response = httpx.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "secret"
})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# List companies
companies = httpx.get(f"{BASE_URL}/companies", headers=headers).json()
print(f"Found {companies['total']} companies")

# Score a company
company_id = companies["companies"][0]["id"]
score = httpx.post(f"{BASE_URL}/scoring/company/{company_id}/score", headers=headers).json()
print(f"Classification: {score['classification']}")
```

### curl

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}' | jq -r .access_token)

# List companies
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/companies

# Score a company
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/scoring/company/YOUR-UUID/score
```

---

## Related Documentation

- [`docs/examples/python/python-client.md`](examples/python/python-client.md) — Full Python client examples
- [`docs/examples/curl/curl-examples.md`](examples/curl/curl-examples.md) — curl examples
- [`docs/api/reference.md`](api/reference.md) — Detailed API reference (41+ endpoints)
- [`docs/architecture.md`](architecture.md) — System architecture
