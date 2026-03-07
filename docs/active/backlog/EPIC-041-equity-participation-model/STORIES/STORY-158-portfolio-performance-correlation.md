# STORY-158: Portfolio Company Performance Correlation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-041: Equity Participation Business Model |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-157 |

## The Strategic Context

> "Demonstrate that Solstein intelligence correlates with portfolio company success."

## Problem Statement

If Solstein takes equity in portfolio companies, we need to prove our intelligence creates value. This requires correlating Solstein signals with company performance: did companies with high Solstein scores outperform? Did AI-readiness predict transformation success? This data becomes the pitch to PE firms: "Our intelligence doesn't just inform decisions — it predicts success."

## Impact

| Dimension | Impact |
|-----------|--------|
| **Value Proof** | Demonstrate intelligence → performance correlation |
| **Sales Pitch** | Data-driven proof of Solstein value |
| **Product Improvement** | Feedback loop for scoring models |

## Affected Files

| File | Issue |
|------|-------|
| `analytics/` | No performance correlation analysis |
| `domain/equity/` | No performance tracking |

## Architectural Requirements

- Performance data ingestion: revenue growth, EBITDA, valuation changes from portfolio companies
- Correlation analysis: Solstein scores vs. actual performance (predictive accuracy)
- AI-readiness validation: did AI-ready companies transform faster/better?
- Attribution modeling: isolate Solstein impact from other factors
- Benchmarking: portfolio performance vs. sector benchmarks
- Reporting: automated performance reports for equity positions
- Feedback loop: use performance data to improve scoring models
- Privacy: handle sensitive financial data securely, appropriate access controls

## Acceptance Criteria

- [ ] Portfolio company performance data ingested
- [ ] Solstein score correlation calculated
- [ ] AI-readiness predictive accuracy measured
- [ ] Performance reports generated automatically
- [ ] Feedback loop improves scoring models

## Definition of Done

- **Tests Required**: Correlation calculation validation
- **Documentation Required**: Performance correlation methodology
- **Code Review Gate**: Reviewer verifies statistical methodology is sound

## Notes

Proof that Solstein intelligence creates tangible value.
