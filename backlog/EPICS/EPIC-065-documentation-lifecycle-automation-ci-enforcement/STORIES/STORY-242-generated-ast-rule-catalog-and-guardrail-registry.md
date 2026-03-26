# STORY-242: Generate AST Rule Catalog and Guardrail Registry

| Field | Value |
|---|---|
| **Status** | 🟡 In Progress |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

AST guardrails exist, but there is no compact generated catalog describing which structural bug classes are already blocked and why those rules exist.

## Acceptance Criteria

- [x] A generated `AST_RULE_CATALOG.md` is committed under `docs/reference/generated/`.
- [x] A machine-readable JSON catalog is generated from `tooling/ast-grep/rules/`.
- [x] Rule entries include severity, blocking status, related audit issues, and test coverage paths.
- [ ] The catalog expands to include non-`ast-grep` structural gates where applicable.

## Definition of Done

- [x] Catalog generation is automated via `scripts/docs/generate_all.py`.
- [x] Generated outputs are refreshed automatically by repo hooks.
- [ ] The catalog is referenced by the engineering guardrail docs and CI policy.
