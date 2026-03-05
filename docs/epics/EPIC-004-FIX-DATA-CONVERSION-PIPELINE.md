# EPIC-004: Fix Data Conversion Pipeline

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 8 story points
## Sprint: Must be completed before production use

---

## Problem Statement

The data conversion pipeline loses **30+ fields** during transformation from input JSON to output scored data. Critical fields are dropped, incorrectly mapped, or reset to default values.

### Current Broken State
```python
# Input has:
- data_quality_score: 0.75
- classification_confidence: 0.95
- revenue.cagr_3yr_pct: 45.0
- profitability.ebitda_margin_pct: 30.0
- employees_confidence: "confirmed"

# Output has:
- data_quality_score: MISSING
- classification_confidence: MISSING
- revenue_cagr_3yr: MISSING
- ebitda_margin: 30.0 (extracted but rest lost)
- employees_confidence: UNKNOWN (reset)
```

### Impact
- **30+ fields lost** during conversion
- **enrichment_source_count reset to 0** (was 2-5 in input)
- **Confidence levels reset to UNKNOWN** (was "high"/"medium"/"low")
- **CAGR data lost** (revenue.cagr_3yr_pct, revenue.cagr_5yr_pct)
- **Profitability details lost** (only ebitda_margin extracted)

---

## Success Criteria

- [ ] All input fields mapped to output or explicitly documented as dropped
- [ ] enrichment_source_count correctly propagated (2-5 in input → 2-5 in output)
- [ ] Confidence levels correctly mapped ("high" → CONFIRMED, "medium" → ESTIMATED)
- [ ] CAGR data preserved and accessible
- [ ] Profitability object fully mapped
- [ ] Data loss audit shows 0 unexpected losses
- [ ] Field mapping documentation complete

---

## Technical Analysis

### Conversion Points
1. **loaders.py**: JSON → Company (lines 95-386)
2. **run_eneve_199.py**: Custom converter (lines 20-96)
3. **research/pipeline.py**: Research → Scored
4. **research/gather.py**: Signals → Company

### Root Causes
1. **Missing field extraction** in run_eneve_199.py
2. **Field name mismatches** between input and domain model
3. **Default values overriding** real data
4. **Nested objects not fully mapped** (profitability, revenue timeline)

### Affected Files
- `scripts/run_eneve_199.py` (main issue)
- `src/solstein/data/loaders.py`
- `src/solstein/research/gather.py`
- `src/solstein/domain/models.py`

---

## Stories

### Story 4.1: Complete Field Mapping Audit
**Priority:** P0 | **Effort:** 3 points

**Description:**
Create comprehensive field mapping documentation and identify all lost fields.

**Acceptance Criteria:**
- [ ] List all 41 input fields from tests/fixtures/synthetic/competitor_data_199.json
- [ ] List all 78 output fields from scored output
- [ ] Identify 30 lost fields with specific paths
- [ ] Create field mapping matrix (input → output → status)
- [ ] Document why each field is lost or mapped
- [ ] Identify fields that should be preserved but aren't

**Field Mapping Matrix:**
```
| Input Field | Output Field | Status | Notes |
|-------------|--------------|--------|-------|
| data_quality_score | - | LOST | Not extracted in run_eneve_199.py |
| classification_confidence | - | LOST | Not extracted |
| revenue.cagr_3yr_pct | revenue_cagr_3yr | LOST | Not extracted from timeline |
| profitability.ebitda_margin_pct | financials.ebitda_margin | MAPPED | Correctly extracted |
| employees_confidence | financials.employees_confidence | RESET | Always set to UNKNOWN |
```

---

### Story 4.2: Fix Confidence Level Mapping
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix confidence level mapping from input strings to domain enum values.

**Acceptance Criteria:**
- [ ] Map "high" → ConfidenceLevel.CONFIRMED
- [ ] Map "medium" → ConfidenceLevel.ESTIMATED
- [ ] Map "low" → ConfidenceLevel.UNKNOWN
- [ ] Extract confidence from all input fields (revenue, employees, funding, etc.)
- [ ] Populate signal_confidences dictionary
- [ ] Add validation for unexpected confidence values

**Implementation:**
```python
# In run_eneve_199.py

confidence_map = {
    "high": ConfidenceLevel.CONFIRMED,
    "medium": ConfidenceLevel.ESTIMATED,
    "low": ConfidenceLevel.UNKNOWN,
}

# Extract confidence from revenue timeline
revenue_confidence = confidence_map.get(
    latest_revenue.get("confidence", ""),
    ConfidenceLevel.UNKNOWN
)

# Extract employee confidence
employees_confidence = confidence_map.get(
    data.get("employees_confidence", ""),
    ConfidenceLevel.UNKNOWN
)

# Build signal_confidences
signal_confidences = {
    "revenue": confidence_map.get(data.get("revenue", {}).get("confidence"), 0.5),
    "employees": confidence_map.get(data.get("employees_confidence"), 0.5),
    "funding": confidence_map.get(data.get("funding_confidence"), 0.5),
    "valuation": confidence_map.get(data.get("valuation_confidence"), 0.5),
    "ai": confidence_map.get(data.get("ai_confidence"), 0.5),
}
```

