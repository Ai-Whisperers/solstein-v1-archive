# STORY-314: Deploy SearXNG instance for web search

| Field | Value |
|-------|-------|
| **Epic** | EPIC-078 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Deploy a SearXNG instance for use by the web search enrichment adapter. SearXNG is already present in docker-compose — this story deploys and verifies it.

## Acceptance Criteria

- [ ] SearXNG instance running and responding to search queries
- [ ] JSON API endpoint (`/search?format=json`) returns results
- [ ] SearXNG URL configured in `.env` as `SEARXNG_URL`
- [ ] Test search for "Volue energy software" returns relevant results
