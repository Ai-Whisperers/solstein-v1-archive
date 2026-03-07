# EPIC-048: Media and Transcript Intelligence

**Status:** 🔴 Not Started  
**Priority:** MEDIUM (P2)  
**Story Points:** 34  
**Sprint Allocation:** 3 sprints  
**Target Date:** Week 31-33

---

## Problem Statement

Important company and market intelligence often appears first in interviews, podcasts, webinars, conference talks, and video content rather than on static pages.

### Impact
- Misses strategy signals, roadmap hints, positioning shifts, and leadership statements
- Underestimates market narratives and competitive messaging
- Loses rich qualitative evidence that could explain quantitative changes

---

## Success Criteria

1. ✅ Public media sources can be discovered and ingested
2. ✅ Transcripts are extracted or collected when available
3. ✅ Speaker, company, and topic attribution are captured
4. ✅ Claims from media content flow through common evidence and contradiction systems
5. ✅ Event and media intelligence can enrich company and market views

---

## Stories

### Story 48.1: Media Source Discovery (8 pts)
**Task:** Discover company-related podcasts, webinars, videos, and event pages

**Acceptance Criteria:**
- [ ] Media discovery supports company, executive, and product queries
- [ ] Event pages, channel pages, and media pages are distinguishable
- [ ] Discovery results can be deduplicated across platforms
- [ ] Media candidates are ranked by relevance and credibility

### Story 48.2: Transcript Acquisition and Parsing (8 pts)
**Task:** Ingest transcripts or transcript-like text from public sources

**Acceptance Criteria:**
- [ ] Transcript text can be captured when publicly available
- [ ] Time-coded transcript metadata is supported when present
- [ ] Transcript segments are stored in a way that supports citations
- [ ] Media source metadata is normalized

### Story 48.3: Speaker and Quote Attribution (8 pts)
**Task:** Attribute claims to speakers, organizations, and event contexts

**Acceptance Criteria:**
- [ ] Speaker identity and role can be stored with claims
- [ ] Quote boundaries are preserved where possible
- [ ] Event context is linked to the source item
- [ ] Ambiguous attribution is flagged for review

### Story 48.4: Event and Narrative Signal Extraction (5 pts)
**Task:** Extract product, strategy, hiring, partnership, and market claims from media

**Acceptance Criteria:**
- [ ] Narrative signals can be classified by topic
- [ ] Company and market claims are separated cleanly
- [ ] Unsupported inferred claims are not promoted as facts
- [ ] Signal extraction quality is measurable

### Story 48.5: Media Provenance and Review (5 pts)
**Task:** Store media-specific provenance and support analyst review for ambiguous claims

**Acceptance Criteria:**
- [ ] Media claims retain source, speaker, and timing provenance
- [ ] Review queue exists for ambiguous speaker or quote attribution
- [ ] Media confidence reflects source and transcript quality
- [ ] Media-derived evidence can appear in reports with citations

---

## Definition of Done

- [ ] Public transcript/media pipeline works for pilot source set
- [ ] Media-derived claims are traceable to source and speaker context
- [ ] Company and market reports can surface media-derived evidence
- [ ] Tests cover parsing, attribution, and provenance storage

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Transcript quality varies widely | High | Medium | Keep source quality flags and review paths |
| Speaker attribution can be wrong | Medium | High | Confidence thresholds and analyst review |
| Media ingestion raises storage costs | Medium | Medium | Store references and processed text selectively |

---

## Resources

- **Developers:** 1 backend engineer
- **Time:** 3 weeks
- **Dependencies:** EPIC-042 and EPIC-043

---

*Epic created as part of public-web intelligence expansion roadmap*
