# STORY-079: Add Checkpointing and Human-in-the-Loop Interruption to Research Graph

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-022: LangGraph Agent Orchestration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [STORY-077: Migrate Coordinator to LangGraph](STORY-077-migrate-coordinator-to-langgraph.md), [STORY-078: Implement Real Agent Nodes](STORY-078-implement-real-agent-nodes.md) |

---

## The Audit Verdict

> The current research pipeline has no checkpointing. A failure at step 8 of 10 restarts the entire pipeline from step 1 on retry — wasting the cost and time of 8 successful steps. Additionally, research results for low-confidence companies — where the AI cannot determine a clear tier classification with sufficient confidence — have no review gate. They are classified and delivered to clients with the same presentation as high-confidence results, with no mechanism for an analyst to review before delivery.

## Problem Statement

Two problems, one story, because LangGraph solves both with the same primitive: interruptible, resumable graph execution.

**Checkpointing**: Without checkpointing, every retry is a full restart. In a pipeline with 7+ external API calls and LLM invocations, the cost of a full restart is non-trivial — both in API costs and in latency. LangGraph's checkpointing persists graph state after each node completion, enabling resume-from-failure instead of restart-from-scratch.

**Human-in-the-loop**: Without a review gate, low-confidence research results are delivered to PE/VC clients with the same implicit "this is authoritative" presentation as high-confidence results. An analyst who could have flagged a misclassification never gets the opportunity. LangGraph's interrupt primitive pauses graph execution at a designated node, creates a review entry, and resumes only after human approval.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Cost** | A crash at step 8 of 10 wastes 80% of the research job cost — retry repeats all 10 steps instead of the 2 remaining |
| **Latency** | Full restart on retry doubles (or more) the time to deliver a research report |
| **Quality** | Low-confidence results delivered without review erode client trust — one bad classification can undermine a client's confidence in the entire platform |
| **Compliance** | PE/VC clients may have regulatory requirements for human review of AI-generated investment analysis — no review gate means no compliance mechanism |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/research/graph/` | Modify | Add LangGraph checkpointer configuration to the research graph |
| Database or Redis | Add | Checkpoint persistence store — durable storage for graph state between nodes |
| New `src/solstein/api/routes/review.py` | Add | API endpoint for human review queue and approval/rejection |
| `src/solstein/research/graph/topology.py` | Modify | Add interrupt node for low-confidence results |
| `src/solstein/config.py` | Modify | Add checkpoint store configuration and confidence threshold settings |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: LangGraph checkpointing must be enabled for the research graph — graph state must be persisted after each node completion so that a crashed graph resumes from the last successful node, not from the beginning
- **REQ-2**: The checkpoint store must be durable — it must survive process restart, deployment, and crash recovery. In-memory checkpointing is not acceptable for production. PostgreSQL or Redis are acceptable backends.
- **REQ-3**: A human-in-the-loop interruption point must be defined in the research graph for results where the confidence score falls below a configurable threshold — the graph must pause execution and create a review queue entry
- **REQ-4**: Interrupted graphs must create a review queue entry accessible via API — containing the research result, confidence score, reason for low confidence, and approval/rejection actions
- **REQ-5**: Approved results must continue graph execution from the interruption point — not restart from the beginning. Rejected results must be marked as rejected with the reviewer's rationale and must not be delivered to clients.
- **REQ-6**: The confidence threshold for triggering human review must be configurable via application settings — not hardcoded. The initial threshold must be determined based on analysis of existing research output quality.

## Acceptance Criteria

- [ ] A graph crashed after completing node 8 of 10 resumes from node 9 on retry — not from node 1
- [ ] Checkpoint state survives application process restart
- [ ] A research result with confidence below the configured threshold creates a review queue entry
- [ ] An approved review item resumes graph execution from the interruption point
- [ ] A rejected review item is marked as rejected and is not delivered to clients
- [ ] The confidence threshold is configurable via application settings

## Definition of Done

**Tests Required:**
- [ ] Integration test: simulate crash at node N → restart → graph resumes from node N+1
- [ ] Integration test: low-confidence result → review queue entry created → approval → graph continues from interruption point
- [ ] Integration test: low-confidence result → review queue entry created → rejection → result marked rejected, not delivered
- [ ] Persistence test: checkpoint state written → application restart → checkpoint state readable and graph resumable
- [ ] Configuration test: confidence threshold change reflected in review trigger behavior

**Documentation Required:**
- [ ] Checkpoint architecture: which backend is used, how state is serialized, retention policy
- [ ] Review queue API documentation: endpoints for listing, approving, and rejecting review items
- [ ] Operator guide: how to monitor the review queue and process pending items

**Code Review Gate:**
- [ ] Checkpoint store is durable (not in-memory)
- [ ] Review queue entries contain all information needed for an informed decision (research result, confidence score, reasoning)
- [ ] Approval resumes from interruption point — not full restart (verified by test)
- [ ] Confidence threshold is not hardcoded

## Notes

This story is deliberately the last in EPIC-022 because it requires the graph (STORY-076), the executor (STORY-077), and the real nodes (STORY-078) to be in place before checkpointing and interruption add value. Checkpointing an empty graph is pointless.

The human-in-the-loop capability has strategic value beyond quality control. PE/VC clients may request it as a feature — the ability to inject human analyst review into AI-generated research reports. This positions Solstein as "AI-assisted" rather than "AI-autonomous," which may be the commercially correct positioning for this market.

The initial confidence threshold should be calibrated empirically. A threshold that is too low (rarely triggers review) provides no quality gate. A threshold that is too high (triggers review for most results) creates an operational bottleneck. Start with a threshold that captures approximately 10–15% of results for review and adjust based on analyst feedback.
