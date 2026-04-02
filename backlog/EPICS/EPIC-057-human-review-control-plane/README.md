# EPIC-057: Declarative Research Recipes and Reviewer Loops

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | STORY-218, STORY-219, STORY-220, STORY-221 |
| **Dependencies** | EPIC-053, EPIC-054, EPIC-056 |

## Context

Research workflows currently depend on code-path coupling and ad-hoc prompt logic. Framework patterns from CrewAI flows and AutoGen teams show better repeatability with declarative recipes compiled into execution plans and bounded reviewer loops.

This epic introduces configuration-defined research recipes and reusable producer-reviewer loop templates.

## Scope

| Category | Action |
|----------|--------|
| Recipe Schema | Define recipe config model with validation |
| Compilation | Compile recipe to deterministic executable plan |
| Review Loop | Add bounded producer-reviewer loop template |
| Versioning | Track recipe versions, rollout, and rollback |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| STORY-218 | Define recipe schema and validator | P1 | 🔴 Not Started |
| STORY-219 | Implement recipe-to-plan compilation with deterministic hashing | P1 | 🔴 Not Started |
| STORY-220 | Add producer-reviewer loop template with bounded retries | P1 | 🔴 Not Started |
| STORY-221 | Add recipe versioning, promotion rules, and rollback controls | P2 | 🔴 Not Started |

## Success Criteria

- Recipes validate before execution with actionable error output.
- Identical recipe + input yields deterministic executable plan hash.
- Reviewer loops have hard retry limits and deterministic terminal state.
- Batch artifacts include recipe id/version; rollback is configuration-only.

## Risks

| Risk | Mitigation |
|------|------------|
| Review queue volume too high | Prioritize by impact and confidence gap |
| Manual review introduces latency | Allow partial automated progression with blocking only on critical fields |
| Feedback loops become non-deterministic | Enforce max retries and invariant checks per iteration |

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
