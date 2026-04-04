# EPIC-066: Architectural Boundaries and Cycle Elimination

> **Priority**: P1 - High
> **Stories**: 4 ([STORY-246](STORIES/STORY-246-break-patents-unified-discovery-registry-cycle.md) through [STORY-249](STORIES/STORY-249-enforce-cycle-and-boundary-checks-in-gates.md))
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
| [STORY-246](STORIES/STORY-246-break-patents-unified-discovery-registry-cycle.md) | Break `patents_unified` / discovery / registry cycle | P1 | S | 🔴 Open |
| [STORY-247](STORIES/STORY-247-move-canonicalization-and-hashing-helpers-lower.md) | Move canonicalization and hashing helpers to a lower shared boundary | P1 | M | 🔴 Open |
| [STORY-248](STORIES/STORY-248-decouple-domain-value-objects-from-analytics-constants.md) | Decouple domain value objects from analytics constants | P1 | S | 🔴 Open |
| [STORY-249](STORIES/STORY-249-enforce-cycle-and-boundary-checks-in-gates.md) | Enforce import-cycle and module-boundary checks in maintained gates | P1 | M | 🔴 Open |

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
