# STORY-287: Create SearXNG-based web search enrichment adapter

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None (SearXNG in docker-compose) |

## Description

Create a new enrichment adapter that uses SearXNG to scrape company websites and news articles. Produces: company description, recent news, technology mentions, partnership announcements.

## Acceptance Criteria

- [ ] Adapter implements `EnrichmentAdapter` interface
- [ ] Returns structured data: description, news_items, technology_mentions
- [ ] Handles SearXNG unavailability gracefully (returns empty result)
- [ ] Unit tests with mocked SearXNG responses
- [ ] Integration test against local SearXNG instance
