# STORY-291: Create arXiv/patent enrichment adapter (R&D and innovation signals)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Create an enrichment adapter that searches arXiv for academic publications and USPTO for patent filings associated with a company. Produces R&D activity signals and innovation indicators.

## Acceptance Criteria

- [ ] Adapter implements `EnrichmentAdapter` interface
- [ ] Searches arXiv for company name in author affiliations
- [ ] Searches USPTO PatentsView API for patent assignee
- [ ] Extracts: publication_count, patent_count, research_topics
- [ ] Unit tests with mocked arXiv and USPTO responses
