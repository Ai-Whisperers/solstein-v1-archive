# Wave 2: Detailed Task Specifications & Implementation Guide
**Generated**: 2026-02-26  
**For**: Tasks 2-5 (Documentation of 41 endpoints)  
**Status**: READY FOR PARALLEL EXECUTION  

---

## Overview

This guide enhances Tasks 2-5 with:
- ✅ Exact code references (line numbers, class names)
- ✅ Response model details from actual code
- ✅ Example curl commands (ready to execute)
- ✅ Concrete QA scenario steps
- ✅ Agent dispatch recommendations

---

## TASK 2: Document Core Endpoints (Companies, Scoring, Market)

### Endpoints to Document
```
5.  GET     /companies
6.  POST    /companies
7.  GET     /companies/{company_id}
8.  DELETE  /companies/{company_id}
39. GET     /scoring/batch
40. POST    /scoring/company/{company_id}/score
41. GET     /scoring/stats
36. GET     /market/analysis
37. GET     /market/overlap/{company_id}
38. GET     /market/search
```

### Code References

**Companies Router**: `src/solstein/api/routers/companies.py`
- `GET /companies` (line 15): Returns `list[Company]`
  - Query params: `skip` (int, default 0), `limit` (int, default 100, max 1000), `tier` (CompanyTier | None), `industry` (str | None), `min_revenue` (float | None)
  - Error: 500 on exception
- `POST /companies` (line 68): Request body `Company`, returns `Company`, 201 Created
  - Error: 400 on bad request, 500 on error
- `GET /companies/{company_id}` (line 41): Returns `Company`
  - Error: 404 if not found, 500 on error
- `DELETE /companies/{company_id}` (line 97): Returns 204 No Content
  - Error: 404 if not found, 500 on error

**Scoring Router**: `src/solstein/api/routers/scoring.py`
- `POST /scoring/company/{company_id}/score` (line 36): Returns dict with scoring breakdown
  - Response includes: `company_id`, `growth_score`, `financial_health_score`, `competitive_position_score`, `composite_score`, `classification`, `scoring_breakdown`, `calculated_at`
  - Error: 404 if company not found, 500 on error
- `GET /scoring/batch` (offset 81+): Returns paginated scores
- `GET /scoring/stats` (offset 130+): Returns market-wide statistics

**Market Router**: `src/solstein/api/routers/market.py`
- `GET /market/analysis` (line 16): Returns `MarketAnalysis`
  - Query params: `industry` (str | None), `region` (str | None)
  - Error: 500 on error, returns empty analysis if no companies match
- `GET /market/overlap/{company_id}` (line 51): Returns `list[CompetitiveOverlap]`
  - Error: 404 if company not found, 500 on error
- `GET /market/search` (offset 130+): Market search endpoint

### Response Model Details

**Company Model** (from `src/solstein/domain/models.py`):
```python
class Company:
    id: str
    name: str
    industry: str | None
    geographic_presence: list[str]
    founder_names: list[str]
    growth_score: float | None
    financial_health_score: float | None
    competitive_position_score: float | None
    composite_score: float | None
    tier: CompanyTier  # "Phoenix" | "Salt" | "Lead"
    # ... more fields
```

**MarketAnalysis Model** (from `src/solstein/domain/models.py`):
```python
class MarketAnalysis:
    market_name: str
    companies: list[Company]
    average_growth_score: float
    market_leaders: list[str]  # company IDs
    # ... more fields
```

**CompetitiveOverlap Model**:
```python
class CompetitiveOverlap:
    company_a_id: str
    company_b_id: str
    overlap_score: float
    overlap_areas: list[str]
    competitive_intensity: str
    notes: str | None
```

### Example Curl Commands

**GET /companies** (list with pagination)
```bash
curl -X GET "http://localhost:8000/companies?skip=0&limit=10&tier=Phoenix" \
  -H "Authorization: Bearer {token}"
```

**GET /companies** (with industry filter)
```bash
curl -X GET "http://localhost:8000/companies?industry=SaaS&min_revenue=10" \
  -H "Authorization: Bearer {token}"
```

