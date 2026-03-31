# Runtime Depth And Duplication Ledger

Date: 2026-03-31
Branch baseline: `origin/develop` at `6ac1a6a`
Primary backlog story: `STORY-271`

## Purpose

This ledger documents the current runtime reality of the Solstein project so EPIC-067 through EPIC-070 can make replacement, deletion, and golden-run decisions from source-backed evidence instead of migration intent.

## Method

- Reviewed current `origin/develop` after fetching remote updates.
- Inventoried in-repo callers for `run_market_intelligence`, `run_market_intelligence_async`, `run_graph_research`, `GraphExecutor`, and graph review resume paths.
- Classified each reviewed surface as one of:
  - `production-capable`
  - `migration-only`
  - `placeholder/mock`
  - `disabled`
  - `orphan/unconfirmed`
- Measured file count and LOC for the current legacy orchestration surface, graph orchestration surface, and duplicate provider families.

## Runtime Entrypoint Ledger

| Surface | Current behavior | In-repo caller evidence | Classification | Key evidence |
|---|---|---|---|---|
| `src/solstein/research/pipeline.py::run_market_intelligence()` | Executes the only behaviorally complete staged path for discovery, gather, gates, scoring, analysis, export, checkpoints, and quality gate. | No confirmed non-test in-repo caller was found, but it is the only complete runtime implementation and is heavily referenced by tests and docs. | `production-capable implementation`, `canonical behavioral oracle` | `src/solstein/research/pipeline.py:198`, `tests/unit/test_research_pipeline.py`, `tests/integration/test_full_pipeline.py` |
| `src/solstein/research/pipeline.py::resume_market_intelligence_run()` | Only mutates checkpoint state to `RUNNING` and returns serialized run state; it does not re-enter stage execution. | No confirmed caller found. | `orphan/unconfirmed` | `src/solstein/research/pipeline.py:285` |
| `src/solstein/research/pipeline.py::cancel_market_intelligence_run()` | Marks checkpoint state `CANCELLED` and returns serialized run state; it does not unwind live execution. | No confirmed caller found. | `orphan/unconfirmed` | `src/solstein/research/pipeline.py:313` |
| `src/solstein/research/pipeline_async.py::run_market_intelligence_async()` | Runs the same broad stage family as the synchronous pipeline, but remains a parallel runtime surface rather than the chosen one. | No confirmed non-test/non-doc caller found. | `migration-only` | `src/solstein/research/pipeline_async.py:33` |
| `src/solstein/research/pipeline_async.py::run_market_intelligence` alias | Backward-compatible alias to the async coroutine. Any synchronous caller importing this symbol from `pipeline_async.py` receives a coroutine-returning function. | No confirmed current caller found in `src/`, but the alias is still exported. | `migration-only`, `compatibility seam` | `src/solstein/research/pipeline_async.py:144` |
| `src/solstein/research/graph/executor.py::run_graph_research()` | Exposes a stable public graph interface compatible with `run_market_intelligence()`, but downstream graph business stages are still incomplete. | No confirmed caller found in `src/` beyond graph exports and review-resume plumbing. Tests cover it directly. | `migration-only`, `orphan/unconfirmed normal entrypoint` | `src/solstein/research/graph/executor.py:305`, `src/solstein/research/graph/__init__.py:13` |
| `src/solstein/api/routers/review.py::approve_review_entry()` | Persists analyst approval and then resumes a paused LangGraph execution using `_get_default_executor().resume_after_approval(run_id)`. | Confirmed API router wiring in `app.include_router(review.router, prefix="/api/v1")`. | `wired`, `narrow graph-linked path` | `src/solstein/api/routers/review.py:127`, `src/solstein/api/main.py:224` |
| `src/solstein/api/routers/jobs.py::get_job_status()` | Hard-disabled job status endpoint that always raises `501 NOT_IMPLEMENTED`. | Public API route exists, but behavior is explicitly disabled. | `disabled` | `src/solstein/api/routers/jobs.py:1` |
| `src/solstein/analytics/workflows.py::BatchScoreMarketWorkflow` | Uses a local stub when Temporal is unavailable; activities raise at runtime through the stub path. | No confirmed active caller found in `src/`. | `placeholder/mock`, `orphan/unconfirmed` | `src/solstein/analytics/workflows.py:7` |

