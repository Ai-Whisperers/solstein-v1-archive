# STORY-145: Portfolio Company AI-Readiness Scoring Model

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-038: AI-Readiness Assessment Framework |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-007 |

## The Strategic Context

> "The traditional PE playbook is broken. AI-enabled due diligence exposes perfume on coal. Companies without AI tooling are bicycles competing against cars."

## Problem Statement

PE firms need to evaluate not just a company's current state, but its ability to transform with AI. Current Solstein scoring evaluates market position and financials, but doesn't assess AI-readiness: data infrastructure quality, technical debt, team AI literacy, process automation potential. This leads to investments in companies that look good on paper but cannot execute AI transformation. The fix is an AI-Readiness scoring dimension that predicts transformation success.

## Impact

| Dimension | Impact |
|-----------|--------|
| **PE Decision Quality** | Avoid "perfume on coal" investments |
| **Differentiation** | Unique capability vs. generic market intelligence |
| **Transformation Success** | Predict which companies can actually transform |

## Affected Files

| File | Issue |
|------|-------|
| `analytics/scoring.py` | No AI-readiness dimension |
| `domain/models/company.py` | No AI-readiness fields |

## Architectural Requirements

- AI-Readiness Score (0-100) as new scoring dimension alongside Growth, Financial Health, Competitive Position
- Sub-dimensions: Data Infrastructure (quality/availability), Technical Debt (legacy vs. modern), AI Literacy (team capabilities), Process Automation (current automation level)
- Data sources: GitHub (code quality, test coverage), job postings (AI/ML roles), tech stack signals (modern vs. legacy), public documentation (APIs, data availability)
- Scoring model trained on successful vs. failed AI transformations (where data available)
- Visual indicator in company profile: AI-Ready / AI-Capable / AI-Challenged / AI-Resistant
- Integration with classification: AI-Ready Phoenix companies are premium targets

## Acceptance Criteria

- [ ] AI-Readiness Score appears in company profile
- [ ] Four sub-dimensions scored and displayed
- [ ] Visual indicator (Ready/Capable/Challenged/Resistant) shown
- [ ] Score influences overall classification (weight configurable)
- [ ] GitHub, job posting, tech stack data feeds into scoring

## Definition of Done

- **Tests Required**: Unit tests for AI-readiness scoring algorithm
- **Documentation Required**: AI-readiness scoring methodology documentation
- **Code Review Gate**: Reviewer verifies score correlates with known AI-successful companies

## Notes

This is the "can they actually transform?" score that PE firms desperately need.
