# Production Path Analysis: LangGraph vs. Adapter-Based Pipeline

**Generated:** 2026-03-23  
**Purpose:** Determine current state of research/enrichment pipeline to decide between Option A (revert OPEN-01, delete dead code) vs Option B (wire LangGraph into production)

---

## Executive Summary

**Two parallel systems exist:**

| Aspect | System A (Production) | System B (LangGraph/Dead Code) |
|--------|------------------------|--------------------------------|
| **Entry Point** | `UnifiedCompanyLoader.enrich_batch()` | `CoordinatorAgent` (never called) |
| **Orchestration** | Adapter-based `SourceRegistry` | LangGraph `StateGraph` |
| **Data Flow** | Connectors → RawDataSource → AggregatedDataRecord | Workflow nodes (never executed) |
| **Status** | ✅ Working, returns REAL API data | ❌ Dead code, never instantiated |

---

## System A — Production Pipeline (WORKING)

### Call Chain
```
API Endpoint (enrichment_batch.py)
  → UnifiedCompanyLoader.enrich_batch()
    → enrich_from_connectors()
      → SourceRegistry.all_enrichment_sources
        → [WebsiteUnifiedAdapter, NewsUnifiedAdapter, FundingUnifiedAdapter, ...]
          → adapter.enrich()  ← REAL API CALLS
      → DefaultFactAggregator.aggregate()
      → extract_signals() → SignalExtractionRecord
    → UnifiedCompany returned with real data
```

### Key Files
- **Entry:** `src/solstein/data/unified/unified.py:UnifiedCompanyLoader`
- **Adapters:** `src/solstein/adapters/` (11 adapters registered)
- **Aggregation:** `src/solstein/research/gather.py:extract_signals()` ← Works correctly
- **API Router:** `src/solstein/api/routers/enrichment_batch.py`

### Evidence of Working
1. `enrichment_batch.py:41` calls `unified_loader.enrich_batch(companies, ...)`
2. `UnifiedCompanyLoader.__init__` creates connectors via `ConnectorFactory`
3. Adapters implement `enrich()` method returning real data
4. `grep "CoordinatorAgent("` shows ZERO instantiation sites

---

## System B — LangGraph Workflow (DEAD CODE)

### Defined But Never Invoked

**File:** `src/solstein/agents/coordinator_agent.py`
- Class `CoordinatorAgent` extends `BaseDataGatheringAgent`
- Has LangGraph `StateGraph` initialization (lines 80+)
- Has `analyze_company()` method that invokes the graph
- **BUT:** No code path calls `CoordinatorAgent()` anywhere

### Workflow Nodes (Never Run)
```
coordinator_agent.py
  → GatherSourcesNode (spawns 5 sub-agents)
  → ProcessRawNode 
  → LogicFusionNode
  → ExtractSignalsNode
```

All defined in `src/solstein/agents/workflow_nodes/`, but none execute.

### Evidence of Dead Code
1. `grep "CoordinatorAgent("` returns ONLY class definition (line 31)
2. No imports in `api/routers/` reference `CoordinatorAgent`
3. No background tasks, cron jobs, or event handlers invoke it
4. `agents/__init__.py` exports it but never creates instance

---

## Comparison Table

| Feature | Adapter Pipeline (A) | LangGraph Agent (B) |
|---------|---------------------|---------------------|
| **Instantiated** | Yes, per-request | No |
| **Data Source** | Real APIs (Exa, GitHub, SEC, etc.) | Would use agents if wired |
| **Signal Extraction** | `research/gather.py:extract_signals()` | Workflow node (dead) |
| **State Management** | Via database | LangGraph checkpointing (unused) |
| **Error Handling** | Per-adapter isolation | Would have graph-level handling |
| **Parallelism** | `asyncio.gather()` per adapter | Would use LangGraph scheduling |

---

## What Ivan's OPEN-01 Fix Actually Did

