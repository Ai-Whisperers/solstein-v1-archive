# EPIC-083: Fix Test Suite (Target 95%+ Pass Rate)

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P5 — Quality & Polish |
| **Effort** | M (3–5 days) |
| **Stories** | 6 ([STORY-334](STORIES/STORY-334.md) through [STORY-339](STORIES/STORY-339.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (corrected stale baseline; flagged STORY-337 coordination with EPIC-013) |
| **Dependencies** | [STORY-302](../EPIC-075-fix-scoring-missing-data/STORIES/STORY-302.md) (scoring formula) for STORY-339 |

## Context

The test suite has interface-drift failures — tests written against old APIs that have since been refactored without updating the tests. These are distinct from the P0 structural contamination in EPIC-013 (module-scope auth bypass, DATABASE_URL poisoning). This epic repairs tests that fail due to stale interfaces only.

## Verified Baseline (2026-04-05)

Two independent runs confirmed the actual baseline:

| Metric | Value |
|--------|-------|
| Passed | 3855 |
| Failed | 291 |
| Errors | 237 |
| Total collected | 4383 |
| Local pass rate | ~93% |

All 291 failures and 237 errors are infrastructure-dependent (no local PostgreSQL/Redis). They pass in CI, which spins up postgres:14-alpine. The previous baseline of "~313 failed + 149 errors" in this file was stale — do not use it.

**Safe local baseline command:**
```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q \
  --ignore=tests/unit/test_async_boundary_regressions.py \
  --ignore=tests/unit/test_api_routers_coverage.py \
  --no-header 2>&1 | tail -3
```

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-334](STORIES/STORY-334.md) | Fix 23 news_signal_detector tests (interface drift: `daily_query_limit` → `_daily_query_count`) | 🔴 READY | Independent |
| [STORY-335](STORIES/STORY-335.md) | Fix 15 test_models tests (FinancialMetric validator change) | 🔴 READY | Independent |
| [STORY-336](STORIES/STORY-336.md) | Fix 21 test_unified_loader tests (refactored loader interface) | 🔴 READY | Independent |
| [STORY-337](STORIES/STORY-337.md) | Fix API router test 401 failures: move auth into proper fixture scope | 🔴 READY | ⚠️ Coordinate with EPIC-013 STORY-374 |
| [STORY-338](STORIES/STORY-338.md) | Mark DB-dependent tests `@pytest.mark.db`; exclude from default local run | 🔴 READY | Independent |
| [STORY-339](STORIES/STORY-339.md) | Update golden dataset expected ranges to match current scoring engine output | 🔴 READY | Blocked by STORY-302 |

> ⚠️ **STORY-337 coordination required**: This story fixes 401 failures in API router tests by ensuring auth is set up in fixture scope. EPIC-013 [STORY-374](../EPIC-013-test-suite-integrity/STORIES/STORY-374.md) modifies the same file (`test_api_routers_coverage.py`) by removing module-scope auth bypass. **Land STORY-374 first**, then reassess what STORY-337 still needs — the scope may shrink or be absorbed.

## Success Criteria

- Test suite local pass rate ≥ 95% excluding `@pytest.mark.db` tests
- All 23 news_signal_detector tests pass
- All 15 test_models tests pass
- All 21 test_unified_loader tests pass
- DB-dependent tests marked and excluded from default `pytest` invocation
- Overall passing count rises from 3855 → ≥ 3920

## Definition of Done

- [ ] [STORY-334](STORIES/STORY-334.md): `pytest -k "news_signal"` → 0 failures
- [ ] [STORY-335](STORIES/STORY-335.md): `pytest -k "test_models"` → 0 failures
- [ ] [STORY-336](STORIES/STORY-336.md): `pytest -k "unified_loader"` → 0 failures
- [ ] [STORY-337](STORIES/STORY-337.md): API 401 failures resolved; coordinated with STORY-374
- [ ] [STORY-338](STORIES/STORY-338.md): `pytest -m "not db"` produces no DB-connection errors locally
- [ ] [STORY-339](STORIES/STORY-339.md): Golden dataset assertions match current scoring output
- [ ] Overall passing count ≥ 3920 on local suite
- [ ] No test deleted — only fixed or marked
