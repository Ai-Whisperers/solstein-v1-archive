# EPIC-058: Data Conversion Pipeline Consolidation

> **Priority**: P0 – Critical (affects all data ingestion)  
> **Stories**: 4 (STORY-202 through STORY-205)  
> **Effort**: L (5–6 days total)  
> **Dependencies**: EPIC-047 (Data Loading Fidelity), EPIC-003 (Core Product Correctness)  
> **Status**: 🔴 Not Started

---

## Problem

The data conversion pipeline has **two competing, incompatible implementations** that process the same data differently:

### The Dual Implementation Problem

**Path A: `scripts/run_eneve_199.py` (Currently Used)**
```python
# Lines 71-85: Expects nested structure
revenue_data = data.get("revenue") or {}
if isinstance(revenue_data, dict):
    revenue_timeline = revenue_data.get("timeline", [])
    latest_revenue = revenue_timeline[0] if revenue_timeline else {}
    growth_rate = latest_revenue.get("yoy_growth_pct")
else:
    growth_rate = None  # ❌ Falls back to None, not looking at top-level field
```

**Path B: `src/solstein/data/converters/company_extractors.py` (Correct Implementation)**
```python
# Lines 40-45: Handles both flat and nested
elif isinstance(revenue_data, (int, float)):
    latest_revenue = float(revenue_data)
    growth_rate = raw_data.get("growth_rate")  # ✅ Looks at top-level!
    if isinstance(growth_rate, (int, float)):
        latest_growth = float(growth_rate)
```

### Field Loss Comparison

| Field | Real JSON | Path A Extraction | Path B Extraction | Loss |
|-------|-----------|-------------------|------------------|------|
| `revenue` (33219.999744) | Float at top level | ✅ Extracted | ✅ Extracted | None |
| `growth_rate` (5.4) | Float at top level | ❌ Returns None | ✅ Extracted | Path A loses it |
| `profit_margin` (14.25) | Float at top level | ❌ Returns None | ✅ Extracted | Path A loses it |
| `employees` (111900) | Integer at top level | ✅ Extracted | ✅ Extracted | None |
| `metric_lineage` | Nested structure | ✅ Stored | ✅ Stored | None |

### Why This Matters

- **Path A is used by manual scripts** (`run_eneve_199.py`, `verify_eneve_pipeline.py`)
- **Path B is used by the data layer** but not invoked from scripts
- **Real data has flat structure** (not nested), so Path A fails silently
- **Scoring receives incomplete data** from Path A, producing lower scores
- **Export quality gates block output** because data is incomplete

---

## Root Causes

1. **Incomplete Migration**: Path B was refactored out of the original loader but Path A wasn't updated to use it
2. **No Format Normalization**: Real data is flat, but Path A expects nested timeline structure
3. **Silent Failure**: When Path A can't find nested data, it returns None instead of checking for flat structure
4. **Dead Code**: Path B exists but is not wired into the main pipeline

---

## Stories

| Story | Title | Priority | Size | Notes |
|-------|-------|----------|------|-------|
| STORY-202 | Replace `convert_json_to_company()` with unified extractor functions | P0 | M | Delete dead code from run_eneve_199.py, use company_extractors.py functions |
| STORY-203 | Add format auto-detection for revenue/growth_rate/profit_margin fields | P0 | M | Handle both flat (float) and nested (dict with timeline) structures |
| STORY-204 | Wire metric_lineage confidence into Company.signal_confidences | P1 | S | Extract 0.72-0.78 confidence values from metric_lineage, use in scoring |
| STORY-205 | Add golden-dataset format verification test | P1 | M | Test conversion against real JSON structure (both flat and nested), verify no field loss |

---

## Definition of Done

- [ ] Single conversion path: `convert_to_domain_company()` from loaders module handles all formats
- [ ] No duplicate conversion logic in scripts or modules
- [ ] Supports flat structure (JSON field directly) AND nested structure (field in dict)
- [ ] All confidence data from `metric_lineage` is extracted and preserved
- [ ] Golden dataset test passes: no field loss for 100+ real company records
- [ ] Score distribution stable before/after (Phoenix, Salt, Lead percentages within 2%)
- [ ] All scripts use unified loader, not custom conversion logic

---

## Acceptance Criteria

**AC-1**: Running `run_eneve_199.py` on real data produces scores that are **higher** (on average) than before, because missing financial data is no longer lost.

**AC-2**: Field mapping validation test runs before scoring and blocks any batch where >2% of companies are missing required fields.

**AC-3**: `metric_lineage` confidence values (0.72, 0.78, etc.) flow through to scoring engine and affect confidence weighting.

**AC-4**: No "None" fields in scored output where flat JSON had a numeric value present.

---

## Implementation Notes

### Recommended Approach

1. **Consolidate in loaders.py**: `convert_to_domain_company()` becomes the single entry point
2. **Extract reusable functions**: Move common logic (revenue, growth, profit) to company_extractors.py
3. **Add format detection**: First try to extract from flat structure, then fall back to nested
4. **Test with real data**: Use actual competitor_data_real_enriched.json as test fixture
5. **Verify scoring impact**: Run full pipeline, compare output distribution to synthetic baseline

### Files to Modify

- `scripts/run_eneve_199.py` - Replace `convert_json_to_company()` with loader function
- `scripts/verify_eneve_pipeline.py` - Verify using new converter
- `src/solstein/data/loaders.py` - Wire unified converter
- `src/solstein/data/converters/company.py` - Update if needed
- `src/solstein/data/converters/company_extractors.py` - Already correct, may just need to be wired

### Risk Mitigation

- Conversion changes could affect scoring → Use golden dataset regression test
- Existing code may rely on None values → Add fallback with warnings
- Performance impact from extra checks → Profile with 1000+ companies

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