**POST /companies** (create new company)
```bash
curl -X POST "http://localhost:8000/companies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "name": "TechCorp",
    "industry": "SaaS",
    "geographic_presence": ["USA", "EU"],
    "founder_names": ["John Doe", "Jane Smith"],
    "id": "tech-corp-001"
  }'
```

**GET /companies/{company_id}**
```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

**DELETE /companies/{company_id}**
```bash
curl -X DELETE "http://localhost:8000/companies/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

**POST /scoring/company/{company_id}/score**
```bash
curl -X POST "http://localhost:8000/scoring/company/tech-corp-001/score" \
  -H "Authorization: Bearer {token}"

# Response:
# {
#   "company_id": "tech-corp-001",
#   "growth_score": 7.5,
#   "financial_health_score": 6.8,
#   "competitive_position_score": 7.2,
#   "composite_score": 7.1,
#   "classification": "Phoenix",
#   "scoring_breakdown": {...},
#   "calculated_at": "2026-02-26T10:30:00"
# }
```

**GET /market/analysis**
```bash
curl -X GET "http://localhost:8000/market/analysis?industry=SaaS" \
  -H "Authorization: Bearer {token}"
```

**GET /market/overlap/{company_id}**
```bash
curl -X GET "http://localhost:8000/market/overlap/tech-corp-001" \
  -H "Authorization: Bearer {token}"

# Returns top 10 competitors by overlap score
```

### QA Scenarios with Concrete Steps

**Scenario 1: GET /companies with pagination works correctly**
```
Steps:
  1. Execute: curl "http://localhost:8000/companies?skip=0&limit=5"
  2. Verify response is array of Company objects
  3. Count returned items: should be ≤5
  4. Execute with skip=5: curl "http://localhost:8000/companies?skip=5&limit=5"
  5. Verify different companies returned than first call
  6. Check each Company has: id, name, industry fields
Expected: Pagination works, returns correct subset
Evidence Path: .sisyphus/evidence/task-2-companies-pagination.txt
```

**Scenario 2: POST /companies creates company with correct response**
```
Steps:
  1. Create test company body with unique name
  2. POST to /companies with valid body
  3. Verify response status code is 201
  4. Check response body has same name as input
  5. Extract returned company_id
  6. GET /companies/{id} with extracted ID
  7. Verify returned company matches what was posted
Expected: Created company can be retrieved, all fields present
Evidence Path: .sisyphus/evidence/task-2-companies-create.txt
```

**Scenario 3: GET /companies/{company_id} returns 404 for non-existent ID**
```
Steps:
  1. GET /companies/nonexistent-id-12345
  2. Verify response status is 404
  3. Verify error message mentions "not found"
Expected: 404 error for missing company
Evidence Path: .sisyphus/evidence/task-2-companies-notfound.txt
```

**Scenario 4: DELETE /companies/{company_id} returns 204**
```
Steps:
  1. POST /companies to create test company (save ID)
  2. DELETE /companies/{id}
  3. Verify response status is 204
  4. GET /companies/{id} again
  5. Verify now returns 404 (company deleted)
Expected: Deletion succeeds, company no longer exists
Evidence Path: .sisyphus/evidence/task-2-companies-delete.txt
```

**Scenario 5: POST /scoring/company/{company_id}/score returns correct breakdown**
```
Steps:
  1. Get a known company ID from GET /companies
  2. POST /scoring/company/{id}/score
  3. Verify response includes: growth_score, financial_health_score, competitive_position_score
  4. Verify classification is one of: "Phoenix", "Salt", "Lead"
  5. Verify growth_score >= 7.0 means "Phoenix" classification
  6. Verify growth_score <= 3.9 means "Lead" classification
Expected: Scoring returns all required fields with correct classification logic
Evidence Path: .sisyphus/evidence/task-2-scoring-response.txt
```

### Agent Profile Recommendation
- **Category**: `unspecified-high`
- **Skills**: None required
- **Why**: Requires careful reading of code, extracting exact response models, writing clear parameter documentation

---

## TASK 3: Document Enrichment Endpoints (9 endpoints)

### Endpoints to Document
```
19. POST    /companies/enrich/batch
20. POST    /companies/{company_id}/enrich
21. GET     /companies/{company_id}/enrichment/audit
22. GET     /companies/{company_id}/enrichment/cache
23. POST    /enrichment/cache/clear
24. POST    /enrichment/cache/clear/{company_id}
25. GET     /health
26. GET     /metrics
27. GET     /ready
```

