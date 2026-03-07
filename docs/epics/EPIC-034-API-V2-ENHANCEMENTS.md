# EPIC-034: API v2 Enhancements

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 6

---

## Problem Statement

Current API limitations:
- No bulk operations (import/export)
- No webhooks for async events
- No GraphQL API for flexible queries
- Limited pagination
- No API versioning strategy
- No client SDKs

### Impact
- Clients make many individual API calls
- No real-time notifications
- Mobile apps inefficient
- Hard to maintain backward compatibility

---

## Success Criteria

1. ✅ Bulk import (10,000 companies)
2. ✅ Bulk export (all formats)
3. ✅ Webhook system operational
4. ✅ GraphQL API available
5. ✅ Cursor-based pagination
6. ✅ Versioned API (v1, v2)
7. ✅ Python SDK published

---

## Stories

### Story 4.1: Bulk Import API (13 pts)
**Task:** Import thousands of companies in one call

**Acceptance Criteria:**
- [ ] POST /api/v2/companies/bulk accepts 10,000 companies
- [ ] Async processing with job tracking
- [ ] Validation errors collected per row
- [ ] Progress reporting
- [ ] Completion webhook

**Implementation:**
```python
@app.post("/api/v2/companies/bulk")
async def bulk_import(
    companies: list[CompanyImport],
    background_tasks: BackgroundTasks
) -> JobResponse:
    job_id = await create_import_job(companies)
    background_tasks.add_task(process_bulk_import, job_id)
    return JobResponse(id=job_id, status="pending")
```

---

### Story 4.2: Bulk Export API (8 pts)
**Task:** Export all data in one operation

**Acceptance Criteria:**
- [ ] POST /api/v2/export/bulk with filters
- [ ] All formats supported (Excel, CSV, PDF, JSON)
- [ ] Streaming for large datasets
- [ ] S3 upload for large exports
- [ ] Download link with expiry

**Implementation:**
```python
@app.post("/api/v2/export/bulk")
async def bulk_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks
) -> ExportJobResponse:
    job_id = await create_export_job(request)
    background_tasks.add_task(process_export, job_id)
    return ExportJobResponse(id=job_id, status="pending")
```

---

### Story 4.3: Webhook System (13 pts)
**Task:** Real-time notifications for events

**Acceptance Criteria:**
- [ ] Webhook subscription management
- [ ] Event types: company.updated, enrichment.completed, score.changed
- [ ] Retry logic with exponential backoff
- [ ] Webhook signature verification
- [ ] Delivery logs

**Implementation:**
```python
# Webhook payload
{
    "event": "company.updated",
    "timestamp": "2024-01-15T10:30:00Z",
    "data": {
        "company_id": "comp-123",
        "changed_fields": ["revenue", "employee_count"],
        "previous_score": 6.5,
        "new_score": 7.2
    },
    "signature": "sha256=abc123..."
}
```

---

### Story 4.4: GraphQL API (13 pts)
**Task:** Flexible query API

**Acceptance Criteria:**
- [ ] GraphQL endpoint at /graphql
- [ ] Query companies with filters
- [ ] Nested resolvers for related data
- [ ] Mutation support
- [ ] Playground UI

**Implementation:**
```graphql
type Query {
    companies(
        filter: CompanyFilter,
        first: Int,
        after: String
    ): CompanyConnection
    
    company(id: ID!): Company
}

type Company {
    id: ID!
    name: String!
    revenue: Float
    classification: Classification
    scores: Scores
    competitors: [Company]
}
```

---

### Story 4.5: Cursor-Based Pagination (5 pts)
**Task:** Efficient pagination for large datasets

**Acceptance Criteria:**
- [ ] Cursor-based pagination on all list endpoints
- [ ] Consistent ordering
- [ ] No duplicate/missed items
- [ ] Previous/next navigation

**Implementation:**
```python
@app.get("/api/v2/companies")
async def list_companies(
    first: int = 20,
    after: Optional[str] = None
) -> PaginatedResponse:
    # Decode cursor
    cursor = decode_cursor(after) if after else None
    
    # Query with cursor
    companies = await get_companies(
        limit=first + 1,
        cursor=cursor
    )
    
    # Build response with next cursor
    has_more = len(companies) > first
    return PaginatedResponse(
        items=companies[:first],
        next_cursor=encode_cursor(companies[-1].id) if has_more else None
    )
```

---

### Story 4.6: API Versioning (3 pts)
**Task:** Versioned API strategy

**Acceptance Criteria:**
- [ ] URL versioning (/api/v1/, /api/v2/)
- [ ] Deprecation headers
- [ ] Migration guide
- [ ] Backward compatibility maintained

---

## Definition of Done

- [ ] Bulk import handles 10k companies
- [ ] Bulk export streams large datasets
- [ ] Webhooks deliver events reliably
- [ ] GraphQL API operational
- [ ] Cursor pagination on all lists
- [ ] API v2 documented
- [ ] Load testing passed (1000 req/s)

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking changes in v2 | Medium | High | Deprecation period, versioning |
| GraphQL performance | Medium | High | Query complexity limits |
| Webhook delivery failures | High | Medium | Retry logic, dead letter queue |

---

## Resources

- **Developers:** 3 backend engineers
- **Time:** 4 weeks
- **Dependencies:** EPIC-031, EPIC-032

---

*Epic created as part of Comprehensive Analysis*
