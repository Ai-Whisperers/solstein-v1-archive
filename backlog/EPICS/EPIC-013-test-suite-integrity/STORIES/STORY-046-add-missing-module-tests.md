# STORY-046: Add Tests for Untested Core Modules

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-013: Test Suite Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict
> `adapters/registry.py` (adapter discovery and registration), `adapters/instrumented.py` (instrumentation wrapper), and `core/monitoring.py` (health checks — see EPIC-014) have zero test coverage. The adapter registry is the mechanism by which the system knows which data sources are available. It is entirely untested.

## Problem Statement
The adapter registry, instrumentation layer, and monitoring module are untested. Failures in these modules will not be caught by the CI pipeline. The registry in particular is a central coordination point — a bug here affects all data source lookups. An instrumentation failure means metrics are silently lost. A monitoring failure means the health endpoint lies (which it already does — see STORY-047 — but at least that lie should be tested).

## Impact

| Dimension | Effect |
|-----------|--------|
| **Registry** | A bug in adapter registration or lookup breaks all data source access — completely untested |
| **Instrumentation** | Instrumentation failures silently drop metrics — no test verifies the wrapper preserves return values |
| **Monitoring** | Health check behaviour is unverified — changes to monitoring logic have no automated guard |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `tests/unit/test_adapter_registry.py` | Add | Create: tests for adapter registration and lookup |
| `tests/unit/test_instrumented_adapter.py` | Add | Create: tests for instrumentation wrapper behaviour |
| `tests/unit/test_monitoring.py` | Add | Create or expand: tests for health check probes |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: `adapters/registry.py` must have tests covering: adapter registration, adapter lookup by name, handling of unknown adapter names, and registration of duplicate names
- **REQ-2**: `adapters/instrumented.py` must have tests verifying that instrumentation wraps adapter calls and records metrics without altering return values
- **REQ-3**: `core/monitoring.py` health check tests must verify real probe behaviour (post-STORY-047 implementation — write tests against the current interface, update when probes become real)
- **REQ-4**: Coverage on these three modules must reach 80% minimum after the tests are added

## Acceptance Criteria
- [ ] `adapters/registry.py` has ≥80% test coverage
- [ ] `adapters/instrumented.py` has ≥80% test coverage
- [ ] `core/monitoring.py` has ≥80% test coverage
- [ ] All new tests pass in CI

## Definition of Done

**Tests Required:**
- [ ] Coverage report confirms ≥80% on all three modules
- [ ] All new tests pass consistently (no flaky tests)

**Documentation Required:**
- [ ] Test patterns for adapter testing documented in test directory

**Code Review Gate:**
- [ ] Reviewer confirms tests verify real behaviour, not implementation details
- [ ] Reviewer confirms no autouse fixtures are introduced (see STORY-044)

## Notes
The monitoring module tests will need to be updated after STORY-047 replaces the fake health checks with real probes. Write the tests now against the current interface — they will serve as regression tests during the STORY-047 migration. The adapter registry and instrumented adapter tests are independent and can be written immediately.
