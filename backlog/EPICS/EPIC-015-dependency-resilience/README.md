# EPIC-015: Dependency Resilience

| Field | Value |
|-------|-------|
| Priority | **P3** |
| Status | 🔴 Open |
| Stories | 1 |
| Created | 2026-02-28 |
| Depends On | None |

## Context

The platform depends on several external packages with non-trivial risk profiles: `yfinance` (scraping-based financial data, no official API), `edgartools` (SEC EDGAR parsing, subject to format changes), and `supabase` (managed Postgres — a vendor lock-in point). None have formal abstraction layers that would allow swapping them out without broad codebase changes.

Additionally, the circuit breaker pattern exists in `agents/resilience.py` but is not wired to any LLM provider calls. LLM provider failures result in uncontrolled error propagation rather than graceful degradation.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-052](STORIES/STORY-052-dependency-audit-and-fallbacks.md) | Audit and Harden External Dependencies | MEDIUM |

## Definition of Done

- [ ] All high-risk external dependencies are abstracted behind interfaces
- [ ] Circuit breaker is wired to LLM provider calls
- [ ] Fallback behaviour is documented for each external dependency

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
