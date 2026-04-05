# EPIC-085: Operator Documentation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P5 — Quality & Polish |
| **Effort** | M (3–5 days) |
| **Stories** | 4 ([STORY-344](STORIES/STORY-344.md) through [STORY-347](STORIES/STORY-347.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, DoD) |

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

## Definition of Done

- [ ] [STORY-344](STORIES/STORY-344.md): `docs/operator/deployment-guide.md` exists; a cold-start test takes < 10 min
- [ ] [STORY-345](STORIES/STORY-345.md): `docs/operator/api-keys.md` documents every `*_API_KEY` env var with feature description
- [ ] [STORY-346](STORIES/STORY-346.md): `docs/operator/market-catalog.md` has step-by-step example of adding a new company
- [ ] [STORY-347](STORIES/STORY-347.md): `docs/operator/pipeline-runbook.md` documents all known failure modes and resolutions

## Dependencies

- STORY-320 ([EPIC-079](../EPIC-079-deploy-application-stack/README.md)) — all health checks pass — for deployment guide
- STORY-330 ([EPIC-081](../EPIC-081-first-real-pipeline-run/README.md)) — golden run baseline — for operations runbook
