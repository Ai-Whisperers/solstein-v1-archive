# STORY-014: Remove Hardcoded Date Path from Data Loader

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | HIGH |
| Epic | [EPIC-004: Data Integrity & Atomicity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `data/unified_loader.py` lines 226–233 construct a file system path using the hardcoded strings `'2026-02-23'` and `'dutch_market'`. The loader returns empty results silently on any other date and raises no error. The system appears to function while returning no data.

## Problem Statement

The data loader has a hardcoded path to a specific date and market. On any date other than 2026-02-23, or for any market other than `dutch_market`, the loader silently returns empty results. No exception is raised. No warning is logged. The caller receives an empty dataset with no indication that the configuration is wrong. The system appears healthy while delivering zero value. This is a time bomb with a known detonation date — and that date has already passed for most deployments.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | The data loader is functionally broken for all deployments except one specific date and market combination |
| **Observability** | Silent empty-result returns make this failure invisible without explicit debugging — health checks pass, API responds, data is empty |
| **Portability** | The platform cannot be used for any market or date range without modifying source code |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/unified_loader.py` | Modify | Lines 226–233: replace hardcoded date and market strings with configurable parameters |
| `tests/unit/test_unified_loader.py` | Add/Modify | Parametrized tests with multiple dates and markets |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: The date component of the data path must be derived from a parameter or runtime configuration — no string literal in `YYYY-MM-DD` format may appear in the data loading code
- **REQ-2**: The market component must be a configurable parameter with no hardcoded default
- **REQ-3**: If the constructed path does not exist on the file system, the loader must raise an explicit, descriptive error naming the attempted path — not return an empty result
- **REQ-4**: No date string (`YYYY-MM-DD` format) or market name may appear as a literal in the data loading code

## Acceptance Criteria

- [ ] The loader succeeds when called with any valid date and market combination where the corresponding data directory exists
- [ ] The loader raises an explicit error (not a silent empty result) when the constructed path does not exist
- [ ] The error message includes the full attempted file system path for debugging
- [ ] Grep for `2026-02-23` returns zero results in the source code
- [ ] Grep for `dutch_market` returns zero results in the data loading code

## Definition of Done

**Tests Required:**
- [ ] Parametrized test: multiple date values — loader constructs correct path for each
- [ ] Parametrized test: multiple market values — loader constructs correct path for each
- [ ] Test: missing path raises `FileNotFoundError` (or equivalent) with the attempted path in the message
- [ ] Test: empty directory raises a distinct, descriptive error (not a silent empty result)

**Documentation Required:**
- [ ] Configuration reference updated with data path parameters: expected directory structure, date format, market naming convention
- [ ] Error message catalogue updated with the new file-not-found error

**Code Review Gate:**
- [ ] Reviewer confirms no date string literal exists in the data loading module
- [ ] Reviewer confirms no market name string literal exists in the data loading module
- [ ] Reviewer confirms the loader never returns an empty result without raising or logging a warning

## Notes

This story is independent of STORY-012 and STORY-013 and can proceed in parallel. The fix is straightforward — replace hardcoded strings with parameters — but the testing is important. The original code's failure mode (silent empty results) is the kind of defect that recurs if tests do not explicitly assert that missing data raises errors rather than returning empty collections. The tests are as important as the fix.
