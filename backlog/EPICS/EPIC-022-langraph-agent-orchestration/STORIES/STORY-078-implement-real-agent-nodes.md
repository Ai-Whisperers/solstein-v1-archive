# STORY-078: Implement Real Agent Nodes as LangGraph Graph Nodes

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-022: LangGraph Agent Orchestration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | STORY-017 (implement or remove stub agents) |
| Dependencies | [STORY-076: Define LangGraph State and Research Graph Architecture](STORY-076-langgraph-architecture.md), [STORY-077: Migrate Coordinator to LangGraph](STORY-077-migrate-coordinator-to-langgraph.md) |

---

## The Audit Verdict

> `src/solstein/agents/additional_agents.py` lines 45–268 define 7 agent classes (`LinkedInAgent`, `SECFilingsAgent`, `PatentsAgent`, `NewsAgent`, `JobPostingsAgent`, `TechTrendsAgent`, `WebsiteAnalysisAgent`) that return hardcoded mock data strings. They have never contacted a real external system. In the current implicit coordinator model, these stubs silently return fake data that is indistinguishable from real data in the research output. In the LangGraph model, each agent becomes a named graph node — and a graph node that returns a hardcoded string is trivially identifiable as unimplemented.

## Problem Statement

STORY-017 identified the 7 stub agents and required a decision: implement each one with a real API integration, or remove it from the pipeline. That decision was deferred. LangGraph makes the decision easier to execute and the outcome easier to verify.

In the LangGraph model, each agent is a graph node with a defined input interface (fields from `ResearchState` it reads) and output interface (fields it writes). A node that is not implemented is simply excluded from the compiled graph — it cannot silently return fake data while appearing to be a real integration. The ambiguity that made stub agents dangerous in the implicit coordinator model is structurally eliminated.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Data Quality** | 7 agents returning hardcoded mock data means up to 7 data sources in every research report contain fabricated information — clients may be making investment decisions based on fake data |
| **Trust** | If a client discovers that "LinkedIn headcount trends" in their report are hardcoded strings, trust in the entire platform is destroyed — not just trust in that one data source |
| **Architecture** | Stub agents in the implicit coordinator are indistinguishable from real agents — the LangGraph model makes the distinction explicit and enforceable |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/agents/additional_agents.py` | Remove | Delete entirely — content is either migrated to real nodes or explicitly removed |
| New `src/solstein/research/graph/nodes/` | Add | One file per implemented agent node (e.g., `github_node.py`, `companies_house_node.py`, `news_node.py`) |
| `src/solstein/research/graph/topology.py` | Modify | Register implemented nodes in the research graph; exclude unimplemented ones |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Each agent that is decided to be implemented must become a LangGraph graph node that contacts a real external API — the node must perform a real HTTP call, parse a real response, and write real data to `ResearchState`
- **REQ-2**: Each agent that is decided not to implement must be explicitly excluded from the compiled graph with a documented rationale — it must not exist as a node that returns mock data. The rationale must be recorded in an Architecture Decision Record (ADR).
- **REQ-3**: Each graph node must have a defined input interface (which fields from `ResearchState` it reads) and output interface (which fields it writes) — this contract must be explicit, not implicit
- **REQ-4**: Graph nodes must be independently testable without running the full research graph — each node must be executable in isolation with mock `ResearchState` input
- **REQ-5**: `agents/additional_agents.py` must be deleted after migration — its content is either migrated to real LangGraph nodes or removed. No partial migration where some stubs remain.

## Acceptance Criteria

- [ ] `agents/additional_agents.py` does not exist in the codebase
- [ ] No graph node in the compiled research graph returns hardcoded data strings
- [ ] Each implemented node has a unit test confirming it calls a real external API (mocked in test, but the mock verifies the correct endpoint and request format)
- [ ] Each excluded node has a documented rationale in an ADR
- [ ] Each node's input/output interface is defined and documented

## Definition of Done

**Tests Required:**
- [ ] Unit test per implemented node: node calls the correct external API with the correct request format (external API mocked)
- [ ] Integration test: implemented nodes return real data in a full research graph run
- [ ] Negative test: the compiled graph does not contain any excluded nodes

**Documentation Required:**
- [ ] ADR documenting the fate of each of the 7 original stub agents: implemented, excluded, or deferred (with rationale for each)
- [ ] Node interface documentation: input fields read from `ResearchState`, output fields written to `ResearchState`

**Code Review Gate:**
- [ ] `additional_agents.py` confirmed deleted
- [ ] No hardcoded data strings in any graph node
- [ ] ADR covers all 7 original stub agents
- [ ] Each implemented node has a corresponding test file

## Notes

This story supersedes **STORY-017** (implement or remove stub agents). The original story required making a decision per agent. This story provides the structural framework (LangGraph nodes) that makes the decision actionable and the outcome verifiable.

The 7 agents requiring disposition are:
1. `LinkedInAgent` — LinkedIn headcount and hiring trends
2. `SECFilingsAgent` — SEC filing analysis
3. `PatentsAgent` — Patent portfolio analysis
4. `NewsAgent` — News aggregation and sentiment
5. `JobPostingsAgent` — Job posting analysis
6. `TechTrendsAgent` — Technology trend tracking
7. `WebsiteAnalysisAgent` — Website traffic and technology stack

For each, the decision is: does a viable, cost-effective external API exist that provides this data? If yes, implement the node. If no, exclude the node with an ADR explaining why. "We haven't gotten to it yet" is not a valid rationale for keeping a stub in production.

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
