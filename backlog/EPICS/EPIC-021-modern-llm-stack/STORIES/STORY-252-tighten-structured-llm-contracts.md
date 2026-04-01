# STORY-252: Tighten Structured LLM Contracts and Reject Empty Extraction Successes

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-021 Modern LLM Stack Migration |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

The current structured LLM layer is typed but still too permissive. In particular, company extraction schemas allow empty or unknown-only payloads to validate successfully, which defeats the point of Instructor-backed schema enforcement and lets meaningless extractions travel as if they were valid structured results.

## Acceptance Criteria

- [ ] Structured extraction success requires a minimum meaningful payload rather than an all-null object.
- [ ] Empty JSON or unknown-only JSON returned from the LLM does not count as a successful extraction.
- [ ] Research-agent fallback behavior distinguishes schema failure from genuine "no extractable data" outcomes.
- [ ] Tests prove failure on empty/underspecified extraction payloads and cover the runtime fallback path.

## Tasks

- [ ] Define explicit minimum-validity rules for `ResearchPlanResponse` and company extraction output.
- [ ] Make the extraction success path reject empty or non-informative payloads.
- [ ] Update agent handling so schema failure is surfaced as fallback, not silent success.
- [ ] Replace trivial schema tests with behavior that exercises actual validation semantics.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story extends STORY-072 because the 2026-03-31 audit found the current contract still too loose to guarantee meaningful structured output.

### Next Agent Action

- Keep free-text generation behavior unchanged.
- Focus on structured extraction paths only.

### Required Working Style

- Prefer explicit validation rules over hidden downstream heuristics.
- Preserve the Instructor-based architecture; harden the contract instead of bypassing it.

### Minimum Verification For Future Agents

- Add tests showing empty or unknown-only extraction payloads fail.
- Show agent fallback behavior after that validation failure.
