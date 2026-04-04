# STORY-333: Merge static catalog + web discovery + LLM discovery with deduplication

| Field | Value |
|-------|-------|
| **Epic** | EPIC-082 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | ⏳ BLOCKED |
| **Dependencies** | STORY-331, STORY-332 |

## Description

Merge the three discovery sources — static market catalog, SearXNG web discovery, and LLM-powered identification — into a single deduplicated company list for the pipeline.

## Acceptance Criteria

- [ ] Deduplication by normalized company name (case-insensitive, common suffix removal)
- [ ] Source provenance tracked per company (catalog / web / llm)
- [ ] No duplicate companies in merged output
- [ ] Merge result includes companies from all 3 sources
