# EPIC-055: Safe Connector Runtime Contracts

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | STORY-210, STORY-211, STORY-212, STORY-213 |
| **Dependencies** | EPIC-050, EPIC-051 |

## Context

Connector execution currently mixes adapter-specific behavior with inconsistent error/status semantics. Patterns from AutoGen tool wrappers and Apify/Spider notebooks show better reliability with typed connector envelopes, deterministic retries, and explicit runtime controls.

This epic standardizes connector runtime contracts and operational controls for research/enrichment connectors.

## Scope

| Category | Action |
|----------|--------|
| Contracts | Define typed connector request/response envelopes |
| Runtime | Add shared retry, timeout, and circuit-breaker wrapper |
| Migration | Migrate acquisition connectors to shared runtime path |
| Controls | Enforce config-driven session/proxy/page-budget behavior |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| STORY-210 | Define connector request/response envelope schema | P1 | 🔴 Not Started |
| STORY-211 | Add shared retry/circuit-breaker connector wrapper | P1 | 🔴 Not Started |
| STORY-212 | Migrate web acquisition connectors to runtime contracts | P1 | 🔴 Not Started |
| STORY-213 | Add config-driven session/proxy/page-budget controls | P1 | 🔴 Not Started |

## Success Criteria

- All connectors return envelope (`success`, `degraded`, `failure`) with typed metadata.
- Retry/termination behavior is deterministic for timeout/429/5xx classes.
- Migrated connectors have no silent failure paths.
- Session/proxy/page-budget limits are enforced from config.

## Risks

| Risk | Mitigation |
|------|------------|
| Over-segmentation adds overhead | Keep initial role set minimal (4 core roles) |
| Hidden coupling between roles | Enforce contracts and forbid implicit shared state |
| Infinite loops in role chatter | Hard-stop budgets + escalation to review gate |

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
