# NULL Handling Strategy for Solstein

**Document Version**: 1.0  
**Date**: 2026-02-25  
**Status**: Active  

## Executive Summary

Solstein's data quality audit revealed 84% NULL values across key financial metrics. This document defines the strategy for handling missing data while maintaining full transparency about data provenance.

**Core Principle**: Never invent data without clear provenance. All interpolations are explicitly flagged.

---

## Problem Statement

### Current State
- 168/199 companies (84%) missing revenue data
- 170/199 companies (85%) missing growth rate
- 107/199 companies (54%) missing employee count
- Scoring engine fails silently on NULL values

### Impact
- Incomplete market analysis
- Biased scoring (only complete companies scored)
- Lost opportunity to analyze 84% of dataset

### Solution
- Implement intelligent interpolation strategies
- Flag all estimated values for transparency
- Maintain full audit trail of data sources

---

## NULL Handling Strategies by Field

### 1. Revenue (€ millions)

**Strategy**: Interpolate from revenue timeline when available

**When to Interpolate**:
- ✓ Timeline has 2+ data points
- ✓ Gap between points ≤ 3 years
- ✓ Both surrounding values are known

**When NOT to Interpolate**:
- ✗ Timeline has < 2 points
- ✗ Gap > 3 years (too uncertain)
- ✗ Either surrounding value is NULL

**Interpolation Method**: Geometric mean
```
interpolated_revenue = (revenue_year1 * revenue_year2) ^ (1/gap_years)
```

**Example**:
```
2022: €10M
2023: [MISSING]
2024: €15M

Interpolated 2023 = (10 * 15) ^ (1/2) = √150 = €12.25M
Flag: is_interpolated = true
```

**Confidence**: Medium (0.6)
- Assumes consistent growth pattern
- May not account for market disruptions

---

### 2. Growth Rate (% per year)

**Strategy**: Calculate from revenue timeline OR use sector average

**When to Calculate from Timeline**:
- ✓ Timeline has 2+ data points
- ✓ Can calculate CAGR from most recent years

**When to Use Sector Average**:
- ✓ Timeline unavailable
- ✓ Explicitly labeled as sector benchmark
- ✓ Used only for analysis, not scoring

**Calculation Method**: CAGR (Compound Annual Growth Rate)
```
growth_rate = ((revenue_recent / revenue_previous) ^ (1/years) - 1) * 100
```

**Example**:
```
2022: €10M
2024: €15M (2 years)

Growth = ((15/10) ^ (1/2) - 1) * 100 = 22.5% per year
Flag: is_interpolated = true, source = "calculated_from_timeline"
```

**Sector Average Fallback**: 10% per year
- Used only when timeline unavailable
- Explicitly marked as "sector_average"
- Confidence: Low (0.3)

---

### 3. Employee Count

**Strategy**: Use last known value OR estimate from revenue

**When to Use Last Known**:
- ✓ Employee timeline has data
- ✓ Most recent data point < 2 years old
- ✓ Reasonable to assume stability

**When to Estimate from Revenue**:
- ✓ No employee timeline
- ✓ Revenue is known
- ✓ Use industry ratio: 1 employee per €3.3M revenue

**Estimation Formula**:
```
estimated_employees = revenue_eur * 0.0003
```

**Example**:
```
Revenue: €450M
Estimated employees = 450M * 0.0003 = 135 employees
Flag: is_interpolated = true, source = "estimated_from_revenue"
```

**Confidence**: Low (0.4)
- Highly variable by industry
- Should be used only for rough analysis

---

### 4. Profit Margin (%)

**Strategy**: Flag as unavailable (no interpolation)

**Rationale**:
- Profit margin is highly business-specific
- Cannot be reliably estimated from other metrics
- Interpolation would be misleading

**Action**: Leave NULL, flag in data quality report

---

### 5. Funding Raised (€ millions)

**Strategy**: Use last known value OR flag as unavailable

**When to Use Last Known**:
- ✓ Funding timeline has data
- ✓ Most recent funding round documented

**When to Flag as Unavailable**:
- ✗ No funding timeline
- ✗ Cannot estimate reliably

---

## Implementation Details

### Data Structure

All interpolated values include metadata:

```python
{
    "field": "revenue",
    "value": 12.25,  # Interpolated value
    "is_interpolated": True,
    "interpolation_method": "geometric_mean",
    "source_data": {
        "year_1": {"year": 2022, "value": 10.0},
        "year_2": {"year": 2024, "value": 15.0}
    },
    "confidence": 0.6,
    "confidence_reason": "Geometric interpolation between 2 timeline points"
}
```

### Confidence Levels

