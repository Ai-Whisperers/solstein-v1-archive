# STORY-306: Integrate capability overlap % into composite score as 4th dimension

| Field | Value |
|-------|-------|
| **Epic** | EPIC-076 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-303 |

## Description

Add capability overlap percentage as a 4th scoring dimension in the composite score formula with 10% weight. Current formula: growth (33%) + financial (33%) + AI (33%). New: growth (30%) + financial (30%) + AI (30%) + capability (10%).

## Acceptance Criteria

- [ ] Capability overlap contributes 10% to composite score
- [ ] Score range (0-10) unchanged
- [ ] Companies with 0 capability overlap see < 1.0 point reduction in composite score
- [ ] Test: company with full capability overlap scores ≥ 0.5 higher than identical company with 0 overlap
