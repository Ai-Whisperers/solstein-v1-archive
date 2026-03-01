# STORY-122: Restore Funding Adapter Wrapper

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `funding.py` has `news_api_key` parameter and `AdditionalDataSources` wrapper. `funding_unified.py` lacks both.

## Problem Statement

The funding unified adapter was written to use the new base connector pattern, but in the process it lost the ability to accept a news API key for cross-referencing and lost the wrapper that handled Crunchbase API errors gracefully. The old adapter could enrich funding data with news signals. The unified adapter cannot. This is a feature regression masquerading as a refactor.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Data Quality** | Lost news cross-reference capability |
| **Reliability** | Unhandled Crunchbase errors |

## Affected Files

| File | Issue |
|------|-------|
| `data/funding_unified.py` | Missing wrapper and news_api_key param |
| `data/funding.py` | Old version with full functionality |

## Architectural Requirements

- `news_api_key` parameter restored to funding_unified.py
- `AdditionalDataSources` wrapper or equivalent error handling added
- Crunchbase API error handling (401, 403, 429, 500) with retry
- Old funding.py deleted after parity verified
- Cross-reference with news signals functionality restored

## Acceptance Criteria

- [ ] funding_unified.py accepts news_api_key parameter
- [ ] Crunchbase 429 triggers retry with backoff
- [ ] News cross-reference works (integration test)
- [ ] funding.py deleted

## Definition of Done

- **Tests Required**: Integration test: trigger funding fetch with news cross-reference
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies news_api_key flows through correctly

## Notes

Feature regression from incomplete migration.
