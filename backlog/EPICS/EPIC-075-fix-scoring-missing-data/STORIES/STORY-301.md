# STORY-301: Weight composite score by data completeness

| Field | Value |
|-------|-------|
| **Epic** | EPIC-075 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-300 |

## Description

Modify the composite scoring formula to weight high-completeness companies more heavily in market analysis rankings. Companies with < 30% completeness are clearly labeled as "insufficient data" in reports.

## Acceptance Criteria

- [ ] Composite score formula includes completeness weighting
- [ ] Companies with < 30% completeness marked as "INSUFFICIENT_DATA" tier
- [ ] Weighting does not change score values — only ranking weight in market analysis
- [ ] Test: two companies with equal raw scores but different completeness rank correctly
