# EPIC-023: Fix Synthetic Data Detection

> **Status**: 🔴 NOT STARTED
> **Priority**: P0 - Critical
> **Effort**: 13 story points
> **Sprint**: Data Quality Foundation
> **Related**: EPIC-006, EPIC-008, ROOT_CAUSE_ANALYSIS
> **Blocked By**: None

---

## 🚨 Problem Statement

**98.5% of company data is synthetic/fake (196 of 199 companies)**, but the `is_synthetic` flag is **always False**. There is no synthetic detection mechanism, no synthetic fallback implementation, and users are unknowingly trusting fake data.

### Current State (Broken)

```python
# In EVERY company record:
{
    "name": "Some Company",
    "revenue": 100.0,
    "is_synthetic": false,  # ALWAYS false, even for fake data
    "sources": ["generated"],  # Sometimes hints at synthetic
}
```

**Root Problem:** The LLM research pipeline generates synthetic data when real data unavailable, but:
1. Never marks it as synthetic
2. No detection mechanism exists
3. No synthetic fallback was implemented
4. Users cannot distinguish real from fake

### The Scale of the Problem

```
Total Companies: 199
Real Data: 3 (1.5%)
Synthetic Data: 196 (98.5%)
Marked as Synthetic: 0 (0%)
```

### Impact

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| **User Trust** | Users trust fake data | 🔴 Critical |
| **Business Decisions** | PE decisions on fabricated data | 🔴 Critical |
| **Legal Risk** | Misrepresenting data origin | 🔴 Critical |
| **System Value** | System produces no real insights | 🔴 Critical |
| **Reputation** | If discovered, complete loss of trust | 🔴 Critical |

### Root Cause Analysis Reference

See `docs/active/programs/root-cause/ROOT_CAUSE_ANALYSIS.md` - Section "Root Cause 3: Data Quality Cascade"

---

## 🎯 Success Criteria

- [ ] Synthetic detection algorithm implemented
- [ ] `is_synthetic` flag accurately reflects data origin
- [ ] Synthetic data ratio <20% (down from 98.5%)
- [ ] Users can see synthetic flag in UI/API
- [ ] Synthetic data clearly labeled in exports
- [ ] Pipeline prefers real data over synthetic
- [ ] Synthetic fallback only when real data unavailable
- [ ] All existing synthetic data flagged

---

## 📊 Current vs Target State

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Synthetic Data Ratio** | 98.5% | <20% | Count synthetic/total |
| **Detection Accuracy** | 0% | >90% | Manual validation sample |
| **False Positives** | N/A | <5% | Real data marked synthetic |
| **False Negatives** | 100% | <10% | Synthetic marked real |
| **User Visibility** | Hidden | Clear | UI/API shows flag |

---

## 📚 Technical Analysis

### Detection Methods

1. **Source Analysis**
   - "generated" in sources list
   - LLM provider in metadata
   - No external URLs

2. **Content Analysis**
   - Round numbers (revenue exactly 100M)
   - Missing specific details
   - Generic descriptions
   - Pattern matching

3. **Metadata Analysis**
   - LLM model in generation metadata
   - Timestamp patterns
   - Generation parameters

4. **Cross-Reference Validation**
   - Cannot find company on web
   - No matching records in databases
   - Mismatches with known data

### Detection Algorithm

```python
class SyntheticDetector:
    def detect(self, company_data: Dict) -> SyntheticScore:
        scores = {
            'source_indicators': self._check_sources(company_data),
            'content_patterns': self._check_content(company_data),
            'metadata_markers': self._check_metadata(company_data),
            'external_validation': self._cross_reference(company_data)
        }

        # Weighted combination
        synthetic_probability = (
            0.3 * scores['source_indicators'] +
            0.2 * scores['content_patterns'] +
            0.2 * scores['metadata_markers'] +
            0.3 * scores['external_validation']
        )

        return SyntheticScore(
            is_synthetic=synthetic_probability > 0.7,
            confidence=synthetic_probability,
            indicators=scores
        )
```

