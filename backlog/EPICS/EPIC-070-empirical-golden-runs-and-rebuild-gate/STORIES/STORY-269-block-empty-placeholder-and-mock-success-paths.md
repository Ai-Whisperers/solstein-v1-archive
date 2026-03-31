# STORY-269: Block Empty, Placeholder, and Mock Success Paths

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-070 Empirical Golden Runs and Rebuild Gate |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

The repo still contains placeholder and mock behavior in active modules, including disabled job surfaces, placeholder enrichment methods, and tenant-service mock returns. Without an explicit gate, these can continue to pass as partial success instead of hard failures.

## Acceptance Criteria

- [ ] Known placeholder/mock paths in the canonical runtime are enumerated.
- [ ] Release verification fails when any placeholder/mock path is exercised.
- [ ] Empty core outputs such as scores, resolved facts, or exports are treated as hard failures.
- [ ] The gate produces actionable failure evidence.

## Tasks

- [ ] Inventory placeholder/mock paths reachable from the canonical runtime.
- [ ] Add detection logic to smoke/golden-run verification.
- [ ] Fail CI or release checks on placeholder success states.
