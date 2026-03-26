# STORY-248: Decouple Domain Value Objects from Analytics Constants

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-066 Architectural Boundaries and Cycle Elimination |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

`domain/value_objects.py` imports analytics-owned scoring constants, which reverses the expected dependency direction and weakens the domain layer as a stable foundation.

## Acceptance Criteria

- [ ] `domain/value_objects.py` no longer imports from `solstein.analytics.constants`.
- [ ] Score range and threshold ownership is clarified in a lower-layer or shared contract module.
- [ ] Existing score validation and helper semantics remain intact.

## Tasks

- [ ] Decide whether thresholds belong in `domain`, a shared constants module, or injected configuration.
- [ ] Refactor `Score` helpers to use the new ownership model.
- [ ] Add focused regression coverage for `Score.valid_range()`, `is_phoenix()`, and `is_lead()`.
