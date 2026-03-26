# Scoring Failure Mode Audit — 2026-03-26

**Issue addressed:** `ISSUE-04`

**Bug class:** Sub-scorer exceptions were converted into plausible-looking fallback scores, allowing the pipeline to continue with corrupted business metrics instead of surfacing a real failure.

---

## Fix Applied

**Primary file:** `src/solstein/analytics/scoring.py`

`GrowthScorer.calculate_scores()` no longer degrades failed components to configured base scores.

New behavior:

- clears previously materialized score fields at the start of scoring
- runs the three sub-scorers independently
- collects component failures into a structured error map
- records `profile.scoring_breakdown = {"status": "failed", "errors": ...}`
- raises `ScoringError` if any component fails

This prevents a company from being emitted with synthetic fallback component scores and a derived composite/classification that look legitimate.

---

## Masking Sites Tightened

**Files:**

- `src/solstein/cli.py`
- `src/solstein/api/routers/scoring.py`

Changes:

- CLI `score` no longer coerces missing scores to `0.0`
- scoring API route now rejects a missing `growth_score` explicitly instead of silently defaulting it to `0.0`

---

## Regression Coverage Added

**Files:**

- `tests/unit/test_scoring.py`
- `tests/unit/test_analytics_scoring_coverage.py`
- `tests/unit/test_cli.py`

Coverage added for:

- sub-scorer exception raises `ScoringError`
- failed scoring leaves score fields unset and marks breakdown as failed
- CLI aborts on scoring failure instead of printing `0.0/10`

---

## Verification

Commands run:

```bash
uv run python -m py_compile \
  src/solstein/analytics/scoring.py \
  src/solstein/cli.py \
  src/solstein/api/routers/scoring.py \
  tests/unit/test_scoring.py \
  tests/unit/test_analytics_scoring_coverage.py \
  tests/unit/test_cli.py

DATABASE__URL=postgresql+asyncpg://user:pass@localhost/test \
SECURITY__SECRET_KEY=test-secret \
GITHUB_TOKEN=test-token \
uv run pytest \
  tests/unit/test_scoring.py::test_calculate_growth_score_phoenix \
  tests/unit/test_scoring.py::test_calculate_scores_raises_on_subscorer_exception \
  tests/unit/test_analytics_scoring_coverage.py::test_growth_scorer_raises_when_subscorer_fails \
  tests/unit/test_cli.py::test_cli_score \
  tests/unit/test_cli.py::test_cli_score_aborts_on_scoring_failure -q
```

Result:

- `5 passed`

---

## Residual Note

The broader scoring suite still contains stale calibration/expectation tests unrelated to this failure-mode fix. Those need separate reconciliation before the scoring package can be used as a strong release gate.
