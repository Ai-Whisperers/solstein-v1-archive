# EPIC-040: Multi-Market Geographic Expansion

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Owner** | Market Expansion |
| **Created** | 2026-03-01 |

## Context

The call identified three geographic markets for expansion: Netherlands (primary, with Energy 21 proof case), Spain (identified opportunity), and UK/London (potential London team). Solstein needs infrastructure to support multi-market operations: localized data sources (e.g., Spanish company registry, UK Companies House), multi-language support, and market-specific scoring adjustments. This is not just translation — it's understanding that Dutch energy markets have different regulatory frameworks than UK or Spanish markets.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-153 | Dutch Market Localization & Data Sources | P2 |
| STORY-154 | Spanish Market Localization & Expansion | P2 |
| STORY-155 | UK/London Market Entry Infrastructure | P2 |
| STORY-156 | Multi-Language Support Infrastructure | P2 |

## Dependencies

- EPIC-019 (Multi-Tenancy) — for market-specific tenant isolation
- EPIC-036 (Configuration Consolidation) — for market-specific settings

## Notes

Geographic expansion requires more than translation — it requires local market intelligence integration.

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
