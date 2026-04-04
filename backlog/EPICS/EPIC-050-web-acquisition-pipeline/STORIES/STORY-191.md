# STORY-191: Implement async crawl executor with queue and polling

| Field | Value |
|-------|-------|
| **Epic** | EPIC-050 |
| **Priority** | P1 |
| **Size** | L |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-028, EPIC-035 |

## Description

Implement the Crawl stage: async job executor that crawls URLs from the Map stage output. Uses Celery for async dispatch, polling for completion, and bounded retries with exponential backoff.

## Acceptance Criteria

- [ ] `AsyncCrawlExecutor` dispatches crawl jobs via Celery
- [ ] Polls for job completion with configurable timeout
- [ ] Exponential backoff on failures: 1s, 2s, 4s, 8s, max 60s
- [ ] Circuit breaker trips after 5 consecutive domain failures
- [ ] Crawl result stored with provenance: source_url, crawled_at, status
- [ ] Integration tests against local HTTP server
