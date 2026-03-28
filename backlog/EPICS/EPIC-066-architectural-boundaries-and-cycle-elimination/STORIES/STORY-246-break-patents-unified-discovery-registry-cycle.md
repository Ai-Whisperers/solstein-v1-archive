# STORY-246: Break `patents_unified` / Discovery / Registry Cycle

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-066 Architectural Boundaries and Cycle Elimination |
| **Created** | 2026-03-26 |
| **Risk** | Medium |

---

## Problem Statement

The recursive structural sweep found a module cycle involving `solstein.adapters.enrichment.patents_unified`, `solstein.research.discovery`, and `solstein.adapters.registry`.

## Acceptance Criteria

- [ ] The dependency cycle is removed without changing patent discovery behavior.
- [ ] `scripts/ci/detect_import_cycles.py` no longer reports the cycle.
- [ ] Discovery and registry contracts remain type-safe without higher-layer back-references.

## Tasks

- [ ] Rework `research.discovery` type ownership so it does not depend on `adapters.registry`.
- [ ] Keep the registry build path lazy and acyclic.
- [ ] Add regression coverage for the chosen import shape if needed.
