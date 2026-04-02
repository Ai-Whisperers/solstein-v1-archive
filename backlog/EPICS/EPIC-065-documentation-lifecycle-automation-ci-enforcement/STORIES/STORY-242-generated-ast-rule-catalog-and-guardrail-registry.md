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

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
