# STORY-144: Create Dead Code Detection CI Job

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-037: Dead Code Elimination Phase 2 |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> Dead code accumulated because there's no automated detection. Forensic audit found it manually.

## Problem Statement

Dead code was discovered by a forensic audit, not by automation. This means dead code accumulates between audits. The fix is CI-based dead code detection that flags potentially unused functions, classes, and modules on every PR. Tools like vulture, pylint, or custom import analysis can catch orphans before they become load-bearing.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Dead code caught early |
| **Developer Experience** | Automated feedback on PRs |

## Affected Files

| File | Issue |
|------|-------|
| `.github/workflows/` | No dead code detection |

## Architectural Requirements

- Dead code detection tool integrated in CI: vulture or pylint with unused checks
- CI job runs on every PR: flags functions/classes with zero callers
- Configurable thresholds: warn on 1+ unused items, fail on 10+
- Exclusions: tests, __init__.py files, intentional exports
- Weekly report: summary of unused code metrics
- Integration with coverage: dead code often has zero coverage

## Acceptance Criteria

- [ ] CI job detects dead code
- [ ] Configurable thresholds
- [ ] Exclusions for intentional cases
- [ ] Weekly metrics report

## Definition of Done

- **Tests Required**: PR with dead code triggers CI warning
- **Documentation Required**: CI configuration documentation
- **Code Review Gate**: Reviewer verifies tool catches known dead code

## Notes

Prevent dead code accumulation through automation.

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
