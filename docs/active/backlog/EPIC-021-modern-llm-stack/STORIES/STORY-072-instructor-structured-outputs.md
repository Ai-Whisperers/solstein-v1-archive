# STORY-072: Implement Structured LLM Outputs with Instructor

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-021: Modern LLM Stack Migration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | — |
| Dependencies | [STORY-071: Replace Custom LLM Client with Anthropic SDK](STORY-071-anthropic-sdk-migration.md) |

---

## The Audit Verdict

> LLM responses across all agent files in `src/solstein/agents/` are parsed ad-hoc — string splitting, regex extraction, and JSON parsing applied without schema validation. A response that deviates from the expected structure causes a `KeyError` or `AttributeError` discovered three to five function calls later, with no indication that the LLM was the source of the failure.

## Problem Statement

Ad-hoc LLM response parsing is inherently fragile. LLMs do not guarantee output format consistency — not across providers, not across model versions, not even across identical prompts. Without schema enforcement at the call site, malformed responses propagate as poisoned data through the analysis pipeline, corrupting competitive intelligence reports silently or crashing with errors that point at the wrong layer.

The failure mode is particularly insidious: a missing field in an LLM response does not raise an error at the LLM call. It raises a `KeyError` when the scoring algorithm tries to access `result["threat_level"]` — three modules and two async boundaries away from where the malformed data entered the system. The engineer debugging the `KeyError` in scoring has no reason to suspect the LLM response as the root cause.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Malformed LLM responses cause failures far from their origin, making debugging opaque and time-consuming |
| **Data Quality** | Partial or malformed responses may be silently accepted and stored as valid competitive intelligence — clients receive corrupted analysis |
| **Testability** | No schema means no automated contract test for LLM outputs — the only way to verify output structure is to run a full research job and manually inspect results |
| **Provider Portability** | Different LLM providers format responses differently — without schema enforcement, switching providers requires re-discovering and fixing every parsing assumption |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| All agent files in `src/solstein/agents/` | Modify | Replace ad-hoc string/regex/JSON parsing with Instructor-validated calls |
| `src/solstein/api/schemas/` | Add | New Pydantic models for all structured LLM response types |
| `src/solstein/llm/` | Modify | Wire Instructor with the Anthropic SDK client from STORY-071 |
| New `src/solstein/llm/schemas/` | Add | Centralized LLM response schema definitions |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Every LLM call that expects structured output must use Instructor to validate the response against a defined Pydantic schema — the response must conform to the schema or the call must fail
- **REQ-2**: A schema violation (missing required field, wrong type, out-of-range value) must raise at the LLM call site — not downstream in scoring, export, or API response serialization
- **REQ-3**: Instructor must be configured with a retry policy for schema violations — if the LLM produces a malformed response, Instructor retries with the validation error as feedback before raising a terminal failure
- **REQ-4**: All LLM response schemas must be defined in a centralized location (`src/solstein/llm/schemas/` or equivalent) — not inline at individual call sites across agent files
- **REQ-5**: Free-text LLM outputs (narrative summaries, prose descriptions) do not require Instructor validation — only structured data extraction calls (threat assessments, financial signals, competitive positioning scores) must be schema-enforced

## Acceptance Criteria

- [ ] A simulated malformed LLM response raises a validation error at the call site — not a `KeyError` downstream
- [ ] No `KeyError` or `AttributeError` from LLM response parsing exists in any agent file
- [ ] All structured output schemas are Pydantic models in a designated module
- [ ] Instructor retry is configured — a recoverable schema violation triggers a retry with feedback before failing
- [ ] Free-text LLM outputs bypass Instructor and are returned as plain strings

## Definition of Done

**Tests Required:**
- [ ] Unit test: mock malformed response raises schema validation error at call site — not downstream
- [ ] Unit test: valid response passes schema validation and returns a fully typed Pydantic object
- [ ] Unit test: Instructor retries on first schema violation and succeeds on corrected second response
- [ ] Integration test: a full research job produces schema-valid output for all structured extraction calls

**Documentation Required:**
- [ ] Schema catalog: list of all LLM response schemas with field descriptions
- [ ] Agent migration guide: how to convert an ad-hoc parsing call to an Instructor-validated call

**Code Review Gate:**
- [ ] No ad-hoc JSON parsing of LLM responses in any agent file
- [ ] All schemas in centralized location — none inline
- [ ] Instructor retry policy configured with reasonable defaults (max retries, backoff)

## Notes

This story depends on STORY-071 because Instructor wraps the SDK client — it patches `client.messages.create()` to add schema validation. Without the SDK client, there is nothing for Instructor to wrap.

The distinction between structured outputs (REQ-1) and free-text outputs (REQ-5) is important. Not every LLM call needs Instructor. A call that generates a narrative summary paragraph should return a string. A call that extracts `{threat_level: "high", confidence: 0.87, reasoning: "..."}` must return a validated Pydantic object.
