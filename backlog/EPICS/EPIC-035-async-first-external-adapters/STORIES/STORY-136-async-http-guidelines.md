# STORY-136: Add Async HTTP Client Guidelines and Linting

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> 12+ files use requests in async context. No guidelines exist for async HTTP.

## Problem Statement

The codebase has no standards for HTTP clients. Developers use requests because it's familiar, even in async code where it doesn't belong. After migrating the existing adapters, new code will still use requests unless there's a standard. The fix is guidelines that mandate httpx for async, document when to use aiohttp (websites with complex JavaScript), and linting that catches requests imports in async files.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | No standard leads to repeated mistakes |
| **Performance** | New blocking code introduced over time |

## Affected Files

| File | Issue |
|------|-------|
| `docs/standards/async-http.md` | Does not exist |

## Architectural Requirements

- Async HTTP standards document: httpx for APIs, aiohttp for complex websites, never requests in async def
- Decision matrix: which client for which use case
- Linting rule: ruff or custom check that flags requests imports in files with async def
- Code review checklist: HTTP client section
- Migration guide: converting requests to httpx
- Examples: good (httpx) and bad (requests in async)

## Acceptance Criteria

- [ ] Standards document committed
- [ ] Linting rule catches requests in async files
- [ ] Code review checklist includes HTTP client check
- [ ] Migration guide with examples

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: Complete standards document
- **Code Review Gate**: New async file with requests import fails CI

## Notes

Prevent future blocking code through standards.
