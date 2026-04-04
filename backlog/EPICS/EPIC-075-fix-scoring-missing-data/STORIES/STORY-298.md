# STORY-298: GrowthMomentumScorer: change base from 0 to 3.0, reduce missing-data penalty

| Field | Value |
|-------|-------|
| **Epic** | EPIC-075 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Change `GrowthMomentumScorer` base score from 0 to 3.0 and reduce missing-data penalty from -1.0 to -0.5. File: `analytics/scorers/growth_momentum.py`.

## Acceptance Criteria

- [ ] Base score = 3.0 (was 0)
- [ ] Missing employee_cagr penalty = -0.5 (was -1.0)
- [ ] Companies with no growth data score ≥ 2.0 (was near 0)
- [ ] Companies with full growth data unchanged in relative ranking
- [ ] Existing tests updated; no new test failures
