# STORY-211: Add shared retry/circuit-breaker connector wrapper

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Size** | M (1-2 days) |
| **Epic** | [EPIC-055](../README.md) |
| **Created** | 2026-03-10 |
| **Risk** | Medium |

## Problem Statement
Retry and fallback behavior differs by connector, creating non-deterministic outcomes.

## Affected Files
- `src/solstein/infrastructure/retry_policy.py`
- `src/solstein/infrastructure/circuit_breaker.py`
- `src/solstein/data/connectors/base.py`

## Acceptance Criteria
- Shared runtime wrapper applies retry/backoff/circuit policies to connector invocations.
- Timeout/429/5xx classes follow deterministic retry and termination behavior.
