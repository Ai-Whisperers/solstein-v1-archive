# STORY-013: Fix Conflict Resolution to Consider Data Recency and Source Reliability

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-004: Data Integrity & Atomicity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `infrastructure/conflict_resolution.py` merges conflicting data records without considering (1) which record is more recent, (2) which source has higher reliability, or (3) whether currency conversion is applicable. The `MANUAL_REVIEW` strategy creates no review record — it silently retains existing data. `data/unified_loader.py` line 929 hardcodes `GBP_EUR_RATE = 1.17`.

## Problem Statement

The conflict resolution system can silently overwrite newer, higher-quality data with older, lower-quality data. When two agents report conflicting revenue figures for the same company, the resolution logic has no mechanism to prefer the more recent or more reliable source. Records flagged for "manual review" are not flagged — the `MANUAL_REVIEW` strategy is a no-op that keeps existing data without creating any operator-visible signal. The word "manual" implies human involvement. No human is notified. No record is created. No queue exists. Financial comparisons across currencies use a static exchange rate (`GBP_EUR_RATE = 1.17`) that will be wrong within weeks.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Data Quality** | Older, less reliable data can silently overwrite newer, higher-quality data during conflict resolution |
| **Operational** | No review queue exists despite the system claiming to flag records for manual review — the strategy is a silent no-op |
| **Financial Accuracy** | Static FX rate produces increasingly incorrect financial comparisons over time; error compounds with every passing week |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/infrastructure/conflict_resolution.py` | Modify | Add recency and source reliability to resolution logic; implement real MANUAL_REVIEW flagging |
| `src/solstein/data/unified_loader.py` | Modify | Line 929: replace hardcoded FX rate with configurable source |
| `tests/unit/test_conflict_resolution.py` | Add | Recency, reliability, and MANUAL_REVIEW tests |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Conflict resolution must prefer records with more recent timestamps when content conflicts exist
- **REQ-2**: Each data source must have an explicit reliability rank that contributes to resolution decisions when recency is equal
- **REQ-3**: The `MANUAL_REVIEW` strategy must create a persisted, queryable review record that operators can retrieve; silently retaining existing data is not acceptable
- **REQ-4**: The GBP-to-EUR conversion rate must be loaded from application configuration or an external rate source; no static numeric literal is permitted

## Acceptance Criteria

- [ ] A newer record with conflicting content wins over an older record from the same source
- [ ] When recency is equal, the record from the higher-reliability source wins
- [ ] A `MANUAL_REVIEW` conflict creates a database record retrievable via a query or API endpoint
- [ ] Grep for `1.17` returns zero results in the codebase
- [ ] The FX rate source is documented in configuration
- [ ] An operator can list all pending manual review records

## Definition of Done

**Tests Required:**
- [ ] Unit test: newer record wins over older record on conflict
- [ ] Unit test: higher-reliability source wins when timestamps are equal
- [ ] Unit test: `MANUAL_REVIEW` creates a persisted review record with both conflicting values
- [ ] Integration test: FX rate loaded from configuration, not hardcoded
- [ ] Unit test: manual review records are retrievable via query

**Documentation Required:**
- [ ] Source reliability rankings documented with rationale
- [ ] Conflict resolution decision matrix documented (recency × reliability)
- [ ] FX rate configuration source documented

**Code Review Gate:**
- [ ] Reviewer confirms `MANUAL_REVIEW` path creates a persisted record — not a log-only or silent-retain operation
- [ ] Reviewer confirms no static exchange rate literal exists in the codebase

## Notes

This story is independent of STORY-012 (atomicity) and STORY-014 (hardcoded path) and can proceed in parallel. The FX rate fix overlaps slightly with STORY-040 (EPIC-011) which addresses it from a business rules documentation perspective. This story handles the technical replacement; STORY-040 handles the business documentation of what rate source to use and how often to refresh.
