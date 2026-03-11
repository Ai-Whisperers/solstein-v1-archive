# EPIC-024: Fix Financial Scoring Algorithm

> **Status**: 🔴 NOT STARTED
> **Priority**: P0 - Critical
> **Effort**: 13 story points
> **Sprint**: Core Scoring
> **Related**: EPIC-001, EPIC-002, ROOT_CAUSE_ANALYSIS
> **Blocked By**: EPIC-022 (needs validated data)

---

## 🚨 Problem Statement

**ALL companies score exactly 5.5/10** — the scoring algorithm is broken and produces no variance. Classification (Phoenix/Salt/Lead) cannot work when every company has the same score.

### Current State (Broken)

```python
# GrowthScorer.calculate_scores() - Current broken implementation
def calculate_scores(self, profile: CompanyProfile) -> CompanyProfile:
    # All paths lead to ~5.5
    growth_score = self._calculate_growth(profile)  # Always ~1.83
    financial_score = self._calculate_financial(profile)  # Always ~1.83
    competitive_score = self._calculate_competitive(profile)  # Always ~1.83

    total = growth_score + financial_score + competitive_score  # Always ~5.5
    profile.final_score = total
    return profile
```

**Debug Output:**
```python
companies = load_all_companies()
scores = [c.final_score for c in companies]
print(f"Mean: {mean(scores)}")  # 5.5
print(f"Std Dev: {stdev(scores)}")  # 0.0
print(f"Unique scores: {len(set(scores))}")  # 1
```

### Impact

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| **Classification** | Cannot classify (all same) | 🔴 Critical |
| **Ranking** | No meaningful ranking | 🔴 Critical |
| **Decision Making** | No differentiation | 🔴 Critical |
| **System Value** | Scores meaningless | 🔴 Critical |
| **User Trust** | Obvious system failure | 🔴 Critical |

### Root Cause Analysis Reference

See `docs/ROOT_CAUSE_ANALYSIS.md` - Section "Root Cause 3: Data Quality Cascade"

---

## 🎯 Success Criteria

- [ ] Score variance >2.0 standard deviation
- [ ] Classification working (Phoenix/Salt/Lead)
- [ ] 10-20% of companies classified as Lead
- [ ] 10-20% of companies classified as Phoenix
- [ ] 60-80% of companies classified as Salt
- [ ] Known high-growth companies score high
- [ ] Known struggling companies score low
- [ ] All existing tests pass

---

## 📊 Current vs Target State

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Score Variance** | 0.0 | >2.0 | Standard deviation |
| **Unique Scores** | 1 | >50 | Distinct values |
| **Classification Rate** | 0% | 100% | Companies classified |
| **Lead Rate** | 0% | 10-20% | Bottom classification |
| **Phoenix Rate** | 0% | 10-20% | Top classification |
| **Score Range** | 5.5 | 2.0-9.0 | Min/max scores |

---

## 📚 Technical Analysis

### Likely Causes of Bug

1. **Normalization Bug**
   ```python
   # All values normalized to same range incorrectly
   normalized = (value - min) / (max - min)  # But min=max, causing division by zero
   ```

2. **Hardcoded Defaults**
   ```python
   # Missing data always returns default score
   if not data:
       return 1.83  # Arbitrary default
   ```

3. **Floating Point Issues**
   ```python
   # Integer division or precision loss
   score = int(revenue) / int(total)  # Results in same value for all
   ```

4. **Data Pipeline Issue**
   ```python
   # All companies getting same input data
   profile.revenue = get_revenue(company_id)  # Returns cached default
   ```

### Debug Strategy

```python
def debug_scoring(company: Company):
    """Instrument scoring to find the bug."""
    print(f"Company: {company.name}")
    print(f"Raw revenue: {company.raw_revenue}")
    print(f"Normalized revenue: {normalize(company.raw_revenue)}")
    print(f"Growth component: {calculate_growth(company)}")
    print(f"Financial component: {calculate_financial(company)}")
    print(f"Competitive component: {calculate_competitive(company)}")
    print(f"Final score: {company.final_score}")
```

### Scoring Components

