# STORY-341: Delete adapters/enrichment/_retired/ directory (8 dead adapter files)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-084 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Delete the `adapters/enrichment/_retired/` directory containing 8 dead adapter files that are no longer registered or callable. These were retired and replaced by current adapters.

## Acceptance Criteria

- [ ] `_retired/` directory deleted
- [ ] No remaining imports of any retired adapter
- [ ] Dead code CI detector confirms clean
- [ ] Test suite unaffected
