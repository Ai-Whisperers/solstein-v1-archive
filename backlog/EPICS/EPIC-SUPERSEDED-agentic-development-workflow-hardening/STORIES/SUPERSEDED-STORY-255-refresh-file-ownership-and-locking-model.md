# STORY-255: Refresh File Ownership and Locking Model into Maintained Docs

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P2 - Medium |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | Medium |

---

## Problem Statement

The current file ownership matrix is historical, stream-specific, and not synced with the current active epics, generated docs, or critical-path modules.

### Audit Context — 2026-04-02

The ownership problem is broader than file labels. Current agent context is split across:

- canonical queue state in `planning/QUEUE.md`
- informational GitHub issue state in `planning/generated/GITHUB_ISSUE_SNAPSHOT.{json,md}`
- generated registries under `docs/reference/generated/`
- operator instructions in `JONATHAN_README.md` and audit docs

Ownership and locking guidance should tell agents which files are execution-control surfaces, which files are generated/informational, and which files can drift if two workers touch them concurrently.

## Acceptance Criteria

- [ ] Ownership and locking guidance is refreshed for current critical paths.
- [ ] The model references canonical backlog epics instead of stale stream labels.
- [ ] Where possible, ownership guidance is generated or derived from current artifact metadata rather than maintained manually.
- [ ] The new ownership surface is linked from active backlog and agent workflow docs.
- [ ] The refreshed guidance explicitly marks `planning/QUEUE.md` as an execution-control file and `planning/generated/*` as generated informational context.

## Definition of Done

- [ ] New ownership/locking docs committed
- [ ] Historical matrix either superseded or explicitly marked as archival
- [ ] Current coordination guidance is short, accurate, and queryable
