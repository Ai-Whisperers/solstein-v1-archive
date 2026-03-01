# STORY-037: Add Pagination to All Bulk Endpoints

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-010: API Layer Hardening](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-034](../../EPIC-009-data-layer-consolidation/STORIES/STORY-034-fix-n-plus-one-queries.md) (database-level filtering must exist first) |

---

## The Audit Verdict

> The export endpoint, statistics endpoint, and batch enrichment endpoint load entire datasets with no result limit. There is no pagination parameter. A single authenticated request can exhaust server memory.

## Problem Statement

Bulk endpoints with no pagination or result limits are a reliability hazard and a potential denial-of-service vector for authenticated users. A single request to the export endpoint can trigger the server to load millions of rows into memory, serialise them into a response, and attempt to transmit the entire result — potentially exhausting memory, blocking the event loop, and degrading service for all other users.

This is not a hypothetical scenario. As the dataset grows — which it will, because the platform is designed to accumulate company data over time — the memory required to serve a single unlimited request grows with it. The trajectory is predictable and the outcome is inevitable.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Large datasets can cause memory exhaustion on unlimited bulk requests |
| **Performance** | Full dataset loads block the server thread for extended periods |
| **DoS Surface** | Authenticated users can trigger expensive server-side operations with a single request |
| **Client UX** | Clients waiting for multi-megabyte responses experience long delays and timeouts |
| **Cost** | Unnecessary bandwidth and compute for data the client may not need |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/export.py` | Modify | Add pagination parameters, enforce maximum page size |
| `src/solstein/api/routers/companies.py` | Modify | Add pagination parameters |
| `src/solstein/api/routers/enrichment.py` | Evaluate | Check batch enrichment endpoints for pagination |
| `src/solstein/api/schemas/pagination.py` | Add | Reusable pagination request/response schemas |
| `src/solstein/infrastructure/company_repository.py` | Modify | Add paginated query methods |

## Architectural Requirements

- **REQ-1**: All endpoints returning multiple records must support `page` and `page_size` query parameters
- **REQ-2**: A configurable maximum `page_size` must be enforced server-side — if a client requests `page_size=50000`, the server returns at most the configured maximum (e.g., 1,000 records)
- **REQ-3**: Responses must include pagination metadata: `total_count`, `page`, `page_size`, `total_pages`, `has_next`, `has_previous`
- **REQ-4**: The default page size must be a reasonable number (e.g., 50) — not unlimited; endpoints called without pagination parameters must still return paginated results

## Acceptance Criteria

- [ ] `GET /companies?page=1&page_size=10` returns exactly 10 companies (or fewer if fewer exist)
- [ ] Response body includes pagination metadata: `total_count`, `page`, `page_size`, `total_pages`, `has_next`, `has_previous`
- [ ] Requesting `page_size=10000` returns the configured maximum page size, not 10,000 records
- [ ] Requesting without pagination parameters returns the default page size (e.g., 50), not all records
- [ ] `GET /export?page=1&page_size=100` returns a paginated export, not the entire dataset
- [ ] The pagination schema is reusable across all bulk endpoints

## Definition of Done

**Tests Required:**
- [ ] Unit test: pagination parameters enforce the maximum page size
- [ ] Unit test: default page size is applied when no pagination parameters are provided
- [ ] Integration test: pagination metadata is correct across page boundaries (page 1 has `has_next=true`, last page has `has_next=false`)
- [ ] Integration test: requesting page beyond total pages returns empty results with correct metadata
- [ ] Test: total_count reflects the total filtered result count, not the page count

**Documentation Required:**
- [ ] API documentation updated to include pagination parameters on all bulk endpoints
- [ ] OpenAPI schema includes pagination metadata in response models
- [ ] Configuration documentation for maximum page size and default page size

**Code Review Gate:**
- [ ] Reviewer confirms all bulk endpoints support pagination
- [ ] Reviewer confirms maximum page size is enforced server-side
- [ ] Reviewer confirms pagination metadata is correct and consistent across endpoints

## Notes

This story depends on STORY-034 (N+1 query fix) because pagination is only meaningful if the database query itself is paginated. Adding `page` and `page_size` parameters to an endpoint that loads all records into memory and then slices the result list provides no memory benefit — the entire dataset is still loaded.

The pagination schema should be a reusable Pydantic model (e.g., `PaginatedResponse[T]`) that wraps any list response with pagination metadata. This avoids duplicating pagination logic across endpoints.
