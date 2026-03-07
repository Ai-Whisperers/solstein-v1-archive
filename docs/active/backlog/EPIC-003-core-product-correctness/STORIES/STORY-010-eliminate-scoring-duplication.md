# STORY-010: Eliminate Scoring Logic Duplication

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-003: Core Product Correctness](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-009](STORY-009-unify-classification-thresholds.md) (Unified thresholds must exist before consolidating the scoring implementations that use them) |

---

## The Audit Verdict

> `analytics/scoring.py` contains its own implementations of `_calculate_growth_score()`, `_calculate_financial_health_score()`, and `_calculate_competitive_position_score()`. These functions already exist in `analytics/scorers/`. Additionally, `_merge_facts_into_financials()` and `_confidence_to_level()` are copy-pasted identically into both `analytics/scorers/financial_health.py` and `analytics/scorers/growth_momentum.py`. The codebase has at least three scoring implementations diverging silently.

## Problem Statement

Three separate scoring implementations exist for the same domain logic. Any bug fix or calibration change applied to one implementation will silently leave the others unmodified. Historical scoring results cannot be reproduced reliably if the call path changed between runs. The duplication is not a conscious design decision — it is the residue of incremental development without consolidation.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Scoring results vary depending on which implementation path executes |
| **Maintainability** | Every scoring change requires identifying and updating all three implementations — and the developer must first know all three exist |
| **Auditability** | Historical scores computed via different code paths cannot be compared or reproduced |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/analytics/scoring.py` | Modify | Remove 3 locally-defined scoring functions; delegate to `scorers/` |
| `src/solstein/analytics/scorers/financial_health.py` | Modify | Remove duplicated helper functions (`_merge_facts_into_financials`, `_confidence_to_level`) |
| `src/solstein/analytics/scorers/growth_momentum.py` | Modify | Remove duplicated helper functions (same two functions) |
| `src/solstein/analytics/scorers/` | Add | New shared utility module for common helper functions |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Each scoring function must be implemented exactly once in the codebase
- **REQ-2**: `analytics/scoring.py` must delegate to the `scorers/` classes rather than re-implementing their logic
- **REQ-3**: Shared helper functions (`_merge_facts_into_financials`, `_confidence_to_level`) must be extracted to a single shared module imported by all scorer classes
- **REQ-4**: After consolidation, the same input data must produce identical output regardless of which module initiated the scoring operation

## Acceptance Criteria

- [ ] Grep for `_calculate_growth_score` shows it defined in exactly one file
- [ ] Grep for `_calculate_financial_health_score` shows it defined in exactly one file
- [ ] Grep for `_calculate_competitive_position_score` shows it defined in exactly one file
- [ ] Grep for `_merge_facts_into_financials` shows it defined in exactly one file
- [ ] Grep for `_confidence_to_level` shows it defined in exactly one file
- [ ] `analytics/scoring.py` contains no local scoring function implementations — only delegation calls

## Definition of Done

**Tests Required:**
- [ ] Test: identical input to `scoring.py` and direct scorer class produces identical output
- [ ] Test: helper functions from both scorer files are demonstrably calling the same shared module
- [ ] Test: modifying the shared helper produces the expected change in all scoring paths (no stale copy)

**Documentation Required:**
- [ ] Each scorer class documented with its responsibility and the formula it implements

**Code Review Gate:**
- [ ] Reviewer confirms `analytics/scoring.py` contains zero private scoring method implementations
- [ ] Reviewer confirms no copy-paste duplication exists between any two scorer files

## Notes

This story depends on STORY-009. The scoring implementations currently embed their own threshold values. If scoring logic is consolidated before thresholds are unified, the consolidated implementation will inherit one of the three conflicting threshold sets — and it will not be obvious which one. Unify thresholds first, then consolidate the scoring logic that uses them.
