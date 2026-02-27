# Solstein API Documentation

## Overview

Solstein provides a RESTful API for accessing competitive intelligence data. All endpoints return JSON and support async operations.

## Base URL

```
Development: http://localhost:8000
Production:  https://api.solstein.app
```

## Authentication

API authentication is via API key in the header:

```
Authorization: Bearer <api_key>
```

## Endpoints

### Companies

#### List Companies
```
GET /companies
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100, max: 1000)
- `status` (string): Filter by status (active, inactive, archived)
- `sector` (string): Filter by sector

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "status": "active",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "metadata": {},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 100
}
```

#### Get Company by ID
```
GET /companies/{company_id}
```

**Response:**
```json
{
  "id": "uuid",
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "status": "active",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "metadata": {
    "employees": 154000,
    "founded": 1976
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Company
```
POST /companies
```

**Request Body:**
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "metadata": {}
}
```

#### Update Company
```
PUT /companies/{company_id}
```

**Request Body:**
```json
{
  "name": "Apple Inc.",
  "status": "active",
  "metadata": {}
}
```

#### Search Companies
```
GET /companies/search?q={query}
```

**Query Parameters:**
- `q` (string): Search query (searches ticker and name)

### Research Runs

#### List Research Runs
```
GET /research-runs
```

**Query Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Maximum records to return
- `status` (string): Filter by status
- `company_id` (uuid): Filter by company

#### Get Research Run
```
GET /research-runs/{run_id}
```

#### Create Research Run
```
POST /research-runs
```

**Request Body:**
```json
{
  "company_id": "uuid",
  "metadata": {
    "query": "competitive analysis",
    "depth": "comprehensive"
  }
}
```

### Facts

#### List Facts
```
GET /facts
```

**Query Parameters:**
- `company_id` (uuid): Filter by company
- `run_id` (uuid): Filter by research run
- `status` (string): Filter by status (active, superseded, retracted)
- `min_confidence` (float): Minimum confidence score (0-1)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "run_id": "uuid",
      "fact_key": "revenue_2024",
      "fact_value": "394328000000",
      "confidence": 0.95,
      "status": "active",
      "source": "10-K Filing",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Fact
```
POST /facts
```

**Request Body:**
```json
{
  "company_id": "uuid",
  "run_id": "uuid",
  "fact_key": "revenue_2024",
  "fact_value": "394328000000",
  "confidence": 0.95,
  "source": "10-K Filing"
}
```

#### Get Company Facts
```
GET /companies/{company_id}/facts
```

### Signals

#### List Signals
```
GET /signals
```

**Query Parameters:**
- `company_id` (uuid): Filter by company
- `signal_type` (string): Filter by type
- `status` (string): Filter by status
- `direction` (string): Filter by direction (bullish, bearish, neutral)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "company_id": "uuid",
      "run_id": "uuid",
      "signal_type": "price_movement",
      "direction": "bullish",
      "confidence": 0.85,
      "strength": 0.75,
      "status": "active",
      "detected_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Company Signals
```
GET /companies/{company_id}/signals
```

### Scoring

#### Get Company Score
```
GET /companies/{company_id}/score
```

**Response:**
```json
{
  "company_id": "uuid",
  "total_score": 85,
  "growth_score": 90,
  "profitability_score": 80,
  "valuation_score": 85,
  "quality_score": 85,
  "quartile": 1,
  "scored_at": "2024-01-01T00:00:00Z"
}
```

### Health Checks

#### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Readiness Check
```
GET /ready
```

**Response:**
```json
{
  "ready": true,
  "checks": {
    "database": true,
    "migrations": true
  }
}
```

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "ticker",
        "message": "Ticker is required"
      }
    ]
  }
}
```

## Rate Limiting

API requests are rate limited:
- 1000 requests per minute per API key
- 100 requests per second burst limit

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

All list endpoints support pagination:

```
GET /companies?skip=0&limit=100
GET /companies?skip=100&limit=100
```

## Filtering

Multiple filters can be combined:

```
GET /facts?company_id=uuid&status=active&min_confidence=0.8
```

## Sorting

Default sorting is by `created_at DESC`. Custom sorting:

```
GET /companies?sort=ticker&order=asc
```

## SDK Examples

### Python

```python
import httpx

async def get_companies():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/companies",
            headers={"Authorization": "Bearer token"}
        )
        return response.json()
```

### JavaScript

```javascript
const response = await fetch('/api/companies', {
  headers: {
    'Authorization': 'Bearer token'
  }
});
const companies = await response.json();
```

### cURL

```bash
curl -H "Authorization: Bearer token" \
     http://localhost:8000/companies
```

---

For detailed schema information, see the OpenAPI documentation at `/docs` when running the server.
