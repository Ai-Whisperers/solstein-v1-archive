# EPIC-082: Live Web Discovery

| Field | Value |
|-------|-------|
| **Status** | ⏳ Blocked |
| **Priority** | P1 |
| **Phase** | P4 — End-to-End Pipeline Execution |
| **Effort** | M (3–5 days) |
| **Stories** | 3 ([STORY-331](STORIES/STORY-331.md) through [STORY-333](STORIES/STORY-333.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, explicit BLOCKED state, DoD) |

## Context

The pipeline currently discovers only companies from the static market catalog. Live web discovery via SearXNG + LLM would allow the platform to find new competitors that aren't in the catalog. This is a capability extension that requires SearXNG (STORY-314) and LLM (STORY-321) to be deployed.

> ⚠️ **All stories BLOCKED** until:
> - STORY-314 ([EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md)) — SearXNG deployed
> - STORY-321 ([EPIC-080](../EPIC-080-configure-llm-providers/README.md)) — LLM provider configured

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

## Definition of Done

- [ ] [STORY-331](STORIES/STORY-331.md): SearXNG adapter returns ≥ 5 companies for Dutch Energy query
- [ ] [STORY-332](STORIES/STORY-332.md): LLM classifier correctly labels test cases as competitor/non-competitor
- [ ] [STORY-333](STORIES/STORY-333.md): merged company list has no duplicates (by name + domain)
- [ ] `pytest tests/unit/ -k "discovery"` passes

## Dependencies

- STORY-314 ([EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md)) — SearXNG deployed
- STORY-321 ([EPIC-080](../EPIC-080-configure-llm-providers/README.md)) — LLM provider configured
- [STORY-331](STORIES/STORY-331.md) → [STORY-332](STORIES/STORY-332.md) → [STORY-333](STORIES/STORY-333.md) (sequential)
