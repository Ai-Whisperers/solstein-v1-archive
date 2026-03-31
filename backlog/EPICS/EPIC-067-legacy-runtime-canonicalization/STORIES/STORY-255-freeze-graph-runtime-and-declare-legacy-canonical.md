# STORY-255: Freeze Graph Runtime and Declare Legacy Pipeline Canonical

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-067 Legacy Runtime Canonicalization |
| **Created** | 2026-03-31 |
| **Risk** | Low |

---

## Problem Statement

`src/solstein/research/graph/topology.py` still returns empty values from `_conflict_resolution_node()` and `_scoring_node()`, while `src/solstein/research/pipeline.py` is the only path that actually performs the full market-intelligence sequence. The backlog and runtime surfaces currently overstate graph readiness.

## Acceptance Criteria

- [ ] The freeze decision cites the runtime-depth ledger from STORY-271, not only prose judgment.
- [ ] The legacy pipeline is documented as the canonical runtime in backlog/program docs.
- [ ] LangGraph execution surfaces are explicitly marked non-production until parity proof exists.
- [ ] No API or CLI path implies that the graph path is production-ready.
- [ ] The freeze decision references the exact runtime evidence files.

## Tasks

- [ ] Audit all runtime docs and entrypoints that imply graph readiness.
- [ ] Add explicit non-production wording to graph-related backlog and planning artifacts.
- [ ] Point all immediate remediation work at the legacy runtime path.
- [ ] Record which graph surfaces remain temporarily retained and why.
