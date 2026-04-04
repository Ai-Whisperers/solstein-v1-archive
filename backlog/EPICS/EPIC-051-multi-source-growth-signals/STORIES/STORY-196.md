# STORY-196: Add growth-signal normalization contract and merge policy

| Field | Value |
|-------|-------|
| **Epic** | EPIC-051 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | STORY-194, STORY-195 |

## Description

Define a typed canonical schema for all growth signals and implement the merge policy that combines signals from multiple adapters with source attribution and confidence weighting.

## Acceptance Criteria

- [ ] `GrowthSignalRecord` Pydantic model with all canonical growth fields
- [ ] Merge policy: higher-confidence source wins on conflict
- [ ] Merge result records which source contributed each field
- [ ] Schema validation rejects untyped growth signal payloads
- [ ] Unit tests for merge conflict resolution scenarios
