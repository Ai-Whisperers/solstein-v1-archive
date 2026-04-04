# STORY-339: Update golden dataset expected ranges to match current scoring engine

| Field | Value |
|-------|-------|
| **Epic** | EPIC-083 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-302 |

## Description

Update golden dataset expected score ranges in test fixtures after the scoring formula changes from STORY-298, STORY-299, and STORY-302.

## Acceptance Criteria

- [ ] All golden dataset tests pass with updated expected ranges
- [ ] Expected ranges reflect corrected base scores
- [ ] Documentation comment in each golden fixture explains the range rationale
