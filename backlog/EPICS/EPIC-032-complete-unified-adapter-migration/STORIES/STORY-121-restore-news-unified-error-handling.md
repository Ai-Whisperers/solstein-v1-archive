# STORY-121: Restore Error Handling in news_unified.py

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> Forensic audit found `news.py` (old) has `AdditionalDataSources` wrapper with error handling and retry. `news_unified.py` (new) lacks this wrapper — errors pass through unhandled.

## Problem Statement

The "unified" news adapter is a regression. The old version had a wrapper that caught API errors, applied retry logic, and transformed responses. The unified version assumes the base connector handles everything — it doesn't. When NewsAPI returns a 429 or 500, the unified adapter propagates the raw exception instead of the structured error the old version would have caught. This is not a migration; it's a partial rewrite that lost functionality.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Unhandled API errors crash the research pipeline |
| **Maintainability** | Two versions with different error semantics |

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | Missing error handling wrapper |
| `data/news.py` | Old version with proper handling |

## Architectural Requirements

- Error handling wrapper restored to news_unified.py matching news.py behavior
- Retry logic for 429/500/503 status codes with exponential backoff
- Structured error transformation (API error → domain error)
- Old news.py deleted after parity verified
- Unit tests for error scenarios (mock 429, 500, timeout)

## Acceptance Criteria

- [ ] news_unified.py handles NewsAPI 429 with retry
- [ ] news_unified.py handles NewsAPI 500 with retry
- [ ] Error messages match old adapter format
- [ ] news.py deleted
- [ ] All news-related tests pass

## Definition of Done

- **Tests Required**: Integration test: mock NewsAPI 429, verify 3 retries with backoff
- **Documentation Required**: Migration notes
- **Code Review Gate**: Reviewer compares error handling line-by-line with old adapter

## Notes

The unified adapter is technically a regression.
