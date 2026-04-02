# STORY-032: Establish a Single Cache Abstraction

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

> Four caching implementations coexist: (1) in-memory Python dicts in some modules, (2) `CacheService` version 1 in `enrichment_service.py`, (3) `CacheService` version 2 in a separate file, (4) a Redis-backed client. Cache hits are not deterministic — they depend on which version of the cache was populated and which version is being queried.

## Problem Statement

Four cache implementations mean a cache write in one part of the system does not benefit a cache read in another. The system performs more external API calls than necessary because cached results in one implementation are invisible to callers using a different implementation.

Cache invalidation — famously one of the two hard problems in computer science — becomes impossible when there are four independent caches to invalidate. Invalidating `CacheService` v1 does not invalidate `CacheService` v2 or the in-memory dicts. The Redis client may hold stale data indefinitely if the invalidation path does not reach it.

The result is a system that caches aggressively but ineffectively: it pays the complexity cost of caching without the performance benefit.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Performance** | Redundant external API calls due to cache fragmentation — data cached in one implementation is invisible to others |
| **Cost** | LLM and external API costs are higher than necessary because cache misses occur even when data has been cached |
| **Reliability** | Cache invalidation is incomplete — stale data persists in implementations not reached by the invalidation path |
| **Debugging** | "Why is this stale?" is unanswerable without knowing which of four caches served the data |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| All modules with in-memory dict caches | Modify | Replace with canonical CacheService |
| `src/solstein/data/enrichment_service.py` | Modify | CacheService v1 — consolidate or remove |
| Separate CacheService v2 file | Modify/Delete | Consolidate or remove |
| Redis client module | Evaluate | May become the backend for the canonical CacheService |
| New: `src/solstein/infrastructure/cache.py` | Add | Canonical CacheService with Protocol |
| All callers of any cache | Modify | Must use the canonical CacheService |

## Architectural Requirements

- **REQ-1**: One `CacheService` abstraction must be the single cache used across the entire application
- **REQ-2**: The cache must be Redis-backed for persistence across process restarts — in-memory caches are acceptable only as an L1 layer in front of Redis
- **REQ-3**: An interface (`Protocol` or `ABC`) must define the cache contract, enabling alternative implementations for testing (in-memory) or future backends
- **REQ-4**: Cache key namespacing must prevent collisions between different data types (e.g., `enrichment:company_id` vs `scoring:company_id`)
- **REQ-5**: Cache TTLs must be configurable per data type — enrichment data may have a different freshness requirement than scoring data

## Acceptance Criteria

- [ ] One `CacheService` class exists with a defined interface (Protocol)
- [ ] All previously in-memory caches are replaced with the canonical `CacheService`
- [ ] All previously independent `CacheService` implementations are replaced
- [ ] Cache invalidation affects all consumers of the same key — there is one cache, not four
- [ ] Cache keys use namespacing to prevent collisions
- [ ] Cache TTLs are configurable per data type
- [ ] `grep -rn "cache = {}" . --include="*.py"` returns zero results (no ad-hoc dict caches)

## Definition of Done

**Tests Required:**
- [ ] Unit test: write via CacheService, read via CacheService — returns cached value
- [ ] Unit test: cache miss returns `None` or raises as documented
- [ ] Unit test: cache invalidation removes the cached value
- [ ] Unit test: TTL expiration causes cache miss
- [ ] Integration test: cache survives process restart (Redis-backed)
- [ ] Test: in-memory test implementation satisfies the cache Protocol

**Documentation Required:**
- [ ] Docstring on the CacheService Protocol explaining the contract
- [ ] Key namespacing convention documented in the cache module
- [ ] TTL configuration documented per data type

**Code Review Gate:**
- [ ] Reviewer confirms zero ad-hoc dict caches remain in the codebase
- [ ] Reviewer confirms one CacheService implementation exists
- [ ] Reviewer confirms cache invalidation path covers all consumers

## Notes

The Redis-backed client is likely the best foundation for the canonical `CacheService`. The in-memory implementations should be replaced, not layered. If an L1 in-memory cache is needed for performance, it should be a documented and intentional part of the `CacheService` implementation, not a separate ad-hoc dict.

For testing, provide an in-memory implementation that satisfies the same Protocol. Tests should not require Redis.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
