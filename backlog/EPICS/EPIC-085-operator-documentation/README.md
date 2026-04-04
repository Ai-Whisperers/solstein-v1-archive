# EPIC-085: Operator Documentation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P5: Quality |
| **Phase** | P5 — Quality & Polish |
| **Created** | 2026-04-01 |

## Context

There is no operator documentation. A new operator cannot deploy the system, configure API keys, add markets, or debug a failed pipeline run without reading source code. This epic creates the four core operator documents: deployment guide, API key config guide, market catalog guide, and pipeline runbook.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-344](STORIES/STORY-344.md) | Write deployment guide: docker-compose up → working system in 10 min | 🔴 READY | Deps: STORY-320 |
| [STORY-345](STORIES/STORY-345.md) | Write API key configuration guide: which keys unlock which features | 🔴 READY | Deps: none |
| [STORY-346](STORIES/STORY-346.md) | Write market catalog customization guide: add new markets and companies | 🔴 READY | Deps: none |
| [STORY-347](STORIES/STORY-347.md) | Write pipeline operations runbook: run, monitor, debug, export | 🔴 READY | Deps: STORY-330 |

## Success Criteria

- New operator can deploy system in < 10 minutes following deployment guide
- API key guide documents every env var and what features it unlocks
- Market catalog guide demonstrates adding a new company end-to-end
- Pipeline runbook covers all failure modes and their resolutions

## Dependencies

- STORY-320 (all health checks pass) for deployment guide
- STORY-330 (golden run baseline) for operations runbook