**Commit:** `18d8d90` — "fix(agents): OPEN-01 extracted signals now returned in AgentTaskResult"

**Changes:**
1. Added `extracted_signals: SignalExtractionRecord | None` to `AgentTaskResult`
2. Modified `coordinator_agent.py` to populate this field

**Problem:**
- `CoordinatorAgent` is NEVER called in production
- Adding field to dead code path fixes NOTHING
- Production signals already extracted correctly in `research/gather.py`

---

## Root Cause Analysis

### Why Does Dead Code Exist?

1. **EPIC-022 (LangGraph Orchestration)** was created to implement agentic research
2. **STORY-076/077/078** define the architecture but were never completed
3. Development started: CoordinatorAgent class, workflow nodes, LangGraph setup
4. **STOPPED** before wiring into production pipeline
5. Production continued using adapter-based `UnifiedCompanyLoader`

### Why Is This Confusing?

1. Both systems use similar terminology ("enrich", "signals", "agents")
2. Both have `SignalExtractionRecord` output
3. No clear architectural boundary between them in docs
4. OPEN-01 assumed LangGraph was the production path (incorrect)

---

## Decision: Option A vs Option B

### Option A: Revert & Delete Dead Code
**Effort:** Low (~1 hour)

| Pros | Cons |
|------|------|
| Removes confusion | Loses potential future LangGraph capability |
| Codebase smaller | EPIC-022 stories become obsolete |
| No risk of regression | Must document as "attempted, not wired" |
| Production already works | - |

**Action:**
1. Revert commit `18d8d90` (OPEN-01 fix)
2. Delete `agents/coordinator_agent.py` (or mark deprecated)
3. Delete `agents/workflow_nodes/` (all dead)
4. Update `agents/__init__.py` to not export CoordinatorAgent
5. Document in EPIC-022 that LangGraph approach was abandoned

### Option B: Wire LangGraph Into Production
**Effort:** High (months)

| Pros | Cons |
|------|------|
| Fulfills original vision (EPIC-022) | Major refactoring required |
| True agentic research capability | Risk of breaking working pipeline |
| Better state management | Must implement all 4 stories |
| Parallel sub-agent orchestration | Significant testing needed |

**Action:**
1. STORY-076: Define `ResearchState` schema
2. STORY-077: Wire `CoordinatorAgent` into API endpoints
3. STORY-078: Replace stub agents with real implementations
4. STORY-079: Implement checkpointing for long-running research
5. Add integration tests

---

## Recommendation

**Go with Option A** (Revert & Delete Dead Code) unless:

1. You have explicit requirement for agentic research with LangGraph
2. You're willing to invest 2-3 months of development
3. The adapter-based pipeline has fundamental limitations that agents would solve

**Rationale:**
- Production pipeline WORKS — returns real data from 11+ API sources
- LangGraph was started but never completed — it's aspirational, not functional
- OPEN-01 fix is incorrect — fixes dead code, not production
- No evidence of adapter pipeline limitations that would require agentic approach

---

## Files to Modify (Option A)

```bash
# Revert OPEN-01 commit
git revert 18d8d90

# Delete dead code
rm src/solstein/agents/coordinator_agent.py
rm -rf src/solstein/agents/workflow_nodes/

# Update exports
# Edit src/solstein/agents/__init__.py (remove CoordinatorAgent export)

# Update docs
# docs/active/backlog/EPIC-022-langraph-agent-orchestration/README.md
# Mark as "Abandoned - adapter-based pipeline used instead"
```

---

## Alternative: Keep But Deprecate

If you want to preserve the option of returning to LangGraph later:

1. Revert `18d8d90` (the wrong fix)
2. Keep `coordinator_agent.py` but add deprecation warning
3. Add comment: `# TODO: EPIC-022 - Wire into production when ready`
4. Keep workflow nodes but mark as experimental
5. Document in EPIC-022 that work is paused, not abandoned

This keeps Option B viable with minimal overhead.
