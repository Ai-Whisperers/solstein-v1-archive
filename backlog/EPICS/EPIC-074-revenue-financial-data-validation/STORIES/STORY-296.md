# STORY-296: Add employee count validation

| Field | Value |
|-------|-------|
| **Epic** | EPIC-074 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Add employee count validation: reject values outside 1-10M range, cross-reference with revenue/employee ratio heuristics (flag if revenue/employee < EUR 10K or > EUR 5M).

## Acceptance Criteria

- [ ] Employee counts outside 1-10M range rejected
- [ ] Revenue/employee ratio outside EUR 10K-5M range flagged
- [ ] Flagged values retained but marked low confidence
