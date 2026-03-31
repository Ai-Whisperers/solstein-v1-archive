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

`src/solstein/research/graph/topology.py` still returns empty values from `_conflict_resolution_node()` and `_scoring_node()`, while `src/solstein/research/pipeline.py` is the only path that actually performs the full market-intelligence sequence. `src/solstein/research/graph/executor.py` still presents `run_graph_research()` as a stable public interface compatible with `run_market_intelligence()`, yet the only confirmed graph wiring found in the current review is `src/solstein/api/routers/review.py`, which resumes a paused graph after analyst approval. The backlog and runtime surfaces currently overstate graph readiness.

## Acceptance Criteria

- [ ] The freeze decision cites the runtime-depth ledger from STORY-271, not only prose judgment.
- [ ] The legacy pipeline is documented as the canonical runtime in backlog/program docs.
- [ ] LangGraph execution surfaces are explicitly marked non-production until parity proof exists.
- [ ] No API or CLI path implies that the graph path is production-ready.
- [ ] The freeze decision references the exact runtime evidence files.
- [ ] The freeze decision explicitly distinguishes graph human-review resume wiring from normal production execution wiring.
- [ ] Graph package exports and docstrings stop describing `run_graph_research()` as a ready drop-in production path until STORY-271 proves otherwise.

## Tasks

- [ ] Audit all runtime docs and entrypoints that imply graph readiness.
- [ ] Add explicit non-production wording to graph-related backlog and planning artifacts.
- [ ] Point all immediate remediation work at the legacy runtime path.
- [ ] Record which graph surfaces remain temporarily retained and why.
- [ ] Audit `src/solstein/research/graph/__init__.py`, `src/solstein/research/graph/executor.py`, and any caller docs so "stable interface" language is treated as migration wording, not readiness evidence.
- [ ] Record that `src/solstein/api/routers/review.py` is currently a resume-only graph path, not proof of end-to-end graph runtime adoption.
