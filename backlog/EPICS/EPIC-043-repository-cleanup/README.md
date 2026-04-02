# EPIC-043: Repository Cleanup & Professional Organization

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

The repository root has accumulated 18+ markdown files that create visual clutter and confusion. Files like `PROFESSIONALIZATION.md`, `PROFESSIONALIZATION_COMPLETE.md`, `PROFESSIONALIZATION_FINAL_REPORT.md` are historical artifacts. `call-summary-michiel-kuiper-2026-02-27.md` belongs with other strategic documents. Multiple setup guides (`SETUP.md`, `SETUP_GUIDE.md`) create confusion. The root should contain only: README, LICENSE, Makefile, and essential config files. Everything else belongs in `docs/`, `docs/archive/`, or `docs/internal/`.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-165 | Archive Historical Professionalization Documents | P2 |
| STORY-166 | Consolidate Setup Documentation | P2 |
| STORY-167 | Organize Strategic Documents and Call Summaries | P2 |
| STORY-168 | Create Repository Organization Standards | P2 |

## Dependencies

- None

## Notes

A clean repository root signals professionalism. Historical documents belong in archives, not the front page.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