### Code References

**Enrichment Router**: `src/solstein/api/routers/enrichment.py`
- File has extensive comments documenting all 8+ endpoints (lines 1-50)
- Imports all schemas from `src/solstein/api/schemas/enrichment.py`
- Response models:
  - `HealthCheckResponse`
  - `ReadinessCheckResponse`
  - `MetricsResponse`
  - `EnrichmentRequest` / `EnrichmentResponse`
  - `BatchEnrichmentRequest` / `BatchEnrichmentResponse`
  - `AuditTrailResponse`
  - `CacheCheckResponse`
  - `CacheClearResponse`

### Request/Response Bodies

**POST /companies/{company_id}/enrich**
```python
Request: EnrichmentRequest
  - company_id: str
  - company_name: str | None
  - sources: list[str] | None
  - use_cache: bool = True

Response: EnrichmentResponse
  - company_id: str
  - enrichment_results: EnrichmentResultData
  - timestamp: str (ISO format)
```

**POST /companies/enrich/batch**
```python
Request: BatchEnrichmentRequest
  - companies: list[dict]  # Each: {id, name}
  - sources: list[str] | None
  - batch_size: int = 10

Response: BatchEnrichmentResponse
  - batch_id: str
  - total_requested: int
  - results: list[BatchEnrichmentResult]
  - timestamp: str
```

**GET /health** (from enrichment.py)
```
Response: HealthCheckResponse
  - status: "healthy" | "unhealthy"
  - timestamp: str (ISO format)
```

**GET /ready** (from enrichment.py)
```
Response: ReadinessCheckResponse
  - ready: bool
  - checks: dict[str, bool]
  - timestamp: str
```

**GET /metrics** (from enrichment.py)
```
Response: MetricsResponse
  - timestamp: str
  - requests: {total, successful, failed, error_rate}
  - cache: {hits, misses, hit_rate}
```

### Example Curl Commands

**POST /companies/{company_id}/enrich** (single)
```bash
curl -X POST "http://localhost:8000/companies/tech-corp-001/enrich" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "company_id": "tech-corp-001",
    "company_name": "TechCorp",
    "sources": ["github", "news", "sec"],
    "use_cache": true
  }'
```

**POST /companies/enrich/batch** (batch)
```bash
curl -X POST "http://localhost:8000/companies/enrich/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "companies": [
      {"id": "tech-corp-001", "name": "TechCorp"},
      {"id": "saas-inc-002", "name": "SaaS Inc"}
    ],
    "sources": ["github", "news"],
    "batch_size": 2
  }'
```

**GET /companies/{company_id}/enrichment/audit**
```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001/enrichment/audit" \
  -H "Authorization: Bearer {token}"

# Returns: {
#   "company_id": "tech-corp-001",
#   "total_enrichments": 5,
#   "recent_audits": [
#     {"timestamp": "...", "source": "github", "status": "success"},
#     ...
#   ]
# }
```

**GET /companies/{company_id}/enrichment/cache**
```bash
curl -X GET "http://localhost:8000/companies/tech-corp-001/enrichment/cache" \
  -H "Authorization: Bearer {token}"

# Returns: {
#   "company_id": "tech-corp-001",
#   "cache_status": "hit" | "miss",
#   "cache_age_seconds": 3600,
#   "cached_fields": ["growth_score", "team_size", ...]
# }
```

**POST /enrichment/cache/clear** (clear all)
```bash
curl -X POST "http://localhost:8000/enrichment/cache/clear" \
  -H "Authorization: Bearer {token}"

# Returns: {
#   "cleared_count": 150,
#   "timestamp": "..."
# }
```

**POST /enrichment/cache/clear/{company_id}** (clear specific)
```bash
curl -X POST "http://localhost:8000/enrichment/cache/clear/tech-corp-001" \
  -H "Authorization: Bearer {token}"
```

**GET /health** (from enrichment.py)
```bash
curl -X GET "http://localhost:8000/health"

# Returns: {
#   "status": "healthy",
#   "timestamp": "2026-02-26T10:30:00"
# }
```

