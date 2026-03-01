# STORY-053: Establish a Unified Caching Strategy Document and Implementation

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P3 |
| Severity | MEDIUM |
| Epic | [EPIC-016: Performance & Scalability](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-032: Consolidate Cache Implementations](../../EPIC-009-data-layer-consolidation/STORIES/STORY-032.md) |

---

## The Audit Verdict
> Even after STORY-032 consolidates the four cache implementations to one, there is no documented caching strategy: what gets cached, for how long, under what TTL policy, and what triggers invalidation. Different engineers will make different caching decisions in new code, re-fragmenting the cache.

## Problem Statement
A single CacheService without a caching strategy document will be used inconsistently. New code will introduce ad-hoc TTLs and key naming patterns, recreating the fragmentation problem over time. The technical debt will regenerate in the absence of a documented standard. STORY-032 solves the implementation fragmentation; this story prevents the decision fragmentation that caused it.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Consistency** | Caching decisions will be made independently by each engineer — TTLs will drift, key formats will diverge |
| **Performance** | Over-caching stale data or under-caching expensive computations without documented rationale |
| **Invalidation** | Cache invalidation logic will be incomplete without a defined strategy — the hardest problem in computer science, unaddressed |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `docs/caching-strategy.md` | Add | Create: comprehensive caching strategy document |
| `src/solstein/core/cache.py` or equivalent | Modify | Ensure TTL constants are defined as named constants in one location |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A `docs/caching-strategy.md` must define: what data is cached, the TTL for each data type, the cache key naming convention, and the invalidation trigger for each cache entry type
- **REQ-2**: TTL values must be named constants in code, not inline literals — the constant name must communicate the business meaning of the duration
- **REQ-3**: The caching strategy must specify behaviour when the cache is cold (first request or TTL expiry) — whether to serve stale data, block until fresh data is available, or return an error
- **REQ-4**: The strategy must define which operations must bypass the cache (e.g., write operations, admin queries, data refresh operations)

## Acceptance Criteria
- [ ] `docs/caching-strategy.md` exists and is reviewed by at least one engineer
- [ ] TTL values are named constants in one module, not scattered as inline literals
- [ ] New cache usages conform to the documented key naming convention
- [ ] Cold cache behaviour is documented and consistently implemented

## Definition of Done

**Tests Required:**
- [ ] TTL constants are importable and have expected values
- [ ] Cache key generation follows the documented naming convention (unit test)

**Documentation Required:**
- [ ] `docs/caching-strategy.md` complete and peer-reviewed

**Code Review Gate:**
- [ ] All new cache usage is reviewed against the strategy document
- [ ] Reviewer confirms no inline TTL literals exist outside the constants module

## Notes
This story is a governance mechanism. The technical implementation (STORY-032) provides a single CacheService. This story provides the rules for using it. Without the rules, the single CacheService will be used 4 different ways by 4 different engineers, and in a year we will have 4 different caching strategies implemented via one CacheService — the same problem with a cleaner interface.
