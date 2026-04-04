# EPIC-054: Durable Research Control Plane

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | [STORY-391](STORIES/STORY-391-typed-state-contract.md), [STORY-392](STORIES/STORY-392-stage-transition-graph.md), [STORY-393](STORIES/STORY-393-checkpoint-resume.md), [STORY-394](STORIES/STORY-394-replay-diagnostics.md) |
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
| [STORY-391](STORIES/STORY-391-typed-state-contract.md) | Persist canonical run state model | P1 | 🔴 Not Started |
| [STORY-392](STORIES/STORY-392-stage-transition-graph.md) | Add stage-level checkpoint and replay primitives | P1 | 🔴 Not Started |
| [STORY-393](STORIES/STORY-393-checkpoint-resume.md) | Implement resume/cancel operations with deterministic transitions | P1 | 🔴 Not Started |
| [STORY-394](STORIES/STORY-394-replay-diagnostics.md) | Build unified run journal for gate and review decisions | P2 | 🔴 Not Started |

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

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Develop-Relevant Evidence

- `[STORY-391](STORIES/STORY-391-typed-state-contract.md)-typed-state-contract.md` already positions typed schema validation as the anti-drift mechanism for node state.
- `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md` and `docs/reference/SCHEMA_INVENTORY_AND_VALIDATION_NOTES.md` already treat boundary schemas as part of the enforcement model, not optional docs.
- Future run-state work should reuse those typed-boundary patterns instead of inventing mock state envelopes.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
