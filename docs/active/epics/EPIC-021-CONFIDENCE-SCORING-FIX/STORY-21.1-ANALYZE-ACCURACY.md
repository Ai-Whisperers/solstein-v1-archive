# STORY-21.1: Analyze Current Confidence Accuracy

> **Epic**: EPIC-021 - Fix Confidence Scoring System
> **Status**: 🔴 NOT STARTED
> **Priority**: P0
> **Points**: 3
> **Dependencies**: None

---

## 🎯 Objective

Measure the accuracy of the current confidence scoring system to establish a baseline and identify specific failure patterns.

---

## 📋 Acceptance Criteria

- [ ] Sample of 50+ company records manually validated for data accuracy
- [ ] Current confidence scores extracted for all sample records
- [ ] Correlation coefficient calculated between confidence and accuracy
- [ ] Failure patterns documented (when is confidence wrong?)
- [ ] Report with recommendations for improvement

---

## 🔧 Implementation Details

### Step 1: Select Validation Sample

```python
# Create validation dataset
# - 50 companies from research_results.json
# - Mix of high/low confidence scores
# - Include known synthetic and known real data
validation_sample = [
    {"company_id": "...", "expected_confidence": 0.9, "actual_accuracy": ?},
    # ... 49 more
]
```

### Step 2: Manual Validation

For each company in sample:
1. Extract all fields with confidence scores
2. Manually verify each field against authoritative sources
3. Calculate actual accuracy per field and overall
4. Record current confidence score

### Step 3: Calculate Correlation

```python
import numpy as np
from scipy.stats import pearsonr

confidence_scores = [0.9, 0.7, 0.3, ...]  # From system
actual_accuracies = [0.3, 0.8, 0.2, ...]  # From manual validation

correlation, p_value = pearsonr(confidence_scores, actual_accuracies)
# Target: correlation > 0.7
# Current: expected ~0.0 (no correlation)
```

### Step 4: Identify Failure Patterns

Document:
- When does system give high confidence to wrong data?
- When does system give low confidence to correct data?
- Which fields have worst confidence accuracy?
- Which sources cause most false confidence?

---

## 📊 Output

### Deliverables

1. **`METRICS-BASELINE.md`** - Baseline measurements
2. **Validation dataset** - 50 validated company records
3. **Analysis report** - Failure patterns and recommendations

### Report Structure

```markdown
# Confidence Scoring Baseline Analysis

## Summary
- Sample Size: 50 companies
- Current Correlation: 0.12 (very low)
- Target Correlation: 0.70+

## Key Findings
1. High confidence given to synthetic data (X% of time)
2. Low confidence on verified data (Y% of time)
3. Worst performing fields: [list]
4. Worst performing sources: [list]

## Recommendations
1. [Specific fixes needed]
2. [Methodology changes]
```

---

## ✅ Definition of Done

- [ ] 50 company sample validated
- [ ] Correlation coefficient calculated
- [ ] Failure patterns documented
- [ ] Report reviewed by team
- [ ] Recommendations approved

---

*Part of EPIC-021: Fix Confidence Scoring System*
