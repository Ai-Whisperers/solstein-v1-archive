# EPIC-001: Fix Financial Health Scoring System

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 8 story points
## Sprint: Must be completed before any production use

---

## Problem Statement

The financial health scoring system is **mathematically broken**. ALL 199 companies receive an identical score of 5.5 due to unit mismatch between data storage (millions) and configuration thresholds (absolute EUR).

### Current Broken State
```python
# Config expects absolute EUR:
revenue_large_threshold = 100_000_000.0  # €100M

# But data stores:
revenue = 5.0  # €5M (stored as millions)

# Comparison: 5.0 > 100_000_000 is ALWAYS FALSE
```

### Impact
- **100% of companies** have identical financial_health_score = 5.5
- Zero variance in financial health component
- Composite scores artificially inflated
- Cannot differentiate financially healthy vs unhealthy companies

---

## Success Criteria

- [ ] Financial health scores vary between 0-10 based on actual company metrics
- [ ] Revenue thresholds correctly applied (€1M, €10M, €100M)
- [ ] Efficiency calculations use correct units
- [ ] Funding cushion ratios calculated correctly
- [ ] Score variance > 2.0 across 199 companies
- [ ] Unit tests pass with edge cases (€0 revenue, €1B+ revenue)

---

## Technical Analysis

### Root Cause
1. **Unit Mismatch**: Data stores revenue in millions, config expects absolute EUR
2. **Funding/Revenue Ratio Bug**: Funding in absolute EUR, revenue in millions
3. **Efficiency Calculation**: rev_per_emp = 5.0/150 = 0.033 (should be €33,333)

### Affected Files
- `src/solstein/analytics/scorers/financial_health.py`
- `src/solstein/core/scoring_config.py`
- `src/solstein/analytics/scoring.py`
- `scripts/run_eneve_199.py`

---

## Stories

### Story 1.1: Standardize Data Units Across Pipeline
**Priority:** P0 | **Effort:** 3 points

**Description:**
Establish consistent unit handling for financial metrics throughout the pipeline.

**Acceptance Criteria:**
- [ ] Define unit standards document (revenue in millions, funding in millions)
- [ ] Update FinancialMetric model to use consistent units
- [ ] Update scoring config thresholds to match data units
- [ ] Add unit validation in data loaders
- [ ] Document unit conventions in AGENTS.md

**Technical Notes:**
```python
# Standard: All financial values in millions EUR
revenue: float  # €5M stored as 5.0
funding_raised: float  # €2M stored as 2.0
valuation: float  # €50M stored as 50.0

# Config thresholds updated to match:
revenue_large_threshold = 100.0  # €100M
revenue_med_threshold = 10.0     # €10M
revenue_small_threshold = 1.0    # €1M
```

---

### Story 1.2: Fix Revenue Scale Scoring Component
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix the revenue scale component to correctly apply bonuses/penalties based on company size.

**Acceptance Criteria:**
- [ ] Companies with revenue < €1M get -1.0 penalty
- [ ] Companies with revenue €1M-€10M get 0.0 (neutral)
- [ ] Companies with revenue €10M-€100M get +1.0 bonus
- [ ] Companies with revenue > €100M get +2.0 bonus
- [ ] Unit tests verify all threshold boundaries

**Implementation:**
```python
# In financial_health.py
if financials.revenue >= self.config.revenue_large_threshold:
    adjustments.append(("Revenue Scale", self.config.revenue_large_bonus))
elif financials.revenue >= self.config.revenue_med_threshold:
    adjustments.append(("Revenue Scale", self.config.revenue_med_bonus))
elif financials.revenue < self.config.revenue_small_threshold:
    adjustments.append(("Revenue Scale", self.config.revenue_small_penalty))
```

---

### Story 1.3: Fix Operating Efficiency Calculation
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix revenue per employee calculation to use correct units and thresholds.

