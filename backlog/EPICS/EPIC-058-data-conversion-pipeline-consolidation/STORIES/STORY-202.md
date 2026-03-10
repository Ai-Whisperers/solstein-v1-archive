# STORY-202: Replace `convert_json_to_company()` with Unified Extractor Functions

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-058 Data Conversion Pipeline Consolidation |
| **Created** | 2026-03-01 |
| **Risk** | Medium — consolidates conversion logic; must verify scoring remains stable |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED DEFECT** — `scripts/run_eneve_199.py` lines 68–85 contain custom conversion logic that duplicates (and contradicts) the correct implementation in `src/solstein/data/converters/company_extractors.py`.

```python
# WRONG (scripts/run_eneve_199.py lines 73–76):
revenue_timeline = revenue_data.get("timeline", [])
latest_revenue = revenue_timeline[0] if revenue_timeline else {}
growth_rate = latest_revenue.get("yoy_growth_pct")  # ❌ Returns None for flat JSON

# RIGHT (company_extractors.py lines 40–45):
elif isinstance(revenue_data, (int, float)):
    latest_revenue = float(revenue_data)
    growth_rate = raw_data.get("growth_rate")  # ✅ Checks top-level
```

---

## Problem Statement

Two separate code paths convert raw JSON to `Company` domain objects:

1. **Manual script path** (`scripts/run_eneve_199.py`): Custom inline conversion, expects nested timeline structure
2. **Data layer path** (`company_extractors.py`): Correct implementation, handles both flat and nested structures

The script path is used for ENEVE pipeline runs but silently fails on flat JSON structures. Real data uses flat structure, causing systematic data loss. The correct implementation exists but is unused.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🔴 Critical — Field loss produces lower scores (5–15% systematic error) |
| Data Completeness | 🔴 Critical — Growth rate, profit margin consistently lost from flat JSON |
| Code Maintainability | 🟠 High — Two parallel implementations create confusion and risk |
| Developer Experience | 🟠 High — Engineers must understand both paths |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `scripts/run_eneve_199.py` | 68–85 | Delete custom converter, import unified function |
| `src/solstein/data/loaders.py` | `CompanyLoader` class | Export unified converter function |
| `src/solstein/data/converters/company_extractors.py` | 40–45+ | Already correct; verify no changes needed |
| `scripts/verify_eneve_pipeline.py` | Similar converter logic | Update to use unified function |

---

## Dependencies

- **Hard**: Must complete before STORY-203 (format auto-detection)
- **Soft**: EPIC-047 (Data Loading Fidelity) — field mapping should be complete
- **Blocks**: STORY-203, STORY-205

---

## Architectural Requirements

**REQ-1**: Single entry point `convert_to_domain_company(raw_data: dict) -> Company` in `loaders.py`.

**REQ-2**: No custom conversion logic in script files — all scripts must use the loaders module function.

**REQ-3**: The unified function must support both flat (raw float/int at top level) and nested (dict with timeline) structures.

---

## Acceptance Criteria

- [ ] `scripts/run_eneve_199.py` imports `convert_to_domain_company()` from `loaders` module (not inline)
- [ ] No duplicate conversion logic remains in `scripts/` directory
- [ ] `scripts/verify_eneve_pipeline.py` also uses unified converter
- [ ] Unit test: Load 5 real companies → all have non-None `growth_rate` (was returning None before)
- [ ] Manual run: `python scripts/run_eneve_199.py` produces same output structure as before
- [ ] Scoring output is stable (no regressions in Phoenix/Salt/Lead percentages)

---

## Definition of Done

- [ ] Dual converters consolidated into single function
- [ ] All scripts use unified converter
- [ ] Unit tests verify conversion from flat JSON
- [ ] No field loss for real data format
- [ ] Scoring stability test passes

---

## Implementation Notes

### Recommended Approach

1. **Export function from loaders**: Create `convert_to_domain_company(raw_data: dict) -> Company` 
2. **Wire company_extractors functions**: Use existing revenue, growth, profit extraction logic
3. **Replace script inline code**: Delete lines 68–85 from run_eneve_199.py, import function
4. **Update verify_eneve_pipeline.py**: Use same unified converter
5. **Add regression test**: Load real JSON, verify all fields extracted

### Files to Create/Modify

- `src/solstein/data/loaders.py` - Add/export `convert_to_domain_company()`
- `scripts/run_eneve_199.py` - Delete inline converter, add import
- `scripts/verify_eneve_pipeline.py` - Use unified converter
- `tests/unit/test_data_conversion.py` - Add real data format test (NEW)

### Risk Mitigation

- Scoring could change due to different extraction → Use golden dataset test (STORY-205)
- Performance regression → Profile with 1000+ companies
- Existing scripts might break → Run full pipeline smoke test post-merge

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Identified dual converter paths; field loss confirmed |
