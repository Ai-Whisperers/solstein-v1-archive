# New Epic Backlog: Master Index

**Created:** 2026-03-06  
**Analyst:** Sisyphus Agent  
**Status:** Ready for Implementation

---

## Overview

This document provides a master index of **18 new epics** created following comprehensive analysis of the Solstein codebase. The first wave addresses production readiness and platform hardening; the second wave expands Solstein into a deeper public-web company and market intelligence platform.

**Total Epics:** 18  
**Total Story Points:** 776  
**Estimated Timeline:** 28-33 weeks  

---

## Epic Summary

| Epic | Title | Priority | Points | Status | Timeline |
|------|-------|----------|--------|--------|----------|
| **EPIC-031** | Test Suite Stabilization | P0 | **55** | 🔴 Not Started | **Week 1-3** |
| **EPIC-032** | Repository Cleanup | P1 | **34** | 🔴 Not Started | **Week 1-2** |
| **EPIC-033** | Data Pipeline Hardening | P1 | 55 | 🔴 Not Started | Week 3-6 |
| **EPIC-034** | API v2 Enhancements | P1 | 55 | 🔴 Not Started | Week 3-6 |
| **EPIC-035** | Documentation Completion | P2 | 34 | 🔴 Not Started | Week 5-6 |
| **EPIC-036** | Advanced Analytics | P2 | 55 | 🔴 Not Started | Week 7-10 |
| **EPIC-037** | Premium Data Sources | P2 | 55 | 🔴 Not Started | Week 7-10 |
| **EPIC-038** | User Experience | P2 | 34 | 🔴 Not Started | Week 10-12 |
| **EPIC-039** | Deployment Automation | P2 | 34 | 🔴 Not Started | Week 13-14 |
| **EPIC-040** | Disaster Recovery | P2 | 34 | 🔴 Not Started | Week 15-16 |
| **EPIC-041** | Deep Web Crawling and Document Ingestion | P0 | 55 | 🔴 Not Started | Week 17-20 |
| **EPIC-042** | Evidence Graph and Claim Provenance | P0 | 55 | 🔴 Not Started | Week 17-20 |
| **EPIC-043** | Open-Data Source Expansion | P1 | 55 | 🔴 Not Started | Week 21-24 |
| **EPIC-044** | Entity Resolution and Market Universe Builder | P1 | 55 | 🔴 Not Started | Week 21-24 |
| **EPIC-045** | Continuous Monitoring and Change Intelligence | P1 | 34 | 🔴 Not Started | Week 25-27 |
| **EPIC-046** | Analyst Workflow and IC Memo Automation | P2 | 34 | 🔴 Not Started | Week 28-30 |
| **EPIC-047** | Multilingual and Global Research Coverage | P2 | 34 | 🔴 Not Started | Week 28-30 |
| **EPIC-048** | Media and Transcript Intelligence | P2 | 34 | 🔴 Not Started | Week 31-33 |

**Total Story Points:** 776
**P0 Points:** 165 (21%)
**P1 Points:** 233 (30%)
**P2 Points:** 378 (49%)

---

## Phase Breakdown

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Stabilize codebase

1. **EPIC-031**: Test Suite Stabilization (34 pts)
   - Fix all unit tests
   - Fix all integration tests
   - Eliminate flaky tests
   - <5 min test execution

2. **EPIC-032**: Repository Cleanup (21 pts)
   - Remove build artifacts
   - Secure .env file
   - Split large files
   - Install pre-commit hooks

---

### Phase 2: Core Infrastructure (Weeks 3-6)
**Goal:** Production-ready data and API

3. **EPIC-033**: Data Pipeline Hardening (55 pts)
   - Change data capture
   - Temporal tables
   - Incremental enrichment
   - Real-time streaming

4. **EPIC-034**: API v2 Enhancements (55 pts)
   - Bulk import/export
   - Webhooks
   - GraphQL API
   - Cursor pagination

5. **EPIC-035**: Documentation Completion (34 pts)
   - Deployment guide
   - Troubleshooting guide
   - ADRs
   - API examples

---

### Phase 3: Feature Development (Weeks 7-12)
**Goal:** Advanced capabilities

6. **EPIC-036**: Advanced Analytics (55 pts)
   - Trend analysis
   - Industry benchmarking
   - Portfolio analysis
   - Risk assessment
   - Predictive models

7. **EPIC-037**: Premium Data Sources (55 pts)
   - PitchBook integration
   - CB Insights integration
   - Tracxn integration
   - Additional sources
   - Cost: $2500-9500/month

8. **EPIC-038**: User Experience (34 pts)
   - Email notifications
   - Scheduled reports
   - Saved searches
   - Alerts
   - Dashboard customization

---

