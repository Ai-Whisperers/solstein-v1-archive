# EPIC-004: Data Integrity & Atomicity

| Field | Value |
|-------|-------|
| Priority | **P0 — Ship Blocker** |
| Status | 🔶 Partial — STORY-012 Complete |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | [EPIC-001: Security Restoration](../EPIC-001-security-restoration/README.md) |

## Context

The research pipeline is the platform's data backbone. It ingests data from multiple external agents, resolves conflicts between sources, and writes the consolidated result to PostgreSQL. Every step of this process is broken in a way that produces silent data corruption.

**No write atomicity.** `infrastructure/research_dual_write.py` (564 lines) performs 7 sequential database commits with no compensating rollback. The outbox record is written before the primary data record. A failure at any commit point leaves the database in an inconsistent state — partial research data coexists with an outbox entry that references records that may not exist. There is no saga pattern, no idempotency key, and no mechanism to detect partial-write states. The system does not know when its own data is corrupt.

**Conflict resolution ignores recency and reliability.** `infrastructure/conflict_resolution.py` merges conflicting data records without considering which record is more recent or which source has higher reliability. When two agents report different revenue figures for the same company, the system has no principled way to choose. The `MANUAL_REVIEW` conflict resolution strategy is particularly concerning: it creates no review record. It silently retains existing data and moves on. The word "manual" implies a human is involved. No human is notified. No record is created. The strategy is a no-op masquerading as a workflow.

**Hardcoded data path.** `data/unified_loader.py` lines 226–233 construct a file system path using the hardcoded strings `'2026-02-23'` and `'dutch_market'`. On any other date or for any other market, the loader silently returns empty results. No exception is raised. No warning is logged. The caller receives an empty dataset with no indication that the system is misconfigured. This is a time bomb with a known detonation date.

Additionally, `data/unified_loader.py` line 929 hardcodes `GBP_EUR_RATE = 1.17`. This static exchange rate will be wrong within weeks and increasingly wrong thereafter, producing silently incorrect financial comparisons for any cross-currency analysis.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-012](STORIES/STORY-012-dual-write-atomicity.md) | Fix Dual-Write Atomicity in Research Pipeline | CRITICAL |
| [STORY-013](STORIES/STORY-013-fix-conflict-resolution-logic.md) | Fix Conflict Resolution to Consider Data Recency and Source Reliability | HIGH |
| [STORY-014](STORIES/STORY-014-remove-hardcoded-date-path.md) | Remove Hardcoded Date Path from Data Loader | HIGH |

## Definition of Done

## Definition of Done

- [x] All writes in a research pipeline execution either all succeed atomically or all roll back with no partial state
- [x] The outbox never contains a record that references a primary record that does not exist
- [ ] Conflict resolution considers data recency and source reliability when merging records
- [ ] The `MANUAL_REVIEW` strategy creates a persisted, queryable review record
- [ ] No date string or market name appears as a hardcoded literal in data loading code
- [ ] No static exchange rate appears as a numeric literal in the codebase
- [ ] The outbox never contains a record that references a primary record that does not exist
- [ ] Conflict resolution considers data recency and source reliability when merging records
- [ ] The `MANUAL_REVIEW` strategy creates a persisted, queryable review record
- [ ] No date string or market name appears as a hardcoded literal in data loading code
- [ ] No static exchange rate appears as a numeric literal in the codebase

## Ordering Rationale

The three stories in this epic are independent of each other and can be executed in parallel. However, STORY-012 (atomicity) should be prioritized as it addresses silent data corruption — the most dangerous class of defect because it is invisible until downstream consumers produce incorrect results.
