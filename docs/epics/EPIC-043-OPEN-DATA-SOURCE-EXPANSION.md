# EPIC-043: Open-Data Source Expansion

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 21-24

---

## Problem Statement

Solstein has several useful public data connectors, but it still misses many high-value open-data ecosystems needed for complete company and market intelligence.

### Impact
- Important company and market signals remain undiscovered
- Coverage is uneven by sector and geography
- Market maps lack procurement, product, regulatory, and sentiment evidence
- Research quality depends too heavily on generic web search

---

## Success Criteria

1. ✅ Official registry coverage expanded for company, ownership, and filing data
2. ✅ Product/developer, review, hiring, and market-signal sources added
3. ✅ Historical/open-web sources added for deleted or changed content
4. ✅ New sources flow through the same evidence and contradiction framework
5. ✅ Source ROI is measurable by coverage and quality uplift

---

## Stories

### Story 43.1: Official Registries and Filings (13 pts)
**Task:** Expand official public-record connectors

**Acceptance Criteria:**
- [ ] Registry adapters added for target jurisdictions
- [ ] Beneficial ownership and filing metadata are supported where public
- [ ] Filing-derived facts use the common claim contract
- [ ] Registry data is normalized by entity and date

### Story 43.2: Product, Developer, and App Ecosystems (13 pts)
**Task:** Add product and engineering footprint sources

**Acceptance Criteria:**
- [ ] Package registry signals supported
- [ ] App store signals supported
- [ ] Release/changelog/docs signals supported
- [ ] Technology adoption evidence maps to company entities

### Story 43.3: Reviews, Hiring, and Demand Signals (8 pts)
**Task:** Add public sentiment and talent-market sources

**Acceptance Criteria:**
- [ ] Review ecosystem sources prioritized
- [ ] Job-board ingestion strategy defined and implemented for selected sources
- [ ] Hiring signals are normalized by role, location, and skill
- [ ] Review and hiring signals are time-aware

### Story 43.4: Procurement, Tenders, and Public Contracts (13 pts)
**Task:** Capture government and public-sector commercial signals

**Acceptance Criteria:**
- [ ] Tender/contract source adapters implemented for target markets
- [ ] Buyer, vendor, value, and contract scope are extracted when public
- [ ] Procurement events can enrich market opportunity and traction models
- [ ] Duplicate notices are clustered across portals

### Story 43.5: Historical Web and Archive Recovery (8 pts)
**Task:** Add archived web and historical snapshot sources

**Acceptance Criteria:**
- [ ] Historical snapshot retrieval supported for target URLs/domains
- [ ] Archived content can be compared with current content
- [ ] Deleted/changed pages can still contribute claims with time bounds
- [ ] Archive-derived evidence is clearly labeled

---

## Definition of Done

- [ ] At least 8 new public source families are integrated or implementation-ready
- [ ] New sources write into the common evidence model
- [ ] Coverage metrics show uplift by sector or geography
- [ ] Source quality and rate-limit constraints are documented
- [ ] Tests cover normalization and deduplication for new adapters

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Source schemas vary wildly | High | Medium | Use adapter normalization contracts |
| Coverage differs by country | High | Medium | Roll out by priority markets |
| Public sources change frequently | Medium | Medium | Version adapters and add contract tests |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 4 weeks
- **Dependencies:** EPIC-042 strongly recommended

---

*Epic created as part of public-web intelligence expansion roadmap*
