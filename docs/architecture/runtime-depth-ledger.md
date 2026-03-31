# Runtime Depth, Wiring, and Duplication Ledger

> STORY-271 | EPIC-067: Legacy Runtime Canonicalization
> Generated: 2026-03-31 | Evidence-backed inventory for consolidation decisions

This ledger records the exact source-backed evidence for every runtime surface,
duplicate implementation pair, and mock placeholder in the Solstein codebase.
Downstream stories (STORY-255 through STORY-258) cite this document when making
freeze, delete, or repair decisions.

---

## 1. Legacy Pipeline Depth

The legacy pipeline is a 10-stage sequential executor with 4-5 levels of call
depth from entrypoint to data source.

### Call Chain

```
CLI (cli.py) or API (api/main.py)
  -> run_market_intelligence()              # research/pipeline.py:42
     -> PipelineContext created
     -> for stage in stages:
        stage.execute(context)              # research/pipeline_stages.py
           -> adapters via registry         # adapters/registry.py
              -> external APIs (HTTP)
```

### Stage Inventory

| # | Stage Class | File | Lines | Purpose |
|---|-------------|------|-------|---------|
| 1 | `DiscoveryStage` | `pipeline_stages.py` | 135-178 | Find companies from target list |
| 2 | `GatherStage` | `pipeline_stages.py` | 179-243 | Enrich via registered adapters |
| 3 | `PerCompanySourceGate` | `pipeline_stages.py` | 244-291 | Filter by per-company source count |
| 4 | `SourceVolumeGate` | `pipeline_stages.py` | 292-324 | Validate total source volume |
| 5 | `ProvenanceValidationStage` | `pipeline_stages.py` | 325-355 | Check data provenance |
| 6 | `ContradictionDetectionStage` | `pipeline_stages.py` | 356-388 | Detect conflicting facts |
| 7 | `EvidenceReadinessStage` | `pipeline_stages.py` | 389-423 | Evaluate evidence sufficiency |
| 8 | `ScoringStage` | `pipeline_stages.py` | 424-448 | Compute company scores |
| 9 | `AnalysisStage` | `pipeline_stages.py` | 449-475 | Market-level aggregation |
| 10 | `ExportStage` | `pipeline_stages.py` | 476-572 | Write artifacts (Excel, JSON) |

**Total LOC**: `pipeline.py` (337) + `pipeline_stages.py` (572) = **909 lines**

### Async Variant

`research/pipeline_async.py` (145 lines) provides an async wrapper around the
same stage sequence. It does not add new stages or change the execution order.

---

## 2. Graph Runtime (LangGraph)

A parallel DAG built on LangGraph with 5 fan-out collection nodes, conflict
resolution fan-in, and an optional human-review interrupt point.

### Topology

```
START -> [dispatch]
           |
           +-- [github_data]        \
           +-- [companies_house]     |  parallel fan-out
           +-- [news_search]         |  (5 nodes)
           +-- [sec_filings]         |
           +-- [web_profile]        /
           |
      [conflict_resolution]          <- fan-in
           |
      [scoring]
           |
      [human_review_router]          <- conditional branch
           |                  \
      [analysis]          [human_review_gate]  <- interrupt()
           |                  |
      [export]           (resume on approve)
           |
          END
```

**Evidence anchors:**

| Component | File | Lines | LOC |
|-----------|------|-------|-----|
| Topology definition | `research/graph/topology.py` | 1-466 | 466 |
| Graph executor | `research/graph/executor.py` | 1-330 | 330 |
| Node implementations | `research/graph/nodes/` | various | ~250 |
| **Total** | | | **~1046** |

### Review-Resume Wiring (Only Active Path)

The graph's `interrupt()` primitive is wired exclusively through the
human-review gate. The conditional router at `topology.py:204-226` sends
execution to `human_review_gate` only when:

1. `human_review_required` is already `True` in state (set by caller), OR
2. Aggregate confidence score falls below threshold (default 0.5)

For normal production runs where all companies exceed the confidence threshold,
the `human_review_gate` node is **never executed** -- graph routes directly from
`scoring` to `analysis`.

**Resume entry point:** `executor.py:241` (`resume_after_approval`) called by
`api/routers/review.py:164` (POST `/review/{review_id}/approve`).

**Conclusion:** The graph interrupt/resume machinery is operational but
exercised only on the review-resume path. There is no confirmed normal
production caller that uses the full graph from `START` to `END` without the
review gate being the motivating use case.

---

## 3. Registry Branching (Feature-Flag Gated)

`adapters/registry.py:94-144` uses `settings.feature_new_unified_loader` to
branch between two complete sets of enrichment adapters.

```python
# registry.py:94
use_unified_enrichment = settings.feature_new_unified_loader

# registry.py:101
if use_unified_enrichment:
    # Register 6 unified adapters
else:
    # Register 6 legacy adapters
```

Feature flag definition: `core/feature_flags.py` (24 lines)

```python
@dataclass(frozen=True)
class FeatureFlags:
    new_classifier: bool
    new_readiness_gate: bool
    new_unified_loader: bool   # <-- controls adapter registration
```

---

