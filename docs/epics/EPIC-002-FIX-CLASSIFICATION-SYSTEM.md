# EPIC-002: Fix Company Classification System

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Must be completed before any production use

---

## Problem Statement

The classification system has **multiple critical failures**:

1. **Lead classification is mathematically impossible** - Minimum composite score (5.417) > Lead threshold (3.9)
2. **Duplicate classification functions** with different logic create inconsistencies
3. **Tier mapping is backwards** - Phoenix companies mapped to worst tier (Tier 4)
4. **24 Lead companies in input are misclassified as Salt**

### Current Broken State
```python
# In scoring.py
LEAD_SCORE_THRESHOLD = 3.9
# But minimum possible score = 5.417 (mathematically impossible to be Lead)

# In run_eneve_199.py
tier_map = {
    "Phoenix": CompanyTier.TIER_4,  # Best companies get worst tier!
    "Lead": CompanyTier.TIER_4      # Same tier as Phoenix
}
```

### Impact
- **0 Lead companies** detected despite 24 in input data
- **Phoenix companies penalized** with -1.0 competitive score
- **Inconsistent classification** between scoring.py and classification.py
- **Classification distribution targets** (15-25% Phoenix, 10-20% Lead) not achievable

---

## Success Criteria

- [ ] Lead classification is achievable (companies can score ≤ 4.0)
- [ ] Phoenix companies map to Tier 1 or Tier 2 (not Tier 4)
- [ ] Lead companies map to Tier 3 or Tier 4 (not same as Phoenix)
- [ ] Single classification function used throughout codebase
- [ ] Classification distribution matches targets (15-25% Phoenix, 60-70% Salt, 10-20% Lead)
- [ ] All 24 Lead companies in input correctly classified

---

## Technical Analysis

### Root Causes

1. **Mathematical Impossibility**:
   ```
   Minimum composite = (6.5 × 0.4) + (5.5 × 0.3) + (3.89 × 0.3) = 5.417
   Lead threshold = 3.9
   5.417 > 3.9 = Cannot classify as Lead
   ```

2. **Duplicate Functions**:
   - `scoring.py:classify_company()` uses thresholds: ≥7.0, 4.0-6.99, ≤3.9
   - `classification.py:classify_company_balanced()` uses: ≥7.0, ≥5.5, <5.5

3. **Backwards Tier Mapping**:
   - Phoenix → Tier 4 (worst)
   - Should be: Phoenix → Tier 1 (best)

### Affected Files
- `src/solstein/analytics/scoring.py`
- `src/solstein/analytics/classification.py`
- `src/solstein/analytics/constants.py`
- `scripts/run_eneve_199.py`

---

## Stories

### Story 2.1: Consolidate Classification Functions
**Priority:** P0 | **Effort:** 2 points

**Description:**
Eliminate duplicate classification logic by consolidating to a single function.

**Acceptance Criteria:**
- [ ] Choose ONE classification function (recommend `scoring.py:classify_company`)
- [ ] Remove or deprecate `classification.py:classify_company_balanced()`
- [ ] Update all call sites to use consolidated function
- [ ] Document classification thresholds in AGENTS.md
- [ ] Add unit tests for classification function

**Implementation:**
```python
# In scoring.py - keep this one
def classify_company(score: float) -> CompanyClassification:
    """Classify company based on composite score.
    
    Thresholds:
    - Phoenix: ≥ 7.0 (high growth, strong position)
    - Salt: 4.0 - 6.99 (moderate growth, established)
    - Lead: < 4.0 (low growth, declining)
    """
    if score >= PHOENIX_SCORE_THRESHOLD:  # 7.0
        return CompanyClassification.PHOENIX
    elif score >= LEAD_SCORE_THRESHOLD:   # 4.0 (not 3.9)
        return CompanyClassification.SALT
    else:
        return CompanyClassification.LEAD

# In classification.py - remove or delegate to scoring.py
def classify_company_balanced(score: float) -> CompanyClassification:
    """DEPRECATED: Use scoring.classify_company() instead."""
    from solstein.analytics.scoring import classify_company
    return classify_company(score)
```

---

### Story 2.2: Fix Tier Mapping Logic
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix the tier mapping so Phoenix companies get best tiers and Lead companies get worst tiers.

**Acceptance Criteria:**
- [ ] Phoenix → Tier 1 (best) or Tier 2
- [ ] Salt → Tier 2 or Tier 3
- [ ] Lead → Tier 3 or Tier 4 (worst)
- [ ] Update `run_eneve_199.py` tier_map
- [ ] Update competitive position scorer to use correct tier scores
- [ ] Verify competitive position scores reflect tier correctly

**Implementation:**
```python
# In run_eneve_199.py
tier_map = {
    "Phoenix": CompanyTier.TIER_1,  # Best tier for best companies
    "Salt": CompanyTier.TIER_2,     # Mid tier for moderate companies
    "Lead": CompanyTier.TIER_4      # Worst tier for struggling companies
}

# In competitive_position.py - verify tier scores
tier_scores: dict[str, float] = {
    "Tier 1": 3.0,   # Best - Phoenix
    "Tier 2": 1.5,   # Good - Salt
    "Tier 3": 0.0,   # Neutral
    "Tier 4": -1.0,  # Worst - Lead
}
```

