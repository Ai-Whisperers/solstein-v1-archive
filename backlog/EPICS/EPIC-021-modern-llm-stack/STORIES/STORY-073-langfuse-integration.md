# STORY-073: Integrate Langfuse for LLM Cost Tracking and Prompt Management

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-021: Modern LLM Stack Migration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | STORY-048 (wire UsageTracker), STORY-055 (centralize prompts) |
| Dependencies | [STORY-071: Replace Custom LLM Client with Anthropic SDK](STORY-071-anthropic-sdk-migration.md) |

---

## The Audit Verdict

> `src/solstein/llm/enhanced_client.py` lines 591–661 define a `UsageTracker` class that is never called from any code path. LLM prompt templates are inline strings scattered across agent files in `src/solstein/agents/`. There is no prompt versioning, no cost tracking per request, and no way to correlate a specific LLM response with its prompt version. Langfuse provides all three as an open-source, self-hostable platform.

## Problem Statement

The dead `UsageTracker` (STORY-048) and inline prompt templates (STORY-055) were planned features that were never completed. Both stories have been open since the initial audit. Rather than completing both independently — building a custom usage tracker and a custom prompt management system — Langfuse provides both capabilities, plus prompt versioning, A/B testing, and cost analytics, as a unified platform that integrates with the Anthropic SDK in a few lines of initialization.

Building custom infrastructure for problems that have mature open-source solutions is the definition of unnecessary investment. Langfuse is self-hostable (no vendor lock-in concern), open-source (MIT license), and has native Python SDK support.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Operations** | Zero cost visibility into per-provider, per-job, per-tenant LLM spend — resolved by Langfuse cost tracking with automatic token counting |
| **Maintainability** | Prompt changes are buried in code commits, not versioned as first-class entities — resolved by Langfuse prompt management with version history and rollback |
| **Debugging** | No way to correlate a specific LLM failure with the prompt version, model, and token usage that produced it — resolved by Langfuse traces |
| **Business** | Cannot answer "how much did LLM calls cost for tenant X last month?" — a question PE/VC clients will ask |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/enhanced_client.py` | Modify | Add Langfuse SDK initialization and tracing decorator to LLM call sites |
| All agent files in `src/solstein/agents/` | Modify | Remove inline prompt strings; replace with Langfuse prompt retrieval calls |
| `src/solstein/config.py` | Modify | Add `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` configuration |
| New `src/solstein/llm/prompts.py` | Add | Langfuse prompt retrieval utility functions |
| New `src/solstein/llm/tracing.py` | Add | Langfuse tracing initialization and decorator utilities |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The Langfuse SDK must be initialized at application startup and wrap all LLM calls — every call must produce a Langfuse trace with token counts, model identifier, provider name, and cost estimate
- **REQ-2**: Traces must include the correlation ID from STORY-049 (request tracing) and the `tenant_id` from EPIC-019 (multi-tenancy) — enabling cost attribution per request and per tenant
- **REQ-3**: All prompt templates currently inline in agent files must be migrated to Langfuse as named, versioned prompts — prompts are data, not code
- **REQ-4**: Prompt retrieval must use the Langfuse SDK's prompt management API — agent files must not contain prompt string literals for any LLM call
- **REQ-5**: If Langfuse is unavailable (network failure, service down), LLM calls must continue unimpeded — Langfuse is observability infrastructure, not in the critical request path. Langfuse failures must be logged at warning level but must not raise exceptions that fail client requests
- **REQ-6**: STORY-048 (wire UsageTracker) and STORY-055 (centralize prompts) must be marked as superseded in their respective epic trackers once this story is complete

## Acceptance Criteria

- [ ] Every LLM call appears as a trace in the Langfuse dashboard with token counts and cost estimate
- [ ] No prompt string literals exist in any agent file — all prompts retrieved from Langfuse
- [ ] Langfuse service unavailability does not cause LLM call failures — calls proceed without tracing
- [ ] Traces include `correlation_id` and `tenant_id` metadata
- [ ] `UsageTracker` class is deleted from `enhanced_client.py`
- [ ] STORY-048 and STORY-055 are marked as superseded

## Definition of Done

**Tests Required:**
- [ ] Integration test: make an LLM call, verify trace appears in Langfuse with correct token counts
- [ ] Resilience test: Langfuse unavailable (connection refused) → LLM call still succeeds and returns valid response
- [ ] Prompt test: agent retrieves prompt from Langfuse, not from a local string literal
- [ ] Metadata test: trace includes `correlation_id` and `tenant_id` fields

**Documentation Required:**
- [ ] Langfuse setup guide: how to configure Langfuse for local development and production
- [ ] Prompt migration guide: how to create and version prompts in Langfuse
- [ ] Cost dashboard guide: how to view per-tenant, per-provider cost breakdowns

**Code Review Gate:**
- [ ] No prompt string literals in agent files
- [ ] `UsageTracker` class deleted
- [ ] Langfuse failure handling confirmed — no exceptions propagated to callers
- [ ] Configuration uses environment variables, not hardcoded keys

## Notes

This story supersedes two existing stories that have been open since the initial audit:

- **STORY-048** (wire UsageTracker): The `UsageTracker` in `enhanced_client.py:591-661` was never called. Rather than wiring a custom tracker, Langfuse provides automatic token counting, cost estimation, and per-tenant attribution out of the box.
- **STORY-055** (centralize prompts): Inline prompts scattered across agent files were identified as a maintainability issue. Rather than building a custom prompt registry, Langfuse provides versioned prompt management with rollback, A/B testing, and prompt analytics.

Langfuse is self-hostable — the team can run it on existing infrastructure without sending LLM data to a third-party SaaS. This addresses any data sensitivity concerns from PE/VC clients.

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
