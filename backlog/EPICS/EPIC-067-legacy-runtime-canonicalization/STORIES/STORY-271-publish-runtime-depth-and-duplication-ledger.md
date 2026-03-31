# STORY-271: Publish Runtime Depth, Wiring, and Duplication Ledger

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-067 Legacy Runtime Canonicalization |
| **Created** | 2026-03-31 |
| **Risk** | Low |

---

## Problem Statement

The repo still lacks one explicit, source-backed inventory of:

- which runtime surfaces are actually wired,
- which graph and legacy components are placeholders or dead-end entrypoints,
- which adapters, services, DTOs, and compatibility seams are orphaned or only reachable through glue code,
- and how much file/LOC duplication is being tolerated by keeping both systems alive.

Without that ledger, the team keeps arguing from partial context and adding compatibility patches instead of deleting ambiguity.

## Acceptance Criteria

- [ ] A canonical ledger exists for runtime entrypoints, wired/unwired components, and orphan objects.
- [ ] The ledger records before-state file count and LOC for the dual-runtime surface and duplicate adapter families.
- [ ] Every retained non-canonical surface has an owner, justification, and deletion condition.
- [ ] The ledger is referenced by EPIC-067 through EPIC-070 as the evidence baseline for runtime decisions.
- [ ] The ledger distinguishes clearly between production-capable runtime paths, migration-only compatibility seams, placeholder/mock components, and orphan/unwired objects.

## Tasks

- [ ] Inventory all research runtime entrypoints across CLI, API, workers, and review/resume paths.
- [ ] Mark each graph node, stage path, converter, registry, and checkpoint surface as wired, unwired, placeholder, or orphaned.
- [ ] Measure file count and LOC for legacy runtime, graph runtime, and duplicate adapter/provider families.
- [ ] Publish a deletion-budget section: if both systems remain temporarily, what must be removed next and by when.