## 4. Duplicate Adapter Pairs

Six data sources have parallel legacy and unified implementations. The unified
versions are 3-6x larger, adding error handling, retry logic, and conflict
resolution.

| Data Source | Legacy File (LOC) | Unified File (LOC) | Ratio |
|-------------|-------------------|-------------------|-------|
| Funding | `funding.py` (57) | `funding_unified.py` (266) | 4.7x |
| LinkedIn | `linkedin.py` (53) | `linkedin_unified.py` (160) | 3.0x |
| News | `news.py` (55) | `news_unified.py` (306) | 5.6x |
| Patents | `patents.py` (71) | `patents_unified.py` (202) | 2.8x |
| Web Search | `web_search_news.py` (47) | `web_search_unified.py` (308) | 6.6x |
| Website | `website.py` (53) | `website_unified.py` (281) | 5.3x |
| **Totals** | **336 LOC** | **1523 LOC** | **4.5x avg** |

All 12 files live under `src/solstein/adapters/enrichment/`.

---

## 5. Loader and Orchestrator Duplication

Multiple parallel loader and orchestrator implementations coexist.

### Loaders

| Loader | File | LOC | Purpose |
|--------|------|-----|---------|
| Unified Loader facade | `data/unified_loader.py` | 71 | Re-export wrapper |
| Unified Loader impl | `data/unified/unified.py` | 228 | Conflict resolution, merge |
| Legacy Orchestrator | `data/loader_orchestrator.py` | 295 | Protocol-based loading |
| Legacy Loaders | `data/loaders.py` | 56 | Individual loader functions |
| Competitor Loader | `data/competitor_loader.py` | 104 | Specialized legacy loader |
| **Total** | | **754** | |

### Orchestrators

| Orchestrator | File | LOC | Purpose |
|--------------|------|-----|---------|
| AI Research | `research/ai_research_orchestrator.py` | 538 | LLM planning + web search |
| Data Enrichment | `data/enrichment/orchestrator.py` | 256 | Parallel adapter execution |
| Application Pipeline | `application/enrichment_pipeline.py` | 197 | Parallel adapter calling |
| **Total** | | **991** | |

**Overlap:** `data/enrichment/orchestrator.py` and
`application/enrichment_pipeline.py` both call enrichment adapters in parallel
with similar fan-out patterns.

---

## 6. Tenant and Workflow Mock Surfaces

### Tenant Services (Mock Implementations)

File: `tenant/services.py` (251 lines)

| Mock | Lines | What It Returns |
|------|-------|-----------------|
| `TenantConfigService.get_config()` | 119-128 | Default config dict (not from DB) |
| `TenantConfigService.save_config()` | 140 | No-op (not persisted to DB) |
| `TenantEnrichmentService.enrich_company()` | 214-219 | `{"enriched": True}` stub |
| `TenantExportService.export_companies()` | 249-251 | `b"mock export data"` |

### Temporal Workflow Stubs

File: `analytics/workflows.py` (56 lines)

Lines 7-10: Import guard with fallback stub class when Temporal SDK unavailable.
Lines 29-40: No-op decorators (`@workflow.defn`, `@workflow.run`) when Temporal
is not installed.

**Effect:** The analytics workflow module compiles and is importable but raises
`RuntimeError("Temporal workflow is unavailable")` at invocation time.

### Dashboard Mock Data

File: `api/routers/dashboard.py` line 161: score trends endpoint explicitly
returns mock trend data with comment "stub -- returns mock data until historical
snapshots exist".

---

## 7. Summary Metrics

| Category | Items | Total LOC | Consolidation Action |
|----------|-------|-----------|---------------------|
| Legacy pipeline | 10 stages + orchestrator | 909 | Canonical runtime (STORY-255) |
| Graph runtime | topology + executor + nodes | ~1046 | Freeze (STORY-255) |
| Async pipeline variant | 1 file | 145 | Align or remove (STORY-256) |
| Duplicate adapters | 6 pairs (12 files) | 1859 | Collapse (STORY-265) |
| Duplicate loaders | 5 files | 754 | Collapse (STORY-257) |
| Duplicate orchestrators | 3 files | 991 | Deduplicate (STORY-257) |
| Registry branching | 1 if/else block | 51 | Remove flag (STORY-256) |
| Tenant mocks | 4 surfaces | ~40 | Implement or remove |
| Workflow stubs | 2 surfaces | 56 | Implement or remove |
| Dashboard mocks | 1 endpoint | ~20 | Implement or remove |
| **Grand total duplicate/mock LOC** | | **~5871** | |

---

## 8. Dependency Map for Downstream Stories

```
STORY-271 (this ledger)
    |
    +-> STORY-255: Freeze graph, declare legacy canonical
    |       |
    |       +-> STORY-256: Delete runtime aliases and feature-flag branching
    |               |
    |               +-> STORY-257: Repair legacy entrypoints (one registry, one converter)
    |
    +-> STORY-258: Define salvage-vs-rebuild trigger (also needs EPIC-070)
```

Each downstream story MUST cite specific sections of this ledger when justifying
freeze, delete, or repair actions. No ad-hoc decisions.
