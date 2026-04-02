# STORY-161: Automated Data Source Discovery for New Markets

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-042: Rapid Market Validation Methodology |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-028 |

## The Strategic Context

> "Click and deploy MVPs for market validation — not 3-month implementations, but 3-day proofs of concept."

## Problem Statement

Entering a new market (new geography or sector) currently requires manual research to identify data sources: company registries, regulatory databases, news sources, job boards. This takes weeks. Solstein needs automated data source discovery: input a market (e.g., "German healthcare"), output a list of relevant data sources with coverage assessment and integration difficulty. This enables 3-day market entry, not 3-month.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Speed to Market** | Reduce market entry from months to days |
| **Scalability** | Enter many markets quickly |
| **Cost Efficiency** | Automated discovery vs. manual research |

## Affected Files

| File | Issue |
|------|-------|
| New: `research/discovery/` | Does not exist |
| `config.py` | No data source registry |

## Architectural Requirements

- Market input: country + sector (e.g., "Netherlands energy", "Spain fintech")
- Source discovery: automated search for company registries, regulatory bodies, news sources, job boards
- Coverage assessment: estimate what % of market companies are covered by each source
- Integration difficulty: API availability, data quality, rate limits, cost
- Prioritization: rank sources by coverage / difficulty ratio
- Integration templates: pre-built adapters for common source types (REST API, CSV, web scraping)
- Validation: quick validation that discovered sources actually work
- Documentation: auto-generated integration guide for discovered sources

## Acceptance Criteria

- [ ] Market input produces discovered data sources
- [ ] Coverage assessment estimates provided
- [ ] Integration difficulty scored
- [ ] Sources prioritized by value/effort
- [ ] Integration templates accelerate connection

## Definition of Done

- **Tests Required**: Discovery accuracy validation for known markets
- **Documentation Required**: Data source discovery guide
- **Code Review Gate**: Reviewer verifies discovered sources are relevant

## Notes

The "3-day market entry" enabler.

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
