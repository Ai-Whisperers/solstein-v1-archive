# STORY-251: Build Deterministic `make agent-ready` Bootstrap

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | Low |

---

## Problem Statement

Agent setup still depends on remembering multiple independent commands for hooks, generated docs, and strict surfaces. That is unnecessary friction and causes inconsistent session starts.

### Audit Context — 2026-04-02

The current repo now has two materially different planning surfaces:

- `planning/QUEUE.md` is the autonomous worker's canonical execution order.
- GitHub issues provide useful context, but they are not the scheduling authority for cron shifts.

Agents need one deterministic bootstrap that makes this distinction visible up front and refreshes the cheap local context artifacts they rely on.

## Acceptance Criteria

- [ ] `make agent-ready` installs hooks, refreshes generated docs, and verifies the maintained engineering surfaces.
- [ ] The command is idempotent and safe to rerun.
- [ ] The command prints actionable failure information when readiness checks fail.
- [ ] The workflow is documented in the engineering/reference docs.
- [ ] The command refreshes or validates the informational GitHub issue snapshot so agents do not need to query the live tracker just to understand current issue context.
- [ ] The command output explicitly states that `planning/QUEUE.md` remains canonical for work selection.

## Definition of Done

- [ ] Bootstrap command added to `Makefile`
- [ ] Hook path and generated-doc checks are included
- [ ] Maintained readiness docs updated
