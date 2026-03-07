# STORY-175: Remove 270 Lines of Dead `_calculate_*` Private Methods from `GrowthScorer`

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P1 — High |
| **Size** | S (half a day) |
| **Epic** | EPIC-046 Scoring Engine Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — removing dead code, zero runtime behavior change |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED DEAD CODE** — confirmed by live execution and source trace on 2026-03-01.

```python
# src/solstein/analytics/scoring.py — GrowthScorer class
# Lines ~110–113 (the live scoring path):
growth_score, growth_expl = self.growth_momentum_scorer.score(profile.financials)
fin_score, fin_expl       = self.financial_health_scorer.score(profile.financials)
comp_score, comp_expl     = self.competitive_position_scorer.score(profile)

# Lines ~141–411 (DEAD — never called):
def _calculate_growth_score(self, profile) -> float:     # 90 lines
def _calculate_financial_health_score(self, profile) -> float:  # 80 lines
def _calculate_competitive_position_score(self, profile) -> float:  # 100 lines
```

The private methods implement **different scoring logic** than the sub-scorers they shadow. If any developer edits `_calculate_growth_score` thinking they're changing how growth is scored, their change has zero effect. The live scoring comes from `analytics/scorers/growth_momentum.py`, `financial_health.py`, `competitive_position.py` — not these methods.

---

## Problem Statement

`GrowthScorer` contains 270 lines of shadow implementation that:
1. Are never called — confirmed by tracing `calculate_scores()` execution path
2. Use slightly different formulas than the sub-scorers actually used
3. Access `profile.revenue_eur_m` and `profile.growth_rate_pct` (flat attributes that don't exist — they would crash if ever called)
4. Create a maintenance trap: any developer seeing `_calculate_growth_score` in `scoring.py` will edit it, believe it works, and ship unchanged behavior

The dead code is larger than the live code in this file.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Maintainability | 🟠 High — maintenance trap; false confidence when editing |
| Code Quality | 🟠 High — 270 lines of confusing, misleading dead code |
| Reliability | 🟡 Medium — dead code references non-existent attributes (would crash if called) |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/scoring.py` | ~141–411 | Delete dead methods |
| `tests/unit/analytics/test_scoring.py` | Existing | Verify tests still pass |

---

## Dependencies

- **Hard**: Confirm via `grep` and coverage that no external caller invokes `_calculate_*` methods
- **Soft**: STORY-174 (do both in same PR — clean up scoring.py once)
- **Supersedes**: EPIC-037 general dead code cleanup (this is a specific instance)

---

## Architectural Requirements

**REQ-1**: Before deletion, run `grep -rn "_calculate_growth_score\|_calculate_financial_health_score\|_calculate_competitive_position_score" src/` to confirm zero callers.

**REQ-2**: After deletion, add a comment at the top of `GrowthScorer.calculate_scores()` documenting the live scoring path:
```python
# Scoring delegated to sub-scorers in analytics/scorers/:
#   growth_momentum.py  → growth_score
#   financial_health.py → financial_health_score
#   competitive_position.py → competitive_position_score
```

**REQ-3**: The sub-scorers in `analytics/scorers/` must have their own unit tests (or inherit them) before this story is closed — the deleted methods may have been used as reference documentation for the scoring logic.

---

## Acceptance Criteria

- [ ] `src/solstein/analytics/scoring.py` is reduced from ~411 lines to ~141 lines
- [ ] `grep _calculate_growth_score src/` returns zero results
- [ ] All existing scoring tests pass unchanged
- [ ] Sub-scorer unit tests exist in `tests/unit/analytics/test_scorers/`
- [ ] `calculate_scores()` has a docstring/comment documenting which sub-scorers it delegates to

---

## Definition of Done

- [ ] Dead methods deleted
- [ ] No broken references anywhere in codebase
- [ ] Sub-scorer tests confirmed present
- [ ] PR description includes before/after line count

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hidden external caller via reflection/dynamic dispatch | Very Low | High | Grep + coverage report before deleting |
| Sub-scorers have subtly different behavior from deleted methods | Medium | Low | Dead methods never ran anyway; no behavior change |

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Source trace confirmed dead methods at lines ~141-411 |
