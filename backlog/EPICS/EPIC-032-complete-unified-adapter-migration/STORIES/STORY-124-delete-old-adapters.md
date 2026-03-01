# STORY-124: Delete Old Adapter Versions After Parity

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-032: Complete Unified Adapter Migration |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-121, STORY-122, STORY-123 |

## The Audit Verdict

> Old adapters (news.py, funding.py, website.py, linkedin.py, patents.py, web_search_news.py) still exist alongside unified versions.

## Problem Statement

The codebase has 12 adapter files where 6 would suffice. Old and unified versions coexist, creating import confusion and maintenance burden. Developers don't know which to use. Bug fixes applied to one don't apply to the other. The "unified" migration was never completed because the old files were never deleted. This is technical debt that compounds with every change.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 2x adapter files to maintain |
| **Developer Experience** | Confusion about canonical versions |
| **Reliability** | Fixes applied to wrong version |

## Affected Files

| File | Issue |
|------|-------|
| `data/news.py` | Old version to delete |
| `data/funding.py` | Old version to delete |
| `data/website.py` | Old version to delete |
| `data/linkedin.py` | Old version to delete |
| `data/patents.py` | Old version to delete |
| `data/web_search_news.py` | Old version to delete |

## Architectural Requirements

- All old adapter files deleted after STORY-121, 122, 123 verify unified parity
- Imports across codebase updated to use unified versions only
- Import aliases removed (no `from data.news import X as NewsX`)
- A migration guide documenting the adapter consolidation for developers
- grep for old adapter filenames returns zero results

## Acceptance Criteria

- [ ] news.py, funding.py, website.py, linkedin.py, patents.py, web_search_news.py do not exist
- [ ] All imports use unified versions
- [ ] `grep -r "from data.news import\|from data.funding import" src/` returns empty
- [ ] Migration guide added to docs/

## Definition of Done

- **Tests Required**: `find src -name "*.py" | xargs grep -l "news.py\|funding.py"` returns only unified versions
- **Documentation Required**: Migration guide
- **Code Review Gate**: Reviewer verifies no old adapter imports remain

## Notes

Complete the migration by deleting the old versions.
