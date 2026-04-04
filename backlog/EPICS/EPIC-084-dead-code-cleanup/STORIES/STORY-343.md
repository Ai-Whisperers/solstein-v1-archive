# STORY-343: Delete research/graph/ frozen runtime (per ADR-009 and ADR-010)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-084 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | ⏳ BLOCKED |
| **Dependencies** | Team sign-off required |

## Description

Delete the `research/graph/` frozen runtime per the decision documented in ADR-009 and ADR-010 (PR #234, PR #235). The graph runtime was declared frozen and scheduled for removal. Requires explicit team sign-off before deletion.

## Acceptance Criteria

- [ ] Team sign-off obtained (documented in this story)
- [ ] `research/graph/` deleted
- [ ] No remaining imports of graph runtime
- [ ] All tests that tested graph runtime updated or removed
- [ ] Dead code CI detector confirms clean

## Blocking Note

This story requires explicit team sign-off. Do not delete without confirmation that no external dependencies exist on the graph runtime.
