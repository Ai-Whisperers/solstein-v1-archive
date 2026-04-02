# STORY-212: Refactor Release Gate to Return Warnings, Not Exceptions

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-060 Export & Release Gate Decoupling |
| **Created** | 2026-03-01 |
| **Risk** | Medium — changes gate interface; must verify all callers |
| **Assigned** | — |
| **Depends On** | EPIC-046 (Scoring Engine Correctness) |

---

## Audit Verdict

**CONFIRMED DESIGN FLAW** — The release gate throws exceptions to block export.

Current behavior:
```python
def assert_report_ready(companies: List[Company]):
    if completeness_score < 50:
        raise ValueError("Completeness score too low")
    # No return value
```

Usage:
```python
try:
    assert_report_ready(scored_companies)
    export_scores(scored_companies)  # Only executes if no exception
except ValueError:
    raise SystemExit(1)  # Crash: no export produced
```

Problem: Gate is binary (pass/crash). No middle ground for warnings, auditing, or override.

---

## Problem Statement

The gate's exception-based design makes it impossible to:
1. Export with warnings (for analysis/debugging)
2. Log gate evaluation details
3. Let users decide whether to override
4. Separate gate validation from export decision

Better design: Gate returns detailed result, caller decides what to do.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Operational Flexibility | 🔴 Critical — No override mechanism |
| Error Visibility | 🟡 Medium — Exception hides gate details |
| User Control | 🟡 Medium — Binary pass/fail, no nuance |

---

## Affected Files

| File | Lines | Change Type |
|-------|-------|-------------|
| `src/solstein/data/report_release_gate.py` | `assert_report_ready()` | Change from exception to result return |
| `scripts/run_eneve_199.py` | Gate calling code | Handle result instead of exception |
| `src/solstein/api/routes/scoring.py` | If used in API | Update gate calls |

---

## Dependencies

- **Hard**: None
- **Blocks**: STORY-211, STORY-213

---

## Architectural Requirements

**REQ-1**: Gate returns structured result:
```python
class GateResult:
    passed: bool
    score: float
    messages: List[str]  # Warning/failure details
    thresholds: Dict[str, float]  # What we checked against
```

**REQ-2**: Gate never throws exceptions — always returns result.

**REQ-3**: Caller decides what to do with result:
- Strict: Fail if `not result.passed`
- Warn: Log warnings, continue
- Force: Ignore result, export anyway

---

## Acceptance Criteria

- [ ] `GateResult` class created with `passed`, `score`, `messages`, `thresholds`
- [ ] `assert_report_ready()` returns `GateResult` (not exception)
- [ ] Gate evaluation details in result messages
- [ ] Caller code handles result explicitly
- [ ] Strict mode: Gate failure → exit with error
- [ ] Warn mode: Gate failure → log and continue
- [ ] Force mode: Gate completely bypassed
- [ ] Manual test: All modes work correctly

---

## Definition of Done

- [ ] `GateResult` class implemented
- [ ] Gate refactored to return result
- [ ] All gate callers updated
- [ ] Result details logged for debugging
- [ ] Backward compatibility (if needed) via wrapper
- [ ] All modes tested

---

## Implementation Notes

### GateResult Class

```python
from dataclasses import dataclass

@dataclass
class GateResult:
    passed: bool
    completeness_score: float
    data_quality_score: float
    overall_score: float
    
    thresholds: Dict[str, float] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)
    
    def add_message(self, level: str, text: str):
        """Add detail message (WARNING, ERROR, INFO)."""
        self.messages.append(f"[{level}] {text}")
    
    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"Gate {status}: completeness={self.completeness_score:.1f}% threshold={self.thresholds['completeness']}"
```

### Refactored Gate

```python
def assert_report_ready(companies: List[Company]) -> GateResult:
    completeness = calculate_completeness_score(companies)
    data_quality = calculate_data_quality_score(companies)
    
    result = GateResult(
        passed=True,
        completeness_score=completeness,
        data_quality_score=data_quality,
        overall_score=(completeness + data_quality) / 2,
        thresholds={"completeness": 50.0, "data_quality": 60.0}
    )
    
    if completeness < 50.0:
        result.passed = False
        result.add_message("ERROR", f"Completeness {completeness:.1f}% < threshold 50%")
    
    if data_quality < 60.0:
        result.add_message("WARNING", f"Data quality {data_quality:.1f}% < ideal 80%")
    
    return result
```

### Updated Caller

```python
gate_result = assert_report_ready(scored_companies)

if args.force_export:
    logger.warning(f"Force export: bypassing gate ({gate_result})")
    export_scores(scored_companies)
elif args.warn_mode:
    for msg in gate_result.messages:
        logger.warning(f"Gate: {msg}")
    export_scores(scored_companies)
elif gate_result.passed:
    export_scores(scored_companies)
else:
    for msg in gate_result.messages:
        logger.error(f"Gate: {msg}")
    raise SystemExit(1)
```

### Files to Create/Modify

- `src/solstein/data/report_release_gate.py` - Refactor to return result
- `scripts/run_eneve_199.py` - Handle result
- `src/solstein/api/routes/scoring.py` - If used in API

### Risk Mitigation

- API might depend on exception behavior → Check all callers first
- Result object might be missing fields → Extend as needed
- Performance regression from creating result object → Negligible

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Gate throws exceptions; no override mechanism |

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
