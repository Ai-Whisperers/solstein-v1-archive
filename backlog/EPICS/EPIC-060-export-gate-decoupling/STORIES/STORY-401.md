# STORY-401: Decouple Export from Gate Validation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< 1 day) |
| **Epic** | EPIC-060 Export & Release Gate Decoupling |
| **Created** | 2026-03-01 |
| **Risk** | Low — separation of concerns; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-401 (Gate Refactor) |

---

## Audit Verdict

**CONFIRMED COUPLING** — Export and gate validation are tightly coupled in script flow.

Current:
```python
try:
    assert_report_ready(scored_companies)  # Validation
    export_excel(scored_companies)          # Export
except ValueError:
    raise SystemExit(1)  # Both fail together
```

Problem: Export can only happen if gate passes. Can't export for analysis if gate fails.

---

## Problem Statement

Export decision should be independent of gate validation. Currently:
- Gate fails → No export (even for debugging)
- Can't produce export to analyze why gate failed

Decoupling means:
- Gate validation separate function (can be skipped or overridden)
- Export separate function (can run regardless of gate status)
- Caller controls both independently

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Debuggability | 🟡 Medium — Can export even if gate fails |
| Operational Flexibility | 🟡 Medium — Separate concerns |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `scripts/run_eneve_199.py` | Main flow | Separate gate and export calls |
| `src/solstein/exporters/excel_exporter.py` | Export logic | No changes (already decoupled) |

---

## Dependencies

- **Hard**: STORY-401 (Gate Refactor)
- **Blocks**: Nothing

---

## Architectural Requirements

**REQ-1**: Gate validation and export are separate function calls.

**REQ-2**: Each can succeed/fail independently.

**REQ-3**: Caller controls both:
```python
gate_result = validate_gate(companies)
export_result = export_excel(companies)  # Can succeed even if gate fails
```

---

## Acceptance Criteria

- [ ] `validate_gate(companies)` function exists, returns GateResult
- [ ] `export_excel(companies)` function exists, produces export (gate-independent)
- [ ] Export succeeds even if gate fails
- [ ] Gate failure doesn't prevent export in warn/force modes
- [ ] Manual test: `--warn-mode` produces export despite gate failure
- [ ] Manual test: `--force-export` produces export with no gate check

---

## Definition of Done

- [ ] Gate validation separated into own function
- [ ] Export function is independent
- [ ] Caller logic clear (gate → export, not single try/except)
- [ ] Both modes tested

---

## Implementation Notes

### Clear Decoupling

```python
def main():
    # Load, convert, score
    companies = load_and_score(input_file)
    
    # Validation (optional based on flags)
    gate_result = validate_gate(companies) if not args.force_export else None
    
    # Export (always attempted unless --no-export)
    if args.force_export or args.warn_mode or gate_result.passed:
        export_result = export_excel(companies, output_file)
        print(f"Export complete: {export_result}")
    else:
        print(f"Gate validation failed, export skipped: {gate_result}")
        return 1
    
    return 0
```

### Files to Create/Modify

- `scripts/run_eneve_199.py` - Separate gate and export calls
- `src/solstein/exporters/` - Already decoupled

### Risk Mitigation

- Export could fail for other reasons → Handle separately
- Large export might be slow → Log progress
- Decoupling could confuse users → Document clearly in help text

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Gate and export tightly coupled; can't export if gate fails |
