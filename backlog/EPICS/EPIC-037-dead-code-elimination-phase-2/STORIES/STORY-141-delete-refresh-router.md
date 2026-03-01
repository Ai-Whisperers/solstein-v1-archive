# STORY-141: Delete Disconnected Refresh Router

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-037: Dead Code Elimination Phase 2 |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> api/routes/refresh.py — defines APIRouter with 4 endpoints but NEVER included in main.py. Completely inaccessible.

## Problem Statement

There's a router with 200+ lines of code for refreshing data sources. It has endpoints for triggering refreshes, checking status, webhooks, and listing sources. It's completely inaccessible because main.py never includes it. This isn't dead code in the traditional sense — it's code that looks alive, has tests probably, but is unreachable from any HTTP request. It's been sitting there, maintained (probably), tested (maybe), and serving zero production traffic.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 200+ lines of unreachable code |
| **Confusion** | Developers think refresh functionality exists |
| **Test Time** | Tests run for unused code |

## Affected Files

| File | Issue |
|------|-------|
| `api/routes/refresh.py` | Disconnected router |

## Architectural Requirements

- Verify refresh.py is truly unreachable (confirm not in main.py, not imported elsewhere)
- Check if any tests depend on refresh.py (move to archive if historical value)
- Delete refresh.py
- Delete associated tests if they only test refresh.py
- Update documentation removing references to refresh endpoints
- If refresh functionality is needed, create new story to implement properly (don't resurrect dead code)

## Acceptance Criteria

- [ ] refresh.py deleted
- [ ] main.py still starts without errors
- [ ] All tests pass (or refresh-specific tests removed)
- [ ] No references to refresh endpoints in docs

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: None
- **Code Review Gate**: grep for "refresh" in api/routes/ returns nothing

## Notes

Unreachable code that looks alive.
