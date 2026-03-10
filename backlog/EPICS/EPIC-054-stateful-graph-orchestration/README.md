# EPIC-054: Durable Research Control Plane

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | STORY-206, STORY-207, STORY-208, STORY-209 |
| **Dependencies** | EPIC-052, EPIC-053, EPIC-055 |

## Context

Solstein has staged pipelines and stage gates, but run lifecycle state is fragmented across execution paths. Durable control-plane patterns from LangGraph and AutoGen emphasize run state persistence, explicit lifecycle transitions, and resumability as first-class operations.

This epic adds a durable run model and recovery controls while preserving existing enrichment and scoring business logic.

## Scope

| Category | Action |
|----------|--------|
| Run Lifecycle | Persist canonical run states (created/running/paused/failed/completed/cancelled) |
| Checkpointing | Durable checkpoints per stage transition |
| Operations | Resume, replay, and cancel controls with safe semantics |
| Journaling | Unified machine + human event journal for each run |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| STORY-206 | Persist canonical run state model | P1 | 🔴 Not Started |
| STORY-207 | Add stage-level checkpoint and replay primitives | P1 | 🔴 Not Started |
| STORY-208 | Implement resume/cancel operations with deterministic transitions | P1 | 🔴 Not Started |
| STORY-209 | Build unified run journal for gate and review decisions | P2 | 🔴 Not Started |

## Success Criteria

- Run lifecycle states are persisted and queryable for every run.
- Failed run resumes from checkpoint without duplicate side effects.
- Cancel operation transitions active run to terminal cancelled state safely.
- Run journal includes machine events and review decisions.

## Risks

| Risk | Mitigation |
|------|------------|
| Runtime complexity increases | Start with minimal graph around existing stages |
| State drift between stages | Enforce typed schema validation at each node |
| Recovery bugs create duplicate writes | Use idempotent stage keys and write guards |
