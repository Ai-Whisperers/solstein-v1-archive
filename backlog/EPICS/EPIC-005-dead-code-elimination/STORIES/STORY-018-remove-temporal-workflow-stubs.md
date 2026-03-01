# STORY-018: Remove Dead Temporal Workflow Stubs

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | LOW |
| Epic | [EPIC-005: Dead Code Elimination](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `analytics/workflows.py` and `analytics/activities.py` contain Temporal workflow and activity definitions that reference a localhost Temporal server (`localhost:7233` hardcoded in `api/routers/jobs.py`). These stubs were apparently built for a Temporal-based workflow orchestration approach that was abandoned. They exist only as dead code and cognitive overhead.

## Problem Statement

Dead Temporal workflow stubs consume cognitive overhead and create confusion about whether Temporal is a dependency of this system. An engineer encountering `workflows.py` and `activities.py` must spend time understanding that these files are non-functional relics of an abandoned architecture decision. The hardcoded `localhost:7233` reference in `jobs.py` is a latent configuration bug — if anyone accidentally enables the Temporal code path, it will attempt to connect to a non-existent local service.

This is the lowest-severity item in this epic because the dead code causes no runtime harm as long as it remains dead. But dead code that references specific infrastructure (Temporal, `localhost:7233`) is more confusing than dead utility functions — it implies an architectural dependency that does not exist.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Engineers must understand Temporal to understand which parts of this code are dead |
| **Confusion** | File names `workflows.py` and `activities.py` suggest an active workflow orchestration system |
| **Configuration Risk** | `localhost:7233` hardcoded in router code is a latent connection failure if accidentally triggered |
| **Dependency Ambiguity** | New engineers may add Temporal to their local setup assuming it is required |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/analytics/workflows.py` | Delete | Contains dead Temporal workflow definitions |
| `src/solstein/analytics/activities.py` | Delete | Contains dead Temporal activity definitions |
| `src/solstein/api/routers/jobs.py` | Modify | Contains `localhost:7233` hardcoded Temporal server reference |
| Any imports referencing workflows/activities | Modify | Remove dead imports |

## Architectural Requirements

- **REQ-1**: If Temporal is not a planned dependency, all workflow and activity stubs must be deleted entirely
- **REQ-2**: The `localhost:7233` hardcoded reference in `jobs.py` must be removed or, if any workflow capability is retained, replaced with a configurable value sourced from environment or settings
- **REQ-3**: If Temporal integration is genuinely planned for the future, an ADR must exist documenting the decision, timeline, and justification — the stubs are still deleted, but the intent is recorded
- **REQ-4**: No `localhost` URL may appear as a string literal in router code under any circumstances

## Acceptance Criteria

- [ ] `workflows.py` and `activities.py` are either deleted or contain only actively-used, non-Temporal code
- [ ] `grep -r "localhost:7233" .` returns zero results
- [ ] `grep -r "temporal" . --include="*.py"` returns zero results (excluding documentation and ADR)
- [ ] An ADR documents the decision regarding Temporal integration (either "not planned" or "planned with timeline")

## Definition of Done

**Tests Required:**
- [ ] `grep` confirms absence of dead Temporal references across the codebase
- [ ] Existing tests pass after file deletion (confirming nothing depended on the dead code)

**Documentation Required:**
- [ ] ADR documenting the Temporal decision: was it explored and rejected, or is it planned for the future?

**Code Review Gate:**
- [ ] Reviewer confirms all Temporal references are removed
- [ ] Reviewer confirms no `localhost` string literals remain in router code

## Notes

This is straightforward cleanup. The risk is near zero — these files are dead code by definition. The ADR is the most valuable output: it captures the architectural decision so the next engineer who considers Temporal for workflow orchestration can learn from the prior evaluation rather than starting from scratch.
