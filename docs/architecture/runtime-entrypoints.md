# Runtime Entrypoints — Canonical vs. Non-Canonical

> STORY-257 / EPIC-067: Documents which entrypoints participate in the
> canonical legacy pipeline runtime and which are standalone utilities.

## Canonical Runtime

The **canonical runtime** is the sequential research pipeline defined in
`src/solstein/research/pipeline.py`.  All new feature work targets this
path.  The graph runtime (`research/graph/`) is frozen (security patches
only; see `docs/architecture/decisions.md`).

### Shared Components (via `solstein.runtime`)

| Component | Function | Location |
|---|---|---|
| Registry builder | `get_registry(settings)` | `solstein.runtime.canonical` |
| Raw-to-domain converter | `convert_raw(raw, index)` | `solstein.runtime.canonical` |
| Pipeline entry-point | `run_pipeline(seed, market, out)` | `solstein.runtime.canonical` |

Every canonical entrypoint MUST import from `solstein.runtime`, not from
the underlying modules directly.  This guarantees a single point of
change if the canonical registry or converter implementation evolves.

### Canonical Entrypoints

| Surface | Module | Uses Registry | Uses Converter | Notes |
|---|---|---|---|---|
| Research pipeline | `research/pipeline.py` | `get_registry()` | via gather stage | Primary canonical path |
| Async pipeline | `research/pipeline_async.py` | `get_registry()` | via gather stage | Migration surface |
| CLI report commands | `cli.py` | N/A (post-research) | `convert_raw` | Load + score + export |
| Enrichment integration | `data/eneve_enrichment_integration.py` | `get_registry()` | N/A | Enrichment orchestrator |
| Application enrichment | `application/enrichment_pipeline.py` | accepts `SourceRegistry` | N/A | Enrichment pipeline |
| ENEVE script | `scripts/run_eneve_199.py` | N/A (post-research) | `convert_raw` | Score + export script |

### Non-Canonical Paths (Standalone Utilities)

These surfaces are **not** part of the canonical runtime.  They use
their own data loading or orchestration strategies and do not need to
converge on the shared registry/converter.

| Surface | Module | Reason |
|---|---|---|
| AI Research CLI | `cli_ai_research.py` | Standalone AI orchestrator with own LLM pipeline |
| Real-Data CLI | `cli_research.py` | Standalone web-research data loader |
| Market pipeline script | `scripts/run_market_pipeline.py` | Extraction + scoring script, no discovery |
| Research queue script | `scripts/run_research_queue.py` | Standalone queue processor |
| Graph runtime | `research/graph/` | Frozen; security patches only |
| Review router | `api/routers/review.py` | Graph-linked resume path only |

### API Enrichment Surface (Parallel Path)

The API enrichment endpoints (`api/routers/enrichment_*.py`) use
`data/unified_loader.py` which is a **parallel enrichment surface** with
its own connector initialization (SEC EDGAR, Companies House, news
detector).  It does not use the `SourceRegistry`.

This is a deliberate architectural divergence: the unified loader merges
data from connectors that work differently from the registry-based
adapter pattern.  Future consolidation (EPIC-070+) may converge these
two paths, but until then both are valid enrichment surfaces.

## Adding a New Entrypoint

1. Import from `solstein.runtime` (never `adapters.registry` or
   `data.converters` directly).
2. If your path discovers or enriches companies, use `get_registry()`.
3. If your path loads raw JSON into `Company` objects, use `convert_raw()`.
4. If your path runs a full pipeline, use `run_pipeline()`.
5. Add your entrypoint to the table above.
