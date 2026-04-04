# EPIC-067: Agentic Development Workflow Hardening

> ⚫ **SUPERSEDED** — This epic was superseded by `EPIC-067-legacy-runtime-canonicalization`
> which took the EPIC-067 number and was completed (STORY-255 through STORY-258, STORY-271 — all DONE).
> Story numbers 250-255 in this directory **conflict** with completed work in other epics:
> STORY-250 (EPIC-033), STORY-251 (EPIC-059), STORY-252 (EPIC-021), STORY-253/254 (EPIC-013),
> STORY-255 (EPIC-067-legacy). **Do not implement these stories under these numbers.**
> Preserved for audit trail only.
>
> **Priority**: P1 - High (SUPERSEDED)
> **Stories**: 6 (STORY-250 through STORY-255 — number-colliding with completed work, superseded)
> **Effort**: L (2-4 weeks)
> **Dependencies**: EPIC-013, EPIC-014, EPIC-017, EPIC-021, EPIC-022, EPIC-054, EPIC-055, EPIC-061, EPIC-065, EPIC-066
> **Status**: ⚫ SUPERSEDED

---

## Problem

Solstein now has stricter tests, AST rules, generated docs, and audit indexes, but the repository is still not fully optimized for repeated Claude/Codex-style agent work.

The core gap is that the backlog heavily covers runtime multi-agent orchestration, but only partially covers the *developer-agent workflow* needed to navigate and modify this repo safely:

- no canonical capability matrix for real vs deprecated agents/nodes
- no deterministic `agent-ready` bootstrap
- no single focused regression pack for agent edits
- no generated boundary/state ownership registry for critical nodes
- no standard handoff artifact bundle between sessions
- no maintained ownership/locking surface for concurrent agent work

Without these, every new agent session still spends too much effort rediscovering context and too little applying verified changes.

### Audit Update — 2026-04-02

Current workflow review confirms a specific context split that this epic should close:

- `planning/QUEUE.md` is still the autonomous worker's execution authority. Cron shifts are documented to pick the first `READY` story from the queue, not from GitHub Issues.
- The live GitHub issue tracker duplicates backlog/epic planning state and is therefore informational today, not canonical.
- A local cached issue snapshot is now available at `planning/generated/GITHUB_ISSUE_SNAPSHOT.{json,md}` so agents can inspect the current tracker without treating it as scheduling authority.
- The remaining workflow gap is not "make the worker follow GitHub issues"; it is "make the canonical queue, cached tracker view, generated indexes, and handoff surfaces explicit and cheap to reuse."

---

## Scope

| Category | Action |
|---|---|
| Bootstrap | Make agent setup deterministic and one-command |
| Context Surfaces | Generate token-cheap capability, boundary, and ownership indexes |
| Regression Safety | Build a maintained focused gate pack for iterative agent edits |
| Handoffs | Standardize compact session handoff artifacts |
| Coordination | Replace stale ownership/locking docs with maintained surfaces |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| STORY-250 | Generate agent capability matrix and coverage ledger | P1 | M | 🔴 Open |
| STORY-251 | Build deterministic `make agent-ready` bootstrap | P1 | S | 🔴 Open |
| STORY-252 | Create focused agent-safe regression and gate pack | P1 | M | 🔴 Open |
| STORY-253 | Generate boundary and state ownership registries | P1 | L | 🔴 Open |
| STORY-254 | Standardize agent handoff artifact bundle and checkpoint docs | P1 | M | 🔴 Open |
| STORY-255 | Refresh file ownership and locking model into maintained docs | P2 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: Agent bootstrap must be deterministic and idempotent.
- **REQ-2**: Generated context surfaces must be derived from source code, tests, and audit artifacts rather than handwritten summaries.
- **REQ-3**: The focused regression pack must cover commercially critical paths without requiring the entire test suite.
- **REQ-4**: Handoff artifacts must be compact enough for fast agent reuse and detailed enough to prevent context drift.
- **REQ-5**: Ownership/locking guidance must be current, not historical.

---

## Success Criteria

- A new agent session can run one command and know whether the repo is ready for safe work.
- An agent can answer "what is real, what is deprecated, what is covered, and what is risky" from generated docs first.
- Iterative edits can be validated with a focused gate pack in minutes, not the full suite in hours.
- Session handoffs are queryable and compact.
- Ownership/locking guidance aligns with current critical-path modules and active epics.
- The workflow makes the distinction between execution authority (`planning/QUEUE.md`) and informational context (`planning/generated/GITHUB_ISSUE_SNAPSHOT.*`) explicit enough that agents do not infer the wrong source of truth.
