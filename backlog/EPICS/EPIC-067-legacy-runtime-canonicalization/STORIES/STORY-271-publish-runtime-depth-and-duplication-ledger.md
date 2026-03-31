# STORY-271: Publish Runtime Depth, Wiring, and Duplication Ledger

| Field | Value |
|---|---|
| **Status** | 🟡 In Progress |
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
- [ ] The ledger names the exact current evidence anchors in `src/solstein/research/pipeline.py`, `src/solstein/research/pipeline_async.py`, `src/solstein/research/graph/executor.py`, `src/solstein/research/graph/topology.py`, `src/solstein/api/routers/review.py`, `src/solstein/adapters/registry.py`, `src/solstein/data/enrichment_service.py`, `src/solstein/analytics/workflows.py`, `src/solstein/tenant/context.py`, `src/solstein/tenant/services.py`, and `src/solstein/tenant/monitoring.py`.

## Tasks

- [ ] Inventory all research runtime entrypoints across CLI, API, workers, and review/resume paths.
- [ ] Mark each graph node, stage path, converter, registry, and checkpoint surface as wired, unwired, placeholder, or orphaned.
- [ ] Measure file count and LOC for legacy runtime, graph runtime, and duplicate adapter/provider families.
- [ ] Publish a deletion-budget section: if both systems remain temporarily, what must be removed next and by when.
- [ ] Record whether `run_graph_research()` has any production caller beyond human-review resume flows, and if not, mark it explicitly as migration-only.
- [ ] Record every mock or placeholder surface reachable from tenant, workflow, enrichment, and review control-plane paths.

## Initial Evidence Anchors (2026-03-31)

| Area | Current evidence anchor | Ledger consequence |
|---|---|---|
| Canonical runtime depth | `src/solstein/research/pipeline.py` executes the full synchronous stage sequence through discovery, gather, gates, scoring, analysis, export, checkpointing, and quality-gate handling. | Treat the legacy pipeline as the current behavioral oracle until replacement parity is proven. |
| Legacy runtime aliasing | `src/solstein/research/pipeline_async.py` runs the same stage family and still exports `run_market_intelligence = run_market_intelligence_async`. | Inventory async/runtime aliases as transitional surfaces, not canonical entrypoints by default. |
| Graph migration seam | `src/solstein/research/graph/executor.py` documents `run_graph_research()` as a stable public interface shaped like `run_market_intelligence()` and initializes empty downstream state fields such as `resolved_facts`, `confidence_scores`, `company_scores`, and `market_analysis`. | Classify the executor surface as compatibility/migration infrastructure unless proven by callers and non-placeholder downstream behavior. |
| Graph placeholder core | `src/solstein/research/graph/topology.py` still returns empty `conflict_flags`/`resolved_facts` from `_conflict_resolution_node()` and empty `confidence_scores`/`company_scores` from `_scoring_node()`. | Mark graph downstream business stages as placeholder, not parity-complete runtime logic. |
| Confirmed graph wiring | `src/solstein/api/routers/review.py` imports `_get_default_executor()` and calls `resume_after_approval(entry.run_id)` after analyst approval. | Review/resume is a real graph-linked surface and must be distinguished from normal production execution. |
| Missing normal graph entrypoint evidence | Current grep review found no confirmed production caller of `run_graph_research()` outside graph package exports and the human-review resume flow. | Ledger must explicitly record "exported but not confirmed as the normal runtime path" instead of implying production adoption. |
| Registry branching | `src/solstein/adapters/registry.py` still selects between unified and legacy enrichment families via `settings.feature_new_unified_loader`. | Inventory provider/runtime feature-flag branching as active dual-system bloat. |
| Provider placeholders | `src/solstein/data/enrichment_service.py` still carries placeholder SEC, Companies House, and News enrichment methods. | Provider placeholder methods must be mapped as non-canonical or deleted. |
| Workflow/control-plane stubs | `src/solstein/analytics/workflows.py` falls back to a local Temporal stub when Temporal is unavailable. | Control-plane surfaces need the same wired/unwired accounting as research runtimes. |
| Tenant mock behavior | `src/solstein/tenant/context.py`, `src/solstein/tenant/services.py`, and `src/solstein/tenant/monitoring.py` still contain mock tenant lookup, mock enrichment/export data, and mock platform analytics paths. | Mock tenant/control-plane behavior must be inventoried as backlog defects, not hidden implementation detail. |

## QA / Analysis Focus

- Verify each exported runtime function has a concrete caller list, not only a public-interface docstring.
- Treat empty dict/list success payloads in graph scoring, conflict resolution, analytics, and export paths as failure candidates for future golden runs.
- Distinguish "reachable from production API" from "reachable only through manual review or test scaffolding" when classifying orphan risk.
- Require before/after file-count and LOC deltas for any decision to keep both legacy and graph systems temporarily.

## Working Artifact

- Runtime ledger: [`docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md`](../../../../docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md)
