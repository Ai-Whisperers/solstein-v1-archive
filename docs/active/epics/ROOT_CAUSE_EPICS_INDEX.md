# 📋 ROOT CAUSE EPICS MASTER INDEX

> **Reference**: All EPICs created to address Root Cause Analysis findings
> **Created**: 2026-03-11
> **Status**: Ready for Implementation

---

## 🎯 Overview

This index tracks all EPICs created to address the root causes identified in the Root Cause Analysis. These EPICs are **P0 critical** and must be completed before claiming the system is production-ready.

---

## 📊 EPIC Summary

| EPIC | Title | Priority | Points | Status | Root Cause |
|------|-------|----------|--------|--------|------------|
| [EPIC-021](#epic-021) | Fix Confidence Scoring System | P0 | 13 | 🔴 Not Started | Root Cause 3 |
| [EPIC-022](#epic-022) | Implement Data Validation Pipeline | P0 | 13 | 🔴 Not Started | Root Cause 3 |
| [EPIC-023](#epic-023) | Fix Synthetic Data Detection | P0 | 13 | 🔴 Not Started | Root Cause 3 |
| [EPIC-024](#epic-024) | Fix Financial Scoring Algorithm | P0 | 13 | 🔴 Not Started | Root Cause 3 |
| [EPIC-025](#epic-025) | Consolidate Documentation | P0 | 8 | 🔴 Not Started | Root Cause 1, 4 |
| [EPIC-026](#epic-026) | Architecture Realignment | P1 | 21 | 🔴 Not Started | Root Cause 2 |

**Total EPICs**: 6
**Total Points**: 81
**Estimated Timeline**: 10-12 weeks (with 2 senior developers)

---

## 🔴 EPIC-021: Fix Confidence Scoring System

**Location**: `docs/active/epics/EPIC-021-CONFIDENCE-SCORING-FIX/`

### Problem
Confidence scoring uses arbitrary weights (0.2, 0.075, 0.05) based on field existence, not actual accuracy. High confidence (8.5/10) given to fake data.

### Solution
Implement statistical confidence model with:
- Source reliability weights (40%)
- Cross-validation score (30%)
- Data freshness (15%)
- Field completeness (15%)

### Stories
1. **21.1** - Analyze Current Confidence Accuracy (3 pts)
2. **21.2** - Design Statistical Confidence Model (3 pts)
3. **21.3** - Implement Source Reliability Weights (3 pts)
4. **21.4** - Add Cross-Validation Confidence Penalties (2 pts)
5. **21.5** - Implement Per-Field Confidence Breakdown (2 pts)

### Success Criteria
- [ ] Confidence scores correlate with actual accuracy (>70%)
- [ ] High confidence only for verified, cross-referenced data

---

## 🔴 EPIC-022: Implement Data Validation Pipeline

**Location**: `docs/active/epics/EPIC-022-DATA-VALIDATION/`

### Problem
No data validation. Bad data flows through:
- Unit inconsistencies ("9" with no unit)
- Currency mismatches (CGI Inc. marked EUR)
- Magnitude errors (5000000 instead of 5.0)

### Solution
Implement validation pipeline:
- Field-level validation
- Unit consistency checks
- Currency verification
- Cross-field validation

### Stories
1. **22.1** - Implement Field-Level Validators (3 pts)
2. **22.2** - Implement Unit Validation (3 pts)
3. **22.3** - Implement Currency Validation (2 pts)
4. **22.4** - Implement Cross-Field Validation (3 pts)
5. **22.5** - Integrate Validation into Pipeline (2 pts)

### Success Criteria
- [ ] Unit consistency >95%
- [ ] Currency accuracy >95%
- [ ] Magnitude errors <1%

---

## 🔴 EPIC-023: Fix Synthetic Data Detection

**Location**: `docs/active/epics/EPIC-023-SYNTHETIC-DETECTION/`

### Problem
98.5% of data is synthetic (196/199 companies) but `is_synthetic` flag is ALWAYS false. Users trust fake data.

### Solution
Implement synthetic detection:
- Source analysis ("generated" markers)
- Content pattern detection (round numbers)
- External validation (web presence check)
- Historical data migration

### Stories
1. **23.1** - Design Synthetic Detection Algorithm (3 pts)
2. **23.2** - Implement Source-Based Detection (2 pts)
3. **23.3** - Implement Content Pattern Detection (2 pts)
4. **23.4** - Implement External Validation (3 pts)
5. **23.5** - Flag Historical Synthetic Data (2 pts)
6. **23.6** - Update UI/API to Show Synthetic Flag (1 pt)

### Success Criteria
- [ ] Synthetic data ratio <20% (from 98.5%)
- [ ] Detection accuracy >90%
- [ ] Synthetic flag visible to users

---

## 🔴 EPIC-024: Fix Financial Scoring Algorithm

**Location**: `docs/active/epics/EPIC-024-SCORING-ALGORITHM/`

### Problem
ALL companies score exactly 5.5/10. No variance = no classification possible.

### Solution
Debug and fix scoring algorithm:
- Identify root cause of "all 5.5" bug
- Fix normalization/calculation issues
- Validate classification boundaries
- Add regression tests

### Stories
1. **24.1** - Debug Scoring Algorithm (3 pts)
2. **24.2** - Fix Score Calculation Bug (3 pts)
3. **24.3** - Validate Classification Boundaries (2 pts)
4. **24.4** - Add Scoring Regression Tests (3 pts)
5. **24.5** - Document Scoring Methodology (2 pts)

### Success Criteria
- [ ] Score variance >2.0 standard deviation
- [ ] Classification working (Phoenix/Salt/Lead)
- [ ] 10-20% Lead, 10-20% Phoenix, 60-80% Salt

---

## 🔴 EPIC-025: Consolidate Documentation and Status

**Location**: `docs/active/epics/EPIC-025-DOCUMENTATION-CONSOLIDATION/`

### Problem
Severe documentation chaos: 39 root markdown files, conflicting EPIC numbering, multiple master plans with contradictory status, claims of "all EPICs complete" when only 2 are partial.

### Solution
- Archive conflicting documentation
- Resolve EPIC numbering (two EPIC-018s)
- Create single source of truth
- Establish definition of done

### Stories
1. **25.1** - Archive Conflicting Documentation (2 pts)
2. **25.2** - Resolve EPIC Numbering Conflicts (1 pt)
3. **25.3** - Consolidate Root Markdown Files (2 pts)
4. **25.4** - Create Single Status Dashboard (2 pts)
5. **25.5** - Establish Definition of Done (1 pt)

### Success Criteria
- [ ] <5 markdown files in root
- [ ] Single status dashboard
- [ ] Definition of done documented and followed

---

## 🟡 EPIC-026: Architecture Realignment

**Location**: `docs/active/epics/EPIC-026-ARCHITECTURE-REALIGNMENT/`

### Problem
Documented: 6-agent LangGraph with cross-validation. Implemented: single sequential function. 80% architecture-documentation drift.

### Solution
**RECOMMENDED: Option B (Simplify)**
- Update docs to match simpler implementation
- Add conflict detection to existing flow
- Focus on data quality over sophistication
- 2-3 weeks effort vs 6-8 weeks

### Stories (Option B - Simplify)
1. **26.1** - Update Architecture Documentation (3 pts)
2. **26.2** - Add Conflict Detection to Pipeline (5 pts)
3. **26.3** - Implement Simple Cross-Validation (5 pts)
4. **26.4** - Create Architecture Decision Record (2 pts)
5. **26.5** - Deprecate/Remove LangGraph References (3 pts)
6. **26.6** - Update Research Orchestrator (3 pts)

### Success Criteria
- [ ] Architecture decision documented
- [ ] Documentation matches implementation
- [ ] No drift between docs and code

---

## 📅 Recommended Implementation Order

### Phase 1: Foundation (Weeks 1-2)
1. **EPIC-025** - Documentation consolidation first (enables everything)
2. **EPIC-024** - Fix scoring algorithm (unblocks classification)

### Phase 2: Data Quality (Weeks 3-5)
3. **EPIC-022** - Data validation pipeline
4. **EPIC-023** - Synthetic detection
5. **EPIC-021** - Confidence scoring

### Phase 3: Architecture (Weeks 6-8)
6. **EPIC-026** - Architecture realignment (decision + implementation)

---

## 🔗 Dependencies Between EPICs

```
EPIC-025 (Documentation)
    └── EPIC-024 (Scoring)
        └── EPIC-022 (Validation)
            ├── EPIC-023 (Synthetic)
            └── EPIC-021 (Confidence)
                └── EPIC-026 (Architecture)
```

**Key Dependencies:**
- EPIC-024 needs EPIC-025 (definition of done)
- EPIC-021 needs EPIC-022 (validation for confidence)
- EPIC-023 should happen with EPIC-022 (both data quality)
- EPIC-026 can happen in parallel after EPIC-025

---

## ✅ Definition of Done for All EPICs

An EPIC is **COMPLETE** when ALL of:
- [ ] All stories implemented and code reviewed
- [ ] All tests passing (including new tests)
- [ ] Documentation updated
- [ ] Demo working
- [ ] Success criteria met
- [ ] Status dashboard updated

**NO EXCEPTIONS.** Previous false claims of "complete" are why we need these EPICs.

---

## 📈 Success Metrics for All EPICs

| Metric | Before | After All EPICs | Measurement |
|--------|--------|-----------------|-------------|
| **Real Data %** | 1.5% | >80% | Count synthetic/total |
| **Score Variance** | 0.0 | >2.0 | Standard deviation |
| **Confidence Accuracy** | ~0% | >70% | Compare to ground truth |
| **Test Pass Rate** | ~60% | >95% | pytest results |
| **Doc-Code Alignment** | 20% | 100% | Review |
| **Unique Scores** | 1 | >50 | Distinct values |

---

## 📚 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../ROOT_CAUSE_ANALYSIS.md) - Full analysis
- [ROOT_CAUSE_SUMMARY.md](../../ROOT_CAUSE_SUMMARY.md) - Executive summary
- [EPIC_STATUS_DASHBOARD.md](../EPIC_STATUS_DASHBOARD.md) - Current status

---

## 📝 Notes

### Why These EPICs Are Critical

These are not "nice to have" improvements. They fix fundamental flaws:
- System produces fake data with false confidence
- Scoring algorithm is broken (all same score)
- Documentation lies about completion status
- Architecture promises what doesn't exist

**Without these EPICs, Solstein cannot be trusted.**

### Resource Requirements

- **2 senior developers**: 10-12 weeks
- **1 QA engineer**: Full time
- **1 product manager**: Part time (status, prioritization)

### Risk if Not Done

- Business decisions on fake data
- Legal liability for misrepresentation
- Complete loss of stakeholder trust
- System must be rebuilt from scratch

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Ready for Implementation*
*Version: 1.0*
