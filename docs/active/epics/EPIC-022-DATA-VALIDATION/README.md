# EPIC-022: Implement Data Validation Pipeline

> **Status**: 🔴 NOT STARTED
> **Priority**: P0 - Critical
> **Effort**: 13 story points
> **Sprint**: Data Quality Foundation
> **Related**: EPIC-013, EPIC-021, ROOT_CAUSE_ANALYSIS
> **Blocks**: EPIC-021 (confidence needs validation)

---

## 🚨 Problem Statement

The system has **no data validation pipeline**. Data flows through without validation, leading to:
- Unit inconsistencies (revenue "9" with no unit)
- Currency mismatches (CGI Inc. marked EUR but is USD)
- Magnitude errors (5000000 instead of 5.0)
- No detection of impossible values
- No cross-field validation

### Current State (No Validation)

```python
# ai_research_orchestrator.py - No validation
def _validate_research_data(self, data: Dict) -> Dict:
    # Current: Naive range checks only
    if data.get("revenue", 0) > 0:
        return data  # Passes with "9" or 5000000
    return data
```

**Examples of Bad Data Getting Through:**

| Company | Field | Value | Problem |
|---------|-------|-------|---------|
| CGI Inc. | currency | EUR | Actually USD company |
| Unknown | revenue | 9 | No unit (M? B? raw?) |
| Unknown | revenue | 5000000 | Should be 5.0 (in millions) |
| Eneve | website | eneve-energy.com | Actually different company |

### Impact

| Impact Area | Current State | Risk Level |
|-------------|---------------|------------|
| **Data Comparability** | Cannot compare companies | 🔴 Critical |
| **Scoring Accuracy** | Wrong magnitudes break scores | 🔴 Critical |
| **Decision Making** | Decisions on bad data | 🔴 Critical |
| **System Trust** | Users see obvious errors | 🔴 Critical |
| **Reconciliation** | Cannot merge datasets | 🟡 High |

### Root Cause Analysis Reference

See `docs/ROOT_CAUSE_ANALYSIS.md` - Section "Root Cause 3: Data Quality Cascade"

---

## 🎯 Success Criteria

- [ ] Unit validation for all financial fields (revenue, valuation)
- [ ] Currency verification against company headquarters
- [ ] Magnitude validation (flags values like 5000000)
- [ ] Cross-field validation (revenue_growth consistent with revenue)
- [ ] Impossible value detection (negative employees, etc.)
- [ ] Validation errors logged with context
- [ ] Invalid data flagged for review, not silently accepted
- [ ] All existing tests pass with validation

---

## 📊 Current vs Target State

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Unit Consistency** | 0% | >95% | Manual sample check |
| **Currency Accuracy** | ~60% | >95% | Known companies check |
| **Magnitude Errors** | Common | Rare | <1% of records |
| **Cross-Field Valid** | No | Yes | Revenue vs growth check |
| **Impossible Values** | Pass | Blocked | Negative employees, etc. |

---

## 📚 Technical Analysis

### Validation Categories

1. **Field-Level Validation**
   - Type checking (number vs string)
   - Range validation (revenue > 0)
   - Format validation (URL, email)

2. **Unit Validation**
   - Revenue in consistent units (millions)
   - Valuation in consistent units
   - Employee count as integer

3. **Currency Validation**
   - Match currency to headquarters country
   - Flag suspicious mismatches

4. **Cross-Field Validation**
   - Revenue growth consistent with year-over-year revenue
   - Valuation reasonable given revenue (P/S ratio check)
   - Employee count reasonable given revenue

5. **Business Rule Validation**
   - No negative values for positive-only fields
   - Founded date in reasonable range
   - Funding rounds chronological

### Implementation Location

```
src/solstein/validation/
├── __init__.py
├── models.py                    # Validation result models
├── field_validators.py          # Individual field validators
├── unit_validators.py           # Unit consistency validators
├── cross_field_validators.py    # Cross-field validators
└── pipeline.py                  # Validation orchestration
```

