# STORY-168: Create Repository Organization Standards

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-043: Repository Cleanup & Professional Organization |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-165, STORY-166, STORY-167 |

## The Problem

> No standards exist for where documents belong — hence the accumulation in root.

## Problem Statement

The repository lacks clear standards for document organization. This leads to documents being dumped in the root "for now" and never moved. The fix is a `REPOSITORY_STRUCTURE.md` document that defines: what belongs in root, what belongs in docs/, naming conventions, and the approval process for adding root-level files. This prevents future accumulation.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Clear rules prevent future clutter |
| **Onboarding** | New developers know where things go |
| **Code Review** | Objective standard for organization PRs |

## Affected Files

| File | Action |
|------|--------|
| New: `REPOSITORY_STRUCTURE.md` | Create standards document |
| `.github/PULL_REQUEST_TEMPLATE.md` | Add organization checklist |

## Architectural Requirements

- `REPOSITORY_STRUCTURE.md` defining:
  - Root-level allowed files (README, LICENSE, Makefile, essential config)
  - `docs/` subdirectory purposes (guides, strategy, archive, internal)
  - Naming conventions (kebab-case, dates, descriptive)
  - Document lifecycle (current vs. archival)
  - Approval process for root-level additions
- PR template update: checklist item for "Files placed in correct location"
- CI check: warn if PR adds new files to root (not blocking, just warning)
- Example: show before/after of properly organized document

## Acceptance Criteria

- [ ] `REPOSITORY_STRUCTURE.md` exists and is clear
- [ ] PR template includes organization checklist
- [ ] CI warns on root-level file additions
- [ ] All existing docs comply with standards (or have migration plan)
- [ ] Team has reviewed and agreed to standards

## Definition of Done

- **Tests Required**: CI check for root-level additions
- **Documentation Required**: Repository structure standards
- **Code Review Gate**: Team approval of standards document

## Notes

Standards prevent the next accumulation.

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
