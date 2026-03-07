# EPIC-045: Continuous Monitoring and Change Intelligence

**Status:** 🔴 Not Started  
**Priority:** HIGH (P1)  
**Story Points:** 34  
**Sprint Allocation:** 3 sprints  
**Target Date:** Week 25-27

---

## Problem Statement

Public-web company and market intelligence becomes stale quickly. Solstein needs scheduled refresh, change detection, and alerting so research stays current.

### Impact
- Scores drift away from reality
- Important launches, pricing changes, leadership moves, and hiring shifts are missed
- Analysts spend time re-checking the same sources manually

---

## Success Criteria

1. ✅ Scheduled refresh policies exist by source and entity priority
2. ✅ Page/document diffs are computed and stored
3. ✅ Material changes trigger alerts and score-delta workflows
4. ✅ Freshness decay is visible in confidence or readiness outputs
5. ✅ Watchlists support companies, competitors, and markets

---

## Stories

### Story 45.1: Refresh Scheduling (8 pts)
**Task:** Add policy-driven refresh for sources and entities

**Acceptance Criteria:**
- [ ] Refresh policies can vary by source type, entity priority, and page type
- [ ] Re-crawl frequency supports daily, weekly, and event-driven schedules
- [ ] Refresh jobs are idempotent and observable
- [ ] Failed refreshes can be retried safely

### Story 45.2: Semantic and Structural Diffing (8 pts)
**Task:** Detect meaningful changes in pages, documents, and extracted claims

**Acceptance Criteria:**
- [ ] Raw and cleaned-content diffs are both supported where needed
- [ ] Boilerplate-only changes are filtered out
- [ ] Claim-level diffs can identify new, changed, and removed evidence
- [ ] Materiality thresholds are configurable

### Story 45.3: Alerting and Watchlists (8 pts)
**Task:** Notify analysts when significant public-web changes occur

**Acceptance Criteria:**
- [ ] Watchlists support companies, competitors, and markets
- [ ] Alerts can be filtered by change type and severity
- [ ] Duplicate alerts are suppressed or grouped
- [ ] Alert history is queryable

### Story 45.4: Freshness Decay and Score Deltas (5 pts)
**Task:** Reflect stale evidence and changed evidence in scoring outputs

**Acceptance Criteria:**
- [ ] Freshness affects confidence or readiness scoring
- [ ] Score deltas can be tied to changed evidence
- [ ] Stale high-impact evidence is flagged clearly
- [ ] Freshness rules are configurable by source family

### Story 45.5: Change Narratives (5 pts)
**Task:** Generate concise explanations of what changed and why it matters

**Acceptance Criteria:**
- [ ] Narratives summarize major changes with citations
- [ ] Narratives differentiate factual changes from inferred impact
- [ ] Narratives can be generated for companies and markets
- [ ] Narratives reference affected scores or signals when applicable

---

## Definition of Done

- [ ] Refresh jobs run automatically for priority entities
- [ ] Material changes are detected on key page types
- [ ] Alerts can be routed to user workflows
- [ ] Freshness visibly affects downstream confidence
- [ ] Tests cover diffing and alert thresholds

---

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Too many noisy alerts | High | Medium | Thresholds, ranking, watchlist controls |
| Diffing creates false positives | Medium | Medium | Boilerplate stripping and page-type rules |
| Refresh cost grows too fast | Medium | High | Priority scheduling and caching |

---

## Resources

- **Developers:** 2 backend engineers
- **Time:** 3 weeks
- **Dependencies:** EPIC-041 and EPIC-042

---

*Epic created as part of public-web intelligence expansion roadmap*
