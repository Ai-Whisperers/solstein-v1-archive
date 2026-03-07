# STORY-054: Implement CQRS Read/Write Model Separation

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P3 |
| Severity | LOW |
| Epic | [EPIC-016: Performance & Scalability](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-025: Repository Interfaces](../../EPIC-007-ddd-migration/STORIES/STORY-025.md), [STORY-036: Service Layer Extraction](../../EPIC-008-service-layer-extraction/STORIES/STORY-036.md) |

---

## The Audit Verdict
> Read and write operations use the same domain models, the same repository implementations, and the same database connections. Read-heavy analytics queries compete with write-heavy research pipeline operations on the same connection pool.

## Problem Statement
Mixed read/write models prevent independent optimisation of read paths (e.g., read replicas, denormalised projections) and write paths (e.g., write-ahead logging, event sourcing). Analytics endpoints that query large datasets compete for database connections with research pipeline writes that create or update company records. The connection pool is the bottleneck — and both paths fight over it.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Performance** | Read and write operations compete for the same database connection pool — analytics queries block research pipeline writes and vice versa |
| **Scalability** | Cannot independently scale read and write throughput — scaling the database scales both, even if only one is the bottleneck |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/` | Modify | Separate read models (projections) from write models (aggregates) |
| Repository implementations | Modify | Create read-optimised repository implementations |
| Database configuration | Modify | Support separate read and write connection strings |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Read operations (analytics, reporting, export) must use dedicated read models or projections distinct from the write domain model
- **REQ-2**: Write operations must use the rich domain model with invariant enforcement — the write model retains all business logic
- **REQ-3**: The application configuration must support separate read and write database connection strings (for future read replica support)
- **REQ-4**: Read model construction must be defined in one location, not scattered across service methods — a read model is a first-class architectural concept, not an ad-hoc DTO

## Acceptance Criteria
- [ ] Read endpoints use read-optimised models, not the write domain model
- [ ] Configuration supports separate `READ_DATABASE_URL` and `WRITE_DATABASE_URL`
- [ ] Write endpoints continue to enforce domain invariants through the rich domain model
- [ ] Read models are defined in a dedicated module, not inline in service methods

## Definition of Done

**Tests Required:**
- [ ] Integration test: read endpoint uses read model and read connection
- [ ] Configuration test: separate read/write database URLs are supported
- [ ] Unit test: write operations still enforce domain invariants

**Documentation Required:**
- [ ] CQRS pattern documented in `docs/architecture.md`
- [ ] Read model definition patterns documented in `docs/contributing.md`

**Code Review Gate:**
- [ ] Reviewer confirms read and write paths use appropriate models
- [ ] Reviewer confirms read models are defined in a dedicated location

## Notes
This is a low-priority, high-effort architectural change. It should only be undertaken after the foundation epics (EPIC-001 through EPIC-010) are complete. The immediate performance benefit is modest — the real value is enabling future scalability via read replicas. The repository interfaces from STORY-025 and service layer extraction from STORY-036 are prerequisites because CQRS requires clean separation of read and write concerns at the service and repository layers. Without those boundaries, CQRS is a cosmetic change.
