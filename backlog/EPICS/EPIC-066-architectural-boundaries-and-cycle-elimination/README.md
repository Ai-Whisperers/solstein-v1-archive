# EPIC-066: Architectural Boundaries and Cycle Elimination

> **Priority**: P1 - High
> **Stories**: 4 (STORY-246 through STORY-249)
> **Effort**: M (1-2 weeks)
> **Dependencies**: EPIC-065 (Documentation Lifecycle Automation and CI Enforcement), EPIC-031 (Shared Library Architecture)
> **Status**: 🔴 Not Started

---

## Problem

The recursive structural sweep found dependency-shape debt that was not captured in the original source audit:

- a live adapter/discovery/registry import cycle
- domain code importing analytics-owned constants
- infrastructure code importing helper functions from higher `research` modules

These issues do not always fail at runtime immediately, but they make strict typing, generated docs, AST enforcement, and future refactors brittle.

---

## Scope

| Category | Action |
|---|---|
| Import Cycles | Eliminate static and runtime-significant cycles in core pipeline modules |
| Module Boundaries | Move helpers and constants to lower shared layers or invert dependencies cleanly |
| Guardrails | Promote cycle and boundary checks from advisory tools into maintained engineering gates |
| Docs | Keep audit/backlog/generated docs aligned with architectural enforcement rollout |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| STORY-246 | Break `patents_unified` / discovery / registry cycle | P1 | S | 🔴 Open |
| STORY-247 | Move canonicalization and hashing helpers to a lower shared boundary | P1 | M | 🔴 Open |
| STORY-248 | Decouple domain value objects from analytics constants | P1 | S | 🔴 Open |
| STORY-249 | Enforce import-cycle and module-boundary checks in maintained gates | P1 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: `domain` must not import from `analytics`.
- **REQ-2**: `infrastructure` must not import from `research` for generic utilities.
- **REQ-3**: Cycle and boundary checks must distinguish true architectural violations from benign tooling noise.
- **REQ-4**: Refactors must preserve current behavior while improving package-addressability and generated-doc fidelity.

---

## Success Criteria

- The `patents_unified` / discovery / registry cycle is removed.
- Shared canonicalization and hashing helpers live in a lower, reusable module.
- `domain/value_objects.py` no longer depends on analytics-owned scoring constants.
- Maintained engineering gates can run cycle and boundary checks without permanent red noise.

## Autonomous Continuation Notes

### Queue Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` before working any story here.
- `planning/QUEUE.md` marks this epic `BLOCKED`.
- Current blockers are `EPIC-065/STORY-245` and the not-yet-started `EPIC-031` stories.

### Next Agent Action

- Do not begin implementation until the blockers are resolved in the queue.
- Once unblocked, execute in dependency order: `STORY-246` -> `STORY-247` -> `STORY-248` -> `STORY-249`.
- Treat `STORY-249` as the capstone gate-promotion story after the underlying cycle and boundary defects are actually removed.

### Required Working Style

- Use the architectural findings from the recursive structural sweep and keep fixes narrowly tied to real cycle/boundary defects.
- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Avoid “cleanup” edits that only move code around without eliminating a measured cycle, boundary violation, or guardrail gap.

### Minimum Verification For Future Agents

- Run the maintained structural gates and supporting checks after each story, not just at epic end.
- Validate that cycle/boundary tooling becomes less noisy because the architecture improved, not because the checks were weakened.
