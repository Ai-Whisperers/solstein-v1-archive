# STORY-020: Consolidate Three Parallel Data Loader Systems

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-006: Unification of Duplicates](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> Three data loading systems coexist: `data/loaders.py` (771 lines, deprecated but still imported), `data/unified_loader.py` (1,142 lines, intended replacement), and `data/company_research.py` (412 lines, not imported in any main execution path). Approximately 2,300 lines of competing loader logic.

## Problem Statement

Three data loading implementations mean any data loading behaviour is potentially defined in three places. Which loader executes depends on which import path is taken — a decision that varies by caller without any documented rationale.

The "deprecated" loader (`loaders.py`) is still actively imported and called. Deprecation that is not enforced is aspirational at best and misleading at worst. The "orphaned" loader (`company_research.py`) is not imported in any main execution path but still exists in the codebase, adding 412 lines of ambiguity about whether it serves some undocumented purpose.

The result: 2,300+ lines of data loading logic with no single source of truth for how data enters the system.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Loading behaviour differs by code path — same company may load differently via different loaders |
| **Maintainability** | Data loading fixes must be evaluated across three implementations |
| **Performance** | Duplicate loading logic may result in redundant external calls or file reads |
| **Debugging** | "Where does this data come from?" requires tracing which loader was invoked |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/loaders.py` | Evaluate/Delete | 771 lines, "deprecated" but still imported |
| `src/solstein/data/unified_loader.py` | Evaluate/Retain | 1,142 lines, intended canonical loader |
| `src/solstein/data/company_research.py` | Evaluate/Delete | 412 lines, orphaned — not in main execution paths |
| All callers of these loaders | Modify | Must import the canonical loader |

## Architectural Requirements

- **REQ-1**: One data loader must be the canonical implementation — the other two must be deleted
- **REQ-2**: All callers must be migrated to the canonical loader
- **REQ-3**: Non-canonical loaders must be deleted entirely, not deprecated or moved
- **REQ-4**: The canonical loader must be split if it exceeds 400 lines (see STORY-029 in EPIC-008 for the decomposition plan)
- **REQ-5**: A clear interface (`Protocol` or `ABC`) must exist that the canonical loader satisfies, enabling future alternative implementations

## Acceptance Criteria

- [ ] One loader module exists (or one loader package if decomposed per STORY-029)
- [ ] All callers import from the canonical loader
- [ ] `grep -r "from solstein.data.loaders import" . --include="*.py"` returns zero results in non-loader files (if `loaders.py` is the retired file)
- [ ] `grep -r "from solstein.data.company_research import" . --include="*.py"` returns zero results
- [ ] The canonical loader satisfies a documented `DataLoader` Protocol

## Definition of Done

**Tests Required:**
- [ ] All existing loader tests pass against the canonical implementation
- [ ] Integration test confirming data is loaded correctly through the canonical path
- [ ] Test: importing a retired loader name raises `ImportError`

**Documentation Required:**
- [ ] Comment in the canonical loader documenting the consolidation decision and date
- [ ] Inline documentation of the `DataLoader` Protocol contract

**Code Review Gate:**
- [ ] Reviewer confirms all three loaders have been audited and the canonical choice is justified
- [ ] Reviewer confirms all callers have been migrated

## Notes

This story must be completed before STORY-029 (unified loader decomposition in EPIC-008). The sequence is: consolidate first, then decompose. Do not attempt to decompose a loader while two other loaders still exist.

Start with a caller audit: determine which loaders are actually invoked in production code paths. The orphaned `company_research.py` may be safe to delete immediately if no active code imports it.

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
