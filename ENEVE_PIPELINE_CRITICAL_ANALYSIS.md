# ENEVE Pipeline: Critical Analysis & Epic Mapping

**Date**: 2026-03-10  
**Analysis Type**: Full Pipeline Flow Critique  
**Severity**: 🔴 CRITICAL (Real data cannot be processed end-to-end)  
**Status**: 10 Issues Identified, 3 New Epics Created, 4 Existing Epics Updated

---

## Executive Summary

The ENEVE data pipeline has **10 critical systemic issues** causing real data to fail silently at multiple stages:

1. **Data is lost** during conversion (two competing incompatible implementations)
2. **Models don't validate** input completeness
3. **Scoring ignores missing data** instead of failing fast
4. **Release gate blocks everything** with hard validation
5. **No fallback mechanisms** exist (hard failures throughout)

**Result**: Real data (5 companies) loads, converts partially, scores weakly, and **never exports** due to failed validation.

---

## The 10 Critical Issues & Their Epics

### ISSUE #1: Two Competing Conversion Functions (Data Loss)
**Severity**: 🔴 CRITICAL | **Impact**: 70% of fields lost

**What**: `scripts/run_eneve_199.py` has custom `convert_json_to_company()` that expects nested data structure, but real JSON is flat.

**Example**:
```json
Real JSON:      {"revenue": 33219.99, "growth_rate": 5.4}
Script expects: {"revenue": {"timeline": [{"eur_millions": 33219.99}]}}
Result:         growth_rate = None ❌
```

**Root Cause**: `convert_to_domain_company()` in `converters/company_extractors.py` is correct but not used by scripts.

**Addressed By**: **EPIC-058 (NEW)** - Data Conversion Pipeline Consolidation
- STORY-202: Replace custom converter with unified extractor
- STORY-203: Add auto-detection for flat vs nested structure
- STORY-204: Wire metric_lineage confidence
- STORY-205: Golden dataset format test

---

### ISSUE #2: Format Mismatch Between JSON Schemas
**Severity**: 🔴 CRITICAL | **Impact**: Silent field loss

**What**: Real JSON has BOTH flat fields AND nested metadata, but converter only looks at one.

**Root Cause**: Script hardcodes expectation of nested timeline structure that doesn't exist in real data.

**Addressed By**: **EPIC-058 (NEW)** - Data Conversion Pipeline Consolidation

---

### ISSUE #3: Company Model Allows Incomplete Data
**Severity**: 🔴 CRITICAL | **Impact**: Downstream systems receive corrupt data

**What**: All FinancialMetric fields are optional; model accepts companies with zero financial data.

```python
class FinancialMetric(BaseModel):
    revenue: float | None = None      # Can be None
    employees: int | None = None      # Can be None
    growth_rate: float | None = None  # Can be None
    # No validation that at least ONE is present!
```

**Root Cause**: No contract enforcing minimum data requirements.

**Addressed By**: **EPIC-059 (NEW)** - Input Validation & Graceful Degradation
- STORY-206: Add validation (revenue OR employees required)
- STORY-207: None-safety in scoring
- STORY-209: Conversion output validation

---

### ISSUE #4: Scoring Handles None Silently
**Severity**: 🔴 CRITICAL | **Impact**: Weak scores, meaningless classifications

**What**: GrowthScorer with `growth_rate=None` doesn't crash; it silently skips the component and produces arbitrary low scores.

**Root Cause**: No input validation in scoring logic, treats None as 0 or skips field without logging.

**Addressed By**: **EPIC-046** (Existing) - Scoring Engine Correctness
- STORY-173: Derive threat_level from score ✓ Addresses part
- STORY-174: Add null guard for saas_maturity ✓ Addresses part

**Also Addressed By**: **EPIC-059 (NEW)** - Input Validation & Graceful Degradation
- STORY-207: Add None-safety checks in scorers

---

### ISSUE #5: Release Gate Too Strict
**Severity**: 🔴 CRITICAL | **Impact**: Blocks ALL real data export

**What**: ReportReleaseGate requires:
- `provenance_boundary`: Source metadata on every field
- `gap_analysis`: No missing enrichment fields
- `completeness`: 50%+ of 19 fields present

Real data only has: 8 fields, no enrichment, ~40% complete → **BLOCKED**

**Root Cause**: Gate checks for synthesis data safety (good intent) but blocks real data with legitimate partial info.

**Addressed By**: **EPIC-052** (Existing, but incomplete) - Provenance, Confidence, Quality Gates
- STORY-200: Add quality-gate policy ✓ Addresses concept
- STORY-201: Add contract tests ✓ Addresses testing

**Also Addressed By**: **EPIC-060 (NEW)** - Export & Gate Decoupling
- STORY-211: Make gate configurable (skip, relax threshold)
- STORY-212: Implement warn-mode for gate
- STORY-213: Decouple export from gate (always export with quality metadata)
- STORY-214: Add quality tiers to exports

---

