# STORY-150: Energy Forecasting Capability Scoring

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-039: Energy Sector Domain Specialization |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Strategic Context

> "Forecasting is one of the four key B2B energy domains where AI creates value."

## Problem Statement

Energy companies live or die by forecasting: demand forecasting, price forecasting, renewable generation forecasting. Solstein needs to assess forecasting capabilities as a core signal. Companies with sophisticated forecasting (AI-powered, multi-variable, accurate) have competitive advantage. Companies with poor forecasting (Excel-based, gut feel, inaccurate) are flying blind. This module evaluates forecasting sophistication through public signals and inferred capabilities.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Competitive Assessment** | Identify forecasting leaders vs. laggards |
| **AI-Readiness** | Forecasting is gateway AI use case for energy |
| **Investment Thesis** | Forecasting capability as value creation lever |

## Affected Files

| File | Issue |
|------|-------|
| `agents/` | No forecasting capability agents |
| `analytics/scoring.py` | No forecasting sophistication dimension |

## Architectural Requirements

- Forecasting sophistication signals: job postings (data science, forecasting roles), tech stack (Python, R, forecasting libraries), public case studies, patent filings
- Accuracy inference: where public data available, compare forecasts to actuals
- Methodology assessment: statistical vs. ML vs. deep learning approaches
- Data infrastructure: access to weather, market, consumption data sources
- Integration sophistication: how well forecasting integrates with trading, operations
- Scoring: Forecasting Maturity Level (1-5) based on methodology, accuracy, integration
- Benchmarking: compare company to energy sector peers
- Use case coverage: demand, price, generation, maintenance forecasting

## Acceptance Criteria

- [ ] Forecasting sophistication scored for energy companies
- [ ] Maturity level (1-5) assigned with justification
- [ ] Peer benchmarking shows relative position
- [ ] Use case coverage (demand/price/generation/maintenance) assessed
- [ ] Forecasting capability feeds into AI-readiness score

## Definition of Done

- **Tests Required**: Validation against known forecasting leaders (e.g., large utilities with AI forecasting)
- **Documentation Required**: Forecasting assessment methodology
- **Code Review Gate**: Reviewer verifies scoring distinguishes AI forecasting from Excel

## Notes

Forecasting is the energy sector's AI gateway drug.
