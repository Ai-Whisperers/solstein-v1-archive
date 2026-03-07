# STORY-174: Add Null Guard for `saas_maturity` in `CompetitivePositionScorer`

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | S (< half a day) |
| **Epic** | EPIC-046 Scoring Engine Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — one-line fix |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED LATENT CRASH** — code path confirmed in source, crash reproducible with any company lacking `saas_maturity`.

```python
# src/solstein/analytics/scoring.py — CompetitivePositionScorer (~line 360)
saas_adj = (profile.saas_maturity - 1) / 9 * 2.0
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: unsupported operand type(s) for -: 'NoneType' and 'int'
# when profile.saas_maturity is None
```

Eneve has `saas_maturity = 7` (doesn't crash). However:
- Companies loaded from the API (no SaaS data field) → `saas_maturity = None`
- Companies from SEC EDGAR (B2B non-SaaS) → `saas_maturity = None`
- Any enrichment partial failure → `saas_maturity = None`

---

## Problem Statement

`saas_maturity` is an optional field. The majority of companies that will be analyzed via the API or enrichment connectors will not have this field. The scorer does not guard against `None`, meaning any company without SaaS data causes a hard crash in `calculate_scores()` — the core function of the platform.

This is currently masked because the CLI demo companies (Eneve, Test Company 2, Test Company 3) all have `saas_maturity` populated in the JSON fixture. As soon as real companies are scored (via enrichment pipeline or API), this crashes.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Reliability | 🔴 Critical — will crash on first real company without SaaS data |
| Data Coverage | 🔴 Critical — blocks scoring of any company not in fixture |
| Business Value | 🟠 High — SaaS adjustment is minor (max ±1.33 points); missing it is acceptable |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/scoring.py` | ~360 (CompetitivePositionScorer) | 1-line guard |
| `tests/unit/analytics/test_scoring_none_inputs.py` | New | Crash reproduction test |

---

## Dependencies

- **Hard**: None — completely isolated fix
- **Soft**: STORY-175 (dead code cleanup may reveal other None-unsafe lines)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: When `saas_maturity` is `None`, treat it as the neutral midpoint (5 on a 1–10 scale) rather than crashing. This produces zero SaaS adjustment, which is the correct behavior when data is absent.

**REQ-2**: Audit the entire `CompetitivePositionScorer` and `GrowthMomentumScorer` for other division-by-zero or None-arithmetic risks.

**REQ-3**: Add a `_safe_numeric(value, default)` helper to the scorer module to DRY this pattern across all numeric fields.

---

## Acceptance Criteria

- [ ] `GrowthScorer().calculate_scores(company)` where `company.saas_maturity = None` completes without error
- [ ] When `saas_maturity = None`, `saas_adj = 0.0` (neutral)
- [ ] When `saas_maturity = 5`, `saas_adj = (5-1)/9*2.0 = 0.889` (same as before)
- [ ] Audit of `CompetitivePositionScorer`, `GrowthMomentumScorer`, `FinancialHealthScorer` produces a list of all None-unsafe lines — any found must be fixed in the same PR
- [ ] Unit test: `test_scoring_with_all_none_optional_fields` — score a company where every optional field is `None`

---

## Implementation Note

```python
# scoring.py — safe helper:
def _safe_float(value, default: float = 0.0) -> float:
    """Return value as float, or default if None/non-numeric."""
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# CompetitivePositionScorer:
saas_maturity = _safe_float(profile.saas_maturity, default=5.0)
saas_adj = (saas_maturity - 1) / 9 * 2.0
```

---

## Definition of Done

- [ ] One-line fix applied
- [ ] Full None-field audit completed and documented in PR
- [ ] Unit test: company with all optional fields = None scores without error
- [ ] Test confirms saas_maturity=None gives saas_adj=0.0

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Line 360 identified in source; crash confirmed for None inputs |
