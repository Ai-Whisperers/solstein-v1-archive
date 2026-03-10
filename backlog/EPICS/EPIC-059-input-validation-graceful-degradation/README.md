# EPIC-059: Input Validation & Graceful Degradation

> **Priority**: P1 – High (prevents silent data corruption)  
> **Stories**: 5 (STORY-206 through STORY-210)  
> **Effort**: M (3–4 days total)  
> **Dependencies**: EPIC-047 (Data Loading Fidelity), EPIC-046 (Scoring Engine Correctness)  
> **Status**: 🔴 Not Started

---

## Problem

The data pipeline silently accepts incomplete or invalid data, passes it through multiple transformation stages, and only fails validation at the export gate. This creates:

1. **Silent None Propagation**: Fields become None during conversion, propagate through scoring untested, only fail at export
2. **No Input Validation**: Company model accepts all fields as optional with no validation that minimum set exists
3. **Scoring Handles None Ungracefully**: GrowthScorer doesn't validate inputs → produces weak/misleading scores with missing data
4. **Confidence Scores Lost**: Metric lineage confidence (0.72–0.78) not extracted or used in weighting
5. **Meaningless Classifications**: All companies score as "Lead" when financial data missing → thresholds become useless

### Issue Examples from Real Run

| Stage | Input | Processing | Output | Problem |
|-------|-------|-----------|--------|---------|
| **Load** | `revenue: 33219.999744, growth_rate: 5.4` | Converter picks nested vs flat | Some fields become None | Wrong converter path chosen |
| **Convert** | Incomplete FinancialMetric | No validation | Company with null fields | Model allows empty financial data |
| **Score** | Company with `growth_rate=None` | Scoring ignores, scores as 0 | Low score, "Lead" classification | Should warn or skip field |
| **Export** | Incomplete scored data | Release gate checks provenance | BLOCKED: "completeness" | Too late to fix data |

---

## Root Causes

1. **No Contract on Input**: Company model doesn't enforce minimum financial data
2. **No Graceful Fallback**: Scoring assumes presence, doesn't handle None
3. **No Validation at Boundaries**: Conversions don't validate output
4. **Confidence Data Ignored**: Metric lineage confidence extracted but never used
5. **No Continue-on-Warning Mode**: Hard failure at gate instead of degraded scoring

---

## Stories

| Story | Title | Priority | Size | Notes |
|-------|-------|----------|------|-------|
| STORY-206 | Add input validation to Company model (require revenue OR employees) | P1 | S | Either one must be present, halt on both-missing |
| STORY-207 | Add None-safety checks in GrowthScorer and CompetitivePositionScorer | P1 | M | Skip scoring for None fields, reduce confidence weight |
| STORY-208 | Extract and apply metric_lineage confidence to signal_confidences | P1 | M | Confidence 0.72→weight 0.72 applied to score component |
| STORY-209 | Add conversion output validation before Company construction | P1 | S | Fail fast if conversion loses too many fields |
| STORY-210 | Implement graceful degradation mode for incomplete data | P2 | M | Score with warnings instead of blocking export |

---

## Definition of Done

- [ ] Company model validates that revenue OR employees is present (not both missing)
- [ ] FinancialMetric warns if >50% of fields are None
- [ ] Scoring code handles None gracefully without crashes or arbitrary defaults
- [ ] Metric lineage confidence extracted and wired into signal_confidences
- [ ] Converter validates output and fails fast if critical fields lost
- [ ] Scoring produces consistent thresholds even with partial data
- [ ] All conversion and scoring tests pass with real data

---

## Acceptance Criteria

**AC-1**: A company with `revenue=None, employees=100, growth_rate=None` is accepted and scored, but confidence is reduced (signal_confidences show weights <1.0).

**AC-2**: GrowthScorer with `growth_rate=None` doesn't crash; instead, it skips the growth component and logs a warning.

**AC-3**: Metric lineage confidence 0.72 on `revenue` field translates to 0.72 multiplier on revenue-dependent scoring components.

**AC-4**: Conversion output validation catches when >30% of expected financial fields are missing and logs error before export.

**AC-5**: Companies with missing growth_rate are not all classified as "Lead" — classification reflects other signals.

---

## Implementation Notes

### Validation Strategy

```python
class FinancialMetric(BaseModel):
    # Current: all optional
    revenue: float | None = None
    employees: int | None = None
    
    # NEW: Require at least one primary indicator
    @model_validator(mode='after')
    def at_least_one_primary(self) -> 'FinancialMetric':
        if self.revenue is None and self.employees is None:
            raise ValueError("At least revenue OR employees must be provided")
        return self
```

### Confidence Weighting

```python
# Extract from metric_lineage
signal_confidences = {
    "revenue": 0.78,  # From metric_lineage["revenue"]["confidence"]
    "growth_rate": 0.72,
    "employees": 0.70,
}

# Apply in scoring
revenue_component_value = 3.5
confidence_weight = signal_confidences.get("revenue", 1.0)  # 0.78
revenue_component_weighted = 3.5 * 0.78  # 2.73
```

### Graceful Degradation Mode

```python
# Option A: Skip missing fields
if company.financials.growth_rate is None:
    logger.warning(f"Skipping growth component for {company.name}")
    # Don't add to composite score, reduce confidence

# Option B: Continue-on-warning
def score_with_confidence(company, require_fields=[]):
    missing = [f for f in require_fields if getattr(company.financials, f) is None]
    if missing:
        logger.warning(f"Scoring with missing: {missing}")
    return calculate_score(company)
```

### Testing

Add test fixtures for:
- Company with only revenue
- Company with only employees
- Company with both None (should fail validation)
- Company with partial growth_rate (should score with reduced confidence)
