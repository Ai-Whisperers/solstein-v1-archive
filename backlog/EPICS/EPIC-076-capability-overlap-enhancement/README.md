# EPIC-076: Capability Overlap Enhancement

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P2: Scoring Accuracy |
| **Phase** | P2 — Make Scores Meaningful |
| **Created** | 2026-04-01 |

## Context

The current capability overlap detector uses narrow keyword lists that miss most real-world terminology. "Smart meter" doesn't match "AMI" or "meter data management". "Balancing" doesn't match "imbalance settlement" or "TSO allocation". The result is near-zero overlap scores for genuinely competitive companies. File: `intelligence/capability_overlap.py`.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-303](STORIES/STORY-303.md) | Expand capability keyword lists: add 20+ synonyms per Eneve capability | 🔴 READY | File: intelligence/capability_overlap.py |
| [STORY-304](STORIES/STORY-304.md) | Add LLM-based capability matching: classify company descriptions against Eneve's 8 capabilities using structured extraction | 🔴 READY | Deps: LLM provider configured |
| [STORY-305](STORIES/STORY-305.md) | Add energy-software-specific capability taxonomy with industry standard terms | 🔴 READY | Deps: none |
| [STORY-306](STORIES/STORY-306.md) | Integrate capability overlap % into composite score formula as 4th dimension (10% weight) | 🔴 READY | Deps: [STORY-303](STORIES/STORY-303.md) |

## Success Criteria

- Capability overlap correctly detects at least 3/8 capabilities for known energy-software competitors
- LLM matcher classifies companies with no keyword matches but clear capability descriptions
- Capability overlap contributes 10% to composite score without destabilizing existing score ranges

## Dependencies

- LLM provider configured (STORY-321) for [STORY-304](STORIES/STORY-304.md)
