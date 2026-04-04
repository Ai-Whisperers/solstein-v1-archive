# EPIC-082: Live Web Discovery

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P4: End-to-End |
| **Phase** | P4 — End-to-End Pipeline Execution |
| **Created** | 2026-04-01 |

## Context

The pipeline currently discovers only companies from the static market catalog. Live web discovery via SearXNG + LLM would allow the platform to find new competitors that aren't in the catalog. This is a capability extension that requires SearXNG (STORY-314) and LLM (STORY-321) to be deployed.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-331](STORIES/STORY-331.md) | Implement SearXNG-based competitor discovery adapter | ⏳ BLOCKED | Deps: STORY-314 |
| [STORY-332](STORIES/STORY-332.md) | Add LLM-powered competitor identification from web search results | ⏳ BLOCKED | Deps: STORY-321, [STORY-331](STORIES/STORY-331.md) |
| [STORY-333](STORIES/STORY-333.md) | Merge static catalog + web discovery + LLM discovery with deduplication | ⏳ BLOCKED | Deps: [STORY-331](STORIES/STORY-331.md), [STORY-332](STORIES/STORY-332.md) |

## Success Criteria

- SearXNG discovery adapter finds 5+ new companies not in static catalog
- LLM classifier correctly identifies energy software competitors from raw search results
- Deduplication correctly merges static + web + LLM discovery sources
- No duplicate companies in final merged set

## Dependencies

- STORY-314 (SearXNG deployed)
- STORY-321 (LLM provider configured)
- [STORY-331](STORIES/STORY-331.md) → [STORY-332](STORIES/STORY-332.md) → [STORY-333](STORIES/STORY-333.md) (sequential)
