# EPIC-041: Deep Web Crawling and Document Ingestion

**Status:** 🔴 Not Started  
**Priority:** CRITICAL (P0)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 17-20

---

## Problem Statement

Solstein can search the web and fetch selected pages, but it does not yet crawl company websites and public web assets deeply enough to support complete company and market research.

### Impact
- Misses product, pricing, docs, careers, investor, compliance, and changelog pages
- Over-indexes on a few search results instead of the full public evidence surface
- Cannot parse PDFs, slide decks, filings, or other long-form documents reliably
- Produces incomplete market maps because source acquisition is shallow

---

## Success Criteria

1. ✅ Robots-aware crawl engine with rate limiting and domain policies
2. ✅ Sitemap discovery and crawl frontier management for company domains
3. ✅ JS-rendered page support for modern websites
4. ✅ PDF/document ingestion with extracted text and metadata
5. ✅ Page-type classification for pricing, docs, careers, investor, blog, and product pages
6. ✅ Crawl snapshots stored with URL, timestamp, content hash, and extraction metadata

---

## Technical Analysis

### Current State
- Search-driven acquisition exists
- Light website scraping exists
- Research persistence exists
- Deep crawl orchestration is missing
- Document extraction is incomplete

### Core Gaps
1. No sitemap-first crawl strategy
2. No structured crawl frontier or revisit policy
3. No browser rendering for JS-heavy sites
4. No first-class PDF/deck/doc ingestion pipeline
5. No site-wide page classification or section-aware extraction

---

## Stories

### Story 41.1: Crawl Policy and Frontier Engine (13 pts)
**Task:** Build a crawl scheduler with robots, rate limits, and per-domain policies

**Acceptance Criteria:**
- [ ] robots.txt is respected
- [ ] Crawl concurrency is configurable per domain
- [ ] Frontier supports depth, breadth, and priority policies
- [ ] Duplicate URLs are canonicalized and deduplicated
- [ ] Crawl metadata is persisted

### Story 41.2: Sitemap and URL Discovery (8 pts)
**Task:** Discover and prioritize important public pages from company domains

**Acceptance Criteria:**
- [ ] XML sitemap and sitemap index discovery works
- [ ] Common high-value paths are seeded automatically
- [ ] Internal link expansion is supported
- [ ] Canonical and alternate URLs are captured

### Story 41.3: Browser Rendering and Dynamic Sites (13 pts)
**Task:** Add JS-rendered crawling for SPA and dynamic websites

**Acceptance Criteria:**
- [ ] Browser-based rendering supported for selected domains
- [ ] DOM stabilization and wait conditions are configurable
- [ ] Rendered HTML is stored separately from raw HTML
- [ ] Rendering fallback policy is implemented

### Story 41.4: Document and Asset Ingestion (13 pts)
**Task:** Ingest PDFs, decks, whitepapers, filings, and downloadable assets

**Acceptance Criteria:**
- [ ] PDFs are parsed into text plus document metadata
- [ ] Title, author, dates, and section structure are extracted when possible
- [ ] Downloaded assets are linked to source pages
- [ ] OCR fallback is defined for scanned documents

### Story 41.5: Page Classification and Storage (8 pts)
**Task:** Classify crawled pages by business intent and store normalized snapshots

**Acceptance Criteria:**
- [ ] Pages are labeled by type (pricing, docs, careers, blog, investor, etc.)
- [ ] HTML/text snapshots are versioned with content hashes
- [ ] Boilerplate removal is applied before downstream extraction
- [ ] Snapshot storage supports later diffing and retrieval

---

## Definition of Done

- [ ] Full crawl pipeline works for at least 20 representative company websites
- [ ] Crawl metadata is persisted and queryable
- [ ] PDFs and public documents are extracted successfully
- [ ] Rendering fallback works on dynamic sites
- [ ] Unit and integration tests cover crawl policy and extraction basics
- [ ] Documentation includes crawl safety and compliance guidance

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sites block scraping | High | Medium | Respect robots, rate limits, browser fallback |
| JS rendering is expensive | Medium | High | Domain-level rendering policy and caching |
| Document parsing quality varies | Medium | Medium | Metadata validation and OCR fallback |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 4 weeks
- **Dependencies:** EPIC-042 recommended in parallel for evidence storage

---

*Epic created as part of public-web intelligence expansion roadmap*