---

## 📖 Stories Overview

| Story | Title | Priority | Points | Dependencies |
|-------|-------|----------|--------|--------------|
| 22.1 | Implement Field-Level Validators | P0 | 3 | None |
| 22.2 | Implement Unit Validation | P0 | 3 | 22.1 |
| 22.3 | Implement Currency Validation | P0 | 2 | 22.1 |
| 22.4 | Implement Cross-Field Validation | P0 | 3 | 22.2, 22.3 |
| 22.5 | Integrate Validation into Pipeline | P1 | 2 | 22.4 |

**Total Stories**: 5
**Total Points**: 13

---

## 🔗 Dependencies

```
Story 22.1 (Field Validators)
    ├── Story 22.2 (Unit Validation)
    │   └── Story 22.4 (Cross-Field)
    └── Story 22.3 (Currency Validation)
        └── Story 22.4 (Cross-Field)
            └── Story 22.5 (Pipeline Integration)
```

---

## ⚠️ Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Overly strict validation rejects good data | Medium | High | Configurable strictness levels |
| Performance impact from validation | Low | Medium | Benchmark, optimize hot paths |
| Currency/country mapping incomplete | High | Medium | Use comprehensive dataset |
| Breaking change to data flow | Medium | High | Feature flag, gradual rollout |

---

## ✅ Definition of Done

- [ ] All 5 stories completed and code reviewed
- [ ] Unit validation working for financial fields
- [ ] Currency validation catching mismatches
- [ ] Cross-field validation implemented
- [ ] Validation errors logged with context
- [ ] Invalid data flagged (not silently accepted)
- [ ] All existing tests pass
- [ ] New tests added for validators
- [ ] Performance benchmark shows <10% regression
- [ ] Documentation updated

---

## 📁 Epic Structure

```
docs/active/epics/EPIC-022-DATA-VALIDATION/
├── README.md                                    # This file
├── STORY-22.1-FIELD-VALIDATORS.md              # Field-level validation
├── STORY-22.2-UNIT-VALIDATION.md               # Unit consistency
├── STORY-22.3-CURRENCY-VALIDATION.md           # Currency verification
├── STORY-22.4-CROSS-FIELD-VALIDATION.md        # Cross-field validation
├── STORY-22.5-PIPELINE-INTEGRATION.md          # Integrate into pipeline
├── VALIDATION-RULES.md                         # Complete validation rules
└── VALIDATION-EXAMPLES.md                      # Example validations
```

---

## 🔗 Related Documentation

- [ROOT_CAUSE_ANALYSIS.md](../../../../ROOT_CAUSE_ANALYSIS.md) - Root cause context
- [EPIC-021](../EPIC-021-CONFIDENCE-SCORING-FIX/) - Confidence scoring (uses validation)
- [EPIC-024](../EPIC-024-SCORING-ALGORITHM/) - Scoring algorithm (needs validated data)
- `src/solstein/research/ai_research_orchestrator.py` - Current validation (none)

---

## 📝 Notes

### Validation Rule Examples

```python
# Unit validation
if revenue > 1000 and revenue < 1000000:
    flag_warning("Revenue may be in wrong units", company_id)

# Currency validation
if headquarters_country == "USA" and currency != "USD":
    flag_error("Currency mismatch with headquarters", company_id)

# Cross-field validation
if revenue_growth_annual > 0 and revenue_current <= revenue_previous:
    flag_error("Revenue growth inconsistent with revenue values", company_id)
```

### Strictness Levels

- **STRICT**: Reject invalid data (for new imports)
- **WARN**: Log warnings but accept (for existing data)
- **AUDIT**: Only log, no action (for analysis)

---

*Created: 2026-03-11*
*Updated: 2026-03-11*
*Status: Ready for Implementation*
*Version: 1.0*
