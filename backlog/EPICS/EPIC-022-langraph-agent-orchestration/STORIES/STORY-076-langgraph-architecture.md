# STORY-076: Define LangGraph State and Research Graph Architecture

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-022: LangGraph Agent Orchestration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [STORY-071: Replace Custom LLM Client with Anthropic SDK](../../EPIC-021-modern-llm-stack/STORIES/STORY-071-anthropic-sdk-migration.md) |

---

## The Audit Verdict

> The research pipeline in `src/solstein/agents/coordinator_agent.py` (373 lines) orchestrates agent calls via implicit function sequences with no explicit state definition, no checkpointing, and no clear graph topology. There is no document or code artifact that shows which agents run in which order, what data they pass between stages, or which agents can run in parallel. Understanding the pipeline requires reading 373 lines of procedural code and reconstructing the execution flow mentally.

## Problem Statement

An implicit, undocumented agent coordination sequence is undebuggable in production and unextensible by engineers who did not write it. Adding a new data source requires understanding the entire coordination flow before knowing where to insert it. Removing a data source requires verifying it is not implicitly depended upon by a downstream step — which is impossible without reading the full coordinator.

LangGraph makes the graph topology explicit, typed, and inspectable. The research pipeline becomes a directed graph where nodes are named, edges are visible, and the execution order is readable from the graph definition — not inferred from procedural code.

This story defines the architecture only. Execution is STORY-077. Node implementation is STORY-078.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Extensibility** | Adding a new data source agent requires understanding 373 lines of implicit orchestration to find the insertion point |
| **Debugging** | A failure in the research pipeline requires tracing through procedural code to determine which agent failed and what state was corrupted |
| **Parallelism** | Independent data collection agents (GitHub, Companies House, news, SEC) run sequentially because the implicit flow does not model independence — parallel execution requires explicit graph topology |
| **Documentation** | The research pipeline has no architectural diagram because the architecture is implicit — it exists only as code |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| New `src/solstein/research/graph/state.py` | Add | `ResearchState` typed definition containing all inter-node data |
| New `src/solstein/research/graph/topology.py` | Add | LangGraph graph definition with named nodes and edges |
| `src/solstein/research/pipeline.py` | Add | Entry point for graph compilation and execution |
| `docs/architecture/` | Add | Mermaid diagram of the research graph topology |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: A `ResearchState` typed definition must be created that contains all data passed between graph nodes — this includes: company identifiers, raw facts collected by each data agent, conflict resolution state (when agents disagree), confidence scores, and the final enriched research result
- **REQ-2**: The research graph topology must be defined as an explicit directed graph with named nodes and named edges — the execution order of the entire research pipeline must be readable from the graph definition without running it
- **REQ-3**: Independent data collection agents (GitHub data, Companies House filings, news aggregation, SEC filings) must be modeled as parallel nodes that fan out from a single dispatch node and fan in to a conflict resolution node — they must not be modeled as sequential steps
- **REQ-4**: The graph definition file must be the authoritative documentation of the research pipeline — inline comments in the graph file must explain the purpose of each node and each edge transition
- **REQ-5**: The graph must be compilable and inspectable without execution — it must be possible to generate a visual representation of the graph topology (Mermaid diagram or Graphviz output) from the graph definition

## Acceptance Criteria

- [ ] `ResearchState` typed definition exists with all fields needed for inter-node data passing
- [ ] The graph topology is defined with named nodes and named edges — the pipeline is readable
- [ ] Independent data collection agents are modeled as parallel nodes (fan-out/fan-in), not sequential
- [ ] The graph can be compiled without errors
- [ ] A visual representation (Mermaid or Graphviz) can be generated from the graph definition
- [ ] The graph topology diagram is committed to `docs/architecture/`

## Definition of Done

**Tests Required:**
- [ ] Unit test: graph compiles without errors
- [ ] Unit test: graph topology contains all expected nodes and edges
- [ ] Unit test: parallel nodes are correctly modeled (fan-out from dispatch, fan-in to resolution)

**Documentation Required:**
- [ ] Mermaid diagram of the research graph committed to `docs/architecture/research-graph.md`
- [ ] `ResearchState` field documentation — what each field contains and which nodes read/write it

**Code Review Gate:**
- [ ] Graph topology matches the documented architecture diagram
- [ ] `ResearchState` contains all fields needed by downstream stories (STORY-077, STORY-078)
- [ ] No implicit sequencing where parallelism is possible
- [ ] Graph definition file has inline comments explaining each node's purpose

## Notes

This is a design-first story. It produces the architecture that STORY-077 (coordinator migration), STORY-078 (agent node implementation), and STORY-079 (checkpointing) build upon. Getting the state definition and graph topology right here prevents rework in the dependent stories.

The `ResearchState` definition will evolve as STORY-078 implements real agent nodes — but the initial definition must be complete enough that node implementers know what fields to read from and write to without guessing.

The fan-out/fan-in pattern for independent agents is the primary architectural improvement over the current sequential coordinator. It reduces research job latency by the difference between running N agents sequentially vs. running them in parallel with a sync point.
