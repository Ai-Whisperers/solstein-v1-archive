# EPIC-066: Architectural Boundaries and Cycle Elimination

> **Priority**: P1 - High
> **Status**: 🔴 Not Started
> **Canonical Backlog**: `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/`

---

## Active Focus

The recursive structural sweep added four new architecture issues to the master audit:

- `ISSUE-268` import cycle around `patents_unified` / discovery / registry
- `ISSUE-269` domain depending on analytics constants
- `ISSUE-270` infrastructure depending on research URL canonicalization
- `ISSUE-271` infrastructure depending on research hashing helpers

## Story Queue

- STORY-246 Break `patents_unified` / discovery / registry cycle
- STORY-247 Move canonicalization and hashing helpers to a lower shared boundary
- STORY-248 Decouple domain value objects from analytics constants
- STORY-249 Enforce import-cycle and module-boundary checks in maintained gates
