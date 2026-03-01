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
