# STORY-21.2: Design Statistical Confidence Model

> **Epic**: EPIC-021 - Fix Confidence Scoring System
> **Status**: 🔴 NOT STARTED
> **Priority**: P0
> **Points**: 3
> **Dependencies**: STORY-21.1

---

## 🎯 Objective

Design a statistically-grounded confidence scoring model that accurately reflects data reliability.

---

## 📋 Acceptance Criteria

- [ ] Mathematical model designed and documented
- [ ] Weight calculation methodology defined
- [ ] Source reliability scoring approach specified
- [ ] Cross-validation penalty formula defined
- [ ] Document reviewed and approved by team

---

## 🔧 Implementation Details

### Proposed Model: Multi-Factor Confidence

```python
class ConfidenceModel:
    """
    Confidence = weighted sum of:
    - Source reliability (40%)
    - Cross-validation score (30%)
    - Data freshness (15%)
    - Field completeness (15%)
    """

    def calculate(self, data: ResearchData) -> ConfidenceScore:
        source_score = self._source_reliability(data.sources)
        validation_score = self._cross_validation(data.field_sources)
        freshness_score = self._temporal_decay(data.timestamp)
        completeness_score = self._field_completeness(data.fields)

        return ConfidenceScore(
            total=(0.40 * source_score +
                   0.30 * validation_score +
                   0.15 * freshness_score +
                   0.15 * completeness_score),
            breakdown={
                "source_reliability": source_score,
                "cross_validation": validation_score,
                "freshness": freshness_score,
                "completeness": completeness_score
            }
        )
```

### Source Reliability Weights

```python
SOURCE_RELIABILITY = {
    # Tier 1: Authoritative (0.9-1.0)
    "bloomberg": 0.95,
    "reuters": 0.95,
    "official_filing": 0.95,

    # Tier 2: Reliable (0.7-0.89)
    "crunchbase": 0.80,
    "linkedin": 0.75,
    "company_website": 0.85,

    # Tier 3: Moderate (0.4-0.69)
    "news_article": 0.60,
    "press_release": 0.65,

    # Tier 4: Unverified (0.0-0.39)
    "blog": 0.30,
    "social_media": 0.20,
    "unknown": 0.10
}
```

### Cross-Validation Scoring

```python
def cross_validation_score(field: str, sources: List[Source]) -> float:
    """
    Score based on agreement between sources.

    - All sources agree: 1.0
    - Most agree (>70%): 0.8
    - Split (40-60%): 0.5
    - Most disagree: 0.2
    - All disagree: 0.0
    """
    values = [s.get_field(field) for s in sources]
    agreement = calculate_agreement(values)

    if agreement > 0.9:
        return 1.0
    elif agreement > 0.7:
        return 0.8
    elif agreement > 0.4:
        return 0.5
    else:
        return 0.2
```

### Temporal Decay

```python
def temporal_decay(timestamp: datetime, half_life_days: int = 90) -> float:
    """
    Confidence decays exponentially with age.

    - Fresh (<30 days): 1.0
    - Recent (30-90 days): 0.8
    - Aging (90-180 days): 0.6
    - Old (180-365 days): 0.4
    - Stale (>365 days): 0.2
    """
    age_days = (datetime.now() - timestamp).days
    return max(0.2, math.exp(-age_days / (half_life_days * 1.44)))
```

---

## 📊 Output

### Deliverables

1. **`CONFIDENCE-METHODOLOGY.md`** - Complete methodology document
2. **Mathematical formulas** - LaTeX or clear notation
3. **Weight justification** - Why each weight was chosen
4. **Validation approach** - How to verify the model works

### Methodology Document Structure

```markdown
# Confidence Scoring Methodology

## Overview
[High-level description]

## Formula
[Mathematical formula]

## Components

### 1. Source Reliability (40%)
[Explanation and weights]

### 2. Cross-Validation (30%)
[Explanation and formula]

### 3. Temporal Decay (15%)
[Explanation and formula]

### 4. Field Completeness (15%)
[Explanation]

## Calibration
[How weights were determined]

## Validation
[How to verify the model]
```

---

## ✅ Definition of Done

- [ ] Model documented in CONFIDENCE-METHODOLOGY.md
- [ ] Source reliability weights defined
- [ ] Cross-validation formula specified
- [ ] Temporal decay function defined
- [ ] Document reviewed by 2+ team members
- [ ] Approved by tech lead

---

*Part of EPIC-021: Fix Confidence Scoring System*
