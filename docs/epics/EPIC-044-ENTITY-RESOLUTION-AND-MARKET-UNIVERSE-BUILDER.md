# EPIC-044: Entity Resolution and Market Universe Builder

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 21-24

---

## Problem Statement

Solstein can enrich companies, but it does not yet build complete market universes with strong entity resolution across aliases, brands, domains, and corporate families.

### Impact
- Duplicate or fragmented company profiles
- Missed competitors, subsidiaries, and product lines
- Weak market-map completeness
- Lower confidence in comparative analytics and sector coverage

---

## Success Criteria

1. ✅ Canonical company identity model supports aliases, domains, brands, and legal entities
2. ✅ Parent/subsidiary and product/company relationships are modeled
3. ✅ Market-universe builder expands from seeds into complete candidate sets
4. ✅ Entity deduplication quality is measurable and reviewable
5. ✅ Discovery pipeline supports sector, geography, and theme-based universes

---

## Stories

### Story 44.1: Canonical Identity Model (13 pts)
**Task:** Define canonical company/entity identity and matching rules

**Acceptance Criteria:**
- [ ] Canonical entity model includes aliases, websites, legal names, and domains
- [ ] Brand/product-to-company links are supported
- [ ] Confidence-scored entity matches are stored
- [ ] Manual override path exists for analyst corrections

### Story 44.2: Corporate Structure Mapping (13 pts)
**Task:** Model parent, subsidiary, investor, partner, and customer relationships

**Acceptance Criteria:**
- [ ] Parent/subsidiary relationships are supported
- [ ] Relationship provenance is stored
- [ ] Time-bounded relationships are supported where possible
- [ ] Corporate family rollups work for scoring and reporting

### Story 44.3: Market Universe Expansion (13 pts)
**Task:** Build market-level company discovery from seed entities and themes

**Acceptance Criteria:**
- [ ] Universe builder can start from a seed company or market theme
- [ ] Competitor, peer, adjacent, and substitute expansion strategies exist
- [ ] Discovery candidates are deduplicated and ranked
- [ ] Coverage metrics are tracked for each universe

### Story 44.4: Candidate Ranking and Review Workflow (8 pts)
**Task:** Add ranking and analyst review for discovered entities

**Acceptance Criteria:**
- [ ] Candidate ranking includes evidence strength and relevance
- [ ] Analysts can accept, reject, or merge candidates
- [ ] Review history is stored
- [ ] False positive rate is measurable

### Story 44.5: Sector and Geography Templates (8 pts)
**Task:** Support market-universe generation by region and sector

**Acceptance Criteria:**
- [ ] Sector taxonomies can seed discovery
- [ ] Geography-aware search and registry expansion are supported
- [ ] Universe templates exist for at least 3 priority sectors
- [ ] Universe completeness summary is available

---

## Definition of Done

- [ ] Canonical entity model is live
- [ ] Duplicate company profiles can be detected and merged safely
- [ ] Market-universe builder produces ranked candidate sets
- [ ] Analyst review flow exists for low-confidence entities
- [ ] Tests cover entity matching, dedupe, and relationship rollups

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Entity ambiguity causes bad merges | High | High | Confidence thresholds and human review |
| Corporate structures change over time | Medium | Medium | Time-bounded relationships |
| Market boundaries are fuzzy | High | Medium | Explicit templates and analyst overrides |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 4 weeks
- **Dependencies:** EPIC-042 and EPIC-043 recommended

---

*Epic created as part of public-web intelligence expansion roadmap*