### Historical Data Migration

```python
def flag_historical_synthetic_data():
    """
    One-time migration to flag existing synthetic data.
    """
    for company in all_companies:
        detection = detector.detect(company)
        if detection.is_synthetic:
            company['is_synthetic'] = True
            company['synthetic_confidence'] = detection.confidence
            company['synthetic_indicators'] = detection.indicators
            save(company)
```

---

## 📖 Stories Overview

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 23.1 | Design Synthetic Detection Algorithm | P0 | 3 | None |
| 23.2 | Implement Source-Based Detection | P0 | 2 | 23.1 |
| 23.3 | Implement Content Pattern Detection | P0 | 2 | 23.1 |
| 23.4 | Implement External Validation | P0 | 3 | 23.1 |
| 23.5 | Flag Historical Synthetic Data | P0 | 2 | 23.2, 23.3, 23.4 |
| 23.6 | Update UI/API to Show Synthetic Flag | P1 | 1 | 23.5 |

**Total Stories**: 6
**Total Points**: 13

---

## 🔗 Dependencies

```
Story 23.1 (Design Algorithm)
    ├── Story 23.2 (Source Detection)
    ├── Story 23.3 (Content Detection)
    └── Story 23.4 (External Validation)
        └── Story 23.5 (Flag Historical)
            └── Story 23.6 (UI/API Update)
```

---

## ⚠️ Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| False positives flag real data | Medium | High | Manual review of flagged data |
| Detection misses sophisticated synthetic | High | Medium | Multiple detection methods |
| User backlash on discovering fake data | High | Critical | Proactive communication |
| Performance impact of web validation | Medium | Medium | Cache external checks |

---

## ✅ Definition of Done

- [ ] All 6 stories completed and code reviewed
- [ ] Detection algorithm >90% accurate
- [ ] Historical data flagged
- [ ] UI/API shows synthetic status
- [ ] Synthetic data clearly labeled in exports
- [ ] Pipeline prefers real data
- [ ] False positive rate <5%
- [ ] All existing tests pass
- [ ] New tests added for detection
- [ ] Documentation updated

---

## 📁 Epic Structure

```
docs/active/epics/EPIC-023-SYNTHETIC-DETECTION/
├── README.md                                    # This file
├── STORY-23.1-DESIGN-ALGORITHM.md              # Design detection algorithm
├── STORY-23.2-SOURCE-DETECTION.md              # Source-based detection
├── STORY-23.3-CONTENT-DETECTION.md             # Content pattern detection
├── STORY-23.4-EXTERNAL-VALIDATION.md           # External validation
├── STORY-23.5-FLAG-HISTORICAL.md               # Flag existing data
├── STORY-23.6-UI-API-UPDATE.md                 # Update UI/API
├── DETECTION-METHODOLOGY.md                    # How detection works
└── SYNTHETIC-ANALYSIS-REPORT.md                # Analysis of current data
```

---

## 🔗 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../programs/root-cause/ROOT_CAUSE_ANALYSIS.md) - Root cause context
- [EPIC-021](../EPIC-021-CONFIDENCE-SCORING-FIX/) - Confidence scoring
- [EPIC-022](../EPIC-022-DATA-VALIDATION/) - Data validation
- `data/research_results/research_results.json` - Current data

---

## 📝 Notes

### Synthetic Indicators Checklist

When reviewing company data, check for:
- [ ] Source list contains "generated" or LLM provider
- [ ] Revenue is round number (e.g., exactly 100M)
- [ ] No specific details (generic descriptions)
- [ ] Cannot find company on Google/LinkedIn
- [ ] No external URLs in sources
- [ ] LLM metadata in generation info

### Communication Strategy

1. **Internal**: Team aware of issue
2. **Stakeholders**: Brief on data quality initiative
3. **Users**: Transparency about synthetic flag
4. **Future**: Clear labeling prevents confusion

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Ready for Implementation*
*Version: 1.0*