## Graph Runtime Depth

### Wired graph pieces

| Surface | Status | Evidence |
|---|---|---|
| Parallel collection topology | Real graph structure exists and compiles. | `src/solstein/research/graph/topology.py:427` |
| Collection nodes | GitHub, Companies House, News, SEC, and web-profile nodes are implemented as real collection nodes. | `src/solstein/research/graph/topology.py:90` |
| Human review interrupt/resume | Interrupt node, review queue store, approval API, and executor resume flow are wired. | `src/solstein/research/graph/topology.py:228`, `src/solstein/api/routers/review.py:159` |
| Graph checkpointer support | Executor can create a default checkpointer and resume approved runs. | `src/solstein/research/graph/executor.py:278` |

### Placeholder or partial graph pieces

| Surface | Current output | Why it is not parity-complete |
|---|---|---|
| Conflict resolution node | Returns empty `conflict_flags` and empty `resolved_facts`. | No actual contradiction merge or reconciliation outcome is produced. |
| Scoring node | Returns empty `confidence_scores` and empty `company_scores`. | No company classification or confidence model is produced. |
| Analysis node | Returns empty lists/dicts plus `ai_adoption_index: 0.0`. | Placeholder market analysis output. |
| Export node | Returns `export_path: ""` and `export_status: "pending"`. | No completed artifact is written or surfaced. |

Evidence:
- `src/solstein/research/graph/topology.py:151`
- `src/solstein/research/graph/topology.py:179`
- `src/solstein/research/graph/topology.py:291`
- `src/solstein/research/graph/topology.py:314`

## Numerical And Functional Edge Cases

| Surface | Edge case | Current behavior | QA consequence |
|---|---|---|---|
| Graph review router | `confidence_scores == {}` | Empty score maps skip the `any(v < threshold)` branch and route directly to `analysis`. | Placeholder scoring can bypass human review completely. Add a failure-mode test that empty scoring output is not treated as success. |
| Graph threshold config | Missing threshold | Falls back to `0.5`. | Threshold fallback is stable, but placeholder scoring means the threshold rarely has meaningful effect. |
| Review resume flow | Approval persisted but graph resume fails | API logs the resume failure but still returns approved review entry. | System can record approval without completing downstream graph work. |
| Legacy async alias | Importing `run_market_intelligence` from `pipeline_async.py` | Alias points at async coroutine function. | Any synchronous caller using the alias incorrectly will get coroutine semantics instead of a result dict. |
| Legacy resume/cancel helpers | Missing checkpoint | Raises runtime error immediately. | These helpers need caller inventory before they can be trusted as recovery surfaces. |

Evidence:
- `src/solstein/research/graph/topology.py:215`
- `src/solstein/research/graph/executor.py:106`
- `src/solstein/api/routers/review.py:155`
- `src/solstein/research/pipeline_async.py:144`
- `src/solstein/research/pipeline.py:285`

## Placeholder, Mock, And Disabled Control-Plane Surfaces

| Surface | LOC | Current state | Evidence |
|---|---:|---|---|
| `src/solstein/data/enrichment_service.py` | 370 | Placeholder SEC, Companies House, and News enrichment methods are still invoked by enrichment executors. | `src/solstein/data/enrichment_service.py:288` |
| `src/solstein/tenant/context.py` | 275 | API key validation hashes the key and returns `None` instead of performing tenant lookup. | `src/solstein/tenant/context.py:143` |
| `src/solstein/tenant/services.py` | 251 | Tenant config returns defaults; tenant enrichment returns mock dict; tenant export returns `b"mock export data"`. | `src/solstein/tenant/services.py:119`, `src/solstein/tenant/services.py:214`, `src/solstein/tenant/services.py:249` |
| `src/solstein/tenant/monitoring.py` | 246 | Platform analytics returns all-zero mock summary. | `src/solstein/tenant/monitoring.py:190` |
| `src/solstein/analytics/workflows.py` | 56 | Temporal workflow import falls back to stub. | `src/solstein/analytics/workflows.py:7` |
| `src/solstein/api/routers/jobs.py` | 36 | Job status endpoint is intentionally disabled and always returns `501`. | `src/solstein/api/routers/jobs.py:18` |

