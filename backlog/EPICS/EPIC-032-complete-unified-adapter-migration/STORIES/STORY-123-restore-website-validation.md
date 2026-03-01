# STORY-123: Restore Website Adapter Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `website.py` has early validation for missing website URL. `website_unified.py` lacks this validation — proceeds to fetch and fails later.

## Problem Statement

The old website adapter checked if a company had a website URL before attempting to fetch it. The unified adapter skips this check and tries to fetch anyway, resulting in a failed HTTP request to an empty or malformed URL. This is wasted resources and misleading error messages. A simple `if not website_url: return None` was lost in the migration.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Efficiency** | Wasted HTTP calls to empty URLs |
| **Error Quality** | Cryptic failures instead of clear "no website" messages |

## Affected Files

| File | Issue |
|------|-------|
| `data/website_unified.py` | Missing early validation |
| `data/website.py` | Old version with validation |

## Architectural Requirements

- Early validation for missing/empty website URL restored
- Clear error message when company has no website
- No HTTP request attempted for missing URLs
- Old website.py deleted after parity verified

## Acceptance Criteria

- [ ] Empty website URL returns early with clear message
- [ ] No HTTP request for missing URLs
- [ ] website.py deleted

## Definition of Done

- **Tests Required**: Unit test: pass company with no website, verify no HTTP call
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies validation happens before any network call

## Notes

Simple validation lost in migration.
