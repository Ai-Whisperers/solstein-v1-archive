# STORY-329: Validate: at least 3 Phoenix, 10 Salt, 5 Lead in results

| Field | Value |
|-------|-------|
| **Epic** | EPIC-081 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | ⏳ BLOCKED |
| **Dependencies** | STORY-328 |

## Description

Pipeline stage validation step. Execute the stage and verify it produces real (non-empty, non-placeholder) output meeting the specified criteria.

## Acceptance Criteria

- [ ] At least 3 Phoenix-tier companies (score > 7.0)
- [ ] At least 10 Salt-tier companies (score 4.5-7.0)
- [ ] At least 5 Lead-tier companies (score < 4.5)
- [ ] Tier distribution is plausible (not all Phoenix or all Lead)
