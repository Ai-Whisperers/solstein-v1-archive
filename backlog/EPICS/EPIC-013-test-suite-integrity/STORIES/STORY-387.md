# STORY-387: Fix `pyproject.toml` — remove global `DeprecationWarning` suppression; add integration test separation

| Field | Value |
|-------|-------|
| **Epic** | EPIC-013 — Test Suite Integrity |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

### Issue 1: Global `DeprecationWarning` suppression hides contamination evidence

`pyproject.toml:257–260`:

```toml
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
```

`CompetitorDataLoader` and other production singletons emit `DeprecationWarning` on
initialisation. With all deprecation warnings globally suppressed, these warnings never
surface during test runs or CI. Contamination from deprecated production singletons is
invisible in test output.

The global suppression also hides deprecation warnings from third-party libraries that may
indicate breaking changes in future versions.

### Issue 2: No integration test separation in default `addopts`

`pyproject.toml:246`:

```toml
addopts = "-v --cov=solstein --cov-report=term-missing"
```

No `-m "not integration"` filter. Integration tests run as part of the default `pytest`
invocation with no enforcement of test type separation. This means:
- Unit tests can be contaminated by integration fixtures that set up real/semi-real resources
- The default test run is slower than necessary
- There is no standard way to run "fast tests only" without custom flags

## Fix

### For Issue 1

Remove the global suppression and replace with targeted suppression for known-safe third-party
warnings:

```toml
filterwarnings = [
    # Remove the global ignore::DeprecationWarning line
    # Add targeted suppressions only for known-safe third-party deprecations:
    "ignore::DeprecationWarning:pkg_resources",
    "ignore::DeprecationWarning:distutils",
    # Add others as needed after reviewing what surfaces
]
```

After removing the suppression, run the test suite and triage each warning:
- If it comes from production `src/` code: fix the deprecation
- If it comes from a vendored/third-party dependency: add a targeted suppression with comment

### For Issue 2

Add a default marker filter for unit tests and create a separate integration test invocation:

```toml
# In pyproject.toml
addopts = "-v --cov=solstein --cov-report=term-missing -m 'not integration'"

[tool.pytest.ini_options.markers]
integration = "marks tests as integration tests (deselected in default run)"
```

Add `@pytest.mark.integration` to all tests in `tests/integration/` and `tests/performance/`.

## Acceptance Criteria

- [ ] `pytest` (default) does not suppress `DeprecationWarning` globally
- [ ] All `DeprecationWarning` from `src/` code are either fixed or have a documented suppression
- [ ] `pytest` default run excludes integration tests
- [ ] `pytest -m integration` runs only integration tests
- [ ] `CompetitorDataLoader` deprecation warning surfaces in test output (or is fixed)
- [ ] CI has a separate `pytest -m integration` job for integration test runs

## Files

- `pyproject.toml` — lines 246, 257–260
- `tests/integration/` — add `@pytest.mark.integration` to all tests
- `tests/performance/` — add `@pytest.mark.integration` to all tests
- Any `src/` code emitting `DeprecationWarning` — fix the deprecation

## Notes

After removing global suppression, expect a large volume of warnings on first run. Triage
systematically: src/ warnings must be fixed, not suppressed. Third-party warnings may be
suppressed with targeted rules and a comment explaining why.
