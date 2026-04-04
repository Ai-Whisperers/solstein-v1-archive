# STORY-302: Update golden dataset expected ranges to match corrected scoring formula

| Field | Value |
|-------|-------|
| **Epic** | EPIC-075 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-298, STORY-299 |

## Description

Update the golden dataset expected score ranges in test fixtures to reflect the corrected scorer base values and reduced missing-data penalties from STORY-298 and STORY-299.

## Acceptance Criteria

- [ ] All golden dataset expected ranges updated
- [ ] Test suite passes after formula changes (STORY-298/299)
- [ ] No existing tests fail due to scoring formula changes (only ranges need updating)
- [ ] New expected ranges documented in test comments