### Phase 4: Operations (Weeks 13-16)
**Goal:** Production operations

9. **EPIC-039**: Deployment Automation (34 pts)
   - Blue/green deployment
   - Automated rollback
   - Database migration safety
   - Canary releases
   - Feature flags

10. **EPIC-040**: Disaster Recovery (34 pts)
    - Automated backups
    - Restore procedures
    - Multi-region failover
    - Chaos engineering
    - Data loss prevention

---

### Phase 5: Public-Web Intelligence Foundation (Weeks 17-24)
**Goal:** Research companies and markets deeply from public evidence

11. **EPIC-041**: Deep Web Crawling and Document Ingestion (55 pts)
    - Sitemap discovery
    - Robots-aware crawl policies
    - JS rendering
    - PDF/document parsing
    - Page classification and snapshots

12. **EPIC-042**: Evidence Graph and Claim Provenance (55 pts)
    - Claim ledger
    - Evidence lineage to metrics and scores
    - Confidence decomposition
    - Claim-level contradiction resolution
    - Citation-ready provenance retrieval

13. **EPIC-043**: Open-Data Source Expansion (55 pts)
    - Official registries and filings
    - Product/developer ecosystems
    - Reviews, hiring, and demand signals
    - Procurement and public contracts
    - Historical archive recovery

14. **EPIC-044**: Entity Resolution and Market Universe Builder (55 pts)
    - Canonical entity identity
    - Corporate structure mapping
    - Market-universe generation
    - Candidate ranking and analyst review
    - Sector and geography templates

---

### Phase 6: Intelligence Operations and Analyst Workflow (Weeks 25-33)
**Goal:** Turn public-web research into continuously monitored, analyst-grade intelligence

15. **EPIC-045**: Continuous Monitoring and Change Intelligence (34 pts)
    - Refresh scheduling
    - Semantic diffing
    - Alerts and watchlists
    - Freshness decay
    - Change narratives

16. **EPIC-046**: Analyst Workflow and IC Memo Automation (34 pts)
    - Evidence explorer
    - Review queues
    - Feedback loop
    - IC memo generation
    - Coverage indicators

17. **EPIC-047**: Multilingual and Global Research Coverage (34 pts)
    - Translation pipeline
    - Region-aware discovery
    - Regional sources
    - Multilingual provenance
    - Global coverage metrics

18. **EPIC-048**: Media and Transcript Intelligence (34 pts)
    - Media discovery
    - Transcript ingestion
    - Speaker attribution
    - Narrative extraction
    - Media provenance review

---

## Critical Path

```
Week 1-2:   EPIC-031 → EPIC-032 (Foundation)
              ↓
Week 3-6:   EPIC-033 + EPIC-034 + EPIC-035 (Core - parallel)
              ↓
Week 7-10:  EPIC-036 + EPIC-037 (Features - parallel)
              ↓
Week 10-12: EPIC-038 (UX)
              ↓
Week 13-16: EPIC-039 → EPIC-040 (Operations)
              ↓
Week 17-20: EPIC-041 + EPIC-042 (Public-web foundation)
              ↓
Week 21-24: EPIC-043 + EPIC-044 (Coverage and entity graph)
              ↓
Week 25-30: EPIC-045 + EPIC-046 + EPIC-047 (Monitoring and analyst workflows)
              ↓
Week 31-33: EPIC-048 (Media intelligence)
```

**Dependencies:**
- EPIC-031 blocks all other epics (tests must pass)
- EPIC-032 blocks EPIC-033+ (repository must be clean)
- EPIC-039 must complete before EPIC-040 (deployment before DR)
- EPIC-042 should begin before EPIC-043 through EPIC-048 (evidence contract first)
- EPIC-041 and EPIC-042 together unlock serious public-web research depth
- EPIC-044 is required for complete market-universe coverage

---

## Resource Requirements

### Development Team
| Role | Count | Duration |
|------|-------|----------|
| Backend Engineers | 3 | Full time |
| DevOps Engineers | 2 | Weeks 13-16 |
| Data Scientist | 1 | Weeks 7-10 |
| Full-Stack Engineers | 2 | Weeks 10-12 |
| Technical Writer | 1 | Weeks 5-6 |
| UX Designer | 1 | Weeks 10-12 |

### Infrastructure
| Resource | Purpose | Cost |
|----------|---------|------|
| Premium APIs | Data enrichment | $2500-9500/mo |
| Additional regions | DR/failover | +50% infra cost |
| Chaos engineering platform | Resilience testing | $500/mo |
| Email service | Notifications | $100-500/mo |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Test fixes take longer than estimated | High | High | Parallel workstreams, mock externals |
| API costs exceed budget | Medium | High | Start with one source, measure ROI |
| Team availability changes | Medium | High | Knowledge sharing, documentation |
| Third-party API changes | Medium | Medium | Abstraction layer, caching |
| Scope creep | High | Medium | Strict backlog management |
| Public-web crawling complexity exceeds estimates | High | High | Start with priority domains and page types |
| Entity resolution quality is lower than expected | Medium | High | Human review for low-confidence matches |
| Multilingual quality varies by market | Medium | Medium | Roll out market by market |

