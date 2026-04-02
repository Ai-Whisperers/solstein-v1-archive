# STORY-146: AI Transformation Readiness Calculator

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-038: AI-Readiness Assessment Framework |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-145 |

## The Strategic Context

> "The gap between companies with AI tooling and without is like bicycles vs. cars — it widens exponentially."

## Problem Statement

PE firms need to quantify the "bicycle vs. car" gap for portfolio companies. A simple score isn't enough — they need a calculator that shows: time to AI transformation, investment required, expected ROI, risk factors. This becomes a pre-investment tool and a post-investment roadmap. Without it, PE firms are flying blind on transformation timelines and costs.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Investment Decisions** | Quantified transformation cost/timeline |
| **Portfolio Management** | Track transformation progress over time |
| **LP Reporting** | Show measurable AI transformation metrics |

## Affected Files

| File | Issue |
|------|-------|
| New: `analytics/ai_transformation_calculator.py` | Does not exist |
| `api/routers/` | No transformation calculator endpoint |

## Architectural Requirements

- Interactive calculator: input company profile, output transformation roadmap with time/cost estimates
- Model considers: company size, current tech stack, data maturity, team size, industry
- Output: Time to AI-Ready (months), Investment Required (EUR), Expected Efficiency Gains (%), Risk Factors (high/medium/low)
- Scenario planning: "What if we invest X in Y?" simulations
- Integration with Solstein company data: pre-populate calculator from existing signals
- Export: PDF transformation roadmap for LP presentations
- Historical tracking: compare predicted vs. actual transformation outcomes (feedback loop)

## Acceptance Criteria

- [ ] Calculator accepts company profile and outputs transformation roadmap
- [ ] Time, cost, ROI estimates generated with confidence intervals
- [ ] Scenario planning allows "what-if" simulations
- [ ] Pre-population from Solstein company data works
- [ ] PDF export generates LP-ready transformation roadmap

## Definition of Done

- **Tests Required**: Validation against known transformation cases
- **Documentation Required**: Calculator methodology and assumptions documentation
- **Code Review Gate**: Reviewer verifies estimates are realistic (not fantasy numbers)

## Notes

This is the "how much and how long?" tool that PE firms need for investment committees.

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