**GET /ready** (from enrichment.py)
```bash
curl -X GET "http://localhost:8000/ready"

# Returns 200 if ready, 503 if not
# {
#   "ready": true,
#   "checks": {
#     "database": true,
#     "cache": true,
#     "data_sources": true
#   },
#   "timestamp": "..."
# }
```

**GET /metrics** (from enrichment.py)
```bash
curl -X GET "http://localhost:8000/metrics"

# Returns: {
#   "timestamp": "...",
#   "requests": {
#     "total": 1250,
#     "successful": 1240,
#     "failed": 10,
#     "error_rate": 0.008
#   },
#   "cache": {
#     "hits": 450,
#     "misses": 150,
#     "hit_rate": 0.75
#   }
# }
```

### QA Scenarios

**Scenario 1: POST /enrich single returns valid response**
```
Steps:
  1. POST /companies/{id}/enrich with valid company_id
  2. Verify response status 200
  3. Verify response has: company_id, enrichment_results, timestamp
  4. Verify enrichment_results is non-empty dict
Expected: Enrichment succeeds with complete response
Evidence: .sisyphus/evidence/task-3-enrich-single.txt
```

**Scenario 2: POST /enrich batch processes multiple companies**
```
Steps:
  1. Create batch request with 3 companies
  2. POST /companies/enrich/batch
  3. Verify response has: batch_id, total_requested=3, results array
  4. Count items in results array
  5. Verify count matches total_requested
Expected: All companies in batch processed
Evidence: .sisyphus/evidence/task-3-enrich-batch.txt
```

**Scenario 3: GET /health returns correct status**
```
Steps:
  1. GET /health
  2. Verify response status 200 (healthy)
  3. Verify response.status === "healthy"
  4. Verify response has timestamp field
Expected: Health check works correctly
Evidence: .sisyphus/evidence/task-3-health-check.txt
```

**Scenario 4: GET /ready shows readiness state**
```
Steps:
  1. GET /ready
  2. Verify response either 200 (ready=true) or 503 (ready=false)
  3. Verify response has checks field (dict of component statuses)
  4. Verify each check is boolean
Expected: Readiness correctly reflects system state
Evidence: .sisyphus/evidence/task-3-ready-check.txt
```

**Scenario 5: GET /metrics shows cache hit rate**
```
Steps:
  1. GET /metrics
  2. Verify response has cache.hits, cache.misses
  3. Verify cache.hit_rate = hits/(hits+misses)
  4. Verify hit_rate between 0 and 1
Expected: Metrics accurately calculated
Evidence: .sisyphus/evidence/task-3-metrics.txt
```

### Agent Profile Recommendation
- **Category**: `unspecified-high`
- **Skills**: None required
- **Why**: Must carefully handle 2 routers (/health from health.py, /health from enrichment.py), clearly document which is which

---

## TASK 4: Document Async Job & Drill-Down Endpoints (14 endpoints)

### Endpoints to Document

**Async Jobs** (4 endpoints):
```
1.  POST    /async/enrich/single
2.  POST    /async/enrich/batch
3.  GET     /async/jobs/{job_id}/status
4.  GET     /async/jobs/{job_id}/result
```

**Drill-Down** (10 endpoints):
```
9.  GET     /drill-down/company/{company_id}/audit-trail
10. GET     /drill-down/company/{company_id}/contradictions
11. GET     /drill-down/company/{company_id}/data-quality
12. GET     /drill-down/company/{company_id}/fact/{fact_type}
13. GET     /drill-down/company/{company_id}/facts
14. GET     /drill-down/company/{company_id}/signals
15. GET     /drill-down/company/{company_id}/source/{source_id}
16. GET     /drill-down/company/{company_id}/sources
17. GET     /drill-down/company/{company_id}/timeline
18. GET     /drill-down/company/{company_id}/why/{signal_name}
```

### Code References

**Async Jobs Router**: `src/solstein/api/routers/async_jobs.py`
- Lines 1-50: Module docstring and imports
- Line 16: `router = APIRouter(prefix="/async", tags=["async-jobs"])`
- Lines 34-47: Request/response models (AsyncEnrichmentRequest, JobStatusResponse)
- Contains Celery integration with graceful fallback to 503 if not available

