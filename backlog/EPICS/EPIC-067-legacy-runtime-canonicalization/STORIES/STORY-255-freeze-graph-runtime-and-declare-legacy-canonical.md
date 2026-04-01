# STORY-255: Freeze Graph Runtime and Declare Legacy Pipeline Canonical

| Field | Value |
|---|---|
| **Status** | 🟢 Done |
| **Priority** | P0 - Ship Blocker |
| **Size** | S (1-2 days) |
| **Epic** | EPIC-067 Legacy Runtime Canonicalization |
| **Created** | 2026-03-31 |
| **Risk** | Low |

---

## Problem Statement

`src/solstein/research/graph/topology.py` still returns empty values from `_conflict_resolution_node()` and `_scoring_node()`, while `src/solstein/research/pipeline.py` is the only path that actually performs the full market-intelligence sequence. `src/solstein/research/graph/executor.py` still presents `run_graph_research()` as a stable public interface compatible with `run_market_intelligence()`, yet the only confirmed graph wiring found in the current review is `src/solstein/api/routers/review.py`, which resumes a paused graph after analyst approval. The backlog and runtime surfaces currently overstate graph readiness.

## Acceptance Criteria

- [x] The freeze decision cites the runtime-depth ledger from STORY-271, not only prose judgment. (ADR-027 in `docs/architecture/decisions.md` line 170)
- [x] The legacy pipeline is documented as the canonical runtime in backlog/program docs. (`research/pipeline.py` docstring lines 1-18, `backlog/README.md` line 44-46)
- [x] LangGraph execution surfaces are explicitly marked non-production until parity proof exists. (`graph/__init__.py`, `graph/topology.py`, `graph/executor.py` all carry FROZEN warnings)
- [x] No API or CLI path implies that the graph path is production-ready. (Zero imports of `run_graph_research` outside graph package)
- [x] The freeze decision references the exact runtime evidence files. (ADR-027 cites `docs/architecture/runtime-depth-ledger.md`)
- [x] The freeze decision explicitly distinguishes graph human-review resume wiring from normal production execution wiring. (ADR-027 lines 173-175, `review.py` comment)
- [x] Graph package exports and docstrings stop describing `run_graph_research()` as a ready drop-in production path until STORY-271 proves otherwise. (Docstring updated with FROZEN warning and stub notice)

## Tasks

- [x] Audit all runtime docs and entrypoints that imply graph readiness.
- [x] Add explicit non-production wording to graph-related backlog and planning artifacts.
- [x] Point all immediate remediation work at the legacy runtime path.
- [x] Record which graph surfaces remain temporarily retained and why. (All retained in `graph/` package; collection nodes are real, conflict/scoring are stubs)
- [x] Audit `src/solstein/research/graph/__init__.py`, `src/solstein/research/graph/executor.py`, and any caller docs so "stable interface" language is treated as migration wording, not readiness evidence.
- [x] Record that `src/solstein/api/routers/review.py` is currently a resume-only graph path, not proof of end-to-end graph runtime adoption. (Comment added at review.py line 165)
