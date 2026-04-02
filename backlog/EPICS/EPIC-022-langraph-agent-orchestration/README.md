# EPIC-022: LangGraph Agent Orchestration

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 4 |
| Created | 2026-02-28 |
| Supersedes | Partially supersedes STORY-017 (stub agents) |
| Depends On | [EPIC-021](../EPIC-021-modern-llm-stack/README.md) (Anthropic SDK must be in place) |

## Context

`agents/coordinator_agent.py` (373 lines) orchestrates 7+ data collection agents with no task deduplication, no checkpointing, and no explicit state machine. If a research job crashes after 8 of 10 agents complete, all 10 run again from scratch on retry. `agents/additional_agents.py` contains 7 agent classes (lines 45–268) that return hardcoded mock data — they have never contacted a real external system.

LangGraph is the right architectural replacement. It provides:

- **Explicit state graph**: agent coordination is a directed graph, not implicit function call sequences
- **Checkpointing**: a crashed graph resumes from the last successful node, not from the beginning
- **Parallel node execution**: fan-out/fan-in for independent data collection agents
- **Human-in-the-loop**: inject review gates for low-confidence research results
- **Native Anthropic SDK integration**: works directly with the SDK from EPIC-021

The structural benefit is not just cleaner code — in LangGraph, each agent is a real node with a real external API integration. The `additional_agents.py` stub problem (STORY-017) becomes structurally impossible: a LangGraph node that returns a hardcoded string cannot be mistaken for a real integration because the graph topology makes data flow explicit and inspectable.

## Scope

| Story | Title | Supersedes | Severity |
|-------|-------|-----------|----------|
| [STORY-076](STORIES/STORY-076-langgraph-architecture.md) | Define LangGraph State and Research Graph Architecture | — | HIGH |
| [STORY-077](STORIES/STORY-077-migrate-coordinator-to-langgraph.md) | Migrate Coordinator Agent to LangGraph State Machine | — | HIGH |
| [STORY-078](STORIES/STORY-078-implement-real-agent-nodes.md) | Implement Real Agent Nodes as LangGraph Graph Nodes | STORY-017 | HIGH |
| [STORY-079](STORIES/STORY-079-checkpointing-human-in-loop.md) | Add Checkpointing and Human-in-the-Loop Interruption | — | MEDIUM |

## Definition of Done

- [ ] Research pipeline is a LangGraph state graph, not an implicit function call sequence
- [ ] All 7 stub agents are replaced with real LangGraph nodes or explicitly removed from the graph
- [ ] Checkpointing is enabled — crashed graphs resume from the last successful node
- [ ] Human-in-the-loop interruption is possible for low-confidence results

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
