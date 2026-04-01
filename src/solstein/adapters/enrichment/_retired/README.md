# Retired Enrichment Adapters

## STORY-265: Unified Adapter Retirement

**Retired by**: STORY-265 (EPIC-069: Provider Surface Rationalization)
**Date**: 2026-03-31

These unified adapter files were retired as part of the provider surface
rationalization.  The legacy adapters (e.g. `funding.py`, `linkedin.py`,
`website.py`) are the canonical production implementations.

### Why Retired (Not Deleted)

The unified adapters contain non-trivial logic (1,523 LOC total) that may
be useful as reference if the team decides to rebuild the enrichment layer.
They are kept here for reference only and must NOT be imported from
production code paths.

### Unified Adapters (STORY-265)

| File | LOC | Legacy Canonical |
|------|-----|-----------------|
| `funding_unified.py` | 266 | `../funding.py` |
| `linkedin_unified.py` | 160 | `../linkedin.py` |
| `news_unified.py` | 306 | `../news.py` (also retired) |
| `patents_unified.py` | 202 | `../patents.py` |
| `web_search_unified.py` | 308 | `../web_search_news.py` (also retired) |
| `website_unified.py` | 281 | `../website.py` |

---

## STORY-264: Replaceable Provider Surface Removal

**Retired by**: STORY-264 (EPIC-069: Provider Surface Rationalization)
**Date**: 2026-03-31

These legacy adapters wrapped replaceable third-party services that have
self-hosted or free alternatives already available in the stack.

### Replaceable Provider Adapters (STORY-264)

| File | Provider | Replacement | LOC |
|------|----------|-------------|-----|
| `news.py` | NewsAPI | GDELT (free, unlimited) | 56 |
| `web_search_news.py` | Exa Search | SearXNG (self-hosted) | 48 |

---

## Deletion Trigger

All files in this directory can be deleted once EPIC-070 (Golden Runs)
confirms the canonical runtime produces equivalent results, or when a
rebuild decision is made per STORY-258.
