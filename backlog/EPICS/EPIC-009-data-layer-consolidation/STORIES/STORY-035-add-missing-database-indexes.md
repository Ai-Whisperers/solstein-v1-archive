# STORY-035: Add Missing Database Indexes on High-Query Tables

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-009: Data Layer Consolidation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-034](STORY-034-fix-n-plus-one-queries.md) |

---

## The Audit Verdict

> `infrastructure/database_models.py` defines `ScoringRecord`, `SignalRecord`, and `EnrichmentAudit` tables. These are the tables most frequently queried in the application. None have indexes on their foreign key columns (`company_id`) or their most-queried lookup fields (timestamps, status columns). Every query on these tables performs a sequential scan.

## Problem Statement

Missing indexes on frequently-queried tables mean every lookup scans the entire table. As data volume grows, query times degrade linearly with record count. This is the difference between O(log n) (index scan) and O(n) (sequential scan).

The scoring and enrichment audit tables are queried on every company view and every health check. Without indexes on `company_id`, each of these queries reads every row in the table to find the matching records. At 100,000 records, this is slow. At 1,000,000 records, it is unacceptable. At 10,000,000 records, it is a production incident.

Foreign key columns without indexes are a particularly common and particularly impactful oversight. PostgreSQL does not automatically create indexes on foreign key columns (unlike some other databases). Every foreign key join without an index becomes a sequential scan on the referenced table.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Performance** | O(n) queries on tables that should be O(log n) with indexes |
| **Scalability** | Predictable, linear performance degradation as the dataset grows |
| **Availability** | Slow queries under load can exhaust connection pool, affecting all users |
| **Cost** | Higher database CPU utilisation for the same throughput |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/infrastructure/database_models.py` | Modify | Add index declarations to model definitions |
| New: database migration script | Add | Migration to create indexes on existing tables |

## Architectural Requirements

- **REQ-1**: `ScoringRecord` must have indexes on `company_id` and `scored_at`
- **REQ-2**: `SignalRecord` must have an index on `company_id`
- **REQ-3**: `EnrichmentAudit` must have indexes on `company_id` and `created_at`
- **REQ-4**: All foreign key columns across all tables must have corresponding indexes — this is not limited to the three tables above
- **REQ-5**: Indexes must be added via a database migration, not by modifying the model definition only — models define schema intent, migrations define schema reality

## Acceptance Criteria

- [ ] `EXPLAIN SELECT * FROM scoring_records WHERE company_id = ?` shows Index Scan, not Seq Scan
- [ ] `EXPLAIN SELECT * FROM signal_records WHERE company_id = ?` shows Index Scan, not Seq Scan
- [ ] `EXPLAIN SELECT * FROM enrichment_audit WHERE company_id = ? ORDER BY created_at DESC` shows Index Scan, not Seq Scan
- [ ] All foreign key columns across all models have corresponding indexes
- [ ] A database migration file exists that creates these indexes
- [ ] The migration is idempotent — it can run on databases where indexes already exist without error

## Definition of Done

**Tests Required:**
- [ ] Integration test: `EXPLAIN` query plan confirms index usage on `ScoringRecord.company_id`
- [ ] Integration test: `EXPLAIN` query plan confirms index usage on `SignalRecord.company_id`
- [ ] Integration test: `EXPLAIN` query plan confirms index usage on `EnrichmentAudit.company_id`
- [ ] Test: migration runs successfully on a fresh database
- [ ] Test: migration runs successfully on a database where indexes already exist (idempotent)

**Documentation Required:**
- [ ] Migration file includes comments explaining which indexes are added and why
- [ ] Database schema documentation updated to reflect new indexes

**Code Review Gate:**
- [ ] Reviewer confirms all foreign key columns have indexes
- [ ] Reviewer confirms indexes are added via migration, not just model changes
- [ ] Reviewer confirms migration is idempotent

## Notes

This story depends on STORY-034 (N+1 query fix) because the queries being pushed to the database by STORY-034 are the queries that need index support. Without STORY-034, the application filters in Python and never executes the WHERE clauses that indexes would accelerate.

After both stories are complete, run `EXPLAIN ANALYZE` on the primary queries to verify that indexes are not only present but actively used by the query planner. PostgreSQL's query planner may choose a sequential scan even when an index exists if the table is small enough or the selectivity is too low.

Index creation on large tables can lock the table. Use `CREATE INDEX CONCURRENTLY` in the migration to avoid locking production tables during the migration.

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
