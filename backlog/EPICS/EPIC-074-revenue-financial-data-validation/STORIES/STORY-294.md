# STORY-294: Normalize revenue units to EUR millions

| Field | Value |
|-------|-------|
| **Epic** | EPIC-074 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Normalize revenue units across all sources: detect strings containing 'thousands', 'millions', 'billions', 'K', 'M', 'B' and convert all values to EUR millions. Apply currency conversion for non-EUR sources.

## Acceptance Criteria

- [ ] All revenue values normalized to EUR millions
- [ ] Unit detection handles: K, M, B, thousand(s), million(s), billion(s)
- [ ] Non-EUR currencies converted using recent exchange rates
