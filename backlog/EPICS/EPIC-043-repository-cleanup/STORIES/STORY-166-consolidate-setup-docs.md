# STORY-166: Consolidate Setup Documentation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-043: Repository Cleanup & Professional Organization |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Problem

> Multiple setup guides (`SETUP.md`, `SETUP_GUIDE.md`) create confusion about which to follow.

## Problem Statement

New developers face a choice: `SETUP.md` (brief) or `SETUP_GUIDE.md` (comprehensive). This is unnecessary cognitive load. There should be ONE canonical setup guide, with the other either deleted (if redundant) or converted to a specific purpose (e.g., "Quick Start" vs. "Detailed Setup"). The comprehensive guide should be the default; quick start can be a section within it.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Developer Experience** | Clear, single source of truth for setup |
| **Onboarding** | No confusion about which guide to follow |
| **Maintenance** | One doc to update, not two |

## Affected Files

| File | Action |
|------|--------|
| `SETUP.md` | Consolidate into SETUP_GUIDE.md or delete |
| `SETUP_GUIDE.md` | Keep as canonical, add quick start section |
| `TROUBLESHOOTING.md` | Keep, link from setup guide |

## Architectural Requirements

- Evaluate `SETUP.md` vs. `SETUP_GUIDE.md` — determine which has better content
- Consolidate into single canonical file: `docs/guides/setup.md`
- Structure: Quick Start (5 min), Full Setup (comprehensive), Troubleshooting (link)
- Delete redundant file after consolidation
- Update all internal links to point to new location
- Update main README setup link
- Add redirect note in old location if file was widely referenced

## Acceptance Criteria

- [ ] Single canonical setup guide in `docs/guides/setup.md`
- [ ] Quick start section for impatient developers
- [ ] Redundant setup file removed
- [ ] All links updated
- [ ] Main README points to correct guide

## Definition of Done

- **Tests Required**: Link checker, manual verification of setup steps
- **Documentation Required**: Consolidated setup guide
- **Code Review Gate**: New developer can follow single guide successfully

## Notes

One guide to rule them all.

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
