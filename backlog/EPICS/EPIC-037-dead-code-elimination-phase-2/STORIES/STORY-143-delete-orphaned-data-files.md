# STORY-143: Audit and Delete Orphaned Data Layer Files

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-037: Dead Code Elimination Phase 2 |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> 21 orphaned files (~2,500 lines): eneve_enrichment.py, enrichment_config.py, repositories.py, interpolation.py, enrichment_orchestrator.py, enrichment_service.py, error_logging.py, enrichment_validators.py, company_research.py, markets.py, lookup_service.py, contracts.py.

## Problem Statement

The data layer has accumulated files that are imported by nothing in production. They're used only by tests, or by other orphaned files, or by nothing at all. Some appear to be from a previous enrichment architecture ("eneve"). Others are utility files that were superseded. Together they represent ~2,500 lines of code that must be maintained, tested, and understood by new developers — for zero production value.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | 2,500 lines of dead code |
| **Onboarding** | Developers study unused code |
| **Build Time** | Longer test runs |

## Affected Files

| File | Issue |
|------|-------|
| `data/eneve_enrichment.py` | Orphaned |
| `data/enrichment_config.py` | Orphaned |
| `data/repositories.py` | Orphaned |
| `data/interpolation.py` | Orphaned |
| `data/enrichment_orchestrator.py` | Orphaned |
| `data/enrichment_service.py` | Orphaned |
| `data/error_logging.py` | Orphaned |
| `data/enrichment_validators.py` | Orphaned |
| `data/company_research.py` | Orphaned |
| `data/markets.py` | Orphaned |
| `data/lookup_service.py` | Orphaned |
| `research/contracts.py` | Orphaned |

## Architectural Requirements

- For each file: confirm zero production imports (grep for "from data.X import" or "import data.X")
- Check test dependencies: if only used by tests, delete tests too
- Check for circular orphaned dependencies (A imports B, B imports C, none imported by production)
- Archive or delete confirmed orphaned files
- Document any historical value before deletion
- Verify system still starts and tests pass after deletion

## Acceptance Criteria

- [ ] Each orphaned file verified as unused
- [ ] Orphaned files deleted
- [ ] Associated tests deleted
- [ ] System starts without errors
- [ ] All remaining tests pass

## Definition of Done

- **Tests Required**: None
- **Documentation Required**: Deletion log
- **Code Review Gate**: 2,500 line reduction in codebase

## Notes

~2,500 lines of code serving zero production value.

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
