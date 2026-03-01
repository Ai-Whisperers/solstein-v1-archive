# STORY-131: Add Null Safety Guards for Division Operations

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> scoring.py:166,280,302 — division by zero if employees/revenue is 0. financial_health.py:93,114 — same.

## Problem Statement

The scoring algorithms divide by revenue and employee count without checking if they're zero or None. When a company has no reported revenue (common for pre-revenue startups) or no employee data, the division raises ZeroDivisionError or TypeError. These exceptions are caught somewhere up the stack and turned into None, which then propagates as a missing score. The analyst sees no score and assumes the company wasn't analyzed. In reality, the analysis crashed on a math error.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Division by zero crashes scoring |
| **Data Quality** | Missing scores for valid companies |
| **Debuggability** | Math errors look like data gaps |

## Affected Files

| File | Issue |
|------|-------|
| `analytics/scoring.py:166,280,302` | Division by zero risk |
| `analytics/scorers/financial_health.py:93,114` | Division by zero risk |
| `analytics/scorers/growth_momentum.py` | Division by zero risk |

## Architectural Requirements

- All division operations check for zero/None denominator before dividing
- Safe division function: safe_div(numerator, denominator, default=0.0) returns default if denominator is 0 or None
- All scoring metrics use safe_div
- Metrics that cannot be calculated (division by zero) return explicit "N/A" or null with reason code, not just None
- Unit tests for zero and None denominator cases

## Acceptance Criteria

- [ ] safe_div function exists and is used for all divisions
- [ ] Zero denominator returns explicit indicator, not None
- [ ] None denominator handled gracefully
- [ ] Unit tests cover zero/None cases

## Definition of Done

- **Tests Required**: Unit tests for zero/None denominator
- **Documentation Required**: None
- **Code Review Gate**: Reviewer finds zero raw "/" operators in scoring files

## Notes

Math errors should not look like missing data.
