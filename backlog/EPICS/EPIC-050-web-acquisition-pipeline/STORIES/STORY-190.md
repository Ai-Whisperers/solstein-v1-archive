# STORY-190: Implement domain mapping stage for company URL discovery

| Field | Value |
|-------|-------|
| **Epic** | EPIC-050 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-028 (External Service Consolidation), EPIC-035 (Async-First External Adapters) |

## Description

Implement the Map stage of the web acquisition pipeline. Given a company website URL, discover all relevant subpages (about, team, products, investors, press) by crawling the sitemap and navigation structure. Output: list of relevant URLs with page type classification.

## Acceptance Criteria

- [ ] `DomainMapper` class implemented in `src/solstein/data/web_research_pipeline.py`
- [ ] Discovers sitemap.xml and robots.txt for URL hints
- [ ] Classifies pages: about, team, product, funding, careers, press
- [ ] Rate-limited to 1 request/second per domain
- [ ] Returns `MappedDomain` with discovered URLs and page type tags
- [ ] Unit tests with mocked HTTP responses
