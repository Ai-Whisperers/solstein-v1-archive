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
