# EPIC-021: Fix Confidence Scoring System

> **Status**: 🔴 NOT STARTED
> **Priority**: P0 - Critical
> **Effort**: 13 story points
> **Sprint**: Data Quality Foundation
> **Related**: EPIC-007, EPIC-023, ROOT_CAUSE_ANALYSIS
> **Blocked By**: None

---

## 🚨 Problem Statement

The confidence scoring system is **fundamentally broken**. It uses arbitrary weights based on field existence rather than actual data accuracy, producing high confidence scores (8.5/10) for unreliable or synthetic data.

### Current State (Broken)

```python
# ai_research_orchestrator.py - Current broken implementation
def _calculate_confidence_score(self, data: Dict) -> float:
    score = 0.0
    if data.get("name"):
        score += 0.2      # Arbitrary - why 0.2?
    if data.get("revenue"):
        score += 0.075    # Arbitrary - why 0.075?
    if data.get("valuation"):
        score += 0.05     # Arbitrary - why 0.05?
    # ... more arbitrary weights
    return min(score, 1.0)
```

**Problems:**
- ❌ Weights have no statistical basis
- ❌ Field existence ≠ Field accuracy
- ❌ No source reliability consideration
- ❌ No penalty for conflicting data
- ❌ Same score for verified vs fabricated data
- ❌ Confidence does not correlate with actual accuracy

### Impact

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| **User Trust** | High confidence on fake data | 🔴 Critical |
| **Decision Making** | Bad data appears reliable | 🔴 Critical |
| **Data Quality** | Cannot identify unreliable data | 🔴 Critical |
| **System Reliability** | No quality gates | 🟡 High |
| **Business Risk** | PE decisions on bad data | 🔴 Critical |

### Root Cause Analysis Reference

See `docs/active/programs/root-cause/ROOT_CAUSE_ANALYSIS.md` - Section "Root Cause 3: Data Quality Cascade"

---

## 🎯 Success Criteria

- [ ] Confidence scores correlate with actual data accuracy (>70% correlation)
- [ ] Source reliability weights implemented and configurable
- [ ] Cross-validation confidence penalties working
- [ ] Confidence breakdown visible (per-source, per-field)
- [ ] High confidence (>0.8) only for verified, cross-referenced data
- [ ] Low confidence (<0.4) for single-source, unverified data
- [ ] Confidence scores have statistical basis (documented methodology)
- [ ] All existing tests pass with new scoring

---

## 📊 Current vs Target State

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Confidence Accuracy** | ~0% | >70% | Compare confidence to ground truth |
| **Weight Basis** | Arbitrary | Statistical | Documented methodology |
| **Source Consideration** | None | Yes | Source reliability scores |
| **Cross-Validation** | None | Yes | Conflict detection |
| **False High Confidence** | Common | Rare | <5% of synthetic data >0.8 |

---

## 📚 Technical Analysis

### Current Implementation Location

```
src/solstein/research/ai_research_orchestrator.py
├── _calculate_confidence_score() - Lines ~945-968
├── _merge_company_data() - Lines ~890-940
└── _validate_research_data() - Lines ~850-889
```

### Problems Identified

1. **Arbitrary Weights**: Values (0.2, 0.075, 0.05) chosen without analysis
2. **No Source Weighting**: Bloomberg vs random blog treated equally
3. **No Validation Impact**: Validated and unvalidated data same score
4. **No Conflict Detection**: Conflicting sources don't reduce confidence
5. **Field Existence Bias**: Empty string "" counts as "has field"
6. **No Temporal Decay**: Old data same score as fresh data

### Data Flow

```
Research Data
     ↓
[Current: Arbitrary weights] → [Target: Statistical model]
     ↓
Confidence Score (0-1)
     ↓
User Decision
```

---

## 📖 Stories Overview

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 21.1 | Analyze Current Confidence Accuracy | P0 | 3 | None |
| 21.2 | Design Statistical Confidence Model | P0 | 3 | 21.1 |
| 21.3 | Implement Source Reliability Weights | P0 | 3 | 21.2 |
| 21.4 | Add Cross-Validation Confidence Penalties | P0 | 2 | 21.2 |
| 21.5 | Implement Per-Field Confidence Breakdown | P1 | 2 | 21.3, 21.4 |

**Total Stories**: 5
**Total Points**: 13

---

## 🔗 Dependencies

```
Story 21.1 (Analyze Accuracy)
    ↓
Story 21.2 (Design Model)
    ├── Story 21.3 (Source Weights)
    │   └── Story 21.5 (Per-Field Breakdown)
    └── Story 21.4 (Cross-Validation)
        └── Story 21.5 (Per-Field Breakdown)
```

---

## ⚠️ Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Statistical model too complex | Medium | Medium | Start simple, iterate |
| Ground truth data unavailable | High | High | Use manual validation sample |
| Performance impact from calculations | Low | Medium | Benchmark before/after |
| Breaking change to API responses | Medium | High | Version confidence schema |
| Requires EPIC-022 (validation) for accuracy | High | High | Coordinate with EPIC-022 |

---

## ✅ Definition of Done

- [ ] All 5 stories completed and code reviewed
- [ ] Confidence accuracy measured at >70% correlation
- [ ] Statistical methodology documented
- [ ] Source reliability weights configurable
- [ ] Cross-validation penalties implemented
- [ ] Per-field confidence breakdown visible
- [ ] All existing tests pass
- [ ] New tests added for confidence calculation
- [ ] Performance benchmark shows <10% regression
- [ ] Documentation updated (API schema, methodology)

---

## 📁 Epic Structure

```
docs/active/epics/EPIC-021-CONFIDENCE-SCORING-FIX/
├── README.md                                    # This file
├── STORY-21.1-ANALYZE-ACCURACY.md              # Analyze current confidence
├── STORY-21.2-DESIGN-MODEL.md                  # Design statistical model
├── STORY-21.3-SOURCE-WEIGHTS.md                # Implement source weights
├── STORY-21.4-CROSS-VALIDATION.md              # Add cross-validation
├── STORY-21.5-PER-FIELD-BREAKDOWN.md           # Per-field confidence
├── CONFIDENCE-METHODOLOGY.md                   # Statistical methodology doc
└── METRICS-BASELINE.md                         # Current accuracy measurements
```

---

## 🔗 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../programs/root-cause/ROOT_CAUSE_ANALYSIS.md) - Root cause context
- [EPIC-022](../EPIC-022-DATA-VALIDATION/) - Data validation (dependency)
- [EPIC-023](../EPIC-023-SYNTHETIC-DETECTION/) - Synthetic detection (dependency)
- `src/solstein/research/ai_research_orchestrator.py` - Current implementation

---

## 📝 Notes

### Historical Context

- EPIC-007 claimed "Implement Confidence System" but was never actually implemented
- Current implementation is placeholder that gives false confidence
- This EPIC replaces/repairs EPIC-007

### Key Design Decisions Needed

1. **Weight Calculation Method**: Bayesian vs frequency-based vs heuristic
2. **Source Reliability**: Static weights or learned from data
3. **Cross-Validation Threshold**: What constitutes a "conflict"
4. **Temporal Decay**: How quickly does confidence decrease with age

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Ready for Implementation*
*Version: 1.0*
