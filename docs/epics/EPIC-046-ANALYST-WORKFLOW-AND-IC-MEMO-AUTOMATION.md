# EPIC-046: Analyst Workflow and IC Memo Automation

**Status:** 🔴 Not Started  
**Priority:** MEDIUM (P2)  
**Story Points:** 34  
**Sprint Allocation:** 3 sprints  
**Target Date:** Week 28-30

---

## Problem Statement

Research quality improves only when analysts can inspect evidence, review contradictions, and turn findings into investment-grade outputs quickly.

### Impact
- High-value research remains difficult to validate and operationalize
- Analysts cannot efficiently review weak or contradictory evidence
- Exported outputs are less useful for investment committee workflows

---

## Success Criteria

1. ✅ Evidence-backed drill-down UX exists for important facts and scores
2. ✅ Manual review queues exist for contradictions and low-confidence claims
3. ✅ Analyst feedback can improve extraction and ranking quality
4. ✅ IC-style memo outputs are generated with citations and change summaries
5. ✅ Completeness, freshness, and confidence are visible to users

---

## Stories

### Story 46.1: Evidence Explorer (8 pts)
**Task:** Build retrieval surfaces for claims, sources, and score explanations

**Acceptance Criteria:**
- [ ] Analysts can drill from score to signal to claim to source
- [ ] Source snippets and timestamps are visible
- [ ] Evidence can be filtered by field, confidence, and freshness
- [ ] Retrieval latency is acceptable for analyst workflows

### Story 46.2: Review Queues and Resolution Tools (8 pts)
**Task:** Add workflows for claim validation, contradiction resolution, and merges

**Acceptance Criteria:**
- [ ] Low-confidence and contradictory items are queued for review
- [ ] Reviewers can accept, reject, merge, or defer claims
- [ ] Review actions are fully auditable
- [ ] Queue prioritization reflects business impact

### Story 46.3: Feedback Loop (5 pts)
**Task:** Capture analyst corrections and route them back into ranking/extraction systems

**Acceptance Criteria:**
- [ ] Feedback can be attached to claims, matches, and rankings
- [ ] Corrections are stored with actor and timestamp
- [ ] Reusable feedback categories are defined
- [ ] Downstream systems can consume approved feedback

### Story 46.4: IC Memo and Research Exports (8 pts)
**Task:** Generate investment-ready memos, evidence appendices, and change summaries

**Acceptance Criteria:**
- [ ] Memo templates support company and market cases
- [ ] Every major assertion can include citations
- [ ] Exports support human-readable and machine-readable formats
- [ ] Memo generation respects completeness/confidence thresholds

### Story 46.5: Coverage and Blind-Spot Indicators (5 pts)
**Task:** Show users where research is complete and where it is weak

**Acceptance Criteria:**
- [ ] Coverage indicators exist by topic and source family
- [ ] Blind spots are surfaced explicitly in outputs
- [ ] Missing-data severity is ranked
- [ ] Users can navigate from gaps to recommended next research actions

---

## Definition of Done

- [ ] Analysts can review and resolve weak evidence cases
- [ ] Evidence-backed score explanations are accessible
- [ ] IC-style exports include citations
- [ ] Feedback is captured with auditability
- [ ] Tests cover workflow permissions and export generation

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| UX scope expands too far | Medium | Medium | Focus on highest-value analyst flows first |
| Memo generation overstates evidence | Medium | High | Enforce citation and completeness checks |
| Feedback loops are ignored | Medium | Medium | Keep reviewer actions lightweight |

---

## Resources

- **Developers:** 1 backend + 1 full-stack engineer
- **Time:** 3 weeks
- **Dependencies:** EPIC-042 and EPIC-045

---

*Epic created as part of public-web intelligence expansion roadmap*
