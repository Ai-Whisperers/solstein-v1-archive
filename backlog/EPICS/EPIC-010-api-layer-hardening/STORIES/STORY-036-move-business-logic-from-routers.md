# STORY-036: Move Business Logic Out of Router Handlers

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-010: API Layer Hardening](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-027](../../EPIC-007-ddd-migration/STORIES/STORY-027-extract-domain-services.md) (domain services must exist first) |

---

## The Audit Verdict

> Router handlers in `api/routers/enrichment.py` (793 lines), `api/routers/scoring.py`, and others contain scoring calculations, classification threshold comparisons, statistical aggregations, and business rule evaluations that have no business being in HTTP handlers.

## Problem Statement

Business logic in HTTP handlers is untestable without a full HTTP stack, unreusable by CLI or background tasks, and conflates transport concerns with domain concerns.

This story is the API-layer counterpart to STORY-027 (domain service extraction). While STORY-027 focuses on creating the domain services that receive the extracted logic, this story focuses on ensuring the routers are clean after extraction — that no business logic remains embedded in HTTP handlers.

The distinction matters: STORY-027 creates the services. This story ensures the routers are thin. Both must be done. Neither is sufficient alone.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Testability** | Domain logic in router handlers requires HTTP context (FastAPI TestClient) to test |
| **Reusability** | CLI and Celery tasks cannot access router-embedded business logic without importing FastAPI |
| **Code Size** | Router files are 2-4x larger than they should be because they contain business logic |
| **Separation of Concerns** | HTTP transport and domain logic are indistinguishable in the same function |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/enrichment.py` | Modify | Remove all business logic — retain only HTTP handling |
| `src/solstein/api/routers/scoring.py` | Modify | Remove all scoring calculations — delegate to service |
| `src/solstein/api/routers/companies.py` | Evaluate | Check for embedded business logic |
| `src/solstein/api/routers/export.py` | Evaluate | Check for embedded business logic |
| `src/solstein/application/services/` | Modify | Services must exist (from STORY-027) before this story can verify router cleanliness |

## Architectural Requirements

- **REQ-1**: Router handlers must contain exactly three operations: deserialise request → call service method → serialise response
- **REQ-2**: No business calculation, threshold comparison, statistical aggregation, or domain rule evaluation may appear in a router handler
- **REQ-3**: Service methods must be callable from a Python test without importing FastAPI — this is the litmus test for proper extraction

## Acceptance Criteria

- [ ] Router handlers average under 20 lines each
- [ ] No arithmetic or conditional business logic in router handlers — only request parsing, service calls, and response construction
- [ ] Service methods have unit tests independent of HTTP context
- [ ] No router handler imports domain models directly for business logic purposes (imports for type hints are acceptable)
- [ ] `grep -rn "score.*threshold\|classify\|calculate" src/solstein/api/routers/ --include="*.py"` returns zero results (adjusted for actual business logic patterns)

## Definition of Done

**Tests Required:**
- [ ] Unit tests for each service method — called directly from Python, not through HTTP
- [ ] Integration test confirming each router endpoint returns the same responses as before the extraction
- [ ] Test: service methods work with mock dependencies — no database, no external APIs

**Documentation Required:**
- [ ] Comment at the top of each router file: `# HTTP handling only — business logic in application/services/`
- [ ] Docstrings on each router handler documenting which service method it delegates to

**Code Review Gate:**
- [ ] Reviewer confirms zero business logic in router handlers
- [ ] Reviewer confirms router handlers follow the three-step pattern (parse → call → respond)
- [ ] Reviewer confirms all API tests pass unchanged

## Notes

This story is a verification and cleanup step after STORY-027 (domain service extraction). If STORY-027 is done correctly, most of this story's acceptance criteria will already be met. This story exists to ensure completeness — to catch any business logic that STORY-027 may have missed and to enforce the architectural boundary explicitly.

If this story reveals business logic that STORY-027 did not extract, extract it as part of this story. Do not leave business logic in routers because "it was missed in the other story."