---

### Story 2.3: Adjust Classification Thresholds
**Priority:** P0 | **Effort:** 2 points

**Description:**
Adjust classification thresholds to make Lead classification achievable while maintaining distribution targets.

**Acceptance Criteria:**
- [ ] Lower Lead threshold from 3.9 to 5.0 (or adjust scoring weights)
- [ ] Ensure minimum possible score < Lead threshold
- [ ] Verify Phoenix threshold (7.0) still achievable
- [ ] Update constants.py with new thresholds
- [ ] Update documentation with threshold rationale
- [ ] Run classification on 199 companies and verify distribution

**Options Analysis:**

**Option A: Lower Lead threshold**
```python
LEAD_SCORE_THRESHOLD = 5.0  # Was 3.9
# Pros: Simple change
# Cons: May classify too many as Lead
```

**Option B: Adjust scoring weights**
```python
# Increase weight of components that can go lower
profile.composite_score = round(
    (growth_score * 0.5) + (financial_health_score * 0.25) + (competitive_position_score * 0.25),
    2,
)
# Pros: More balanced scoring
# Cons: Changes all historical scores
```

**Option C: Add penalty system**
```python
# Add negative scoring for missing data, low metrics
if not financials.revenue:
    score -= 2.0
if growth_rate < 0:
    score -= 1.0
# Pros: Precise control
# Cons: More complex
```

**Recommendation:** Option A (lower threshold to 5.0) + Option C (add penalties for missing/negative metrics)

---

### Story 2.4: Add Classification Distribution Validation
**Priority:** P1 | **Effort:** 2 points

**Description:**
Add validation to ensure classification distribution matches targets.

**Acceptance Criteria:**
- [ ] Add `validate_classification_distribution()` function
- [ ] Check Phoenix: 15-25% of total
- [ ] Check Salt: 60-70% of total
- [ ] Check Lead: 10-20% of total
- [ ] Log warnings if distribution is outside targets
- [ ] Add configuration option to enforce distribution (optional)

**Implementation:**
```python
def validate_classification_distribution(
    companies: list[Company],
    strict: bool = False
) -> dict[str, any]:
    """Validate classification distribution matches targets."""
    total = len(companies)
    phoenix_count = sum(1 for c in companies if c.classification == "Phoenix")
    salt_count = sum(1 for c in companies if c.classification == "Salt")
    lead_count = sum(1 for c in companies if c.classification == "Lead")
    
    phoenix_pct = phoenix_count / total
    salt_pct = salt_count / total
    lead_pct = lead_count / total
    
    results = {
        "phoenix": {
            "count": phoenix_count,
            "percentage": phoenix_pct,
            "target": "15-25%",
            "valid": 0.15 <= phoenix_pct <= 0.25
        },
        "salt": {
            "count": salt_count,
            "percentage": salt_pct,
            "target": "60-70%",
            "valid": 0.60 <= salt_pct <= 0.70
        },
        "lead": {
            "count": lead_count,
            "percentage": lead_pct,
            "target": "10-20%",
            "valid": 0.10 <= lead_pct <= 0.20
        }
    }
    
    if strict and not all(r["valid"] for r in results.values()):
        raise ValueError(f"Classification distribution outside targets: {results}")
    
    return results
```

---

### Story 2.5: Fix Synthetic Data Classification Bug
**Priority:** P1 | **Effort:** 1 point

**Description:**
Fix the classification bug in synthetic data generator where growth_rate is compared as decimal instead of percentage.

**Acceptance Criteria:**
- [ ] Fix line 198 in generate_synthetic_companies.py
- [ ] Compare growth_rate (0.25) against 0.30 (not 30)
- [ ] Regenerate synthetic data with correct classifications
- [ ] Verify classification distribution in new data

**Implementation:**
```python
# OLD (buggy):
"classification": "Phoenix" if growth_rate > 30 else "Salt" if growth_rate > 10 else "Lead",

# NEW (fixed):
growth_decimal = growth_rate / 100  # Convert 25% to 0.25
"classification": "Phoenix" if growth_decimal > 0.30 else "Salt" if growth_decimal > 0.10 else "Lead",
```

---

## Dependencies

- Story 2.1 and 2.2 can be done in parallel
- Story 2.3 depends on EPIC-001 (financial scoring fix)
- Story 2.4 can be done after 2.1-2.3
- Story 2.5 is independent

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing thresholds affects historical data | High | Version classification logic, migration script |
| Tier mapping changes competitive scores | Medium | Recalculate all scores after change |
| Distribution targets may not be achievable | Medium | Adjust targets based on actual data |

## Definition of Done

- [ ] Single classification function used throughout
- [ ] Tier mapping corrected (Phoenix → Tier 1/2, Lead → Tier 4)
- [ ] Lead classification achievable (threshold ≤ 5.0)
- [ ] Classification distribution within targets
- [ ] All 24 Lead companies correctly classified
- [ ] Unit tests pass for all classification scenarios
- [ ] Documentation updated with classification logic
