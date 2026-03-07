# EPIC-021: Modern LLM Stack Migration

| Field | Value |
|-------|-------|
| Priority | **P1** |
| Status | 🔴 Open |
| Stories | 5 |
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

## Definition of Done

- [ ] `llm/enhanced_client.py` is replaced by Anthropic SDK + Instructor wrappers
- [ ] All LLM calls are traced in Langfuse with token counts and cost estimates
- [ ] All prompt templates are managed in Langfuse — none inline in code
- [ ] LLM response schema violations raise at the call site, not downstream
- [ ] Provider fallback is implemented using SDK-native mechanisms
