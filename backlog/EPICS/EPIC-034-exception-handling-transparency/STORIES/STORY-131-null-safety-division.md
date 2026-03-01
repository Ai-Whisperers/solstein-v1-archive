# STORY-131: Add Null Safety Guards for Division Operations

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-034: Exception Handling Transparency |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-132 (Exception Standards Document) |

---

## The Audit Verdict

> `scoring.py:166,280,302` — division by zero if `employees` or `revenue` is `0`. `financial_health.py:93,114` — same.

---

## Problem Statement

The scoring algorithms divide by revenue and employee count without checking if they are zero or `None`. When a company has no reported revenue — common for pre-revenue startups, which are a primary use case for this platform — or no employee data, the division raises `ZeroDivisionError` or `TypeError`. These exceptions are caught somewhere up the stack and converted to `None`, which then propagates as a missing score. The analyst sees no score and assumes the company wasn't analyzed. In reality, the analysis crashed on arithmetic.

This is a particularly embarrassing failure mode for a competitive intelligence platform targeting PE/VC professionals. Pre-revenue startups are not edge cases; they are a core segment of the deal pipeline. A platform that cannot score a pre-revenue company without crashing is not fit for purpose. The fact that the crash is silent makes it worse: the analyst does not receive an error message explaining that the company has no revenue data. They receive a blank field and are left to wonder.

The root cause is the absence of a defensive division utility. Every division operation in the scoring layer performs raw arithmetic on values that may be zero or `None`. The fix is not to add zero-checks at every division site — that approach is error-prone and will be missed in future additions. The fix is a single `safe_div` utility that encapsulates the defensive logic and is used consistently across all scoring calculations. When the denominator is zero or `None`, `safe_div` returns a configurable default and, critically, the caller knows the result is a default rather than a calculated value.

The distinction between "calculated as zero" and "could not be calculated" is meaningful in financial analysis. A company with zero revenue growth is different from a company whose revenue growth could not be calculated. The current implementation conflates these cases. The target implementation must not.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Division by zero crashes scoring for any company with zero revenue or zero employees; pre-revenue startups are unscoreable |
| **Data Quality** | Missing scores are indistinguishable from "company not analyzed"; analysts cannot assess scoring completeness |
| **Correctness** | "Could not calculate" is conflated with "calculated as zero" and with "calculated as None"; all three are semantically distinct |
| **Debuggability** | Math errors surface as missing data fields, not as exceptions; root cause is obscured by the time it reaches the analyst |
| **Trust** | Analysts who discover that a startup was unscored due to a division error lose confidence in the platform's handling of non-standard companies |

---

## Affected Files

| File | Issue |
|------|-------|
| `analytics/scoring.py:166` | Division by `employees` without zero/None check |
| `analytics/scoring.py:280` | Division by `revenue` without zero/None check |
| `analytics/scoring.py:302` | Division by `revenue` without zero/None check |
| `analytics/scorers/financial_health.py:93` | Division by `revenue` without zero/None check |
| `analytics/scorers/financial_health.py:114` | Division by `employees` without zero/None check |
| `analytics/scorers/growth_momentum.py` | Division operations without zero/None checks (specific lines to be confirmed during implementation) |

---

## Architectural Requirements

