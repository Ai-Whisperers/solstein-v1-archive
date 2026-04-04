# STORY-252: Create Focused Agent-Safe Regression and Gate Pack

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Agentic Development Workflow Hardening |
| **Created** | 2026-03-27 |
| **Risk** | High |

---

## Problem Statement

The full test suite is too large and too noisy for iterative agent work, but the current focused gates are still incomplete for orchestration and contract-heavy changes.

## Acceptance Criteria

- [ ] A maintained focused gate pack exists for high-risk agent edits.
- [ ] The pack covers scoring/enrichment outcomes, connector envelopes, async boundaries, generated docs freshness, and critical orchestration contracts.
- [ ] The pack is runnable in minutes and is documented as the default validation surface for agent work.
- [ ] Known stale or misleading tests are excluded or replaced with explicit rationale.

## Definition of Done

- [ ] Gate command added to `Makefile`
- [ ] Test inventory documented
- [ ] At least one orchestration-focused regression slice added
