# ENEVE Epic Backlog - Master Index

## Overview

This document provides a master index of all epics created to address the 55+ fundamental issues identified in the ENEVE competitive intelligence system.

**Total Epics**: 8  
**Total Story Points**: 67  
**Status**: 🔴 Critical - System Unusable in Current State

---

## Epic Summary

| Epic | Title | Priority | Points | Status | Key Issue |
|------|-------|----------|--------|--------|-----------|
| EPIC-001 | Fix Financial Health Scoring | P0 | 8 | 🔴 Critical | ALL companies score 5.5 |
| EPIC-002 | Fix Classification System | P0 | 5 | 🔴 Critical | Lead classification impossible |
| EPIC-003 | Implement Real Enrichment | P0 | 13 | 🔴 Critical | Enrichment is 100% fake |
| EPIC-004 | Fix Data Conversion Pipeline | P0 | 8 | 🔴 Critical | 30+ fields lost |
| EPIC-005 | Fix Excel Export | P0 | 5 | 🔴 Critical | Margins always "N/A" |
| EPIC-006 | Fix Synthetic Data Generation | P1 | 5 | 🟡 High | 196/199 companies synthetic |
| EPIC-007 | Implement Confidence System | P0 | 5 | 🔴 Critical | Confidence weighting disabled |
| EPIC-008 | Replace Synthetic with Real Data | P0 | 13 | 🔴 Critical | 98.5% fake data |

**Total P0 Points**: 57 (85% of total)  
**Total P1 Points**: 10 (15% of total)

---

## Critical Path

The following epics **must** be completed before the system can be used:

### Phase 1: Core Scoring (Sprint 1-2)
1. **EPIC-001**: Fix Financial Health Scoring
   - Story 1.1: Standardize units
   - Story 1.2: Fix revenue scale
   - Story 1.3: Fix efficiency calculation
   - Story 1.4: Fix funding cushion

2. **EPIC-002**: Fix Classification System
   - Story 2.1: Consolidate classification functions
   - Story 2.2: Fix tier mapping
   - Story 2.3: Adjust thresholds

### Phase 2: Data Integrity (Sprint 3-4)
3. **EPIC-004**: Fix Data Conversion Pipeline
   - Story 4.1: Field mapping audit
   - Story 4.2: Fix confidence mapping
   - Story 4.3: Preserve CAGR data
   - Story 4.4: Fix enrichment count

4. **EPIC-005**: Fix Excel Export
   - Story 5.1: Fix field access
   - Story 5.2: Fix headers
   - Story 5.3: Add null checks

### Phase 3: Enrichment & Confidence (Sprint 5-6)
5. **EPIC-003**: Implement Real Enrichment
   - Story 3.1: Replace mock with real pipeline
   - Story 3.2: Configure API keys
   - Story 3.3: Implement fallbacks

6. **EPIC-007**: Implement Confidence System
   - Story 7.1: Extract confidence
   - Story 7.2: Populate signal_confidences
   - Story 7.3: Enable weighting

### Phase 4: Data Quality (Sprint 7-8)
7. **EPIC-006**: Fix Synthetic Data Generation
   - Story 6.1: Fix classification logic
   - Story 6.2: Fix website URLs
   - Story 6.3: Eliminate duplicates

8. **EPIC-008**: Replace Synthetic with Real Data
   - Story 8.1: Design collection pipeline
   - Story 8.2: Crunchbase integration
   - Story 8.3: LinkedIn integration
   - Story 8.4: Data validation

---

## Issue Categories

### Scoring Issues (Epics 1, 2, 7)
- Financial health stuck at 5.5
- Lead classification impossible
- Duplicate classification functions
- Backwards tier mapping
- Confidence weighting disabled
- Hardcoded composite weights

### Data Issues (Epics 4, 6, 8)
- 30+ fields lost in conversion
- enrichment_source_count reset to 0
- Confidence levels reset to UNKNOWN
- CAGR data lost
- 196/199 companies synthetic
- 38 duplicate company names
- Website URLs don't match names

### Enrichment Issues (Epic 3)
- 100% fake enrichment (mock data)
- No real API calls
- enrichment_source_count: 0 in output
- Data quality score from fake data

### Export Issues (Epic 5)
- profit_margin always "N/A"
- ebitda_margin always "N/A"
- Headers on row 3 (breaks parsing)
- Magic numbers throughout
- Division by zero risk

---

## Success Metrics

### Before Fix
- Financial health variance: **0** (all 5.5)
- Lead classification rate: **0%**
- Real data ratio: **1.5%**
- Field loss rate: **73%** (30/41 fields)
- Enrichment authenticity: **0%**

### After Fix (Target)
- Financial health variance: **> 2.0**
- Lead classification rate: **10-20%**
- Real data ratio: **> 80%**
- Field loss rate: **< 5%**
- Enrichment authenticity: **100%**

---

## Resource Requirements

### Development
- **Backend Engineers**: 2-3
- **Data Engineers**: 1-2
- **DevOps**: 1 (for API integrations)

### Infrastructure
- **Crunchbase API**: $100-500/month
- **LinkedIn API**: $500-2000/month (or scraping infrastructure)
- **News API**: Free tier sufficient
- **Redis/Cache**: For enrichment caching

### Timeline
- **Phase 1**: 2-3 weeks
- **Phase 2**: 2-3 weeks
- **Phase 3**: 3-4 weeks
- **Phase 4**: 4-6 weeks
- **Total**: **11-16 weeks** (3-4 months)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API costs exceed budget | Medium | High | Use free tiers, cache aggressively |
| LinkedIn API unavailable | High | High | Use alternative data sources |
| Data quality issues persist | Medium | High | Validation pipeline, manual review |
| Timeline extends | High | Medium | Prioritize P0, defer P1 |
| Breaking changes to existing users | Low | High | Version API, migration guide |

---

## Next Steps

1. **Review and prioritize** epics with stakeholders
2. **Assign teams** to Phase 1 epics (001, 002)
3. **Set up API accounts** (Crunchbase, LinkedIn, News)
4. **Create development branches** for each epic
5. **Begin Sprint 1** with EPIC-001 Story 1.1

---

## Documentation

Each epic contains:
- **Problem Statement**: What's broken and why
- **Success Criteria**: How we know it's fixed
- **Technical Analysis**: Root causes and affected files
- **Stories**: Detailed implementation tasks
- **Dependencies**: What must be done first
- **Risks**: What could go wrong
- **Definition of Done**: When it's complete

---

## Contact

For questions about epics:
- Technical Lead: [Name]
- Product Owner: [Name]
- Data Engineering: [Name]

---

*Last Updated: 2026-03-01*  
*Version: 1.0*  
*Status: Ready for Implementation*
