# STORY-034: Fix N+1 Query Patterns in Data Loading

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-009: Data Layer Consolidation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `data/loaders.py` loads all companies from the database into Python memory and applies filter criteria in application code. `api/routers/export.py` loads the entire dataset with no limit or pagination before applying any filter. At scale, this is a memory and performance catastrophe.

## Problem Statement

Loading entire database tables into Python memory to filter them is an anti-pattern that makes query time and memory usage proportional to the total dataset size, regardless of how many results are needed. A request for 10 companies that match a filter currently loads all 10,000 companies into memory, applies a Python filter, and returns 10 results.

This pattern has predictable scaling characteristics — all of them bad:
- Memory: proportional to total dataset size, not result size
- CPU: Python list filtering is orders of magnitude slower than SQL WHERE clauses
- I/O: entire table transferred from database to application on every request
- Latency: query time grows linearly with dataset size

The export endpoint is particularly egregious: it loads the entire dataset with no pagination, meaning a single request can allocate hundreds of megabytes of memory for a response the client may not even need in full.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Performance** | Query time scales with total record count, not result count |
| **Memory** | Entire dataset loaded into application memory on every request |
| **Scalability** | The system will degrade predictably as data volumes grow — this is not a "maybe" problem |
| **Availability** | A large dataset + concurrent requests = OOM conditions |
| **Cost** | Database-to-application data transfer bandwidth wasted on discarded rows |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/loaders.py` | Modify | Push filter criteria to database WHERE clauses |
| `src/solstein/api/routers/export.py` | Modify | Add pagination, push filters to database |
| `src/solstein/api/routers/companies.py` | Evaluate | Check for similar patterns |
| `src/solstein/infrastructure/company_repository.py` | Modify | Add filtered query methods with SQL-level predicates |
| Any endpoint that returns list responses | Evaluate | Check for load-all-then-filter patterns |

## Architectural Requirements

- **REQ-1**: All filtering must be expressed as database predicates (WHERE clauses), not Python list comprehensions on loaded data
- **REQ-2**: All bulk data endpoints must support pagination with configurable page size and offset
- **REQ-3**: No endpoint may return more than a configurable maximum number of records in a single response (e.g., 1,000) — this limit must be enforced server-side regardless of client request
- **REQ-4**: Query plans for the most frequently executed queries must be validated — `EXPLAIN` should show index usage, not sequential scans

## Acceptance Criteria

- [ ] A request for 10 companies executes a SQL query that returns exactly 10 rows — not all rows filtered in Python
- [ ] The export endpoint requires pagination parameters (`page`, `page_size`)
- [ ] Requesting `page_size=10000` returns the configured maximum (e.g., 1,000), not 10,000 records
- [ ] `EXPLAIN` on primary loader queries shows index scans, not sequential scans
- [ ] No Python-side filtering of full datasets exists — `grep -rn "for.*in.*all_companies" . --include="*.py"` returns zero results (or equivalent patterns)

## Definition of Done

**Tests Required:**
- [ ] Performance test: 10-record query time is not proportional to total record count (measure with 100 and 10,000 records)
- [ ] Integration test: paginated export returns correct page with correct page metadata
- [ ] Test: exceeding maximum page size returns the maximum, not the requested size
- [ ] Test: filter criteria are in the SQL query, not applied in Python (inspect query log or mock)

**Documentation Required:**
- [ ] API documentation updated to include pagination parameters on all bulk endpoints
- [ ] Maximum page size documented in application configuration

**Code Review Gate:**
- [ ] Reviewer confirms no load-all-then-filter patterns remain
- [ ] Reviewer confirms all bulk endpoints support pagination
- [ ] Reviewer confirms maximum page size is enforced server-side

## Notes

This story should be completed before STORY-035 (missing indexes) because the queries pushed to the database by this story are the queries that need indexes. The sequence is: push filtering to SQL, then ensure the SQL queries have proper index support.

The load-all-then-filter pattern may exist in more places than the two identified in the audit. A codebase-wide search for patterns like `session.query(Company).all()` followed by list comprehensions will identify additional occurrences.