---

## Success Metrics

### Technical Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Test pass rate | <100% | 100% |
| Test execution time | Unknown | <5 min |
| Code coverage | Unknown | >80% |
| Build artifacts in repo | 54+ dirs | 0 |
| Files >500 lines | 12 | 0 |
| API latency p95 | Unknown | <200ms |
| Data freshness | Hours | Minutes |

### Business Metrics
| Metric | Current | Target |
|--------|---------|--------|
| Data quality score | ~6.0 | >8.0 |
| Funding data coverage | ~60% | >90% |
| Competitive coverage | ~40% | >80% |
| Deployment frequency | Weekly | Daily |
| Deployment failure rate | Unknown | <5% |
| Recovery time | Unknown | <4 hours |
| Evidence-backed key metrics | Partial | >95% |
| Company website crawl completeness | Unknown | >85% key-page coverage |
| Public source family coverage | Limited | 15+ source families |
| Change-alert precision | Unknown | >80% useful alerts |
| Global market coverage | Low | Target regions fully supported |

---

## Recommendation

**Priority Order:**

1. **Start immediately:** EPIC-031 (Test Suite)
   - This is blocking all other work
   - Highest technical risk
   - Enables confident development

2. **Next:** EPIC-032 (Repository Cleanup)
   - Quick win (1 week)
   - Security risk (.env file)
   - Unblocks parallel development

3. **Then:** EPIC-033 + EPIC-034 (Core Infrastructure)
   - Run in parallel with separate teams
   - Foundation for features
   - High business value

4. **Finally:** Remaining epics by priority

5. **Public-web intelligence expansion:** EPIC-041 through EPIC-048
   - Start with evidence and crawling foundations
   - Expand sources and market-universe coverage next
   - Layer monitoring, workflow, and global/media intelligence on top

---

## Next Steps

1. [ ] Review epics with stakeholders
2. [ ] Assign teams to Phase 1 (EPIC-031, EPIC-032)
3. [ ] Set up project tracking (Jira/Linear)
4. [ ] Schedule weekly epic reviews
5. [ ] Begin Sprint 1 with EPIC-031 Story 1.1
6. [ ] Review EPIC-041 through EPIC-048 as the next roadmap wave

---

## Epic Files

All epics are in `docs/epics/`:

### Critical (P0)
- `EPIC-031-TEST-SUITE-STABILIZATION.md`

### High (P1)
- `EPIC-032-REPOSITORY-CLEANUP.md`
- `EPIC-033-DATA-PIPELINE-HARDENING.md`
- `EPIC-034-API-V2-ENHANCEMENTS.md`

### Medium (P2)
- `EPIC-035-DOCUMENTATION-COMPLETION.md`
- `EPIC-036-ADVANCED-ANALYTICS.md`
- `EPIC-037-PREMIUM-DATA-SOURCES.md`
- `EPIC-038-USER-EXPERIENCE.md`
- `EPIC-039-DEPLOYMENT-AUTOMATION.md`
- `EPIC-040-DISASTER-RECOVERY.md`
- `EPIC-046-ANALYST-WORKFLOW-AND-IC-MEMO-AUTOMATION.md`
- `EPIC-047-MULTILINGUAL-AND-GLOBAL-RESEARCH-COVERAGE.md`
- `EPIC-048-MEDIA-AND-TRANSCRIPT-INTELLIGENCE.md`

### Critical (P0) - Public-Web Intelligence
- `EPIC-041-DEEP-WEB-CRAWLING-AND-DOCUMENT-INGESTION.md`
- `EPIC-042-EVIDENCE-GRAPH-AND-CLAIM-PROVENANCE.md`

### High (P1) - Public-Web Intelligence
- `EPIC-043-OPEN-DATA-SOURCE-EXPANSION.md`
- `EPIC-044-ENTITY-RESOLUTION-AND-MARKET-UNIVERSE-BUILDER.md`
- `EPIC-045-CONTINUOUS-MONITORING-AND-CHANGE-INTELLIGENCE.md`

### Analysis
- `COMPREHENSIVE-ANALYSIS.md`

---

## Contact

For questions about epics:
- Technical Lead: [Name]
- Product Owner: [Name]
- Engineering Manager: [Name]

---

*Master Index created by Sisyphus Agent*  
*Last Updated: 2026-03-06*  
*Version: 1.0*
