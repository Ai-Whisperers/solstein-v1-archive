# STORY-071: Replace Custom LLM Client with Anthropic SDK

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-021: Modern LLM Stack Migration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [EPIC-002: Configuration Integrity](../../EPIC-002-configuration-integrity/README.md) |

---

## The Audit Verdict

> `src/solstein/llm/enhanced_client.py` is 661 lines of custom HTTP client code implementing provider selection, request formatting, response parsing, retry logic, and streaming — all built from scratch. The Anthropic SDK provides all of this, officially maintained, with streaming, async support, and automatic retry built in. The custom client is maintenance debt with no differentiation value.

## Problem Statement

A 661-line custom LLM client that reimplements what the Anthropic SDK provides is 661 lines of code that needs to be read, understood, debugged, and updated every time a provider changes their API. It is also 661 lines that will inevitably lag behind SDK improvements — streaming protocol updates, new model parameters, rate limit handling refinements, and retry policy improvements all require manual porting from the SDK changelog to the custom client.

The custom client is not a competitive advantage. It is a maintenance liability masquerading as infrastructure.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintenance** | Every Anthropic SDK update requires manual port to the custom client — features the SDK ships for free require engineering effort to replicate |
| **Reliability** | Custom retry and backoff logic has not been hardened against production failure modes that the SDK team has encountered and fixed across thousands of production deployments |
| **Features** | Streaming improvements, structured outputs, and tool use require separate implementation effort vs. being SDK-native capabilities |
| **Onboarding** | New engineers must learn a custom LLM client API instead of the well-documented Anthropic SDK |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/enhanced_client.py` | Replace | 661-line custom client → thin configuration wrapper over Anthropic SDK (target: under 100 lines) |
| `src/solstein/llm/health_checker.py` | Modify | Migrate health checking to use SDK's built-in error types and retry semantics |
| All agent files importing from `enhanced_client` | Modify | Update import paths — public interface must remain stable |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The Anthropic SDK must be the only HTTP client used for Anthropic model calls — no custom HTTP requests to `api.anthropic.com` outside of the SDK
- **REQ-2**: A thin configuration wrapper may exist to set provider selection, model defaults, and timeout configuration — but it must not reimplement request/response logic that the SDK already provides
- **REQ-3**: All other LLM provider calls (Groq, Fireworks, Kimi) must use their respective official SDKs where available, or OpenAI-compatible client libraries where the provider supports the OpenAI API format
- **REQ-4**: `enhanced_client.py` must be reduced to under 100 lines after migration — primarily configuration, provider selection, and any Solstein-specific defaults
- **REQ-5**: The public interface seen by agent callers must remain stable — callers must not require changes beyond import path updates

## Acceptance Criteria

- [ ] `enhanced_client.py` is under 100 lines
- [ ] No direct HTTP calls to `api.anthropic.com` outside of the Anthropic SDK
- [ ] All existing LLM call tests pass against the SDK-backed implementation
- [ ] Streaming works via the SDK's native streaming interface
- [ ] Agent callers require no changes beyond import path updates

## Definition of Done

**Tests Required:**
- [ ] Unit tests: all existing LLM call tests pass with the SDK backend
- [ ] Integration test: a full research job completes end-to-end using the SDK client
- [ ] Smoke test: streaming response received correctly via SDK streaming interface

**Documentation Required:**
- [ ] Updated LLM client architecture section in `docs/architecture/`
- [ ] Migration notes for any agent callers that required import path changes

**Code Review Gate:**
- [ ] `enhanced_client.py` line count verified under 100
- [ ] No raw HTTP calls to LLM provider endpoints outside of official SDKs
- [ ] Public interface compatibility confirmed — no breaking changes for callers

## Notes

This is the foundation story for EPIC-021. STORY-072 (Instructor), STORY-073 (Langfuse), and STORY-075 (multi-provider fallback) all depend on the SDK being in place first. The Anthropic SDK's `client.messages.create()` interface is the call site that Instructor wraps, Langfuse traces, and the fallback chain selects between.

The 100-line target for `enhanced_client.py` is not arbitrary — it reflects the expected scope of a configuration wrapper that selects a provider, sets model defaults, and delegates to the SDK. If the file exceeds 100 lines, it likely reimplements SDK functionality.

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