**Acceptance Criteria:**
- [ ] rev_per_emp calculated as (revenue × 1,000,000) / employees
- [ ] Thresholds: €100K (low), €500K (med), €1M (high)
- [ ] Companies with rev_per_emp < €100K get -1.0 penalty
- [ ] Companies with rev_per_emp > €1M get +2.0 bonus
- [ ] Handle edge case: employees = 0 (avoid division by zero)

**Implementation:**
```python
if financials.employees and financials.employees > 0:
    rev_per_emp = (financials.revenue * 1_000_000) / financials.employees
    # Compare against thresholds in same units
    if rev_per_emp >= self.config.efficiency_high_threshold:
        adjustments.append(("Operating Efficiency", self.config.efficiency_high_bonus))
    elif rev_per_emp >= self.config.efficiency_med_threshold:
        adjustments.append(("Operating Efficiency", self.config.efficiency_med_bonus))
    elif rev_per_emp < self.config.efficiency_low_threshold:
        adjustments.append(("Operating Efficiency", self.config.efficiency_low_penalty))
```

---

### Story 1.4: Fix Funding Cushion Ratio
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix funding to revenue ratio calculation for funding cushion scoring.

**Acceptance Criteria:**
- [ ] Ratio calculated as funding_raised / revenue (both in same units)
- [ ] Ratio > 10.0 (well-funded) gets +2.5 bonus
- [ ] Ratio 3.0-10.0 (adequate) gets +1.0 bonus
- [ ] Ratio < 3.0 (constrained) gets -1.0 penalty
- [ ] Handle edge case: revenue = 0 (avoid division by zero)

**Implementation:**
```python
if financials.revenue and financials.revenue > 0 and financials.funding_raised:
    cushion_ratio = financials.funding_raised / financials.revenue
    if cushion_ratio >= self.config.cushion_high_ratio:
        adjustments.append(("Funding Cushion", self.config.cushion_high_bonus))
    elif cushion_ratio >= self.config.cushion_med_ratio:
        adjustments.append(("Funding Cushion", self.config.cushion_med_bonus))
    else:
        adjustments.append(("Funding Cushion", self.config.cushion_low_penalty))
```

---

### Story 1.5: Add Comprehensive Unit Tests
**Priority:** P0 | **Effort:** 3 points

**Description:**
Create unit tests that verify financial health scoring with various company profiles.

**Acceptance Criteria:**
- [ ] Test company with €0 revenue (edge case)
- [ ] Test company with €500K revenue (small penalty)
- [ ] Test company with €5M revenue (neutral)
- [ ] Test company with €50M revenue (medium bonus)
- [ ] Test company with €500M revenue (large bonus)
- [ ] Test company with 10 employees, €10M revenue (high efficiency)
- [ ] Test company with 1000 employees, €1M revenue (low efficiency)
- [ ] Test company with funding/revenue = 15.0 (well-funded)
- [ ] Test company with funding/revenue = 1.0 (constrained)
- [ ] Verify score variance > 2.0 across test suite

**Test Structure:**
```python
def test_financial_health_score_variance():
    """Verify scores vary based on company metrics."""
    scorer = FinancialHealthScorer()
    
    small_company = create_company(revenue=0.5, employees=50, funding=0.1)
    large_company = create_company(revenue=500.0, employees=5000, funding=5000.0)
    
    small_score = scorer.calculate(small_company)
    large_score = scorer.calculate(large_company)
    
    assert small_score < 5.0  # Should be penalized
    assert large_score > 7.0  # Should be rewarded
    assert large_score - small_score > 3.0  # Significant variance
```

---

## Dependencies

- Story 1.1 must be completed before Stories 1.2-1.4
- All implementation stories must be completed before Story 1.5

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Changing units breaks other scorers | High | Comprehensive regression testing |
| Config changes affect existing data | Medium | Migration script for existing scores |
| Edge cases not covered | Medium | Extensive unit testing |

## Definition of Done

- [ ] All stories completed and code reviewed
- [ ] Unit tests pass with >90% coverage
- [ ] Integration tests verify end-to-end scoring
- [ ] Score variance > 2.0 confirmed across 199 companies
- [ ] Documentation updated with unit standards
- [ ] No regression in other scoring components