| Source | Confidence | Usage |
|--------|-----------|-------|
| Actual data | 1.0 | Full scoring |
| Interpolated (timeline) | 0.6 | Scoring with discount |
| Calculated (CAGR) | 0.6 | Scoring with discount |
| Last known (< 2 yrs) | 0.7 | Scoring with discount |
| Estimated (from revenue) | 0.4 | Analysis only, not scoring |
| Sector average | 0.3 | Analysis only, not scoring |

### Configuration

```python
InterpolationConfig(
    # Revenue
    revenue_min_timeline_points=2,
    revenue_interpolation_method="geometric",
    revenue_max_gap_years=3,
    
    # Growth
    growth_min_timeline_points=2,
    growth_use_sector_average=True,
    growth_sector_average_fallback=10.0,
    
    # Employees
    employee_min_timeline_points=2,
    employee_use_last_known=True,
    employee_estimate_from_revenue=True,
    employee_revenue_ratio=0.0003,
    
    # General
    flag_all_interpolations=True
)
```

---

## Transparency Requirements

### Always Document

1. **Original NULL value**: Show what was missing
2. **Interpolation method**: How was it estimated?
3. **Source data**: What data was used?
4. **Confidence level**: How reliable is this?
5. **Audit trail**: Who did this and when?

### Never Hide

- ✗ Don't silently fill NULLs
- ✗ Don't mix real and estimated data without marking
- ✗ Don't use sector averages without labeling
- ✗ Don't lose track of data provenance

### Always Flag

- ✓ Mark all interpolated values
- ✓ Include confidence scores
- ✓ Document interpolation method
- ✓ Preserve original NULL indicator

---

## Usage Examples

### Example 1: Revenue Interpolation

```python
from solstein.data.interpolation import interpolation_engine

# Company with revenue timeline
company_data = {
    "revenue": None,  # Missing current revenue
    "revenue_timeline": [
        {"year": 2022, "revenue": 10.0},
        {"year": 2024, "revenue": 15.0}
    ]
}

# Interpolate
revenue, is_interpolated = interpolation_engine.interpolate_revenue(
    revenue_timeline=company_data["revenue_timeline"],
    current_revenue=company_data["revenue"]
)

# Result: revenue = 12.25, is_interpolated = True
```

### Example 2: Growth Rate Calculation

```python
# Calculate growth from timeline
growth, is_interpolated = interpolation_engine.interpolate_growth_rate(
    revenue_timeline=company_data["revenue_timeline"]
)

# Result: growth = 22.5%, is_interpolated = True
```

### Example 3: Employee Estimation

```python
# Estimate employees from revenue
employees, is_interpolated = interpolation_engine.interpolate_employees(
    current_employees=None,
    revenue=450.0  # €450M
)

# Result: employees = 135, is_interpolated = True
```

---

## Validation & Quality Assurance

### Validation Rules

1. **Range Check**: Interpolated value must be positive
2. **Reasonableness Check**: Value shouldn't differ >2x from original
3. **Timeline Check**: Gap must be ≤ max_gap_years
4. **Data Point Check**: Must have minimum data points

### Testing Strategy

- Unit tests for each interpolation method
- Edge cases: NULL values, zero values, extreme values
- Regression tests: Known companies with known values
- Audit trail: Verify all interpolations are documented

---

## Rollback & Disable

### If Issues Arise

1. **Disable interpolation**: Set `flag_all_interpolations = False`
2. **Revert to NULL**: Leave missing values as NULL
3. **Audit**: Review all interpolated values
4. **Fix**: Correct interpolation logic
5. **Re-enable**: Gradually enable with monitoring

### Configuration Override

```python
# Disable all interpolation
config = InterpolationConfig(
    revenue_min_timeline_points=999,  # Impossible to meet
    growth_use_sector_average=False,
    employee_estimate_from_revenue=False
)
```

---

## Future Enhancements

1. **Machine Learning**: Train model on known companies to predict missing values
2. **Sector-Specific Ratios**: Use industry benchmarks instead of global average
3. **Peer Comparison**: Estimate from similar companies in same market
4. **Time Series Analysis**: Use ARIMA or other forecasting methods
5. **Expert Review**: Manual validation for high-value companies

---

## References

- Task 1: Data Quality Audit (`.sisyphus/evidence/task-1-audit-complete.json`)
- Task 2: Unified Company Loader (`.sisyphus/evidence/task-2-unified-tests-complete.json`)
- Task 3: Completeness Scoring (`.sisyphus/evidence/task-3-completeness-complete.json`)
- Implementation: `src/solstein/data/interpolation.py`
- Tests: `tests/unit/test_interpolation.py`

---

**Document Owner**: Solstein Data Team  
**Last Updated**: 2026-02-25  
**Next Review**: 2026-03-25
