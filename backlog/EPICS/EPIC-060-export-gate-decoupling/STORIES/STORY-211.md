# STORY-211: Add --force-export and --warn-mode CLI Flags

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-060 Export & Release Gate Decoupling |
| **Created** | 2026-03-01 |
| **Risk** | Low — CLI flags only; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-212 (Gate Refactor) |

---

## Audit Verdict

**CONFIRMED MISSING** — The `scripts/run_eneve_199.py` script has no way to override the release gate.

Current behavior:
```bash
python scripts/run_eneve_199.py
# If gate fails: SystemExit(1) — no export produced
```

Desired behavior:
```bash
# Strict mode (default)
python scripts/run_eneve_199.py
# Gate fails: exit with error, no export

# Warn mode (audit/debug)
python scripts/run_eneve_199.py --warn-mode
# Gate fails: log warnings, produce export anyway

# Force export (final resort)
python scripts/run_eneve_199.py --force-export
# Gate bypassed entirely, export produced
```

---

## Problem Statement

The release gate blocks export when data completeness < 50%. Real data has 40% completeness due to format mismatch (being fixed in EPIC-058). Until fixed, there's no way to produce an export for analysis, verification, or debugging.

Script users need three modes:
1. **Strict**: Fail if data quality issues (production/CI)
2. **Warn**: Log issues but export anyway (analysis/debug)
3. **Force**: Skip gate entirely (emergency/final resort)

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Debuggability | 🔴 Critical — Can't export to verify pipeline |
| Operational Flexibility | 🟠 High — No override for temporary issues |
| Production Readiness | 🟠 High — Gate is binary: pass or crash |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `scripts/run_eneve_199.py` | Main entry point | Add argparse flags |
| `src/solstein/data/report_release_gate.py` | Gate logic | Integrate with flags |

---

## Dependencies

- **Hard**: STORY-212 (Gate Refactor to return warnings)
- **Blocks**: STORY-213, STORY-214

---

## Architectural Requirements

**REQ-1**: CLI flags:
- `--warn-mode`: Log warnings, continue to export
- `--force-export`: Skip gate entirely, force export
- Default (no flag): Strict mode (fail on gate issues)

**REQ-2**: Flag values accessible to gate evaluation function.

**REQ-3**: Help text explains each mode.

---

## Acceptance Criteria

- [ ] `python scripts/run_eneve_199.py` defaults to strict mode (fail on gate)
- [ ] `python scripts/run_eneve_199.py --warn-mode` logs warnings, produces export
- [ ] `python scripts/run_eneve_199.py --force-export` produces export without gate check
- [ ] Help text (`--help`) explains all three modes
- [ ] Manual test: All three modes work with real data
- [ ] Exit codes correct (0 for success, 1 for failure in strict mode)

---

## Definition of Done

- [ ] CLI flags added to run_eneve_199.py
- [ ] Flags passed through to gate evaluation
- [ ] All three modes tested
- [ ] Help text documenting flags
- [ ] Manual verification with real data

---

## Implementation Notes

### CLI Pattern

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="ENEVE Pipeline Runner")
    parser.add_argument(
        "--warn-mode",
        action="store_true",
        help="Log warnings but produce export even if gate fails (analysis/debug mode)"
    )
    parser.add_argument(
        "--force-export",
        action="store_true",
        help="Skip release gate entirely and force export (emergency only)"
    )
    
    args = parser.parse_args()
    
    # ... load data, convert, score ...
    
    if args.force_export:
        logger.warning("Force export: bypassing release gate")
        export_scores(scored_companies)
    else:
        try:
            gate_result = assert_report_ready(scored_companies, warn_mode=args.warn_mode)
            if not gate_result.passed and not args.warn_mode:
                raise SystemExit(1)
            export_scores(scored_companies)
        except ValueError as e:
            logger.error(f"Release gate failed: {e}")
            raise SystemExit(1)

if __name__ == "__main__":
    main()
```

### Files to Create/Modify

- `scripts/run_eneve_199.py` - Add argparse
- `src/solstein/data/report_release_gate.py` - Accept warn_mode parameter

### Risk Mitigation

- Users might abuse --force-export → Document as emergency only
- --warn-mode might hide real issues → Log at WARNING level (visible)
- Modes could be confusing → Add verbose help text and examples

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | No override mechanism for release gate |
