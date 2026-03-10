# STORY-206: Implement Company Model Field Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-059 Input Validation & Graceful Degradation |
| **Created** | 2026-03-01 |
| **Risk** | Medium — validation could reject currently-accepted data |
| **Assigned** | — |
| **Depends On** | EPIC-047 (Data Loading Fidelity) |

---

## Audit Verdict

**CONFIRMED DEFECT** — The `Company` model accepts incomplete data without validation. Fields critical to scoring can be None without warnings.

Current behavior:
```python
company = Company(
    name="ABB",
    financials=FinancialMetrics(growth_rate=None, revenue=None),
    ai_score=None
)
# ✅ Accepted, no validation error
# Scoring engine receives incomplete data and produces low scores
```

Desired behavior: Validation prevents data from reaching the scorer if critical fields are missing or malformed.

---

## Problem Statement

The `Company` domain model has no field validation. The scoring engine can receive companies with:
- `revenue = None` when JSON has `33219.999744`
- `growth_rate = None` when JSON has `5.4`
- `ai_score = None` when JSON has `7.5`
- `employees = 0` (invalid — indicates no data)
- Negative margins, growth rates > 100%, etc.

Without validation, bad data silently flows to scorer, producing meaningless scores. Real data converts correctly now (EPIC-058), but validation will catch future regressions and data format changes.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Data Quality | 🔴 Critical — Invalid data passes silently |
| Scoring Correctness | 🔴 Critical — Scorer receives malformed inputs |
| Debuggability | 🟠 High — Silent failures hard to trace |
| Robustness | 🟠 High — No guard against future field loss |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/domain/models.py` | `Company`, `FinancialMetrics` classes | Add Pydantic validators |
| `tests/unit/test_domain_models.py` | NEW | Validation test suite |

---

## Dependencies

- **Soft**: EPIC-047 (Data Loading Fidelity) — field mapping should be correct
- **Blocks**: STORY-207, STORY-209

---

## Architectural Requirements

**REQ-1**: `Company` model uses Pydantic validators for:
- Required fields: `name`, `revenue`, `growth_rate`, `ai_score`, `employees`
- Range validation: `revenue > 0`, `growth_rate ∈ [-100, 100]`, `ai_score ∈ [0, 10]`
- Type safety: All numeric fields are float, not None

**REQ-2**: Validation errors include field name and reason (e.g., "revenue must be > 0, got: -500").

**REQ-3**: Validation is logged but doesn't block loading (graceful degradation in STORY-207).

---

## Acceptance Criteria

- [ ] `Company(name=None)` raises `ValidationError`
- [ ] `Company(revenue=-500)` raises `ValidationError`
- [ ] `Company(growth_rate=150)` raises `ValidationError` (>100%)
- [ ] `Company(ai_score=11)` raises `ValidationError` (>10)
- [ ] `Company(revenue=0)` raises `ValidationError` (must be > 0)
- [ ] Valid company `Company(name="Test", revenue=1000, growth_rate=5, ai_score=7, employees=100)` passes
- [ ] Unit test suite covers all validation rules
- [ ] Error messages are user-facing (explain the problem)

---

## Definition of Done

- [ ] Validators implemented in domain model
- [ ] All validation rules documented
- [ ] Unit tests verify all rules
- [ ] Error messages are clear
- [ ] Real data loads without validation errors (backward compatible)

---

## Implementation Notes

### Validator Pattern (Pydantic v2)

```python
from pydantic import BaseModel, field_validator

class Company(BaseModel):
    name: str
    revenue: float
    growth_rate: float
    ai_score: float
    employees: int
    
    @field_validator('revenue')
    @classmethod
    def revenue_positive(cls, v):
        if v <= 0:
            raise ValueError('revenue must be > 0')
        return v
    
    @field_validator('growth_rate')
    @classmethod
    def growth_rate_bounded(cls, v):
        if v < -100 or v > 100:
            raise ValueError('growth_rate must be ∈ [-100, 100]')
        return v
    
    @field_validator('ai_score')
    @classmethod
    def ai_score_bounded(cls, v):
        if v < 0 or v > 10:
            raise ValueError('ai_score must be ∈ [0, 10]')
        return v
```

### Files to Create/Modify

- `src/solstein/domain/models.py` - Add validators
- `tests/unit/test_domain_models.py` - Comprehensive validator tests (NEW)

### Risk Mitigation

- Validation might reject old data → Check compatibility with existing companies
- Performance impact → Validators run once per company (negligible)
- False positives → Review validation rules against real data distribution

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | No field validation; invalid data passes silently |