---

### Story 4.3: Preserve CAGR Data
**Priority:** P0 | **Effort:** 2 points

**Description:**
Extract and preserve CAGR (Compound Annual Growth Rate) data from revenue timeline.

**Acceptance Criteria:**
- [ ] Extract revenue.cagr_3yr_pct from input
- [ ] Extract revenue.cagr_5yr_pct from input
- [ ] Map to Company.revenue_cagr_3yr and Company.revenue_cagr_5yr
- [ ] Handle missing CAGR gracefully (set to None)
- [ ] Use CAGR in growth scoring if available
- [ ] Display CAGR in Excel export

**Implementation:**
```python
# In run_eneve_199.py

revenue_data = data.get("revenue", {})
revenue_cagr_3yr = revenue_data.get("cagr_3yr_pct")
revenue_cagr_5yr = revenue_data.get("cagr_5yr_pct")

# In Company model
revenue_cagr_3yr: Optional[float] = None
revenue_cagr_5yr: Optional[float] = None

# In growth scoring
if financials.revenue_cagr_3yr:
    # Use CAGR as additional growth signal
    cagr_bonus = min(financials.revenue_cagr_3yr / 20, 2.0)
    score += cagr_bonus
```

---

### Story 4.4: Fix enrichment_source_count Propagation
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix the pipeline so enrichment_source_count is correctly passed from input to output.

**Acceptance Criteria:**
- [ ] Trace enrichment_source_count through all conversion points
- [ ] Fix any resets to 0
- [ ] Ensure count matches actual sources list length
- [ ] Add validation: count == len(enrichment_sources)
- [ ] Log discrepancies for debugging

**Investigation Path:**
1. Input JSON: `enrichment_source_count: 3`
2. run_eneve_199.py: Extract and pass to Company
3. Company model: Store in enrichment_source_count field
4. Scoring: Preserve in scored output
5. Output JSON: `enrichment_source_count: 3`

**Fix:**
```python
# In run_eneve_199.py
enrichment_source_count = data.get("enrichment_source_count", 0)

# In Company creation
return Company(
    ...
    enrichment_source_count=enrichment_source_count,
    ...
)

# In domain/models.py - ensure field exists
enrichment_source_count: int = Field(default=0)
```

---

### Story 4.5: Map Profitability Object Completely
**Priority:** P1 | **Effort:** 2 points

**Description:**
Fully map the profitability object from input to financials.

**Acceptance Criteria:**
- [ ] Map profitability.ebitda_margin_pct → financials.ebitda_margin
- [ ] Map profitability.recurring_revenue_pct → financials.recurring_revenue_pct
- [ ] Map profitability.revenue_per_employee_eur_k → financials.revenue_per_employee
- [ ] Map profitability.confidence → financials.profit_margin_confidence
- [ ] Handle missing profitability fields gracefully

**Implementation:**
```python
# In run_eneve_199.py

profitability = data.get("profitability", {})

financials = FinancialMetric(
    ...
    ebitda_margin=profitability.get("ebitda_margin_pct"),
    recurring_revenue_pct=profitability.get("recurring_revenue_pct"),
    revenue_per_employee=profitability.get("revenue_per_employee_eur_k"),
    profit_margin_confidence=confidence_map.get(
        profitability.get("confidence"),
        ConfidenceLevel.UNKNOWN
    ),
    ...
)
```

---

### Story 4.6: Preserve data_quality_score
**Priority:** P1 | **Effort:** 1 point

**Description:**
Extract and preserve data_quality_score from input to output.

**Acceptance Criteria:**
- [ ] Extract data_quality_score from input JSON
- [ ] Add data_quality_score field to Company model
- [ ] Pass through to scored output
- [ ] Display in Excel export

**Implementation:**
```python
# In run_eneve_199.py
data_quality_score = data.get("data_quality_score", 0.0)

# In Company model
data_quality_score: float = Field(default=0.0)

# In Company creation
return Company(
    ...
    data_quality_score=data_quality_score,
    ...
)
```

---

## Dependencies

- Story 4.1 should be done first to identify all issues
- Stories 4.2-4.6 can be done in parallel
- All stories must be completed before EPIC is done

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Field mapping changes break existing code | High | Comprehensive testing, gradual rollout |
| Missing fields discovered late | Medium | Thorough audit in Story 4.1 |
| Domain model changes affect database | Medium | Migration script for schema changes |

## Definition of Done

- [ ] Field mapping matrix complete
- [ ] All P0 fields preserved (confidence, CAGR, enrichment count)
- [ ] Data loss audit shows 0 unexpected losses
- [ ] Unit tests verify field preservation
- [ ] Integration tests verify end-to-end conversion
- [ ] Documentation updated with field mappings
