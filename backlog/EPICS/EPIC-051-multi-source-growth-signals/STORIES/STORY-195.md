# STORY-195: Build product and web-momentum extractors from crawl output

| Field | Value |
|-------|-------|
| **Epic** | EPIC-051 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-050 (Web Acquisition Pipeline) |

## Description

Build extractors that detect product release velocity and website activity momentum from web crawl outputs. Signals: changelog entries, press release frequency, blog post cadence, product page updates.

## Acceptance Criteria

- [ ] `ProductMomentumExtractor` extracts: release_count_6m, last_release_date, blog_post_count_6m
- [ ] Sources: changelog pages, press release pages, blog from EPIC-050 crawl output
- [ ] Momentum score: 0-1 scale based on release frequency
- [ ] Works without crawl output (returns `unknown` gracefully)
- [ ] Unit tests with sample HTML fixtures
