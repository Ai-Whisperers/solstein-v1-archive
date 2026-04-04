# STORY-299: FinancialHealthScorer: change base from 2.5 to 4.0, reduce missing-revenue penalty

| Field | Value |
|-------|-------|
| **Epic** | EPIC-075 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Change `FinancialHealthScorer` base score from 2.5 to 4.0 and reduce missing-revenue penalty from -2.0 to -0.5. File: `analytics/scorers/financial_health.py`.

## Acceptance Criteria

- [ ] Base score = 4.0 (was 2.5)
- [ ] Missing revenue penalty = -0.5 (was -2.0)
- [ ] Companies with no financial data score ≥ 3.0 (was ~0.5)
- [ ] Companies with full financial data unchanged in relative ranking
- [ ] Existing tests updated; no new test failures
