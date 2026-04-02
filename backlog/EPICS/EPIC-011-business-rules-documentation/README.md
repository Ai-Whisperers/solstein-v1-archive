# EPIC-011: Business Rules Documentation

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 2 |
| Created | 2026-02-28 |
| Depends On | [EPIC-003](../EPIC-003-core-product-correctness/README.md) (thresholds unified first) |

## Context

The scoring system is the product. It is also the most opaque part of the codebase.

Magic numbers govern every investment-critical classification: `0.4 / 0.3 / 0.3` weight the three scoring components, `7.0` is the score ceiling, `3.9` and `5.5` compete as the Lead threshold (see EPIC-003), and `1.0 - (d / 3.0)` computes data freshness decay. None of these literals are named. None have explanatory comments. None have documented business rationale.

Additionally, `data/unified_loader.py` line 929 hardcodes a GBP-to-EUR conversion rate of `1.17`. This number was correct on some date in 2024 and has been wrong every day since.

This epic is about making the business rules legible — not changing them.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-039](STORIES/STORY-039-document-scoring-business-rationale.md) | Document Business Rationale for All Scoring Rules | MEDIUM |
| [STORY-040](STORIES/STORY-040-replace-hardcoded-fx-rate.md) | Replace Hardcoded FX Rate with Configurable Source | HIGH |

## Definition of Done

- [ ] Every scoring constant is a named variable with a docstring
- [ ] No hardcoded numeric FX rate exists anywhere in the codebase
- [ ] A business glossary document explains the scoring methodology in plain language

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
