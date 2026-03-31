# Agentic Workflow Backlog Review 2026-03-27

## Purpose

This review answers a narrower question than the master audit:

What backlog work still needs to be described explicitly so Claude-style agentic development can operate safely, quickly, and repeatedly on Solstein without reintroducing drift?

This is not the same as the product's runtime multi-agent roadmap.

Two separate concerns exist:

1. **Product/runtime agent orchestration**: research graph nodes, checkpointing, approvals, connector contracts.
2. **Developer-agent workflow over the repository**: generated context surfaces, deterministic bootstrap, focused regression packs, ownership/locking, handoff artifacts, and strict structural gates.

The backlog already covers much of the first category. It only partially covers the second.

## Existing Backlog Coverage That Already Helps Agentic Work

These epics are already materially relevant and should remain dependencies instead of being duplicated:

- `EPIC-013` Test Suite Integrity
- `EPIC-014` Observability & Telemetry
- `EPIC-017` Developer Experience
- `EPIC-021` Modern LLM Stack Migration
- `EPIC-022` LangGraph Agent Orchestration
- `EPIC-034` Exception Handling Transparency
- `EPIC-035` Async-First External Adapters
- `EPIC-054` Durable Research Control Plane
- `EPIC-055` Safe Connector Runtime Contracts
- `EPIC-056` Inline Claim Adjudication and Approval Workflow
- `EPIC-057` Human Review Control Plane
- `EPIC-061` Adaptive Research Planning and Source Intelligence
- `EPIC-065` Documentation Lifecycle Automation and CI Enforcement
- `EPIC-066` Architectural Boundaries and Cycle Elimination

## What Is Still Missing From The Backlog

The remaining gaps are mostly in the developer-agent workflow layer.

### Gap 1: No Canonical Agent Capability Matrix

The repo still lacks a generated source-of-truth artifact that answers:

- which runtime agents/nodes are real
- which are deprecated, stubbed, or excluded
- which external tools each one calls
- which schemas each one reads/writes
- which tests and audits cover each one

Without this, every new agent session has to infer capability and status from scattered docs and source.

### Gap 2: No Deterministic `agent-ready` Bootstrap

There is still no single command or workflow that makes the repo ready for agent execution with:

- hook installation
- generated docs refresh
- strict gate availability
- minimal env/profile setup
- verification that the core tokenless surfaces are current

This remains spread across ad-hoc commands.

### Gap 3: No Focused Regression Pack For Agent Edits

The repo now has several targeted gates, but there is not yet a single maintained "agent edit safety pack" that validates:

- core scoring/enrichment behavior
- connector boundary contracts
- async boundary rules
- generated docs freshness
- orchestration-critical state/output contracts

The existing test universe is too large and too noisy for iterative agent use.

### Gap 4: No Generated Boundary And State Ownership Registry

The docs automation work is underway, but the most valuable agent-reading artifacts are still missing:

- pipeline boundary registry
- state ownership map
- connector contract surface map
- release-critical surface manifest

Without these, agents still need to open too many files to answer simple structural questions.

### Gap 5: No Durable Handoff Artifact Standard

There is not yet a standard bundle for passing work between agent sessions that captures:

- current target issue/story
- touched files
- relevant generated indexes
- verification commands/results
- unresolved risks

The dev log helps historically, but it is not yet a concise, queryable handoff surface.

### Gap 6: No Maintained Ownership/Locking Model For Current Agent Work

`docs/FILE-OWNERSHIP-MATRIX.md` is historical and stream-based, but it is not generated, not synced with current epics, and not integrated into the active docs topology. For agentic collaboration, ownership/lock surfaces need to be current or they become misdirection.

## Backlog Decision

These gaps justify a dedicated epic:

- `EPIC-067` Agentic Development Workflow Hardening

This epic does not replace the runtime graph/orchestration epics.
It makes the repository itself legible and safe for repeated agent-driven change.

## New Stories Added

- `STORY-250` Generate agent capability matrix and coverage ledger
- `STORY-251` Build deterministic `make agent-ready` bootstrap
- `STORY-252` Create focused agent-safe regression and gate pack
- `STORY-253` Generate boundary/state ownership registries for critical pipeline nodes
- `STORY-254` Standardize agent handoff artifact bundle and session checkpoint docs
- `STORY-255` Refresh file ownership/locking model into maintained generated docs

## Priority Order

Recommended implementation order:

1. `STORY-251` deterministic bootstrap
2. `STORY-252` focused regression pack
3. `STORY-253` boundary/state registries
4. `STORY-250` capability matrix
5. `STORY-254` handoff bundle standard
6. `STORY-255` maintained ownership/locking model

This order gives the highest short-term leverage for agent reliability and reduces re-audit cost immediately.
