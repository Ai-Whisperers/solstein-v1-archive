# EPIC-075: Fix Scoring for Missing Data

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P2: Scoring Accuracy |
| **Phase** | P2 — Make Scores Meaningful |
| **Created** | 2026-04-01 |

## Context

Current scorers produce near-zero composite scores for companies with incomplete data because missing fields apply large negative penalties. Companies with 40% data completeness score in the 0.5-2.0 range when they should score in the 4.0-5.0 range with appropriate uncertainty markers. This makes the platform unusable for real-world analysis where 100% data completeness is impossible.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-298](STORIES/STORY-298.md) | GrowthMomentumScorer: change base from 0 to 3.0, reduce missing-data penalty from -1.0 to -0.5 | 🔴 READY | Deps: none. File: analytics/scorers/growth_momentum.py |
| [STORY-299](STORIES/STORY-299.md) | FinancialHealthScorer: change base from 2.5 to 4.0, reduce missing-revenue penalty from -2.0 to -0.5 | 🔴 READY | Deps: none. File: analytics/scorers/financial_health.py |
| [STORY-300](STORIES/STORY-300.md) | Add DataCompletenessScorer: new scorer that measures % of data fields populated per company | 🔴 READY | Deps: none |
| [STORY-301](STORIES/STORY-301.md) | Weight composite score by data completeness — high-data companies weighted more in market analysis | 🔴 READY | Deps: STORY-300 |
| [STORY-302](STORIES/STORY-302.md) | Update golden dataset expected ranges to match corrected scoring formula | 🔴 READY | Deps: STORY-298, STORY-299 |

## Success Criteria

- Companies with 40%+ data completeness score ≥ 3.5 baseline
- No zero scores for companies with valid name + industry
- Golden dataset expected ranges updated to match corrected formula
- DataCompletenessScorer produces 0.0-1.0 completeness ratio per company

## Dependencies

- STORY-302 blocks STORY-339 (update golden dataset expected ranges)
