# STORY-033: Establish a Single Validation Service

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-009: Data Layer Consolidation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> Three validation systems coexist: `data/enrichment_validators.py` (standalone module), `DataValidationService` class inside `data/enrichment_service.py` (duplicate), and inline validation logic inside `data/unified_loader.py` (inline duplicate). The same field may be validated with different rules depending on which path the data entered through.

## Problem Statement

Three validation implementations mean data can pass validation by one system and fail another. There is no guarantee that the same rules are applied consistently. Revenue might be validated as non-negative by `enrichment_validators.py`, validated as positive by `DataValidationService`, and not validated at all by the inline logic in `unified_loader.py`.

The practical consequence: the same data can be accepted or rejected depending on which code path it enters through. A company with revenue of `0.0` might pass validation through the loader path but fail through the enrichment path — or vice versa. This is not a theoretical concern; it is a data quality issue that makes validation rules unenforceable.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Inconsistent validation rules produce inconsistent data quality |
| **Performance** | Redundant validation adds processing overhead — the same data may be validated three times |
| **Maintainability** | Validation rule changes must be applied in three places — and the engineer must know that three places exist |
| **Debugging** | "Why was this data accepted?" requires tracing which validation path was taken |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/enrichment_validators.py` | Evaluate/Retain | Standalone validation module — candidate for canonical version |
| `src/solstein/data/enrichment_service.py` | Modify | Extract `DataValidationService` — consolidate with canonical module |
| `src/solstein/data/unified_loader.py` | Modify | Remove inline validation — delegate to canonical module |
| New or modified canonical validation module | Add/Modify | Single validation service with all rules |

## Architectural Requirements

- **REQ-1**: One validation module must define all data validation rules — no validation logic may exist outside this module
- **REQ-2**: All data ingestion paths must use this single module for validation — the loader, enrichment service, and any other entry point must delegate to it
- **REQ-3**: The validation module must be independently testable without data loading context — you should be able to validate a data record without loading it from a file
- **REQ-4**: Validation failures must produce structured error objects with field-level detail — not bare exception messages, but objects identifying which field failed, what the value was, and which rule it violated

## Acceptance Criteria

- [ ] One validation module exists and is the sole validation path for all data entry
- [ ] Changing a validation rule in the canonical module affects all data entry points — no entry point bypasses validation
- [ ] Validation failures return structured error objects: `{field: str, value: Any, rule: str, message: str}`
- [ ] `grep -rn "def validate" . --include="*.py"` returns results only in the canonical validation module (and its tests)
- [ ] `DataValidationService` no longer exists as a separate class in `enrichment_service.py`
- [ ] No inline validation logic exists in `unified_loader.py`

## Definition of Done

**Tests Required:**
- [ ] Unit tests for each validation rule (revenue bounds, employee count, required fields, etc.)
- [ ] Test: structured error object contains correct field name, value, and violation detail
- [ ] Integration test: invalid data rejected at all entry points (loader, enrichment, API)
- [ ] Test: adding a new validation rule in the canonical module is sufficient to enforce it everywhere

**Documentation Required:**
- [ ] Docstrings on the validation module documenting each rule and its rationale
- [ ] Structured error format documented with examples

**Code Review Gate:**
- [ ] Reviewer confirms no validation logic exists outside the canonical module
- [ ] Reviewer confirms all entry points delegate to the canonical module
- [ ] Reviewer confirms structured error objects contain sufficient detail for debugging

## Notes

Start by auditing the three validation implementations to produce a union of all validation rules. Some rules may exist in only one implementation. The canonical module must contain the union — not just the rules from one implementation.

Pay attention to rule differences: if `enrichment_validators.py` rejects revenue ≤ 0 but `DataValidationService` accepts revenue = 0, you must decide which rule is correct and apply it consistently. Document the decision.

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
