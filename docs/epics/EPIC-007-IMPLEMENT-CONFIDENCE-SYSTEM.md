# EPIC-007: Implement Confidence Scoring System

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 5 story points
## Sprint: Must be completed before production use

---

## Problem Statement

The confidence scoring system is **completely disabled**. All confidence levels are reset to UNKNOWN and confidence weighting never applies.

### Current Broken State
```python
# In run_eneve_199.py - signal_confidences NEVER populated
return Company(
    ...
    # signal_confidences NOT SET (defaults to {})
)

# In scoring.py line 115
if profile.signal_confidences:  # ALWAYS FALSE (empty dict)
    weighted_score = self._apply_confidence_weighting(score, profile, component)
    # This code NEVER executes
```

### Impact
- **Confidence weighting completely disabled**
- **All scores use weight 1.0** regardless of data quality
- **Low-confidence data treated same as high-confidence**
- **Cannot differentiate reliable vs unreliable signals**
- **Investment decisions based on potentially poor data**

---

## Success Criteria

- [ ] signal_confidences populated for all companies
- [ ] Confidence levels mapped correctly ("high" → CONFIRMED, "medium" → ESTIMATED)
- [ ] Confidence weighting applied in scoring
- [ ] Low-confidence data reduces score weight
- [ ] High-confidence data increases score weight
- [ ] Confidence scores displayed in output

---

## Technical Analysis

### Root Causes
1. **signal_confidences not populated** in run_eneve_199.py
2. **ConfidenceLevel enum values** not mapped to numeric weights
3. **_confidence_weight function** exists but never called
4. **Input confidence strings** ("high"/"medium"/"low") not extracted

### Affected Files
- `scripts/run_eneve_199.py` (main issue)
- `src/solstein/analytics/scoring.py`
- `src/solstein/domain/models.py`
- `src/solstein/data/loaders.py`

---

## Stories

### Story 7.1: Extract Confidence from Input Data
**Priority:** P0 | **Effort:** 2 points

**Description:**
Extract confidence levels from all input fields and map to domain enum values.

**Acceptance Criteria:**
- [ ] Map "high" → ConfidenceLevel.CONFIRMED
- [ ] Map "medium" → ConfidenceLevel.ESTIMATED
- [ ] Map "low" → ConfidenceLevel.UNKNOWN
- [ ] Extract confidence from: revenue, employees, funding, valuation, AI
- [ ] Handle missing confidence gracefully (default to UNKNOWN)
- [ ] Add validation for unexpected confidence values

**Implementation:**
```python
# In run_eneve_199.py

confidence_map = {
    "high": ConfidenceLevel.CONFIRMED,
    "medium": ConfidenceLevel.ESTIMATED,
    "low": ConfidenceLevel.UNKNOWN,
}

# Extract from revenue timeline
revenue_data = data.get("revenue", {})
latest_revenue = revenue_data.get("timeline", [{}])[0]
revenue_confidence = confidence_map.get(
    latest_revenue.get("confidence", ""),
    ConfidenceLevel.UNKNOWN
)

# Extract from other fields
employees_confidence = confidence_map.get(
    data.get("employees_confidence", ""),
    ConfidenceLevel.UNKNOWN
)
funding_confidence = confidence_map.get(
    data.get("funding_confidence", ""),
    ConfidenceLevel.UNKNOWN
)
valuation_confidence = confidence_map.get(
    data.get("valuation_confidence", ""),
    ConfidenceLevel.UNKNOWN
)
ai_confidence = confidence_map.get(
    data.get("ai_confidence", ""),
    ConfidenceLevel.UNKNOWN
)
```

---

### Story 7.2: Populate signal_confidences Dictionary
**Priority:** P0 | **Effort:** 2 points

**Description:**
Build and populate the signal_confidences dictionary when creating Company objects.