**Drill-Down Router**: `src/solstein/api/routers/drill_down.py`
- Contains 10 GET endpoints for company deep-dive analysis
- All require company_id path parameter
- Some require signal_name, source_id, fact_type parameters

### Example Curl Commands

**POST /async/enrich/single** (start async job)
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

# Response:
# {
#   "job_id": "enrich-12345",
#   "status": "submitted",
#   "created_at": "..."
# }
```

**GET /async/jobs/{job_id}/status** (poll for status)
```bash
curl -X GET "http://localhost:8000/async/jobs/enrich-12345/status" \
  -H "Authorization: Bearer {token}"

# Response (poll every 1-5 seconds):
# {
#   "job_id": "enrich-12345",
#   "status": "pending" | "running" | "completed" | "failed",
#   "progress_percent": 45,
#   "error_message": null
# }
```

**GET /async/jobs/{job_id}/result** (get result when done)
```bash
curl -X GET "http://localhost:8000/async/jobs/enrich-12345/result" \
  -H "Authorization: Bearer {token}"

# Response when status=completed:
# {
#   "job_id": "enrich-12345",
#   "enrichment_data": {...},
#   "completed_at": "..."
# }
```

**GET /drill-down/company/{company_id}/sources**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/sources" \
  -H "Authorization: Bearer {token}"

# Response:
# {
#   "company_id": "tech-corp-001",
#   "sources": [
#     {"source_id": "github-001", "type": "github", "last_updated": "..."},
#     {"source_id": "sec-001", "type": "sec", "last_updated": "..."}
#   ]
# }
```

**GET /drill-down/company/{company_id}/why/{signal_name}**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/why/growth_score" \
  -H "Authorization: Bearer {token}"

# Response explains what factors contributed to this signal
```

**GET /drill-down/company/{company_id}/contradictions**
```bash
curl -X GET "http://localhost:8000/drill-down/company/tech-corp-001/contradictions" \
  -H "Authorization: Bearer {token}"

# Returns conflicting data points from different sources
```

### QA Scenarios

**Scenario 1: POST /async/enrich/single returns job_id**
```
Steps:
  1. POST /async/enrich/single with valid company_id
  2. Verify response status 202 (Accepted)
  3. Extract job_id from response
  4. Verify job_id is non-empty string
Expected: Job submitted, job_id returned
Evidence: .sisyphus/evidence/task-4-async-submit.txt
```

**Scenario 2: GET /async/jobs/{job_id}/status shows progress**
```
Steps:
  1. Submit async job (from Scenario 1)
  2. Immediately GET /async/jobs/{job_id}/status
  3. Verify status is one of: pending, running, completed, failed
  4. Wait 2-3 seconds
  5. GET again
  6. Verify status progressed or remained same (not backwards)
Expected: Status endpoint works, shows progress
Evidence: .sisyphus/evidence/task-4-async-status.txt
```

**Scenario 3: GET /drill-down/company/{id}/sources lists all sources**
```
Steps:
  1. GET /drill-down/company/{id}/sources
  2. Verify response has sources array
  3. Verify each source has: source_id, type, last_updated
  4. Count sources (should be > 0 for populated company)
Expected: All sources listed with metadata
Evidence: .sisyphus/evidence/task-4-sources.txt
```

**Scenario 4: GET .../why/{signal_name} explains signal**
```
Steps:
  1. GET /drill-down/company/{id}/why/growth_score
  2. Verify response explains what factors affect this signal
  3. Verify response includes contributing data points