## Duplication And Bloat Measurements

### Runtime surface footprint

Measurement scope:
- Legacy orchestration surface: `pipeline.py`, `pipeline_async.py`, `pipeline_stages.py`, `discovery.py`, `gather.py`, `contracts.py`, `checkpoints.py`
- Graph orchestration surface: full `src/solstein/research/graph/` package

| Surface | Files | LOC |
|---|---:|---:|
| Legacy orchestration surface | 7 | 1,944 |
| Graph orchestration surface | 12 | 2,085 |
| Combined orchestration footprint currently retained | 19 | 4,029 |

### Duplicate enrichment-family footprint

| Family | Files | LOC | Branching/wrapper note |
|---|---:|---:|---|
| `news.py` + `news_unified.py` | 2 | 361 | Registry picks one family via `feature_new_unified_loader`. |
| `funding.py` + `funding_unified.py` | 2 | 323 | Same branching pattern. |
| `website.py` + `website_unified.py` | 2 | 334 | Same branching pattern. |
| `linkedin.py` + `linkedin_unified.py` | 2 | 213 | Same branching pattern. |
| `patents.py` + `patents_unified.py` | 2 | 273 | Same branching pattern. |
| `web_search_news.py` + `web_search_unified.py` | 2 | 355 | Same branching pattern. |
| Total measured duplicate-family footprint | 12 | 1,859 | Excludes always-on singleton enrichers such as Yahoo Finance and Global Market. |

Registry branching evidence:
- `src/solstein/adapters/registry.py:58`
- `src/solstein/adapters/registry.py:94`

## Test Coverage Signal

| Surface | Direct test references |
|---|---:|
| `run_market_intelligence(` in `tests/` | 15 |
| `run_graph_research(` in `tests/` | 9 |
| `compile_research_graph(` or `GraphExecutor(` in `tests/` | 24 |

Interpretation:
- The graph runtime has meaningful architecture-level test coverage, but those tests do not change the fact that downstream graph business stages still return placeholder payloads.
- The legacy runtime still has the more behavior-oriented end-to-end test footprint for actual pipeline execution.

## Retention And Deletion Budget

| Surface | Temporary owner | Why retained right now | Deletion or replacement trigger |
|---|---|---|---|
| Legacy synchronous pipeline | EPIC-067 runtime canonicalization track | Only complete behavioral implementation for staged research. | Remove only after graph or another canonical runtime passes parity and golden-run evidence. |
| Async pipeline alias surface | EPIC-067 runtime canonicalization track | Transitional compatibility surface only. | Delete once canonical runtime entrypoint is declared and callers are migrated. |
| Graph executor public interface | EPIC-067 runtime canonicalization track | Needed for current migration experiments and human-review resume plumbing. | Downgrade or remove "drop-in" semantics unless a normal production caller exists and downstream nodes stop returning placeholders. |
| Graph review/resume path | EPIC-067 and EPIC-070 | Only confirmed narrow graph-linked runtime path. | Keep until canonical runtime choice is finalized; if graph is frozen, remove with the unfinished graph surfaces. |
| Duplicate provider families | EPIC-069 provider rationalization track | Registry still switches between unified and legacy families. | Collapse immediately after STORY-263 defines the canonical provider matrix. |
| Tenant mock/control-plane surfaces | EPIC-070 rebuild gate and EPIC-067 runtime inventory | They remain reachable and distort platform completeness claims. | Either wire real implementations or quarantine/remove from product-facing routes before any production claim. |
| Disabled job-status and Temporal stub surfaces | EPIC-070 rebuild gate | Present in tree but not fit as active product capabilities. | Remove or replace when the actual control-plane runtime is chosen. |

## Immediate Backlog Consequences

1. `STORY-255` should freeze graph production claims, not just graph code growth.
2. `STORY-256` should target `pipeline_async.py` alias removal and graph "stable interface" messaging once the canonical runtime is declared.
3. `STORY-265` should use the 1,859 LOC duplicate-family baseline when measuring provider collapse.
4. `STORY-269` should block empty graph scoring/conflict/analysis/export outputs from being counted as success.
5. Any future "keep both systems" proposal should reference this ledger and explain why 4,029 orchestration LOC plus 1,859 duplicate-provider LOC remains justified.
