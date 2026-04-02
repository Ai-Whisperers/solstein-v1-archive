# STORY-155: UK/London Market Entry Infrastructure

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-040: Multi-Market Geographic Expansion |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-019, STORY-153 |

## The Strategic Context

> "London team potential — UK market entry."

## Problem Statement

UK represents a major PE market with London as financial hub. UK energy market is post-Brexit, with different regulatory framework (Ofgem), different grid (National Grid), and different market dynamics. Solstein needs UK infrastructure to support potential London team and serve UK PE clients. English language is native, but regulatory complexity is high.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Major Market** | UK is top-tier PE market |
| **London Hub** | Access to international PE firms |
| **Brexit Complexity** | Post-Brexit regulatory landscape |

## Affected Files

| File | Issue |
|------|-------|
| `adapters/` | No UK-specific adapters beyond Companies House |
| `config.py` | No UK market configuration |

## Architectural Requirements

- Companies House deep integration: already partially done, expand to full annual reports, PSC data
- Ofgem integration: energy licensing, regulatory decisions, market monitoring
- National Grid: grid connection data, balancing services, capacity market
- Brexit considerations: GB market separate from EU, different trading arrangements
- Language: English (already supported), British vs. American spelling consistency
- Currency: GBP (not EUR), currency conversion handling
- Regulatory: UK ETS (not EU ETS), different subsidy schemes (CfDs), different net zero framework
- Market structure: different supplier obligations, different consumer protection

## Acceptance Criteria

- [ ] Companies House deep integration complete
- [ ] Ofgem regulatory data accessible
- [ ] National Grid data connected
- [ ] GBP currency handling implemented
- [ ] Post-Brexit regulatory framework captured

## Definition of Done

- **Tests Required**: End-to-end UK company research workflow
- **Documentation Required**: UK market entry guide
- **Code Review Gate**: Reviewer verifies UK data covers major energy suppliers

## Notes

UK is the major leagues — high complexity, high reward.

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
