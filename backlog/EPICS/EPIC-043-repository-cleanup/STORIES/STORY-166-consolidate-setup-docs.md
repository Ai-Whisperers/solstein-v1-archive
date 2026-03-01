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
