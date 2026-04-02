# EPIC-038: AI-Readiness Assessment Framework

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Owner** | Product Strategy |
| **Created** | 2026-03-01 |

## Context

The call with Michiel Kuiper revealed a critical gap in the PE market: the traditional PE playbook (buy, repackage, sell) is breaking because AI-enabled due diligence exposes "perfume on coal." Portfolio companies without AI tooling are like bicycles competing against cars — the gap widens exponentially. Solstein needs an AI-Readiness Assessment Framework to evaluate PE portfolio companies' transformation potential. This becomes a core differentiator: not just market intelligence, but transformation readiness scoring that predicts which companies can successfully adopt AI and which cannot.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-145 | Portfolio Company AI-Readiness Scoring Model | P1 |
| STORY-146 | AI Transformation Readiness Calculator | P1 |
| STORY-147 | PE Due Diligence Integration Module | P1 |
| STORY-148 | Transformation Roadmap Generator | P2 |

## Dependencies

- EPIC-007 (DDD Migration) — domain models for assessment
- EPIC-021 (Modern LLM Stack) — LLM-powered assessment generation

## Notes

This framework becomes a core differentiator in PE sales. It answers the question: "Can this company actually transform, or is it just a coat of paint?"

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
