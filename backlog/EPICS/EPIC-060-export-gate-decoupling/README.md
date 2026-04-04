# EPIC-060: Export & Release Gate Decoupling

> **Priority**: P1 – High (blocks all real data export)  
> **Stories**: 4 (STORY-399 through STORY-402)  
> **Effort**: M (3–4 days total)  
> **Dependencies**: EPIC-052 (Provenance, Confidence, Quality Gates), EPIC-033 (Data Completeness & Export Integrity)  
> **Status**: 🔴 Not Started

---

## Problem

The export pipeline has a **hard coupling** to the release gate validation:

```python
# Current flow (from run_eneve_199.py line 320-326):
scored = scorer.calculate_scores(companies)

try:
    assert_report_ready(scored)  # ← Gate blocks here
    print("✅ Release gate passed")
except ValueError as exc:
    print(f"❌ Release gate blocked export: {exc}")
    raise SystemExit(1)  # ← No export happens

# This code never executes if gate fails:
ExcelExporter().create_dashboard(scored, output_path)
```

### Why This Blocks Real Data

Real data from `competitor_data_real_enriched.json` **fails validation on**:

1. **provenance_boundary**: Missing `metric_sources`, `metric_justifications`, `source_links` metadata
2. **gap_analysis**: Missing enrichment fields like `ai_maturity`, `tech_stack`, `key_customers`
3. **completeness**: Only 40-45% complete (threshold is 50%), fails due to missing optional fields

### The Result

- ✅ Data loads successfully (5 companies)
- ✅ Scoring completes (produces scores 1.2-3.9)
- ✅ JSON output saved
- ❌ **Excel export never happens** because gate blocks it
- ❌ **No output** delivered to user

---

## Root Causes

1. **No Fallback**: Gate throws exception immediately, no continue option
2. **No Configurable Thresholds**: min_completeness_score=50.0 is hardcoded, can't relax it
3. **All-Or-Nothing**: Single failed check blocks entire export
4. **No Export Warnings**: Missing degraded-quality export option
5. **Scoring Decoupled from Gate**: Scoring doesn't consider data quality, gate blocks after scoring

---

## Stories

| Story | Title | Priority | Size | Notes |
|-------|-------|----------|------|-------|
| STORY-399 | Make ReportReleaseGate configurable: add --skip-gate and --min-completeness flags | P1 | S | Allow CLI to override gate thresholds at runtime |
| STORY-400 | Implement warn-mode for release gate (log issues, don't block) | P1 | M | Gate logs violations but returns OK, allowing export |
| STORY-401 | Decouple export from gate: always export with quality metadata | P1 | M | Export JSON with data_quality scores, optional Excel only if passing |
| STORY-402 | Add quality tiers to exports: gold/silver/bronze based on gate evaluation | P1 | M | Export different output based on confidence/completeness levels |

---

## Definition of Done

- [ ] `--skip-gate` flag allows export even if validation fails
- [ ] `--min-completeness <value>` flag allows relaxing threshold at runtime
- [ ] `--warn-mode` flag logs gate violations but doesn't block export
- [ ] Export happens with or without gate passing (may have quality warnings)
- [ ] JSON export always produced, Excel only if data quality acceptable
- [ ] Export metadata includes gate evaluation results (what failed, confidence scores)
- [ ] User has visibility into why data passed/failed quality check

---

## Acceptance Criteria

**AC-1**: Running with `--skip-gate` produces Excel even if completeness <50%.

**AC-2**: Running with `--warn-mode` logs "WARNING: provenance_boundary" but exports successfully.

**AC-3**: Running with `--min-completeness 40` allows export at 40% instead of default 50%.

**AC-4**: Export includes metadata: `data_quality_tier: "silver"` (passed 2/5 gates), `completeness_score: 42.0`.

**AC-5**: Two exports from same data with different gate settings produce identical core scores (only metadata differs).

---

## Implementation Notes

### CLI Changes

```bash
# Current (fails)
python scripts/run_eneve_199.py
# Output: ❌ Release gate blocked export: completeness; provenance_boundary
# Result: No export

# NEW - Skip gate entirely
python scripts/run_eneve_199.py --skip-gate
# Output: ✅ Export complete (data quality warnings in metadata)
# Result: Excel + JSON exported

# NEW - Relax threshold
python scripts/run_eneve_199.py --min-completeness 40
# Output: ✅ Export complete (passed gate at 40% threshold)
# Result: Excel + JSON exported

# NEW - Warn instead of block
python scripts/run_eneve_199.py --warn-mode
# Output: ✅ Export complete with warnings (violations logged but not blocking)
# Result: Excel + JSON exported, logs show gate evaluation
```

### Gate Configuration

```python
class ReportReleaseGate:
    def __init__(
        self,
        completeness: CompletenessCalculator | None = None,
        min_completeness_score: float = 50.0,  # Can be overridden
        min_confidence: float = 0.5,
        allow_synthetic: bool = False,
        warn_mode: bool = False,  # Log violations, don't block
    ):
        self.min_completeness_score = min_completeness_score
        self.warn_mode = warn_mode
    
    def evaluate(self, companies: list[Company]) -> ReportGateResult:
        reasons = []
        
        # ... collect reasons ...
        
        if self.warn_mode:
            for reason in reasons:
                logger.warning(f"Gate: {reason.code} - {reason.message}")
            return ReportGateResult(passed=True, reasons=[])  # Always pass in warn mode
        
        return ReportGateResult(
            passed=len(reasons) == 0,
            reasons=reasons
        )
    
    def ensure_release_ready(self, companies: list[Company]) -> None:
        result = self.evaluate(companies)
        if not result.passed:
            # In warn mode, this is a no-op
            if not self.warn_mode:
                raise ValueError(f"Gate failed: {'; '.join(r.code for r in result.reasons)}")
```

### Export Metadata

```json
{
  "export_metadata": {
    "gate_evaluation": {
      "passed": false,
      "mode": "warn_mode",
      "min_completeness_score": 40,
      "actual_completeness_score": 42,
      "violations": [
        {
          "code": "provenance_boundary",
          "severity": "warning",
          "message": "Some fields lack provenance metadata"
        }
      ]
    },
    "data_quality_tier": "silver",
    "completeness_percentage": 42.0,
    "recommendation": "Use for analysis with caution. Some fields lack source verification."
  }
}
```

### Testing

Test scenarios:
1. Run with default gate → fails (completeness <50%)
2. Run with `--skip-gate` → succeeds
3. Run with `--min-completeness 40` → succeeds
4. Run with `--warn-mode` → succeeds with warnings logged
5. Verify scores identical in all successful runs
6. Verify metadata differs only in quality tier
