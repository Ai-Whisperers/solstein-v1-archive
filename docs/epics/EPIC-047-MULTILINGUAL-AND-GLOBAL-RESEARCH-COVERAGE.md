# EPIC-047: Multilingual and Global Research Coverage

**Status:** 🔴 Not Started  
**Priority:** MEDIUM (P2)  
**Story Points:** 34  
**Sprint Allocation:** 3 sprints  
**Target Date:** Week 28-30

---

## Problem Statement

Public-web intelligence is currently biased toward English-language and familiar-source ecosystems. Global market research requires multilingual ingestion and region-aware source strategies.

### Impact
- Non-English markets are under-covered
- Global competitors are missed or mischaracterized
- Coverage quality varies by geography

---

## Success Criteria

1. ✅ Language detection and translation workflow exists for crawled content
2. ✅ Search and source strategies are region-aware
3. ✅ Evidence stores original text plus translated form where needed
4. ✅ Region-specific source adapters are prioritized for target markets
5. ✅ Confidence reflects translation and source-locality risk

---

## Stories

### Story 47.1: Language Detection and Translation Pipeline (8 pts)
**Task:** Detect language and create reliable translated research views

**Acceptance Criteria:**
- [ ] Language detection works on crawled pages and extracted documents
- [ ] Original and translated text can be stored together
- [ ] Translation quality flags are available
- [ ] Translation failures do not block source persistence

### Story 47.2: Region-Aware Search and Discovery (8 pts)
**Task:** Tailor discovery strategies by market and language

**Acceptance Criteria:**
- [ ] Search strategies can vary by target region
- [ ] Locale-aware query generation is supported
- [ ] Regional search results are tagged and ranked separately when needed
- [ ] Discovery evaluation includes region coverage metrics

### Story 47.3: Regional Source Adapter Strategy (8 pts)
**Task:** Add priority non-US/non-UK public sources

**Acceptance Criteria:**
- [ ] Priority source list exists for initial target regions
- [ ] At least one regional source family is integrated per pilot market
- [ ] Source normalization works across regional schemas
- [ ] Regional source limitations are documented

### Story 47.4: Multilingual Claim Provenance (5 pts)
**Task:** Preserve original-language evidence and translated snippets together

**Acceptance Criteria:**
- [ ] Claims link to original-language source text
- [ ] Translated snippets retain source alignment
- [ ] Confidence reflects translation risk when applicable
- [ ] Provenance retrieval can show both forms side by side

### Story 47.5: Global Coverage Metrics (5 pts)
**Task:** Measure coverage gaps by region, language, and market

**Acceptance Criteria:**
- [ ] Coverage metrics are segmented by region and language
- [ ] Gaps can be ranked by business importance
- [ ] Market-level coverage dashboards are supported
- [ ] Metrics distinguish missing sources from missing extraction quality

---

## Definition of Done

- [ ] Multilingual ingestion works for target pilot languages
- [ ] Original and translated evidence are both accessible
- [ ] Region-aware search improves candidate discovery
- [ ] Coverage metrics expose global blind spots
- [ ] Tests cover translation and provenance integrity

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Translation errors distort meaning | Medium | High | Preserve original text and add review flows |
| Regional sources vary widely | High | Medium | Roll out market by market |
| Search quality differs by locale | High | Medium | Use source-specific strategies and evaluation |

---

## Resources

- **Developers:** 1 backend engineer
- **Time:** 3 weeks
- **Dependencies:** EPIC-041, EPIC-042, EPIC-043

---

*Epic created as part of public-web intelligence expansion roadmap*
