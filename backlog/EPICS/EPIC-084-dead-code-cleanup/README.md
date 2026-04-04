# EPIC-084: Dead Code Cleanup

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P5: Quality |
| **Phase** | P5 — Quality & Polish |
| **Created** | 2026-04-01 |

## Context

Several files and directories are confirmed dead code: broken imports, retired adapters, and a frozen legacy runtime that was deprecated by ADR-009 and ADR-010. These should be deleted to reduce noise and reduce the surface area of the codebase.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-340](STORIES/STORY-340.md) | Delete data/real_data_integration.py (broken import of non-existent web_research_pipeline) | 🔴 READY | Deps: none |
| [STORY-341](STORIES/STORY-341.md) | Delete adapters/enrichment/_retired/ directory (8 dead adapter files) | 🔴 READY | Deps: none |
| [STORY-342](STORIES/STORY-342.md) | Delete adapters/discovery/_retired/ directory (dead Exa web search adapter) | 🔴 READY | Deps: none |
| [STORY-343](STORIES/STORY-343.md) | Delete research/graph/ frozen runtime (per ADR-009 and ADR-010) | ⏳ BLOCKED | Needs team sign-off |

## Success Criteria

- `data/real_data_integration.py` deleted; no remaining imports
- `adapters/enrichment/_retired/` deleted; no remaining imports
- `adapters/discovery/_retired/` deleted; no remaining imports
- `research/graph/` deleted after team sign-off ([STORY-343](STORIES/STORY-343.md))
- Dead code CI detector confirms no new orphaned modules

## Dependencies

- [STORY-343](STORIES/STORY-343.md) requires explicit team sign-off (ADR-009/010 reference frozen graph runtime)
