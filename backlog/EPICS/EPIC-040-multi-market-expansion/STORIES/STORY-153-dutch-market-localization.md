# STORY-153: Dutch Market Localization & Data Sources

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-040: Multi-Market Geographic Expansion |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019 |

## The Strategic Context

> "Netherlands is the primary market with Energy 21 as the proof case."

## Problem Statement

Solstein needs deep Dutch market integration: KVK (Chamber of Commerce) data, Dutch energy regulator (ACM) filings, Dutch grid operators (TenneT, Stedin, Liander), and Dutch-specific regulatory frameworks. Energy 21 proves the methodology works in Netherlands — now Solstein needs to productize this for broader Dutch energy market coverage.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Market Penetration** | Deep Dutch market coverage |
| **Proof Case Scale** | Expand Energy 21 methodology |
| **Local Credibility** | Dutch data sources = local trust |

## Affected Files

| File | Issue |
|------|-------|
| `adapters/` | No Dutch-specific adapters |
| `config.py` | No Dutch market configuration |

## Architectural Requirements

- KVK integration: Dutch Chamber of Commerce company data, annual reports, officer information
- ACM (Authority for Consumers & Markets): regulatory filings, market monitoring data
- Grid operators: TenneT (TSO), Stedin/Liander/Enexis (DSO) connection data
- Energy-specific: Energieakkoord participation, SDE++ subsidy data, renewable energy certificates (GOs)
- Language: Dutch language support for company names, descriptions, documents
- Localization: Dutch number formats, currency (EUR), date formats
- Market-specific scoring: adjust scoring models for Dutch regulatory environment
- Data quality: validate Dutch data sources for completeness and freshness

## Acceptance Criteria

- [ ] KVK company data integrated
- [ ] ACM regulatory filings accessible
- [ ] Grid operator data connected
- [ ] Dutch language support active
- [ ] Dutch market scoring models calibrated

## Definition of Done

- **Tests Required**: End-to-end Dutch company research workflow
- **Documentation Required**: Dutch market data source guide
- **Code Review Gate**: Reviewer verifies Dutch data covers >80% of energy market

## Notes

Netherlands is the beachhead — get it right here first.

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
