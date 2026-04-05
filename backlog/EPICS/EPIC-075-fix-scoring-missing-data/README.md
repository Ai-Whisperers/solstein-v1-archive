# EPIC-075: Fix Scoring for Missing Data

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P2 — Make Scores Meaningful |
| **Effort** | M (3–5 days) |
| **Stories** | 5 ([STORY-298](STORIES/STORY-298.md) through [STORY-302](STORIES/STORY-302.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, Verified Codebase State, DoD) |

## Context

Current scorers produce near-zero composite scores for companies with incomplete data because missing fields apply large negative penalties. Companies with 40% data completeness score in the 0.5-2.0 range when they should score in the 4.0-5.0 range with appropriate uncertainty markers. This makes the platform unusable for real-world analysis where 100% data completeness is impossible.

## Verified Codebase State (2026-04-05)

- `src/solstein/analytics/scorers/growth_momentum.py:49-50` — `base_score = 0` then large deductions for missing fields confirmed
- `src/solstein/analytics/scorers/financial_health.py:54-55` — `base_score = 2.5` with `-2.0` penalty for missing revenue confirmed
- No `DataCompletenessScorer` class exists anywhere in `src/`
- Composite score formula in `src/solstein/analytics/composite_scorer.py` does not weight by completeness

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-298](STORIES/STORY-298.md) | GrowthMomentumScorer: change base from 0 to 3.0, reduce missing-data penalty from -1.0 to -0.5 | 🔴 READY | File: analytics/scorers/growth_momentum.py |
| [STORY-299](STORIES/STORY-299.md) | FinancialHealthScorer: change base from 2.5 to 4.0, reduce missing-revenue penalty from -2.0 to -0.5 | 🔴 READY | File: analytics/scorers/financial_health.py |
| [STORY-300](STORIES/STORY-300.md) | Add DataCompletenessScorer: new scorer that measures % of data fields populated per company | 🔴 READY | Deps: none |
| [STORY-301](STORIES/STORY-301.md) | Weight composite score by data completeness — high-data companies weighted more in market analysis | 🔴 READY | Deps: [STORY-300](STORIES/STORY-300.md) |
| [STORY-302](STORIES/STORY-302.md) | Update golden dataset expected ranges to match corrected scoring formula | 🔴 READY | Deps: [STORY-298](STORIES/STORY-298.md), [STORY-299](STORIES/STORY-299.md) |

## Success Criteria

- Companies with 40%+ data completeness score ≥ 3.5 baseline
- No zero scores for companies with valid name + industry
- Golden dataset expected ranges updated to match corrected formula
- DataCompletenessScorer produces 0.0-1.0 completeness ratio per company

## Definition of Done

- [ ] [STORY-298](STORIES/STORY-298.md): `growth_momentum.py` base_score = 3.0; penalty for missing fields ≤ -0.5
- [ ] [STORY-299](STORIES/STORY-299.md): `financial_health.py` base_score = 4.0; missing-revenue penalty = -0.5
- [ ] [STORY-300](STORIES/STORY-300.md): `DataCompletenessScorer` class exists and returns float 0.0–1.0
- [ ] [STORY-301](STORIES/STORY-301.md): composite scorer weights results by completeness score
- [ ] [STORY-302](STORIES/STORY-302.md): golden dataset expected ranges match output of corrected scorer
- [ ] `pytest tests/unit/ -k "scoring or scorer"` passes
- [ ] No existing test broken

## Dependencies

- [STORY-302](STORIES/STORY-302.md) blocks STORY-339 ([EPIC-083](../EPIC-083-fix-test-suite/README.md) — update golden dataset expected ranges)
