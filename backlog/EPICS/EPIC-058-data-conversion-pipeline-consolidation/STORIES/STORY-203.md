# STORY-203: Add Format Auto-Detection for Revenue/Growth/Profit Fields

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-058 Data Conversion Pipeline Consolidation |
| **Created** | 2026-03-01 |
| **Risk** | Medium — adds conditional logic; must test against both formats |
| **Assigned** | — |
| **Depends On** | STORY-202 (Unified Converter) |

---

## Audit Verdict

**CONFIRMED DEFECT** — The data format differs between script expectations and actual JSON structure:

- **Script expects**: `revenue.timeline[0].yoy_growth_pct` (nested dict with timeline array)
- **Real data has**: `revenue: 33219.999744`, `growth_rate: 5.4` (flat float values at top level)

Result: Silent field loss. Script returns `None` instead of checking top-level alternative.

---

## Problem Statement

Real company data (`competitor_data_real_enriched.json`) uses a flat structure:

```json
{
  "company_name": "Enphase Energy",
  "revenue": 33219.999744,           // Float at top level
  "growth_rate": 5.4,                 // Float at top level
  "profit_margin": 14.25,             // Float at top level
  "metric_lineage": { ... }           // Metadata with confidence
}
```

But the converter expects nested structure:

```json
{
  "revenue": {
    "timeline": [
      { "year": 2024, "yoy_growth_pct": 5.4, ... }
    ]
  }
}
```

The converter must handle BOTH structures without field loss.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Data Completeness | 🔴 Critical — Growth rate, profit margin lost for all flat JSON |
| Scoring Accuracy | 🔴 Critical — Incomplete data produces 5–15% lower scores |
| Production Readiness | 🟠 High — Script works only on one data format |
| Robustness | 🟠 High — No fallback; fails silently |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/data/converters/company_extractors.py` | Revenue/Growth/Profit extraction | Add multi-format detection |
| `src/solstein/data/loaders.py` | `convert_to_domain_company()` | Wire format detection |
| `tests/unit/test_data_conversion.py` | NEW | Add flat vs. nested test fixtures |

---

## Dependencies

- **Hard**: STORY-202 (Unified Converter) must be complete first
- **Blocks**: STORY-205 (Format Verification Test)

---

## Architectural Requirements

**REQ-1**: For each field (revenue, growth_rate, profit_margin):
1. Check if field exists at top level as float/int → use directly
2. If not, check nested structure (e.g., `revenue.timeline[0].value`)
3. If neither, return None with warning

**REQ-2**: Log warnings for each format detected (debug-level) so engineers can understand which path was taken.

**REQ-3**: No performance penalty for format detection (single pass, early return).

---

## Acceptance Criteria

- [ ] `convert_to_domain_company()` successfully loads `competitor_data_real_enriched.json` with flat structure
- [ ] Result has `growth_rate = 5.4` (not None) for Enphase Energy
- [ ] Result has `profit_margin = 14.25` for Enphase Energy
- [ ] Format detection logs indicate "flat structure detected" for real data
- [ ] Nested structure test fixtures still work (backward compatibility)
- [ ] No field is lost when both formats are present in same batch
- [ ] Unit test: Load mixed batch (flat + nested) → all fields extracted

---

## Definition of Done

- [ ] Multi-format detection implemented for revenue, growth_rate, profit_margin
- [ ] Real data loads with 100% field retention
- [ ] Format detection logs added
- [ ] Backward compatibility with nested format verified
- [ ] Mixed format batch test passes
- [ ] No silent failures (all None fields log warnings)

---

## Implementation Notes

### Recommended Approach

```python
def extract_growth_rate(raw_data: dict) -> Optional[float]:
    # Try flat structure first
    if "growth_rate" in raw_data and isinstance(raw_data["growth_rate"], (int, float)):
        return float(raw_data["growth_rate"])
    
    # Try nested structure as fallback
    revenue_data = raw_data.get("revenue", {})
    if isinstance(revenue_data, dict):
        timeline = revenue_data.get("timeline", [])
        if timeline and isinstance(timeline[0], dict):
            yoy_growth = timeline[0].get("yoy_growth_pct")
            if isinstance(yoy_growth, (int, float)):
                return float(yoy_growth)
    
    # Log warning if both failed
    logger.debug(f"Company {raw_data.get('name')}: growth_rate not found in either flat or nested structure")
    return None
```

### Files to Create/Modify

- `src/solstein/data/converters/company_extractors.py` - Add format detection per field
- `src/solstein/data/loaders.py` - Wire detection functions
- `tests/unit/test_data_conversion.py` - Add flat/nested/mixed fixtures

### Risk Mitigation

- Format detection logic could have bugs → Add unit tests for each format
- Nested structure users might be affected → Test backward compatibility
- Performance regression from extra checks → Profile with 10K companies

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified format mismatch: flat vs. nested structure |

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
