# STORY-331: Implement SearXNG-based competitor discovery adapter

| Field | Value |
|-------|-------|
| **Epic** | EPIC-082 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | ⏳ BLOCKED |
| **Dependencies** | STORY-314 (SearXNG deployed) |

## Description

Implement a competitor discovery adapter that uses SearXNG to search for companies in the target market segment. Queries like "Dutch energy software companies" and "European grid management software" to discover companies not in the static catalog.

## Acceptance Criteria

- [ ] Discovery adapter finds 5+ new companies not in static catalog
- [ ] Each discovered company has: name, website_url, description snippet
- [ ] Adapter respects rate limits (max 10 queries per run)
- [ ] Results deduplicated against existing catalog entries