```python
class FinancialScorer:
    def calculate(self, company: Company) -> Score:
        # Growth Score (1-10)
        revenue_growth = self._revenue_growth_score(company)
        employee_growth = self._employee_growth_score(company)

        # Financial Health (1-10)
        profitability = self._profitability_score(company)
        funding = self._funding_score(company)

        # Competitive Position (1-10)
        market_position = self._market_position_score(company)
        tech_adoption = self._tech_adoption_score(company)

        # Weighted combination
        final_score = (
            0.3 * revenue_growth +
            0.2 * employee_growth +
            0.2 * profitability +
            0.1 * funding +
            0.1 * market_position +
            0.1 * tech_adoption
        )

        return Score(value=final_score, components={...})
```

---

## 📖 Stories Overview

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 24.1 | Debug Scoring Algorithm | P0 | 3 | None |
| 24.2 | Fix Score Calculation Bug | P0 | 3 | 24.1 |
| 24.3 | Validate Classification Boundaries | P0 | 2 | 24.2 |
| 24.4 | Add Scoring Regression Tests | P0 | 3 | 24.3 |
| 24.5 | Document Scoring Methodology | P1 | 2 | 24.2 |

**Total Stories**: 5
**Total Points**: 13

---

## 🔗 Dependencies

```
Story 24.1 (Debug Algorithm)
    └── Story 24.2 (Fix Bug)
        ├── Story 24.3 (Validate Boundaries)
        │   └── Story 24.4 (Regression Tests)
        └── Story 24.5 (Documentation)
```

**External Dependencies:**
- EPIC-022 (Data Validation) - Need validated data for accurate scoring

---

## ⚠️ Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Bug in different component than expected | Medium | High | Systematic debugging |
| Data quality affects scoring | High | High | Complete EPIC-022 first |
| Breaking change to existing classifications | Medium | Medium | Version scores or flag change |
| Performance regression from fix | Low | Medium | Benchmark before/after |

---

## ✅ Definition of Done

- [ ] All 5 stories completed and code reviewed
- [ ] Root cause of "all 5.5" bug identified and fixed
- [ ] Score variance >2.0 standard deviation
- [ ] Classification boundaries validated
- [ ] Regression tests added
- [ ] Known companies score appropriately
- [ ] All existing tests pass
- [ ] Documentation updated

---

## 📁 Epic Structure

```
docs/active/epics/EPIC-024-SCORING-ALGORITHM/
├── README.md                                    # This file
├── STORY-24.1-DEBUG-ALGORITHM.md               # Debug the scoring
├── STORY-24.2-FIX-BUG.md                       # Fix the bug
├── STORY-24.3-VALIDATE-BOUNDARIES.md           # Validate classification
├── STORY-24.4-REGRESSION-TESTS.md              # Add regression tests
├── STORY-24.5-DOCUMENTATION.md                 # Document methodology
├── DEBUG-REPORT.md                             # Bug investigation report
└└── SCORING-METHODOLOGY.md                      # How scoring works
```

---

## 🔗 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../../../ROOT_CAUSE_ANALYSIS.md) - Root cause context
- [EPIC-001](../EPIC-001-FIX-FINANCIAL-SCORING/) - Original financial scoring EPIC
- [EPIC-002](../EPIC-002-FIX-CLASSIFICATION/) - Classification system
- [EPIC-022](../EPIC-022-DATA-VALIDATION/) - Data validation (dependency)
- `src/solstein/analytics/scoring.py` - Current scoring implementation

---

## 📝 Notes

### Known High-Growth Companies (Should Score High)
- Octopus Energy (known rapid growth)
- Any Y Combinator recent graduates

### Known Struggling Companies (Should Score Low)
- Companies with recent layoffs
- Companies with declining revenue

### Classification Boundaries

```python
CLASSIFICATIONS = {
    "Phoenix": ScoreRange(min=7.0, max=10.0),  # High growth
    "Salt": ScoreRange(min=4.0, max=7.0),     # Stable
    "Lead": ScoreRange(min=0.0, max=4.0)      # Struggling
}
```

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Ready for Implementation*
*Version: 1.0*
