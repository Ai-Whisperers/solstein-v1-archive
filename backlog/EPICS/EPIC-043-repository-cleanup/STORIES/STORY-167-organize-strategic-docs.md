# STORY-167: Organize Strategic Documents and Call Summaries

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-043: Repository Cleanup & Professional Organization |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Problem

> `call-summary-michiel-kuiper-2026-02-27.md` belongs with other strategic documents, not cluttering the root.

## Problem Statement

Strategic documents (call summaries, meeting notes, strategic plans) are important for context but don't belong in the repository root. They should be organized in `docs/strategy/` or `docs/internal/strategy/` with clear naming conventions. This keeps the root clean while preserving institutional knowledge.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Repository Cleanliness** | Root contains only essential files |
| **Knowledge Preservation** | Strategic docs organized and findable |
| **Professionalism** | External contributors see clean structure |

## Affected Files

| File | Action |
|------|--------|
| `call-summary-michiel-kuiper-2026-02-27.md` | Move to `docs/strategy/calls/` |
| `AGENT_DEPLOYMENT_GUIDE.md` | Move to `docs/internal/` or `docs/ops/` |
| `CHANGELOG.md` | Keep in root (standard practice) |

## Architectural Requirements

- Create `docs/strategy/calls/` for call summaries
- Create `docs/strategy/plans/` for strategic planning docs
- Create `docs/internal/` for internal operational guides
- Naming convention: `YYYY-MM-DD-descriptive-name.md` for dated docs
- Index file: `docs/strategy/README.md` listing all strategic documents
- Update main README with link to strategy docs section
- Preserve git history (git mv)

## Acceptance Criteria

- [ ] Strategic documents organized in `docs/strategy/`
- [ ] Call summaries in `docs/strategy/calls/`
| [ ] Internal ops guides in `docs/internal/`
- [ ] Index document lists all strategic docs
- [ ] Naming convention applied consistently

## Definition of Done

- **Tests Required**: Link checker
- **Documentation Required**: Strategy docs index
- **Code Review Gate**: Reviewer can find any strategic doc within 30 seconds

## Notes

Strategic docs are valuable — organized, not deleted.

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
