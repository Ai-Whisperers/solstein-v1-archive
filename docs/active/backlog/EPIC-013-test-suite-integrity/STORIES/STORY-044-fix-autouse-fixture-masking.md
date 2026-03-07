# STORY-044: Fix autouse Fixture Masking in Test Suite

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-013: Test Suite Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> `tests/conftest.py` contains an `autouse=True` fixture named `patch_competitor_data_loader` that replaces the real data loader with a stub across every test in the suite. Tests that believe they are exercising data loading logic are silently testing a stub. The coverage report attributes lines in the real loader as covered when they were never executed.

## Problem Statement
An autouse fixture that patches core infrastructure silently invalidates the coverage metrics for every test that depends on that infrastructure. The test suite provides false confidence that data loading logic has been tested. Engineers looking at the coverage report see green numbers that represent stub execution, not real code execution. The test suite is not testing what it claims to test.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Test Validity** | Approximately 28% of reported coverage is against stub behaviour, not real code — the coverage number is a lie |
| **False Confidence** | Data loading bugs can exist undetected because the real loader was never exercised in any test |
| **Regression Risk** | Changes to the real loader will not be caught by the test suite — the stub absorbs all variations |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `tests/conftest.py` | Modify | Remove or scope the `patch_competitor_data_loader` autouse fixture |
| All tests that previously relied on the patch | Modify | May require explicit mocking or test data fixtures |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: The `patch_competitor_data_loader` autouse fixture must be removed from conftest.py or converted to an explicit opt-in fixture
- **REQ-2**: Tests that require stub data loading must explicitly request the fixture rather than receiving it automatically
- **REQ-3**: Integration tests that exercise real data loading must be identifiable and runnable independently (e.g., via a pytest mark)
- **REQ-4**: After the fix, the coverage report must reflect actual execution of real code paths
- **REQ-5**: Any tests that break after removing the autouse fixture must be fixed with explicit fixtures — not by re-instating the autouse pattern

## Acceptance Criteria
- [ ] `autouse=True` does not appear in conftest.py for data-loading-related fixtures
- [ ] Tests that need stub data loading explicitly request the stub fixture by name
- [ ] At least one integration test exercises the real data loader against test data
- [ ] Coverage report numbers change to reflect real code execution (expect a drop — that drop is the truth)

## Definition of Done

**Tests Required:**
- [ ] Run the full test suite after removing autouse — all tests must pass (with explicit fixtures where needed)
- [ ] Verify coverage report reflects real code execution — document the coverage delta

**Documentation Required:**
- [ ] Test fixture usage patterns documented in test directory README or contributing guide

**Code Review Gate:**
- [ ] Reviewer confirms no autouse fixture silently patches core infrastructure
- [ ] Reviewer confirms the coverage delta is explained (drop expected and documented)

## Notes
This story will likely cause a visible drop in coverage numbers. That drop is the point — it reveals the true coverage. Resist the temptation to add quick tests to restore the old number. The coverage should be rebuilt honestly via STORY-045 and STORY-046 with tests that exercise real code paths.
