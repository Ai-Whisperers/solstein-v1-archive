# STORY-077: Migrate Coordinator Agent to LangGraph State Machine

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-022: LangGraph Agent Orchestration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [STORY-076: Define LangGraph State and Research Graph Architecture](STORY-076-langgraph-architecture.md) |

---

## The Audit Verdict

> `src/solstein/agents/coordinator_agent.py` (373 lines) orchestrates agent calls with no task deduplication (two agents requesting the same company data trigger two independent API calls), no checkpointing (a crash after 8 of 10 agents complete means all 10 agents re-run on retry), and no explicit state machine. It is an implicit state machine implemented as procedural code — the state transitions are function call sequences, not declared edges.

## Problem Statement

The coordinator is an implicit state machine with no checkpointing. Every crash restarts the entire research pipeline from scratch, regardless of how much work completed before the failure. In a pipeline with 7+ external API calls to data sources of varying reliability, the probability of at least one failure per research job is non-trivial. Each failure costs real money (re-invoking LLM providers and external APIs) and real time (PE/VC clients waiting for intelligence reports).

Task deduplication is absent: if both the SEC agent and the financial analysis agent need the same company filing, two HTTP requests are made. The coordinator has no awareness that the same external resource is being requested twice because it has no shared state — each agent call is a standalone function invocation.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Cost** | A crash at step 8 of 10 wastes the cost of steps 1–8 — all work is lost and repeated on retry |
| **Latency** | No deduplication means redundant API calls to external data sources — each adding latency to the total research job |
| **Reliability** | The probability of at least one failure in a 10-step sequential pipeline with external dependencies is cumulative — the coordinator does not mitigate this |
| **Maintainability** | 373 lines of implicit orchestration is the most complex single file in the agents package — modifications carry high regression risk |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/agents/coordinator_agent.py` | Replace | 373-line implicit orchestration → thin entry point delegating to LangGraph executor |
| `src/solstein/research/pipeline.py` | Modify | Update to execute the LangGraph-compiled research graph |
| New `src/solstein/research/graph/executor.py` | Add | LangGraph graph runner with deduplication and error isolation |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The coordinator's orchestration logic must be replaced by LangGraph graph execution — the graph defined in STORY-076 becomes the execution engine
- **REQ-2**: Task deduplication must be implemented at the graph level — if two nodes request the same external resource (same company, same data source, same time range), only one HTTP call is made and the result is shared
- **REQ-3**: The existing public interface of the coordinator (what callers use to initiate a research job) must remain stable — callers must not require changes beyond import path updates
- **REQ-4**: The `coordinator_agent.py` file must not contain orchestration logic after migration — it may remain as a thin entry point that invokes the graph, or be deleted entirely if the graph is invoked directly
- **REQ-5**: All error handling from the coordinator must be preserved in the graph — a node failure must be isolated (logged, state recorded) and must not crash the entire graph if other nodes can proceed independently

## Acceptance Criteria

- [ ] The research pipeline runs via LangGraph graph execution — not via the coordinator's procedural function calls
- [ ] A single external resource requested by two independent nodes results in only one API call
- [ ] A node failure is logged, its state is recorded, and the graph continues executing independent nodes
- [ ] Existing callers of the coordinator's public interface require no code changes
- [ ] `coordinator_agent.py` contains no orchestration logic (under 50 lines, or deleted)

## Definition of Done

**Tests Required:**
- [ ] Integration test: a full research job completes end-to-end via LangGraph execution
- [ ] Deduplication test: two nodes requesting the same external resource produce exactly one API call
- [ ] Resilience test: one node failure does not abort the full graph — independent nodes continue
- [ ] Interface test: existing callers produce the same research output with the new executor

**Documentation Required:**
- [ ] Migration notes documenting the transition from coordinator to graph executor
- [ ] Updated architecture documentation reflecting the new execution model

**Code Review Gate:**
- [ ] No orchestration logic remains in `coordinator_agent.py`
- [ ] Deduplication is implemented at the graph level, not at individual node level
- [ ] Error isolation confirmed — node failures are contained
- [ ] Public interface compatibility verified

## Notes

This is the core migration story. STORY-076 defines the architecture; this story makes it run. The risk is in preserving behavioral compatibility — the research pipeline must produce the same quality output after migration as before. The recommended approach is to run both paths (old coordinator, new graph) in parallel during testing to verify output equivalence.

The 50-line target for `coordinator_agent.py` (if retained) mirrors the philosophy from STORY-071: infrastructure that delegates to well-maintained libraries should be thin configuration, not thick reimplementation.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
