# EPIC-021: Modern LLM Stack Migration

| Field | Value |
|-------|-------|
| Priority | **P1** |
| Status | 🔴 Open |
| Stories | 6 |
| Created | 2026-02-28 |
| Supersedes | Partially supersedes STORY-048, STORY-055, STORY-056 in existing epics |
| Depends On | [EPIC-002](../EPIC-002-configuration-integrity/README.md) |

## Context

`llm/enhanced_client.py` is 661 lines of custom HTTP client code wrapping LLM provider APIs. It manages provider selection, retry logic, and response parsing — all implemented from scratch, all requiring ongoing maintenance, all accumulating bugs.

In the same file, lines 591–661 define a `UsageTracker` class that is never called. LLM costs are invisible. Prompt templates are inline strings scattered across agent files. LLM output is parsed ad-hoc with no schema enforcement — a malformed response causes a failure three steps later when the missing field is accessed.

The industry has solved all of these problems:

- **Anthropic SDK**: official, maintained, streaming-native client for Claude models
- **Instructor**: wraps any LLM client and validates every response against a Pydantic schema before it reaches your code — a malformed response raises a `ValidationError` at the call site, not a `KeyError` three layers deep
- **Langfuse**: open-source, self-hostable LLM observability. Replaces the dead UsageTracker, centralizes prompts as versioned entities, and provides an evaluation harness

This epic deletes 661 lines of custom client code and replaces them with three well-maintained libraries. The existing STORY-048 (wire UsageTracker), STORY-055 (centralize prompts), and STORY-056 (LLM eval harness) are superseded by this epic.

## Scope

| Story | Title | Supersedes | Severity |
|-------|-------|-----------|----------|
| [STORY-071](STORIES/STORY-071-anthropic-sdk-migration.md) | Replace Custom LLM Client with Anthropic SDK | — | HIGH |
| [STORY-072](STORIES/STORY-072-instructor-structured-outputs.md) | Implement Structured LLM Outputs with Instructor | — | HIGH |
| [STORY-073](STORIES/STORY-073-langfuse-integration.md) | Integrate Langfuse for Cost Tracking and Prompt Management | STORY-048, STORY-055 | HIGH |
| [STORY-074](STORIES/STORY-074-langfuse-evaluation.md) | Migrate LLM Evaluation to Langfuse | STORY-056 | MEDIUM |
| [STORY-075](STORIES/STORY-075-multi-provider-fallback.md) | Implement Provider Fallback and Circuit Breaking via SDK | — | MEDIUM |
| [STORY-252](STORIES/STORY-252-tighten-structured-llm-contracts.md) | Tighten Structured LLM Contracts and Reject Empty Extraction Successes | — | HIGH |

## Definition of Done

- [ ] `llm/enhanced_client.py` is replaced by Anthropic SDK + Instructor wrappers
- [ ] All LLM calls are traced in Langfuse with token counts and cost estimates
- [ ] All prompt templates are managed in Langfuse — none inline in code
- [ ] LLM response schema violations raise at the call site, not downstream
- [ ] Empty or unknown-only structured payloads do not count as successful extractions
- [ ] Provider fallback is implemented using SDK-native mechanisms

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Develop-Relevant Evidence

- `STORY-072` is already the canonical structured-output/schema-enforcement backlog item for LLM boundaries.
- `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` and `docs/reference/TYPESCRIPT_CRITICAL_NODES_PLAN.md` both point to strict contract boundaries, not ad-hoc parsing, as the intended develop direction.
- Ivan should treat schema-validated LLM outputs as an existing requirement, not a speculative optional refinement.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
