# STORY-334: Fix 23 news_signal_detector tests (interface drift)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-083 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Fix 23 failing tests in `test_news_signal_detector.py` caused by interface drift: attribute `daily_query_limit` was renamed to `_daily_query_count`. Update test assertions to use the new attribute name.

## Acceptance Criteria

- [ ] All 23 news_signal_detector tests pass
- [ ] No production code changes (tests only)
- [ ] No new test failures introduced