### ISSUE #6: No Fallback or Bypass Mechanism
**Severity**: 🔴 CRITICAL | **Impact**: Hard failures, no continue option

**What**: When gate fails, entire export halts. No option to:
- Skip gate validation
- Relax thresholds
- Export with quality warnings
- Continue with degraded mode

**Root Cause**: Gate throws exception; no configurable parameters; export coupled to gate.

**Addressed By**: **EPIC-060 (NEW)** - Export & Gate Decoupling
- STORY-211: Add CLI flags (--skip-gate, --min-completeness, --warn-mode)
- STORY-213: Decouple export from gate

---

### ISSUE #7: Export Coupled to Release Gate
**Severity**: 🔴 CRITICAL | **Impact**: Export never happens if gate fails

**What**: 
```python
assert_report_ready(scored)  # Throws exception
ExcelExporter().create_dashboard(...)  # Never reaches here
```

If gate fails, export code never executes.

**Root Cause**: Architectural coupling: export is gated, not independent.

**Addressed By**: **EPIC-060 (NEW)** - Export & Gate Decoupling
- STORY-213: Decouple export from gate (always export with metadata)

**Also Addressed By**: **EPIC-033** (Existing) - Data Completeness & Export Integrity
- STORY-125: Restore 20 dropped fields ✓ Addresses field restoration
- STORY-126: Add export schema validation ✓ Addresses validation

---

### ISSUE #8: Confidence Scores Lost
**Severity**: 🟡 HIGH | **Impact**: Scoring accuracy degraded

**What**: Real JSON has metric_lineage with confidence:
```json
"metric_lineage": {
  "revenue": {"value": 33219.99, "confidence": 0.78},
  "growth_rate": {"value": 5.4, "confidence": 0.72}
}
```

But converter doesn't extract it. Scoring uses default confidence (UNKNOWN).

**Root Cause**: Converter ignores metric_lineage field; scoring can't access confidence data.

**Addressed By**: **EPIC-058 (NEW)** - Data Conversion Pipeline Consolidation
- STORY-204: Extract metric_lineage confidence into signal_confidences

**Also Addressed By**: **EPIC-059 (NEW)** - Input Validation & Graceful Degradation
- STORY-208: Apply metric_lineage confidence to weighting

---

### ISSUE #9: No Normalization Validation
**Severity**: 🟡 HIGH | **Impact**: Corrupt data passes through silently

**What**: `normalize_financial_payload()` takes incomplete data and returns it unchanged if fields are already None. No validation that output is acceptable.

**Root Cause**: Normalization is pass-through; no failure on invalid output.

**Addressed By**: **EPIC-059 (NEW)** - Input Validation & Graceful Degradation
- STORY-209: Add conversion output validation before Company construction

---

### ISSUE #10: Meaningless Classifications
**Severity**: 🟡 HIGH | **Impact**: All companies classified "Lead" (worst tier)

**What**: With incomplete financial data, all 5 real companies score 1.2-3.9 → all classified as "Lead".

Classification becomes meaningless because thresholds are:
- Phoenix: 7.0+
- Salt: 4.0-7.0
- Lead: 0-4.0 ← All real companies end up here

**Root Cause**: Scores based on incomplete data are artificially low.

**Addressed By**: **EPIC-046** (Existing) - Scoring Engine Correctness
- STORY-173: Derive threat_level from composite score ✓ 
- STORY-175: Remove dead scoring methods ✓ 

**Also Addressed By**: **EPIC-059 (NEW)** - Input Validation & Graceful Degradation
- STORY-206-210: Validation and graceful degradation ensure complete data before scoring

---

## Epic Dependency Graph

```
EPIC-058 (Data Conversion)
    ↓
EPIC-059 (Input Validation)
    ↓
EPIC-046 (Scoring Correctness) ← Already in backlog
    ↓
EPIC-052 (Quality Gates) ← Already in backlog
    ↓
EPIC-060 (Export Decoupling)
    ↓
EPIC-033 (Data Completeness) ← Already in backlog
```

**Execution Order** (Dependencies):
1. **EPIC-058** (must complete first) - Fix data loss
2. **EPIC-059** (depends on 058) - Add validation
3. **EPIC-046** (depends on 059) - Fix scoring None handling
4. **EPIC-052** (depends on 046) - Configure quality gates
5. **EPIC-060** (depends on 052) - Decouple export from gate
6. **EPIC-033** (depends on 060) - Ensure export integrity

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1) - EPIC-058 & EPIC-059
**Goal**: Eliminate data loss and add validation

- [ ] STORY-202: Consolidate converters
- [ ] STORY-203: Add format auto-detection
- [ ] STORY-206: Add Company model validation
- [ ] STORY-209: Add conversion output validation
- **Success Metric**: Real data converts with 100% field retention

### Phase 2: Scoring Resilience (Week 2) - EPIC-046 & EPIC-059
**Goal**: Make scoring robust to missing data

