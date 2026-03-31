# Retired Unified Adapters

**Retired by**: STORY-265 (EPIC-069: Provider Surface Rationalization)
**Date**: 2026-03-31

These unified adapter files were retired as part of the provider surface
rationalization.  The legacy adapters (e.g. `funding.py`, `news.py`,
`website.py`) are the canonical production implementations.

## Why Retired (Not Deleted)

The unified adapters contain non-trivial logic (1,523 LOC total) that may
be useful as reference if the team decides to rebuild the enrichment layer.
They are kept here for reference only and must NOT be imported from
production code paths.

## Files

| File | LOC | Legacy Canonical |
|------|-----|-----------------|
| `funding_unified.py` | 266 | `../funding.py` |
| `linkedin_unified.py` | 160 | `../linkedin.py` |
| `news_unified.py` | 306 | `../news.py` |
| `patents_unified.py` | 202 | `../patents.py` |
| `web_search_unified.py` | 308 | No legacy pair (web_search_news.py) |
| `website_unified.py` | 281 | `../website.py` |

## Deletion Trigger

These files can be deleted once EPIC-070 (Golden Runs) confirms the legacy
runtime is sufficient, or when a rebuild decision is made per STORY-258.
