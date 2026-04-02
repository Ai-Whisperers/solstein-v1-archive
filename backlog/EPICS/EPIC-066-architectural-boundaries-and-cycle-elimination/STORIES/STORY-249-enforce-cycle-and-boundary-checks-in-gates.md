# STORY-249: Enforce Import-Cycle and Module-Boundary Checks in Maintained Gates

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-066 Architectural Boundaries and Cycle Elimination |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

The repo already has cycle and boundary scanners, but they are not yet part of the maintained blocking gate set. That lets architectural debt re-enter even after it is discovered.

## Acceptance Criteria

- [ ] Cycle and boundary checks have a documented maintained scope.
- [ ] Known false positives are either fixed or explicitly carved out with rationale.
- [ ] The maintained engineering gate runs these checks for the agreed scope.
- [ ] Generated docs reference the enforced structural policies.

## Tasks

- [ ] Review the current scanner outputs and eliminate or document false positives.
- [ ] Add the maintained checks to `Makefile` and the strict engineering workflow.
- [ ] Document the scope and exceptions in the engineering guardrail docs.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- `planning/QUEUE.md` marks this story `BLOCKED` on `STORY-245` and EPIC-031 progress.

### Next Agent Action

- Treat this as the capstone enforcement story after the architectural defects are actually removed.

### Required Working Style

- Promote checks only after reducing real red noise.
- Do not make the gate pass by weakening the scanner instead of improving the architecture.

### Minimum Verification For Future Agents

- Show the maintained gate catches a real structural violation.
- Show the post-fix baseline is quieter because the code improved, not because the rule was softened.