- [ ] STORY-207: Add None-safety to scorers
- [ ] STORY-208: Wire metric_lineage confidence
- [ ] STORY-174: Add null guard for saas_maturity
- [ ] STORY-173: Derive threat_level correctly
- **Success Metric**: Scoring never crashes on None inputs

### Phase 3: Quality Control (Week 3) - EPIC-052
**Goal**: Enforce provenance and quality standards

- [ ] STORY-198: Enforce provenance at boundaries
- [ ] STORY-199: Implement confidence calibration
- [ ] STORY-200: Configure quality gates with configurable thresholds
- [ ] STORY-201: Add contract tests
- **Success Metric**: Gate can be configured/skipped via CLI

### Phase 4: Export & Delivery (Week 4) - EPIC-060 & EPIC-033
**Goal**: Ensure exports happen and are complete

- [ ] STORY-211: Add CLI flags to gate
- [ ] STORY-212: Implement warn-mode
- [ ] STORY-213: Decouple export from gate
- [ ] STORY-214: Add quality tiers
- [ ] STORY-125: Restore dropped export fields
- [ ] STORY-126: Add export schema validation
- **Success Metric**: Real data produces complete Excel/JSON export regardless of gate status

---

## Success Criteria for ENEVE Pipeline

After all 4 phases complete:

| Criterion | Before | After | Status |
|-----------|--------|-------|--------|
| Real data (5 companies) loads | ✅ 5/5 | ✅ 5/5 | SAME |
| Data converts without loss | ❌ 70% loss | ✅ 0% loss | FIXED |
| Companies pass validation | ❌ 0/5 | ✅ 5/5 | FIXED |
| Scoring completes without error | ✅ Yes | ✅ Yes | SAME |
| Scores are higher (complete data) | ❌ 1.2-3.9 | ✅ Should be 4.0+ | IMPROVED |
| All classified "Lead" | ❌ Yes | ✅ Mixed tiers | FIXED |
| Export happens | ❌ BLOCKED | ✅ SUCCEEDS | FIXED |
| Excel produced | ❌ No file | ✅ Full export | FIXED |

---

## Risk Mitigation

### Risk 1: Conversion changes affect all data pipelines
**Mitigation**: Golden dataset regression test (STORY-205) ensures no regressions

### Risk 2: Validation is too strict, rejects good data
**Mitigation**: Graceful degradation mode (STORY-210) allows degraded scoring instead of block

### Risk 3: Removing gate delays catching actual bad data
**Mitigation**: Quality metadata in export (STORY-214) gives visibility into quality tier

### Risk 4: Existing systems depend on None-returning scorers
**Mitigation**: Add logging (STORY-130 in EPIC-034) before changing scorer behavior

---

## Files Modified by New Epics

### EPIC-058 Changes
- `scripts/run_eneve_199.py` - Remove custom converter
- `scripts/verify_eneve_pipeline.py` - Use unified converter
- `src/solstein/data/loaders.py` - Wire unified converter
- `src/solstein/data/converters/company_extractors.py` - Already correct, just wire it

### EPIC-059 Changes
- `src/solstein/domain/models.py` - Add FinancialMetric validation
- `src/solstein/analytics/scorers/growth_momentum.py` - Add None checks
- `src/solstein/analytics/scorers/competitive_position.py` - Add None checks
- `src/solstein/data/converters/company.py` - Add output validation

### EPIC-060 Changes
- `scripts/run_eneve_199.py` - Add CLI flags (--skip-gate, --min-completeness, --warn-mode)
- `src/solstein/data/report_release_gate.py` - Add warn_mode, make configurable
- `src/solstein/exporters/excel.py` - Always create export, add quality metadata
- `src/solstein/exporters/markdown/client.py` - Add quality tier to output

---

## Next Steps

1. **Review this analysis** with the team
2. **Approve new epics**: EPIC-058, EPIC-059, EPIC-060
3. **Update backlog priorities**: These block all real data work
4. **Start Phase 1**: Begin EPIC-058 this sprint
5. **Block real data work**: Don't attempt data pipelines until Phase 2 complete

---

## Appendix: Issue→Epic Cross-Reference

| Issue | Problem | Existing Epic | New Epic | Stories |
|-------|---------|---------------|----------|---------|
| #1 | Two converters | — | EPIC-058 | 202-205 |
| #2 | Format mismatch | — | EPIC-058 | 202-205 |
| #3 | No input validation | — | EPIC-059 | 206-210 |
| #4 | Scoring None handling | EPIC-046 | EPIC-059 | 174, 207 |
| #5 | Gate too strict | EPIC-052 | EPIC-060 | 200, 211-212 |
| #6 | No bypass | — | EPIC-060 | 211-213 |
| #7 | Export coupled to gate | EPIC-033 | EPIC-060 | 213 |
| #8 | Confidence lost | — | EPIC-058 | 204, 208 |
| #9 | No validation | — | EPIC-059 | 209 |
| #10 | Meaningless classifications | EPIC-046 | EPIC-059 | 206 |
