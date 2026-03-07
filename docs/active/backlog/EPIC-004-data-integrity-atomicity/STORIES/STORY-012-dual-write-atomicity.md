# STORY-012: Fix Dual-Write Atomicity in Research Pipeline

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-004: Data Integrity & Atomicity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `infrastructure/research_dual_write.py` (564 lines) executes 7 sequential database commits with no compensating rollback. The outbox record is written before the primary data record. A failure at commit 3 leaves the database with partial data and an outbox entry pointing to nonexistent records. There is no saga pattern, no idempotency key, and no detection of partial-write states.

## Problem Statement

Research pipeline writes are not atomic. Multiple sequential commits with no rollback mechanism mean any failure mid-sequence produces permanently inconsistent database state. The outbox — designed to notify downstream consumers of new data — is written before the data it describes, creating a window where the outbox references records that do not yet exist. If the subsequent data write fails, the outbox reference becomes permanently dangling. The system has no mechanism to detect, report, or recover from partial writes.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Data Integrity** | Partial research results persist indefinitely with no indication they are incomplete |
| **Downstream Processing** | Outbox entries reference nonexistent primary records, causing silent failures in downstream consumers |
| **Operational** | There is no mechanism to identify or repair inconsistent records — the corruption is invisible |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/infrastructure/research_dual_write.py` | Modify | Implement atomic write strategy with rollback on failure across all 7 commit points |
| `tests/integration/test_dual_write_atomicity.py` | Add | Failure injection at each commit point to verify rollback |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: All writes in a research pipeline execution must either all succeed atomically or all be rolled back with no partial state remaining
- **REQ-2**: The outbox record must not be written until the primary data write has been durably committed
- **REQ-3**: If a single database transaction cannot span all required writes, a compensating transaction pattern must be implemented with explicit rollback steps for each completed write
- **REQ-4**: Each write operation must be idempotent — retrying a failed write must not produce duplicate records
- **REQ-5**: The system must detect and log any partial-write state discovered at startup or during health checks

## Acceptance Criteria

- [ ] A simulated failure at each of the 7 commit points leaves the database in its pre-write state
- [ ] The outbox never contains a record that references a primary record that does not exist
- [ ] Retrying the same research write twice produces exactly one record, not two
- [ ] Partial-write detection runs at startup and logs any inconsistencies found

## Definition of Done

**Tests Required:**
- [ ] Integration test: inject failure at commit point 1 — assert full rollback, database unchanged
- [ ] Integration test: inject failure at commit point 4 (mid-sequence) — assert full rollback
- [ ] Integration test: inject failure at commit point 7 (final) — assert full rollback
- [ ] Integration test: retry idempotency — same write executed twice produces exactly one record
- [ ] Integration test: outbox-primary consistency — no outbox entry exists without its referenced primary record

**Documentation Required:**
- [ ] Write ordering documented: which records are written in which order and why
- [ ] Rollback strategy documented: what happens at each failure point

**Code Review Gate:**
- [ ] Reviewer confirms no `session.commit()` call exists outside the transaction boundary
- [ ] Reviewer confirms outbox write occurs after (not before) primary data write within the same transaction

## Notes

This is the most dangerous defect in the EPIC-004 scope. Silent data corruption is worse than loud failures because it is invisible until downstream consumers produce incorrect results — and at that point, the corruption may have propagated through multiple analysis runs. This story has no dependencies and should be started immediately.
