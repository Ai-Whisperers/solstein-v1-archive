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

## Acceptance Criteria

- [ ] `make agent-ready` installs hooks, refreshes generated docs, and verifies the maintained engineering surfaces.
- [ ] The command is idempotent and safe to rerun.
- [ ] The command prints actionable failure information when readiness checks fail.
- [ ] The workflow is documented in the engineering/reference docs.

## Definition of Done

- [ ] Bootstrap command added to `Makefile`
- [ ] Hook path and generated-doc checks are included
- [ ] Maintained readiness docs updated