- A `safe_div` utility function must be defined in a shared utilities module accessible to all scoring components; it must not be defined inline or duplicated across files
- `safe_div` must accept: numerator (numeric or `None`), denominator (numeric or `None`), and an optional `default` parameter (numeric, default value `0.0`)
- `safe_div` must return the `default` value when the denominator is `0`, `0.0`, or `None`; it must also handle `None` numerators gracefully (returning `default`)
- `safe_div` must be the exclusive mechanism for division in all scoring files; raw `/` operators on financial metrics are prohibited in scoring modules
- When `safe_div` returns the default due to an invalid denominator, the calling code must be able to distinguish this outcome from a calculated result — either through a sentinel return value, a separate boolean flag, or a structured result type; the specific mechanism is an implementation decision but must be documented
- Scoring metrics that cannot be calculated due to zero/None denominators must return an explicit indicator in the output — not `None`, not `0`, but a value that communicates "this metric was not calculable for this company" (e.g., a `null` with a `reason_code` field, or a sentinel value defined in the scoring schema)
- The `reason_code` for uncalculable metrics must distinguish between: `ZERO_DENOMINATOR` (denominator is zero), `NULL_DENOMINATOR` (denominator is `None`/missing), and `NULL_NUMERATOR` (numerator is `None`/missing)
- Unit tests must cover: zero denominator, `None` denominator, `None` numerator, both zero, both `None`, and normal calculation cases
- The `safe_div` utility must be documented with its contract: inputs, outputs, edge cases, and the meaning of the default return value

---

## Acceptance Criteria

- [ ] A `safe_div` utility function exists in a shared module and is importable by all scoring components
- [ ] `safe_div` returns the configured default when denominator is `0`, `0.0`, or `None`
- [ ] `safe_div` handles `None` numerator without raising an exception
- [ ] All five confirmed division sites (`scoring.py:166,280,302`, `financial_health.py:93,114`) use `safe_div` instead of raw `/`
- [ ] `growth_momentum.py` division operations are audited and any unsafe divisions are converted to `safe_div`
- [ ] Scoring output for a company with `revenue = 0` includes an explicit indicator that revenue-dependent metrics could not be calculated, not a bare `None`
- [ ] Scoring output for a company with `employees = None` includes an explicit indicator that employee-dependent metrics could not be calculated
- [ ] Unit tests exist for `safe_div` covering: zero denominator, `None` denominator, `None` numerator, normal calculation, and custom default value
- [ ] Unit tests exist for scoring functions that verify correct behavior when revenue or employee count is zero or `None`
- [ ] A code review search for raw `/` operators in scoring files returns only non-financial-metric divisions (e.g., percentage calculations on already-validated values)

---

## Definition of Done

- **Tests Required**: Unit tests for `safe_div` covering all edge cases (zero, `None`, both, normal). Unit tests for each scoring function that exercises zero and `None` denominator paths and asserts the output contains an explicit "not calculable" indicator rather than `None` or `0`. Tests must be in `tests/unit/` and follow existing test naming conventions.
- **Documentation Required**: Docstring on `safe_div` describing its contract. Update to scoring module documentation describing how uncalculable metrics are represented in output. If a `reason_code` field is added to scoring output schema, the schema documentation must be updated.
- **Code Review Gate**: Reviewer verifies zero raw `/` operators remain in scoring files for financial metric calculations. Reviewer verifies `safe_div` is in a shared module, not duplicated. Reviewer verifies uncalculable metrics produce explicit indicators, not bare `None`.

---

## Notes

The choice of where to define `safe_div` matters. It should live in a shared utilities module (`src/solstein/utils/math.py` or equivalent) rather than in any scoring module, to prevent circular imports and to make it available to future scoring components without modification.

The "explicit indicator for uncalculable metrics" requirement needs careful design. The simplest approach is a structured result type for scoring metrics that includes both a `value` field and a `calculable` boolean (or `reason_code` string). A more pragmatic approach is to use a sentinel value (e.g., `float('nan')`) that is explicitly documented and handled in the export layer. The implementation team should decide and document the approach; the requirement is that the distinction exists, not that it uses a specific mechanism.

This story is the narrowest in scope within EPIC-034 — it touches fewer files and has a clearer fix than STORY-129 or STORY-130. However, it should not be implemented before STORY-132 (standards document), because the standards document will define the canonical pattern for "uncalculable metric" representation, and this story must follow that pattern.

Pre-revenue startups are not an edge case. They are a primary use case. Any scoring system that cannot handle `revenue = 0` without crashing is not ready for production use in a PE/VC context.
