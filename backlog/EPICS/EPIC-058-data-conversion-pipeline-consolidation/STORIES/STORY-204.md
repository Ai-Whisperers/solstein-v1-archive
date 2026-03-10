# STORY-204: Wire Metric_Lineage Confidence into Company.signal_confidences

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< 1 day) |
| **Epic** | EPIC-058 Data Conversion Pipeline Consolidation |
| **Created** | 2026-03-01 |
| **Risk** | Low — wiring existing data; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-202 (Unified Converter) |

---

## Audit Verdict

**CONFIRMED CAPABILITY LOSS** — Real JSON contains `metric_lineage` with confidence scores (0.72–0.78), but these are stored without being wired into the scoring engine.

```json
{
  "metric_lineage": {
    "revenue": { "value": 33219.999744, "confidence": 0.78 },
    "growth_rate": { "value": 5.4, "confidence": 0.72 },
    "profit_margin": { "value": 14.25, "confidence": 0.65 }
  }
}
```

**Current behavior**: Values extracted, confidence discarded.
**Desired behavior**: Both value AND confidence flow to scoring engine.

---

## Problem Statement

Confidence scores (evidence of data quality) are lost during conversion. The `Company` model stores raw values but confidence metadata from `metric_lineage` is discarded. Scoring engine has no visibility into data quality.

This means:
- A revenue figure with 0.95 confidence is weighted same as one with 0.65 confidence
- Scoring decisions are based on point estimates, not on confidence-weighted data
- Export narratives cannot explain "we're 78% confident in this number"

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Scoring Accuracy | 🟡 Medium — Point estimates treated equally; confidence not used |
| Data Quality Signals | 🟡 Medium — Quality metadata exists but is invisible |
| Explainability | 🟡 Medium — Can't show users why we're confident in data |
| Signal Weighting | 🟠 High — Scoring should weight low-confidence inputs less |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/domain/models.py` | `Company` class | Add `signal_confidences: Dict[str, float]` field |
| `src/solstein/data/converters/company_extractors.py` | Extraction functions | Extract confidence from `metric_lineage` |
| `src/solstein/analytics/scoring.py` | Scorers | Use `signal_confidences` for weighting |
| `tests/unit/test_data_conversion.py` | NEW | Verify confidence preservation |

---

## Dependencies

- **Hard**: STORY-202 (Unified Converter) — must have conversion function
- **Soft**: EPIC-046 (Scoring Engine Correctness) — for using confidences in scoring

---

## Architectural Requirements

**REQ-1**: `Company.signal_confidences: Dict[str, float]` stores metric → confidence mapping.

```python
company.signal_confidences = {
    "revenue": 0.78,
    "growth_rate": 0.72,
    "profit_margin": 0.65
}
```

**REQ-2**: During conversion, extract confidence values from `metric_lineage[field_name]["confidence"]`.

**REQ-3**: Default to 0.50 (neutral) if no confidence metadata available (backward compatible with old data).

---

## Acceptance Criteria

- [ ] `Company` model has `signal_confidences: Dict[str, float]` field
- [ ] Enphase Energy loaded from real JSON has `signal_confidences["revenue"] = 0.78`
- [ ] Enphase Energy has `signal_confidences["growth_rate"] = 0.72`
- [ ] Old data format (without metric_lineage) loads with default 0.50 confidence
- [ ] Unit test: Load real JSON → verify all confidences extracted and stored
- [ ] Scoring engine can access confidence values for weighting

---

## Definition of Done

- [ ] `signal_confidences` field added to `Company` model
- [ ] Confidence extraction implemented in converters
- [ ] Backward compatibility for data without metric_lineage
- [ ] Unit test verifies extraction and storage
- [ ] Scoring engine prepared to use confidences (wiring in separate story)

---

## Implementation Notes

### Recommended Approach

```python
def extract_signal_confidences(raw_data: dict) -> Dict[str, float]:
    confidences = {}
    
    if "metric_lineage" in raw_data:
        lineage = raw_data["metric_lineage"]
        for field_name, metadata in lineage.items():
            if isinstance(metadata, dict) and "confidence" in metadata:
                confidences[field_name] = float(metadata["confidence"])
            else:
                confidences[field_name] = 0.50  # Default neutral
    
    # Fill in defaults for fields without metadata
    for field_name in ["revenue", "growth_rate", "profit_margin"]:
        if field_name not in confidences:
            confidences[field_name] = 0.50
    
    return confidences
```

### Files to Create/Modify

- `src/solstein/domain/models.py` - Add field
- `src/solstein/data/converters/company_extractors.py` - Add extraction function
- `src/solstein/data/loaders.py` - Call extraction during conversion
- `tests/unit/test_data_conversion.py` - Test confidence preservation

### Risk Mitigation

- Default confidence could mask old data quality issues → Log when defaults are used
- Scoring might break if it doesn't handle None → Add validation
- Old data loss → Backward compatible via defaults

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified metadata loss in conversion pipeline |
