# EPIC-083: Fix Test Suite (Target 95%+ Pass Rate)

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P5: Quality |
| **Phase** | P5 — Quality & Polish |
| **Created** | 2026-04-01 |

## Context

The test suite currently has ~313 failed + 149 errors (pre-existing baseline). Most failures are due to interface drift, not code bugs. This epic fixes the known failure categories to restore the test suite to a useful signal. These are distinct from the P0 test isolation stories in EPIC-013 which address structural contamination.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-334](STORIES/STORY-334.md) | Fix 23 news_signal_detector tests (interface drift: daily_query_limit → _daily_query_count) | 🔴 READY | Deps: none |
| [STORY-335](STORIES/STORY-335.md) | Fix 15 test_models tests (FinancialMetric validator change) | 🔴 READY | Deps: none |
| [STORY-336](STORIES/STORY-336.md) | Fix 21 test_unified_loader tests (refactored loader interface) | 🔴 READY | Deps: none |
| [STORY-337](STORIES/STORY-337.md) | Fix API router tests (add test auth bypass for 401 failures) | 🔴 READY | Deps: none |
| [STORY-338](STORIES/STORY-338.md) | Skip or conditionally run 210 database-dependent tests (mark with @pytest.mark.db) | 🔴 READY | Deps: none |
| [STORY-339](STORIES/STORY-339.md) | Update golden dataset expected ranges to match current scoring engine output | 🔴 READY | Deps: STORY-302 |

## Success Criteria

- Test suite passes at 95%+ rate excluding `@pytest.mark.db` tests
- All 23 news_signal_detector tests pass
- All 15 test_models tests pass
- All 21 test_unified_loader tests pass
- Database-dependent tests marked and excluded from default run

## Dependencies

- STORY-302 (scoring formula update) for [STORY-339](STORIES/STORY-339.md)
