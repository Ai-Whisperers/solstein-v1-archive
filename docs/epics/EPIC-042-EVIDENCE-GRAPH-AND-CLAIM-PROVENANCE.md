# EPIC-042: Evidence Graph and Claim Provenance

**Status:** 🔴 Not Started  
**Priority:** CRITICAL (P0)  
**Story Points:** 55  
**Sprint Allocation:** 4 sprints  
**Target Date:** Week 17-20

---

## Problem Statement

Solstein already stores sources, evidence readiness, and contradictions, but it still lacks a strict evidence contract that makes every fact, metric, and score fully auditable.

### Impact
- Hard to prove why a score exists
- High-risk facts cannot be traced to exact snippets quickly
- Contradictions are harder to resolve at claim level
- Analyst trust is limited when outputs are summarized but not inspectable

---

## Success Criteria

1. ✅ Every extracted fact maps to a claim with URL, snippet, timestamp, and extraction method
2. ✅ Claims roll up into metrics, signals, and scores with traceability
3. ✅ Contradictions are tracked at claim level, not just record level
4. ✅ Confidence is decomposed by source quality, agreement, freshness, and extraction quality
5. ✅ Analyst-facing provenance retrieval is supported by API/export layers

---

## Technical Analysis

### Current State
- Source document persistence exists
- Evidence readiness exists
- Contradiction tracking exists
- Claim ledger is missing
- Score traceability is incomplete

### Core Gaps
1. No first-class claim object for extracted statements
2. No mandatory snippet/span storage for important facts
3. No uniform evidence-to-score lineage
4. No completeness score by research domain
5. No analyst-ready provenance explorer

---

## Stories

### Story 42.1: Claim Data Model (13 pts)
**Task:** Introduce claim-level persistence and lineage contracts

**Acceptance Criteria:**
- [ ] Claim model includes entity, field, value, unit, source URL, snippet, timestamp, and method
- [ ] Claims can link to source documents and crawl snapshots
- [ ] Claims support status transitions (accepted, conflicting, stale, rejected)
- [ ] Claim schema is enforced in extraction pipelines

### Story 42.2: Evidence Lineage to Metrics and Scores (13 pts)
**Task:** Connect claims to metrics, signals, and scoring outputs

**Acceptance Criteria:**
- [ ] Metrics reference supporting claims
- [ ] Signals reference contributing metrics/claims
- [ ] Scores can be explained with underlying evidence lineage
- [ ] High-impact fields require minimum evidence thresholds

### Story 42.3: Confidence Decomposition (8 pts)
**Task:** Break confidence into explicit components

**Acceptance Criteria:**
- [ ] Source credibility score exists
- [ ] Agreement/disagreement score exists
- [ ] Freshness score exists
- [ ] Extraction-quality score exists
- [ ] Composite confidence is explainable

### Story 42.4: Contradiction Resolution Workflow (13 pts)
**Task:** Upgrade contradiction handling to claim-level resolution

**Acceptance Criteria:**
- [ ] Conflicting claims are grouped by entity/field/timeframe
- [ ] Resolution strategy is recorded
- [ ] Analyst review queue exists for unresolved contradictions
- [ ] Resolved contradictions preserve audit history

### Story 42.5: Provenance Retrieval UX/API (8 pts)
**Task:** Expose evidence retrieval for downstream APIs and exports

**Acceptance Criteria:**
- [ ] API can return score explanations with citations
- [ ] Exports can include evidence appendix or citation links
- [ ] Completeness and confidence summaries are exposed
- [ ] Source drill-down is supported for key metrics

---

## Definition of Done

- [ ] Claim model is live in ingestion and research pipelines
- [ ] At least 10 critical company metrics are evidence-linked end-to-end
- [ ] Contradictions can be reviewed and resolved at claim level
- [ ] Confidence decomposition is exposed in APIs or exports
- [ ] Tests cover lineage and contradiction scenarios

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Schema complexity increases quickly | Medium | High | Start with critical facts and expand incrementally |
| Extraction quality is inconsistent | High | High | Add validation and reviewer workflow |
| Provenance payloads become too large | Medium | Medium | Store compact references and lazy-load details |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 4 weeks
- **Dependencies:** None; unlocks EPIC-041, EPIC-043, EPIC-045, EPIC-046

---

*Epic created as part of public-web intelligence expansion roadmap*
