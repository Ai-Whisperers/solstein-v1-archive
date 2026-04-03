# STORY-365: Fix Pre-Existing Test Fixture Failures (3 broken unit tests)

| Field | Value |
|---|---|
| **Status** | 🔴 READY |
| **Priority** | P3 |
| **Size** | XS (1 hour) |
| **Epic** | EPIC-003 Core Product Correctness |
| **Created** | 2026-04-03 |
| **Risk** | Low — test fixture fixes only, no production code changes |

---

## Actual Codebase State (verified 2026-04-03)

Three unit tests have been failing since before EPIC-086 (not caused by STORY-348):

**1. `tests/unit/test_scoring.py::test_growth_score_always_clamped_to_10` (line 149)**
```python
company = make_company(financials=FinancialMetric(growth_rate=10_000.0, employees=1))
```
Fails because `FinancialMetric` has a validator (line 147 of `domain/models.py`) requiring `growth_rate` to be in `[-100, 1000]`. The test intent is to verify the scorer clamps extreme values — the fixture itself is invalid.
**Fix**: Use `growth_rate=999.0` (max valid) or mock the validator.

**2. `tests/unit/test_scoring.py::test_growth_score_never_below_zero` (line 156)**
```python
company = make_company(financials=FinancialMetric(growth_rate=-10_000.0, employees=1))
```
Same cause — `growth_rate=-10_000` is outside `[-100, 1000]`.
**Fix**: Use `growth_rate=-99.0` (min valid) or `growth_rate=-100.0`.

**3. `tests/unit/test_scorers_financial.py::TestFinancialHealthScorer::test_profit_margin_boundaries` (line 178)**
```python
financials = FinancialMetric(profit_margin=margin)  # no revenue or employees
```
Fails because `require_primary_metric` validator rejects a `FinancialMetric` with neither `revenue` nor `employees` (unless `allow_empty_primary=True`).
**Fix**: Pass `employees=1` or `allow_empty_primary=True`.

---

## Acceptance Criteria

- [ ] All 3 tests pass without changing production code
- [ ] The test intent is preserved: clamp tests still verify extreme values are clamped; boundary test still verifies all margin values produce scores in [0, 10]
- [ ] `pytest tests/unit/test_scoring.py tests/unit/test_scorers_financial.py` passes at 0 failures

---

## Tasks

- [ ] `tests/unit/test_scoring.py:151` — change `growth_rate=10_000.0` to `growth_rate=999.0`
- [ ] `tests/unit/test_scoring.py:158` — change `growth_rate=-10_000.0` to `growth_rate=-99.0`
- [ ] `tests/unit/test_scorers_financial.py:182` — add `allow_empty_primary=True` or `employees=1` to the `FinancialMetric` constructor
- [ ] Run `pytest tests/unit/test_scoring.py tests/unit/test_scorers_financial.py -q` — confirm 0 failures

## Key Files

| File | Line | Note |
|------|------|------|
| `tests/unit/test_scoring.py` | 151, 158 | growth_rate out of range |
| `tests/unit/test_scorers_financial.py` | 182 | missing required primary metric |
| `src/solstein/domain/models.py` | 147, 114 | the validators causing the failure (do NOT modify) |
