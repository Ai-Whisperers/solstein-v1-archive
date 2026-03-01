# STORY-030: Decompose the Enrichment Router God File

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-008: God File Decomposition](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-027](../../EPIC-007-ddd-migration/STORIES/STORY-027-extract-domain-services.md) (domain service extraction must happen first) |

---

## The Audit Verdict

> `api/routers/enrichment.py` is 793 lines. It handles enrichment initiation, status polling, result retrieval, data validation, statistical aggregation, and business rule evaluation — all as a single router file. Router handlers contain business logic that should live in domain services.

## Problem Statement

A 793-line router file contains far too many responsibilities. After STORY-027 extracts business logic into domain services, the router will be significantly smaller — but it will still need decomposition into logically grouped sub-routers. A single enrichment router should not handle every enrichment-related endpoint in one file.

FastAPI routers should contain:
1. Request parsing (path/query params, request body validation)
2. Service method invocation
3. Response construction

If a router handler does anything beyond these three operations, it has too many responsibilities. After STORY-027, the remaining code should be thin HTTP handlers — but 793 lines of thin handlers still means too many endpoints in one file.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Too many endpoints in one file, even after service extraction |
| **Code Review** | Router diffs are hard to review when the file handles many endpoint groups |
| **Navigation** | Finding the right endpoint handler in a long router file wastes time |
| **Merge Conflicts** | Multiple developers adding or modifying enrichment endpoints will conflict |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/enrichment.py` | Split | After service extraction, split into focused sub-routers |
| New: `src/solstein/api/routers/enrichment_initiation.py` | Add | Endpoints for starting enrichment jobs |
| New: `src/solstein/api/routers/enrichment_status.py` | Add | Endpoints for polling enrichment status |
| New: `src/solstein/api/routers/enrichment_results.py` | Add | Endpoints for retrieving enrichment results |
| `src/solstein/api/main.py` | Modify | Register new sub-routers with appropriate prefixes |

## Architectural Requirements

- **REQ-1**: After service extraction (STORY-027), the router must be split into logically grouped sub-routers — each sub-router handles one operation group
- **REQ-2**: Each sub-router file must focus on one resource or operation group (initiation, status, results)
- **REQ-3**: No router file may exceed 200 lines — routers are HTTP handlers, not application logic
- **REQ-4**: All endpoints must maintain their existing URL paths and response contracts — this is an internal reorganisation, not an API change

## Acceptance Criteria

- [ ] `enrichment.py` does not exist as a single 793-line file
- [ ] Each resulting router file is under 200 lines
- [ ] All endpoint URLs are unchanged — `GET /enrichment/{id}/status` still works from the same URL
- [ ] All response schemas are unchanged — clients see no difference
- [ ] Each sub-router file handles one logical group of endpoints

## Definition of Done

**Tests Required:**
- [ ] Integration tests confirming all enrichment endpoints remain accessible at their original URLs
- [ ] Integration tests confirming response schemas are unchanged
- [ ] Test: each sub-router can be imported and registered independently

**Documentation Required:**
- [ ] Comment at the top of each sub-router documenting which endpoint group it handles
- [ ] Updated router registration in `main.py` with comments explaining the grouping

**Code Review Gate:**
- [ ] Reviewer confirms all endpoint URLs are unchanged
- [ ] Reviewer confirms no router file exceeds 200 lines
- [ ] Reviewer confirms router handlers contain only request parsing, service invocation, and response construction

## Notes

This story MUST NOT start until STORY-027 (domain service extraction) is complete. The sequence is:
1. Extract business logic from router handlers into services (STORY-027)
2. Decompose the now-thinner router into sub-routers (this story)

If you attempt to decompose the router before extracting services, you will be splitting 793 lines of mixed HTTP and business logic into multiple files of mixed HTTP and business logic — which solves nothing.

The suggested sub-router names (initiation, status, results) are starting points. Read the endpoints in `enrichment.py` after service extraction and let the endpoint groups dictate the module boundaries.
