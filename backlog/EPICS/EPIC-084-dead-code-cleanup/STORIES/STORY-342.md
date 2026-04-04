# STORY-342: Delete adapters/discovery/_retired/ directory (dead Exa web search adapter)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-084 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Delete `adapters/discovery/_retired/` directory containing the deprecated Exa web search adapter. Exa was removed per EPIC-069 STORY-264 (PR #216). Remaining files are dead code.

## Acceptance Criteria

- [ ] `adapters/discovery/_retired/` deleted
- [ ] No remaining imports of Exa discovery adapter
- [ ] Dead code CI detector confirms clean
