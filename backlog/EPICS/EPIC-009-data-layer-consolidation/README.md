# EPIC-009: Data Layer Consolidation

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-032, STORY-033, STORY-034, STORY-035 |
| Created | 2026-02-28 |

---

## Summary

Four cache implementations means none of them are the cache.

The data layer has accumulated redundant implementations of every major concern: caching, validation, and querying. Each redundancy means that the system's behaviour depends on which code path was taken to reach the data — a condition that is antithetical to reliability.

## The Problems

### Four Incompatible Caching Implementations

| Cache Type | Location | Scope |
|-----------|----------|-------|
| In-memory Python dicts | Various modules | Per-process, lost on restart |
| `CacheService` v1 | `data/enrichment_service.py` | Module-scoped |
| `CacheService` v2 | Separate cache module | Application-scoped |
| Redis-backed client | Infrastructure layer | Persistent across restarts |

Whether a cache hit occurs depends entirely on which code path was taken to retrieve the data. A cache write via `CacheService` v1 does not benefit a cache read via `CacheService` v2. The in-memory dict caches are invisible to all other implementations. The Redis client is the only cache that survives process restarts, but not all code paths use it.

### Three Parallel Validation Systems

| Validation System | Location | Type |
|------------------|----------|------|
| `enrichment_validators.py` | `data/enrichment_validators.py` | Standalone module |
| `DataValidationService` | `data/enrichment_service.py` | Embedded class |
| Inline validation | `data/unified_loader.py` | Inline code |

The same data field is potentially validated three times with different rules. Or validated once with rules that differ from the other two implementations. There is no guarantee of consistency.

### N+1 Query Patterns

`data/loaders.py` loads all companies from the database into Python memory and filters in application code. `api/routers/export.py` loads the entire dataset with no limit or pagination. At scale, both patterns are memory and performance disasters.

### Missing Database Indexes

`ScoringRecord`, `SignalRecord`, and `EnrichmentAudit` — the tables most frequently queried in the application — have no indexes on their foreign key columns or lookup fields. Every query performs a sequential scan. This is O(n) where O(log n) is trivially achievable.

## Stories

| Story | Title | Priority | Severity |
|-------|-------|----------|----------|
| [STORY-032](STORIES/STORY-032-single-cache-abstraction.md) | Establish a Single Cache Abstraction | P1 | HIGH |
| [STORY-033](STORIES/STORY-033-single-validation-service.md) | Establish a Single Validation Service | P1 | HIGH |
| [STORY-034](STORIES/STORY-034-fix-n-plus-one-queries.md) | Fix N+1 Query Patterns in Data Loading | P1 | HIGH |
| [STORY-035](STORIES/STORY-035-add-missing-database-indexes.md) | Add Missing Database Indexes on High-Query Tables | P1 | HIGH |

## Definition of Done

- [ ] One cache implementation exists — all others are deleted
- [ ] One validation service exists — all data entry points use it
- [ ] All filtering is database-side — no Python-side filtering of full datasets
- [ ] All bulk endpoints support pagination with enforced limits
- [ ] All foreign key columns have indexes
- [ ] EXPLAIN on primary queries shows index scans, not sequential scans

## Ordering Notes

STORY-032 (cache), STORY-033 (validation), and STORY-034 (N+1 queries) are independent and can be executed in parallel. STORY-035 (indexes) should follow STORY-034 because the index additions should be verified by testing the queries that STORY-034 pushes to the database.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