Expected: Signal explanation provided
Evidence: .sisyphus/evidence/task-4-signal-why.txt
```

### Agent Profile Recommendation
- **Category**: `unspecified-high`
- **Skills**: None required
- **Why**: Must handle async job polling patterns, explain drill-down analysis endpoints clearly

---

## TASK 5: Document Health & Export Endpoints (7 endpoints)

### Endpoints to Document

**Health** (4 endpoints from health.py):
```
31. GET     /health (base path via prefix)
32. GET     /health/live
33. GET     /health/ready
34. GET     /metrics/data-quality
```

**Export** (3 endpoints):
```
28. GET     /export/excel
29. GET     /export/json
30. GET     /export/search/llm
```

**Simulation** (1 endpoint):
```
42. POST    /simulation/run
```

### Code References

**Health Router**: `src/solstein/api/routers/health.py`
- Lines 18-82: Main health router with /health prefix
- Line 21: `GET /` (health check, becomes /health due to prefix)
- Line 42: `GET /status` (becomes /health/status)
- Line 50: `GET /ready` (becomes /health/ready, DUPLICATE with enrichment.py)
- Line 73: `GET /live` (becomes /health/live)
- Line 85: `metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])`
- Line 88: `GET /` on metrics_router (becomes /metrics, also in enrichment.py)
- Line 113: `GET /data-quality` on metrics_router (becomes /metrics/data-quality)

**Export Router**: `src/solstein/api/routers/export.py`
- Line 14: `router = APIRouter(tags=["Export"])` (registered with prefix="/export")
- Line 42: `GET /excel` — Starts background Excel generation
- Line 77: `GET /json` — Synchronous JSON export
- Line 127: `GET /search/llm` — LLM-powered natural language search

**Simulation Router**: `src/solstein/api/routers/simulation.py`
- Line XX: `router = APIRouter(prefix="/simulation", tags=["Simulation"])`
- POST /run endpoint for market simulations

### Response Details

**Export /excel Response**:
```python
{
  "message": "Export started",
  "filename": "solstein_dashboard_20260226_103000.xlsx",
  "status": "processing"
}
```

**Export /json Response**:
```python
{
  "exported_at": "2026-02-26T10:30:00",
  "total_companies": 150,
  "companies": [
    # Array of Company objects in JSON format
  ]
}
```

**Health /ready Response** (status 200 if ready, 503 if not):
```python
{
  "ready": true,
  "timestamp": "2026-02-26T10:30:00"
}
```

**Health /live Response** (always 200):
```python
{
  "alive": true,
  "timestamp": "2026-02-26T10:30:00"
}
```

### Example Curl Commands

**GET /health (base health)**
```bash
curl -X GET "http://localhost:8000/health"

# Returns:
# {
#   "status": "healthy",
#   "timestamp": "..."
# }
```

**GET /health/live (liveness probe)**
```bash
curl -X GET "http://localhost:8000/health/live"

# Always returns 200 if process running
```

**GET /health/ready (readiness probe)**
```bash
curl -X GET "http://localhost:8000/health/ready"

# Returns 200 if ready, 503 if not
# Can use in Kubernetes readinessProbe
```

**GET /health/status (full status)**
```bash
curl -X GET "http://localhost:8000/health/status"

# Returns detailed status of all components
```

**GET /metrics/data-quality**
```bash
curl -X GET "http://localhost:8000/metrics/data-quality"

# Returns data quality metrics:
# {
#   "completeness_percent": 94.5,
#   "validation_errors": 12,
#   "stale_records": 5
# }
```

**GET /export/excel** (starts background job)
```bash
curl -X GET "http://localhost:8000/export/excel?industry=SaaS&include_charts=true" \
  -H "Authorization: Bearer {token}"

# Response:
# {
#   "message": "Export started",
#   "filename": "solstein_saas_20260226_103000.xlsx",
#   "status": "processing"
# }
```

**GET /export/json** (synchronous)
```bash
curl -X GET "http://localhost:8000/export/json?industry=SaaS" \
  -H "Authorization: Bearer {token}" \
  > export.json

# Response is JSON array of companies
```

**GET /export/search/llm** (LLM-powered search)
```bash
curl -X GET "http://localhost:8000/export/search/llm?criteria=fast%20growing%20saas%20with%20large%20team&limit=10" \
  -H "Authorization: Bearer {token}"

# Returns:
# {
#   "criteria": "fast growing saas with large team",
#   "total_matched": 7,
#   "companies": [...],
#   "filter_reasoning": "Found companies with..."
# }
```

**POST /simulation/run**
```bash
curl -X POST "http://localhost:8000/simulation/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "scenario": "market_downturn",
    "severity": 0.8,
    "months": 12
  }'

