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

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `BLOCKED` on `STORY-245` and EPIC-031 progress.

### Next Agent Action

- Wait for blockers to move, then re-home threshold ownership without weakening domain invariants.

### Required Working Style

- Keep the domain layer lower than analytics.
- Avoid solving this by duplicating constants in multiple layers.

### Minimum Verification For Future Agents

- Prove the domain layer no longer imports analytics-owned constants.
- Run focused score/value-object regressions after the refactor.
