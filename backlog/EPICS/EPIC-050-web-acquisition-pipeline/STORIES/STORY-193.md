# STORY-193: Integrate crawl outputs into enrichment orchestrator with provenance

| Field | Value |
|-------|-------|
| **Epic** | EPIC-050 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | STORY-190, STORY-191, STORY-192 |

## Description

Integrate the web acquisition pipeline output (map → crawl → extract) into the enrichment orchestrator. Extracted fields flow through the conflict resolver with full provenance metadata before entering scoring.

## Acceptance Criteria

- [ ] Web acquisition registered as enrichment source in orchestrator
- [ ] All extracted fields include: source_url, crawled_at, confidence, extractor_version
- [ ] Conflict resolver correctly handles web-vs-API field conflicts
- [ ] Provenance stored in `data_source_per_field` per field
- [ ] Integration test: company enriched from web acquisition produces valid EnrichmentResult
