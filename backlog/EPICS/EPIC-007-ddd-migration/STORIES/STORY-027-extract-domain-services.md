# STORY-027: Extract Domain Services from Router Handlers

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-007: Domain-Driven Design Migration](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-024](STORY-024-migrate-company-rich-domain.md), [STORY-025](STORY-025-abstract-repository-interfaces.md) |

---

## The Audit Verdict

> Scoring logic, classification thresholds, statistical calculations, and business rule enforcement live in `api/routers/enrichment.py` (793 lines), `api/routers/scoring.py`, and other router files. Router handlers are mixing HTTP concerns with domain logic.

## Problem Statement

Business logic in router handlers cannot be unit-tested without an HTTP context. It cannot be reused by CLI commands, background tasks, or other entrypoints. It couples domain behaviour to HTTP transport.

The enrichment router alone is 793 lines because it handles enrichment initiation, status polling, result retrieval, data validation, statistical aggregation, and business rule evaluation — all within FastAPI route handler functions. These handlers are not thin wrappers around service methods; they are the service methods, entangled with HTTP request parsing and response formatting.

This means:
- A CLI tool that needs to trigger enrichment must either import a router handler (wrong) or duplicate the logic (worse)
- Celery background tasks that need scoring logic face the same choice
- Testing business rules requires standing up a FastAPI test client
- Changing the HTTP API (e.g., adding a new query parameter) risks breaking business logic

## Impact

| Dimension | Effect |
|-----------|--------|
| **Testability** | Domain logic requires HTTP context (FastAPI TestClient) to test |
| **Reusability** | CLI and Celery tasks cannot reuse router-embedded logic without importing HTTP code |
| **Maintainability** | Logic changes require understanding of FastAPI dependency injection |
| **Separation of Concerns** | HTTP transport and domain logic are indistinguishable |
| **Code Review** | 793-line router files make review impractical |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/enrichment.py` | Modify | Extract business logic to services — retain only HTTP handling |
| `src/solstein/api/routers/scoring.py` | Modify | Extract scoring calculations to services |
| `src/solstein/application/services/enrichment_service.py` | Add/Modify | Receive extracted enrichment business logic |
| `src/solstein/application/services/scoring_service.py` | Add/Modify | Receive extracted scoring business logic |
| `src/solstein/application/services/statistics_service.py` | Add/Modify | Receive extracted statistical calculations |

## Architectural Requirements

- **REQ-1**: Business logic must be extracted from router handlers into dedicated application or domain service classes
- **REQ-2**: Routers must contain only three operations per handler: request parsing → service method invocation → response construction
- **REQ-3**: Service classes must be independently testable without a FastAPI application context — calling a service method requires only the service instance and its dependencies (repositories, configuration)
- **REQ-4**: Existing functionality must be preserved — this is extraction, not rewriting; the same inputs must produce the same outputs

## Acceptance Criteria

- [ ] Router handlers contain no scoring calculations, threshold comparisons, or statistical aggregations
- [ ] Router handlers contain no classification logic
- [ ] Service methods can be called from a Python test without importing FastAPI
- [ ] Each service method has a clear, documented interface (typed parameters and return value)
- [ ] Router handlers average under 20 lines each (request → service → response)
- [ ] All existing API endpoint tests continue to pass with the same inputs and outputs

## Definition of Done

**Tests Required:**
- [ ] Unit tests for each extracted service method — called directly, not through HTTP
- [ ] Integration test confirming each router endpoint still returns correct responses after extraction
- [ ] Test: service methods work with mock repositories (from STORY-025) — no database required

**Documentation Required:**
- [ ] Docstrings on each service method documenting parameters, return types, and business rules
- [ ] Comment in each router file noting its role: "HTTP handling only — business logic in services"

**Code Review Gate:**
- [ ] Reviewer confirms zero business logic in router handlers
- [ ] Reviewer confirms service methods are independently testable
- [ ] Reviewer confirms all existing API tests pass unchanged

## Notes

This story is the bridge between the DDD migration (EPIC-007) and the god file decomposition (EPIC-008, STORY-030). Once business logic is extracted from `enrichment.py`, the remaining HTTP handling code will be much smaller and the router decomposition in STORY-030 becomes straightforward.

The dependency on STORY-024 (rich domain model) ensures that the extracted services use entity methods rather than reimplementing business logic. The dependency on STORY-025 (repository interfaces) ensures that the extracted services depend on Protocols, not concrete repository classes.
