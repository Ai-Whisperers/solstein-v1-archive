# STORY-205: Add Golden-Dataset Format Verification Test

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-058 Data Conversion Pipeline Consolidation |
| **Created** | 2026-03-01 |
| **Risk** | Low — test-only; establishes regression safety net |
| **Assigned** | — |
| **Depends On** | STORY-202, STORY-203, STORY-204 |

---

## Audit Verdict

**CONFIRMED NEED** — No regression test exists for data format handling. When conversion logic changes, there is no automated check that fields aren't lost.

Current state:
- Real data (flat JSON): Manual verification only, field loss discovered by visual inspection
- Nested data: No test fixtures
- Mixed data: Untested

Needed: Automated verification that prevents future field loss regressions.

---

## Problem Statement

The conversion pipeline has been modified multiple times without regression tests. Each change risks silent field loss. Without a golden dataset test, defects are discovered in production (manual dashboard inspection) rather than in CI/CD.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Code Safety | 🔴 Critical — No safety net for conversion changes |
| Regression Detection | 🔴 Critical — Defects slip to production unnoticed |
| CI/CD Quality Gates | 🟠 High — No automated prevention of field loss |
| Developer Confidence | 🟠 High — Can't safely refactor conversion logic |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `data/test/golden_dataset_real.json` | NEW | 100+ real companies (duplicate of input data) |
| `tests/integration/test_data_conversion_parity.py` | NEW | Format verification test suite |

---

## Dependencies

- **Hard**: STORY-202, STORY-203, STORY-204 (implementation must be done first)
- **Blocks**: Nothing; safety net story

---

## Architectural Requirements

**REQ-1**: Golden dataset test loads 100+ real companies and verifies:
- No field with non-None value in JSON becomes None in Company object
- Confidence values from `metric_lineage` are preserved
- Both flat and nested structures load without loss

**REQ-2**: Test failure includes explicit field-by-field comparison showing what was lost.

**REQ-3**: Test runs as part of CI/CD and blocks merges if field loss detected.

---

## Acceptance Criteria

- [ ] Test loads real JSON from `data/test/golden_dataset_real.json` (100+ companies)
- [ ] For each company: JSON field → Company attribute mapping verified
- [ ] Test identifies any None that should be non-None (e.g., growth_rate should be 5.4, not None)
- [ ] Test verifies confidences from metric_lineage are stored in signal_confidences
- [ ] Flat structure test passes (real data format)
- [ ] Nested structure test passes (backward compatibility)
- [ ] Mixed format batch test passes
- [ ] CI/CD runs test on every merge and blocks on failure
- [ ] Test output shows field-by-field mapping (debug visibility)

---

## Definition of Done

- [ ] Golden dataset fixture created
- [ ] Parity test implemented for all known formats
- [ ] Test detects field loss and reports specifically what was lost
- [ ] CI/CD integration complete
- [ ] Baseline run passes (no pre-existing field loss)

---

## Implementation Notes

### Test Structure

```python
def test_flat_json_conversion_parity():
    """Verify flat JSON structure is loaded without field loss."""
    with open("data/test/golden_dataset_real.json") as f:
        golden_data = json.load(f)
    
    for raw_company in golden_data:
        company = convert_to_domain_company(raw_company)
        
        # For each top-level field with a value, Company must have non-None value
        for field_name in ["revenue", "growth_rate", "profit_margin"]:
            if field_name in raw_company and raw_company[field_name] is not None:
                assert getattr(company.financials, field_name) is not None, \
                    f"{field_name} lost during conversion for {company.name}"
        
        # Confidence values must be preserved
        for field_name in raw_company.get("metric_lineage", {}):
            assert field_name in company.signal_confidences, \
                f"{field_name} confidence not preserved for {company.name}"

def test_score_distribution_stability():
    """Verify conversion changes don't affect Phoenix/Salt/Lead percentages."""
    companies = load_all_golden_companies()
    scores = [score_company(c) for c in companies]
    
    phoenix_pct = sum(1 for s in scores if s.classification == "Phoenix") / len(scores)
    salt_pct = sum(1 for s in scores if s.classification == "Salt") / len(scores)
    lead_pct = sum(1 for s in scores if s.classification == "Lead") / len(scores)
    
    # Percentages should not change more than 2% from baseline
    assert abs(phoenix_pct - 0.25) < 0.02, f"Phoenix pct: {phoenix_pct}"
    assert abs(salt_pct - 0.50) < 0.02, f"Salt pct: {salt_pct}"
    assert abs(lead_pct - 0.25) < 0.02, f"Lead pct: {lead_pct}"
```

### Files to Create/Modify

- `data/test/golden_dataset_real.json` - 100+ real companies (NEW - can copy from competitor_data_real_enriched.json)
- `tests/integration/test_data_conversion_parity.py` - Full test suite (NEW)
- `.github/workflows/ci.yml` - Add test to CI pipeline

### Risk Mitigation

- Golden dataset might be outdated → Use live data as fixture
- Test might be too strict → Allow 1-2% score distribution variance
- Performance impact → Run in separate CI job if needed

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified lack of regression tests for conversion pipeline |
