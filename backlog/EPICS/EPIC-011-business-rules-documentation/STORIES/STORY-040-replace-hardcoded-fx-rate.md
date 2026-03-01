# STORY-040: Replace Hardcoded FX Rate with a Configurable Source

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-011: Business Rules Documentation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> `data/unified_loader.py` line 929 contains `GBP_EUR_RATE = 1.17`. This static rate was accurate on some day in the past. It is applied to every GBP-denominated financial figure to convert it to EUR for cross-market comparison. No date is recorded. No source is cited. The rate has been wrong for an unknown period.

## Problem Statement
A hardcoded FX conversion rate produces incorrect financial comparisons for any company reporting in GBP. The error compounds over time as the rate drifts further from reality, and there is no mechanism to detect or correct it. Every cross-market comparison involving a UK company is silently wrong by an increasing margin.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Financial Accuracy** | GBP-denominated revenue and cost figures are converted at a wrong rate, skewing cross-market comparisons and potentially changing company tier classifications |
| **Audit Trail** | No record of which rate was applied to which figures on which date — financial analysis is not reproducible |
| **Trust** | Clients who notice the stale rate lose confidence in the platform's data accuracy — this is the kind of error that gets noticed in investor presentations |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/unified_loader.py` | Modify | Line 929: remove hardcoded `1.17` literal |
| `src/solstein/config.py` | Modify | Add configurable FX rate settings or FX source configuration |
| `tests/unit/test_currency_conversion.py` | Add | Tests for FX rate loading and application |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: No numeric FX rate may appear as a literal in any source file
- **REQ-2**: The FX rate must be loaded from one of: application configuration (operator-set), or an external rate provider with a configurable refresh interval
- **REQ-3**: The rate source and timestamp must be recorded alongside each converted financial figure for audit purposes
- **REQ-4**: If an external rate source is unavailable, the system must fail with a clear error rather than fall back to a stale hardcoded rate — silent use of wrong data is worse than no data
- **REQ-5**: Currency pairs that require conversion must be explicitly listed in configuration; unlisted pairs must raise an error rather than silently apply a wrong rate

## Acceptance Criteria
- [ ] `grep -r "1.17" src/` returns zero results
- [ ] No numeric FX rate appears as a literal anywhere in source code
- [ ] The FX rate source and timestamp are logged when a conversion is applied
- [ ] A missing FX rate source configuration causes a clear startup or runtime error
- [ ] Converted financial figures carry metadata indicating the rate used and the timestamp of that rate

## Definition of Done

**Tests Required:**
- [ ] Unit test: FX rate loaded from configuration
- [ ] Unit test: missing FX rate configuration raises explicit error
- [ ] Integration test: converted figures carry rate timestamp metadata
- [ ] Unit test: unlisted currency pair raises an error

**Documentation Required:**
- [ ] FX configuration documented in `docs/environment-variables.md` or equivalent

**Code Review Gate:**
- [ ] Reviewer confirms no numeric FX rate literal exists in any source file
- [ ] Reviewer confirms failure mode produces a clear, actionable error message

## Notes
This is a data correctness issue disguised as a configuration issue. The hardcoded rate silently corrupts every GBP-denominated financial figure. The fix is straightforward — the risk of not fixing it grows daily as the real rate diverges further from 1.17. This story has no dependencies and can be started immediately.
