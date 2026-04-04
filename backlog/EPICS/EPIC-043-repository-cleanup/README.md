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
| [STORY-165](STORIES/STORY-165-archive-professionalization-docs.md) | Archive Historical Professionalization Documents | P2 |
| [STORY-166](STORIES/STORY-166-consolidate-setup-docs.md) | Consolidate Setup Documentation | P2 |
| [STORY-167](STORIES/STORY-167-organize-strategic-docs.md) | Organize Strategic Documents and Call Summaries | P2 |
| [STORY-168](STORIES/STORY-168-repository-organization-standards.md) | Create Repository Organization Standards | P2 |

## Dependencies

- None

## Notes

A clean repository root signals professionalism. Historical documents belong in archives, not the front page.
