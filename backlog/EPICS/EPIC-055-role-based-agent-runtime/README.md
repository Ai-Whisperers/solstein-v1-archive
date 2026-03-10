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