# Returns simulation results showing impact on all companies
```

### QA Scenarios

**Scenario 1: GET /health/ready distinguishes from enrichment.py /ready**
```
Steps:
  1. Document notes that /ready exists in TWO routers:
     - health.py: registered as /health/ready
     - enrichment.py: registered as /ready (no prefix)
  2. GET /health/ready — Should get health.py version
  3. GET /ready — Should get enrichment.py version
  4. Both should return similar status (ready: bool)
  5. Document which is "canonical" (router registration order)
Expected: Clear documentation of dual implementation
Evidence: .sisyphus/evidence/task-5-ready-routing.txt
```

**Scenario 2: GET /export/excel starts background job**
```
Steps:
  1. GET /export/excel?industry=SaaS
  2. Verify response status 200
  3. Verify response.status === "processing"
  4. Extract filename
  5. Verify filename matches pattern: solstein_*.xlsx
Expected: Export job queued, filename provided
Evidence: .sisyphus/evidence/task-5-excel-export.txt
```

**Scenario 3: GET /export/json returns all companies synchronously**
```
Steps:
  1. GET /export/json
  2. Verify response is array of Company objects
  3. Verify each company has required fields
  4. Compare count to GET /companies count
  5. Verify response includes exported_at timestamp
Expected: All companies exported in JSON
Evidence: .sisyphus/evidence/task-5-json-export.txt
```

**Scenario 4: GET /export/search/llm filters by natural language**
```
Steps:
  1. GET /export/search/llm?criteria=saas+companies&limit=5
  2. Verify response.total_matched >= 0
  3. Verify count(response.companies) <= 5
  4. Verify response.filter_reasoning is non-empty string
Expected: LLM search returns reasoning and filtered results
Evidence: .sisyphus/evidence/task-5-llm-search.txt
```

**Scenario 5: GET /metrics/data-quality shows quality metrics**
```
Steps:
  1. GET /metrics/data-quality
  2. Verify response has: completeness_percent, validation_errors, stale_records
  3. Verify completeness_percent is 0-100
  4. Verify counts are non-negative integers
Expected: Data quality metrics returned
Evidence: .sisyphus/evidence/task-5-data-quality.txt
```

### Agent Profile Recommendation
- **Category**: `unspecified-high`
- **Skills**: None required
- **Why**: Must carefully distinguish between /ready implementations, document export async vs sync pattern clearly, explain LLM search endpoint

---

## Wave 2 Execution Summary

### Tasks at a Glance
| Task | Endpoints | Est. Time | Dependency |
|------|-----------|-----------|-----------|
| **Task 2** | Companies, Scoring, Market (10) | 20-25 min | Task 1 ✅ |
| **Task 3** | Enrichment (9) | 20-25 min | Task 1 ✅ |
| **Task 4** | Async Jobs, Drill-Down (14) | 20-25 min | Task 1 ✅ |
| **Task 5** | Health, Export, Simulation (8) | 15-20 min | Task 1 ✅ |

### Execution Strategy
- **Wave 2 Parallelization**: ALL 4 tasks run in parallel (no interdependencies)
- **Total Wall-Clock Time**: ~25 minutes (longest single task)
- **Total Effort**: 75-95 minutes across team
- **Blocked Downstream**: Tasks 6-7 (navigation + routing docs), Tasks 8-10 (verification)

### Quality Gates
- Each task must include at least 2 QA scenarios
- All curl examples must be verified against actual code
- Response models must match code exactly
- All acceptance criteria must be met before commit

---

## Agent Dispatch Summary

**Recommended Agent Configuration**:
```
Category: unspecified-high
Skills: None required (but having code-quality/writing-skills helpful)
Model: claude-haiku-4-5 (fast, sufficient for documentation writing)
```

**Each agent should**:
1. Read this document (wave2-detailed-task-specs.md)
2. Read their assigned task section above
3. Read actual code files for verification
4. Write documentation to docs/api/reference.md
5. Execute QA scenarios in Evidence section
6. Create evidence file with scenario results
7. Commit with provided message template

---

## Ready for Execution ✅

**Current Status**:
- ✅ Task 1 COMPLETE: Endpoint inventory ready
- ✅ Wave 2 specifications enhanced with exact code details
- ✅ All curl examples provided and ready to test
- ✅ QA scenarios have concrete, testable steps
- ✅ Agent dispatch recommendations clear

**Next Action**: Execute Tasks 2-5 in parallel using `/start-work` command.