**Acceptance Criteria:**
- [ ] Create signal_confidences dict with all signal types
- [ ] Map confidence levels to numeric weights (0.0-1.0)
- [ ] Pass to Company constructor
- [ ] Verify dictionary is not empty in output
- [ ] Document signal types and weights

**Implementation:**
```python
# In run_eneve_199.py

# Map confidence levels to numeric weights
confidence_weights = {
    ConfidenceLevel.CONFIRMED: 1.0,
    ConfidenceLevel.ESTIMATED: 0.7,
    ConfidenceLevel.UNKNOWN: 0.3,
}

signal_confidences = {
    "revenue": confidence_weights[revenue_confidence],
    "growth_rate": confidence_weights[revenue_confidence],  # Same as revenue
    "employees": confidence_weights[employees_confidence],
    "funding": confidence_weights[funding_confidence],
    "valuation": confidence_weights[valuation_confidence],
    "ai_maturity": confidence_weights[ai_confidence],
}

# Pass to Company constructor
return Company(
    ...
    signal_confidences=signal_confidences,
    ...
)
```

---

### Story 7.3: Enable Confidence Weighting in Scoring
**Priority:** P0 | **Effort:** 2 points

**Description:**
Fix the scoring logic to apply confidence weighting when signal_confidences is populated.

**Acceptance Criteria:**
- [ ] Change condition from `if profile.signal_confidences:` to check for non-empty
- [ ] Apply _confidence_weight to all scoring components
- [ ] Weight affects final composite score
- [ ] Log confidence weighting for debugging
- [ ] Verify weighting changes scores appropriately

**Implementation:**
```python
# In scoring.py

def calculate_scores(self, profile: Company) -> Company:
    ...
    
    # Apply confidence weighting if available
    if profile.signal_confidences and len(profile.signal_confidences) > 0:
        growth_score = self._apply_confidence_weighting(
            growth_score, profile, "growth"
        )
        financial_health_score = self._apply_confidence_weighting(
            financial_health_score, profile, "financial"
        )
        competitive_position_score = self._apply_confidence_weighting(
            competitive_position_score, profile, "competitive"
        )
        logger.debug(f"Applied confidence weighting for {profile.name}")
    
    # Calculate composite
    profile.composite_score = round(
        (growth_score * self.config.growth_weight) +
        (financial_health_score * self.config.financial_weight) +
        (competitive_position_score * self.config.competitive_weight),
        2
    )
    ...
```

---

### Story 7.4: Display Confidence in Output
**Priority:** P1 | **Effort:** 1 point

**Description:**
Add confidence scores to output data and Excel export.

**Acceptance Criteria:**
- [ ] Add confidence_weight to scored output JSON
- [ ] Display confidence level in Excel (High/Medium/Low)
- [ ] Show confidence breakdown by signal type
- [ ] Color-code cells based on confidence (green/yellow/red)
- [ ] Add confidence legend to Excel

**Implementation:**
```python
# In Excel export
confidence_level = "High" if avg_confidence > 0.8 else "Medium" if avg_confidence > 0.5 else "Low"
cell = ws.cell(row=row, column=confidence_col, value=confidence_level)

# Color coding
if confidence_level == "High":
    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
elif confidence_level == "Medium":
    cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
else:
    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
```

---

## Dependencies

- Story 7.1 must be done before Story 7.2
- Story 7.2 must be done before Story 7.3
- Story 7.4 can be done in parallel with 7.3

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Confidence weighting changes all scores | High | Recalculate baseline, notify users |
| Confidence mapping incorrect | Medium | Validate mapping with sample data |
| Performance impact from weighting | Low | Benchmark scoring performance |

## Definition of Done

- [ ] signal_confidences populated for all companies
- [ ] Confidence levels correctly mapped
- [ ] Confidence weighting applied in scoring
- [ ] Confidence displayed in output and Excel
- [ ] Unit tests verify confidence weighting
- [ ] Documentation updated with confidence system
