# EPIC-046: Scoring Engine Correctness

> **Discovered**: 2026-03-01 via live end-to-end run analysis  
> **Priority**: P0–P1 — Core output of the platform is wrong  
> **Stories**: 4 ([STORY-173](STORIES/STORY-173.md) through [STORY-176](STORIES/STORY-176.md))  
> **Effort**: M (3–4 days total)

---

## Problem

The scoring engine (`src/solstein/analytics/scoring.py`) computes correct numeric scores but produces incorrect or dangerous metadata output. Most critically, `threat_level` is never updated after scoring — a company classified as `Phoenix` (highest competitive threat) retains whatever `threat_level` was in the input JSON (often `"Low"`). PE/VC analysts use `threat_level` as a primary signal; getting it wrong invalidates the analysis.

Additionally, the scoring module contains 270 lines of dead private methods (`_calculate_growth_score`, `_calculate_financial_health_score`, `_calculate_competitive_position_score`) that are never called, creating severe maintenance risk: anyone editing the wrong method believes they're changing scoring behavior when they are not.

### Scoring Output Issues for Eneve (live run)

| Field | Expected | Actual | Problem |
|-------|----------|--------|---------|
| `classification` | `Phoenix` | `Phoenix` | ✅ Correct |
| `threat_level` | `HIGH` or `CRITICAL` | `Low` | ❌ Never updated |
| `composite_score` | `8.37` | `8.37` | ✅ Correct |
| `competitive_position_score` | `7.14` | `7.138888...` | ❌ Never rounded |
| `saas_maturity=None` company | Graceful score | `TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'` | ❌ Hard crash |

---

## Stories

| Story | Title | Priority | Size |
|-------|-------|----------|------|
| [STORY-173](STORIES/STORY-173.md) | Derive `threat_level` from composite score and classification after scoring | P0 | S |
| [STORY-174](STORIES/STORY-174.md) | Add null guard for `saas_maturity` in `CompetitivePositionScorer` | P0 | S |
| [STORY-175](STORIES/STORY-175.md) | Remove 270 lines of dead `_calculate_*` private methods from `GrowthScorer` | P1 | S |
| [STORY-176](STORIES/STORY-176.md) | Define authoritative `classification → threat_level` mapping in constants | P1 | S |

---

## Definition of Done

- [ ] `threat_level` on any scored company reflects its composite score and classification
- [ ] No crash when any scoring input field is `None`
- [ ] All score outputs are rounded to 2 decimal places
- [ ] Dead code removed and tests confirm the live scoring path
- [ ] `tests/unit/analytics/test_scoring_correctness.py` covers all classification → threat_level combinations
