# STORY-297: Add funding amount validation with currency conversion

| Field | Value |
|-------|-------|
| **Epic** | EPIC-074 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add funding amount validation: normalize all funding amounts to EUR using live currency rates. Reject obviously wrong values (< EUR 1K or > EUR 100B for a single round).

## Acceptance Criteria

- [ ] All funding amounts in EUR
- [ ] Currency conversion uses rates no older than 24 hours
- [ ] Funding amounts outside EUR 1K-100B rejected as data errors
