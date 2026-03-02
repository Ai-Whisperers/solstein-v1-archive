# STORY-180: Add Field Mapping Parity Test Between Raw JSON and `Company` Objects

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-047 Data Loading Fidelity |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive test, no production code change |
| **Assigned** | — |

---

## Audit Verdict

**DESIGN GAP** — no automated test verifies that all JSON fields are mapped to Company attributes.

The bugs in STORY-177 (ai_score truncation), STORY-178 (funding not mapped), and STORY-179 (profitability fields missing) were only discovered by manual inspection during a live run. A parity test would have caught these at build time.

---

## Problem Statement

The `Company` domain model and the JSON input format evolve independently. When new fields are added to the JSON (e.g., a new enrichment source), there's no mechanism to ensure they're mapped to the domain model. Silent data loss occurs: the data is in the file but never reaches the scoring engine.

A parity test will:
1. Enumerate all leaf fields in the JSON schema
2. Verify each has a corresponding Company attribute
3. Verify type compatibility (float stays float, int stays int)
4. Fail the build if unmapped fields are found

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Maintainability | 🟠 High — prevents silent data loss on schema changes |
| Test Coverage | 🟠 High — currently no test covers field mapping completeness |
| Business Accuracy | 🟠 High — ensures all available data reaches scoring |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `tests/unit/test_loader_parity.py` | New (~150 lines) | New test module |
| `src/solstein/data/json_schema.py` | Optional | Schema definition for parity checking |
| `.github/workflows/ci.yml` | Optional | Ensure parity test runs in CI |

---

## Dependencies

- **Hard**: STORY-177, STORY-178, STORY-179 (fixes must land first so parity test passes)
- **Soft**: STORY-171 (loader migration — once unified, only one loader to test)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Create `tests/unit/test_loader_parity.py` with a test that:
1. Loads `data/input/competitor_data.json`
2. Recursively walks all JSON fields (including nested objects like `profitability`, `revenue.timeline`)
3. For each leaf field, asserts that a corresponding attribute exists on the loaded `Company` object
4. For each mapped field, asserts type compatibility (JSON number → Company float/int)

**REQ-2**: Allow an explicit allowlist for fields that are intentionally not mapped (e.g., internal IDs, deprecated fields). The allowlist must be documented with reasons.

**REQ-3**: The test must fail with a clear message showing:
- Which JSON fields are unmapped
- Which Company attributes exist but have no JSON source (orphaned attributes)
- Suggested attribute names for unmapped fields

**REQ-4**: The test must run in under 1 second (lightweight, no DB required).

---

## Acceptance Criteria

- [ ] `pytest tests/unit/test_loader_parity.py` passes after STORY-177/178/179 fixes
- [ ] Test fails if a new field is added to JSON without corresponding Company attribute
- [ ] Test output shows: `Unmapped JSON fields: ['profitability.new_field']`
- [ ] Test output shows: `Orphaned Company attributes: ['company.deprecated_field']`
- [ ] Test covers both `CompetitorDataLoader` and `UnifiedCompanyLoader`
- [ ] Test runs in CI and fails the build on parity violations

---

## Implementation Note

```python
# test_loader_parity.py
import json
import pytest
from solstein.data.loaders import CompetitorDataLoader
from solstein.data.unified_loader import UnifiedCompanyLoader

JSON_FIELDS_ALLOWLIST = {
    # Fields intentionally not mapped (with reasons)
    "internal_id": "Internal tracking ID, not used in scoring",
    "legacy_field": "Deprecated, will be removed in v2",
}

def extract_json_fields(obj, prefix=""):
    """Recursively extract all leaf field paths from JSON."""
    fields = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in JSON_FIELDS_ALLOWLIST:
                continue
            new_prefix = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)) and v and isinstance(v[0], dict) if isinstance(v, list) else isinstance(v, dict):
                fields.extend(extract_json_fields(v, new_prefix))
            else:
                fields.append(new_prefix)
    elif isinstance(obj, list) and obj:
        fields.extend(extract_json_fields(obj[0], prefix))
    return fields

def get_company_attributes(company):
    """Get all non-None attributes from Company object."""
    return {k for k, v in vars(company).items() if v is not None}

@pytest.mark.parametrize("loader_class", [CompetitorDataLoader, UnifiedCompanyLoader])
def test_loader_parity(loader_class):
    raw = json.load(open("data/input/competitor_data.json"))
    json_fields = set(extract_json_fields(raw["competitors"][0]))
    
    loader = loader_class()
    companies = loader.load_companies()
    company_attrs = get_company_attributes(companies[0])
    
    # Map JSON field names to expected Company attribute names
    field_mapping = {
        "company_name": "name",
        "funding_raised": "financials.total_funding_raised",
        # ... etc
    }
    
    unmapped = json_fields - set(field_mapping.keys()) - company_attrs
    orphaned = company_attrs - set(field_mapping.values())
    
    assert not unmapped, f"Unmapped JSON fields: {unmapped}"
    assert not orphaned, f"Orphaned Company attributes: {orphaned}"
```

---

## Definition of Done

- [ ] `test_loader_parity.py` created and passing
- [ ] Test runs in CI
- [ ] Documentation in test file explains how to update the mapping when adding new fields

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified gap: no automated check for field mapping completeness |
