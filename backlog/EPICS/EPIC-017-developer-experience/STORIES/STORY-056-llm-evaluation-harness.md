# STORY-056: Build an LLM Output Evaluation Harness

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-017: Developer Experience](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-055: Centralize Prompt Templates](STORY-055-centralize-prompt-templates.md) |

---

## The Audit Verdict
> No LLM output evaluation exists. Prompt changes are assessed by running a request and reading the output. There is no systematic test for prompt regression, hallucination detection, or output format compliance. Prompt quality is entirely subjective.

## Problem Statement
Without an evaluation harness, prompt changes cannot be validated before deployment. A prompt that produces worse output than its predecessor will be deployed if the developer does not happen to test the right inputs. There is no definition of "correct" LLM output for the platform's prompts — quality is assessed by whatever the developer thinks looks good at the time of review.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Quality** | Prompt regressions are undetectable — a change that improves one case may break ten others, invisibly |
| **Reliability** | LLM outputs may not conform to expected schema — downstream parsers fail on malformed output |
| **Confidence** | Engineers cannot safely improve prompts without risk of regression — the safest prompt change is no change |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `tests/llm_eval/` | Add | New directory: evaluation test suite |
| `src/solstein/llm/prompts/` | Reference | Prompts to evaluate against (from STORY-055) |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: An evaluation harness must exist that runs a set of defined test cases against each prompt and reports pass/fail
- **REQ-2**: Test cases must define: input data, expected output structure, and evaluation criteria (schema compliance, required field presence, prohibited content)
- **REQ-3**: At least 5 evaluation test cases must be defined for the core research analysis prompt
- **REQ-4**: The harness must run against real LLM output (not mocked) in a designated evaluation environment
- **REQ-5**: Output format violations (e.g., missing required JSON fields) must be reported as test failures

## Acceptance Criteria
- [ ] `pytest tests/llm_eval/` runs and produces pass/fail results
- [ ] At least 5 test cases exist for the core analysis prompt
- [ ] A prompt that produces a response missing a required field causes a test failure
- [ ] Evaluation results include which specific criteria passed and which failed

## Definition of Done

**Tests Required:**
- [ ] The harness itself runs successfully and produces meaningful pass/fail results
- [ ] At least one test case intentionally tests a malformed output scenario (negative test)

**Documentation Required:**
- [ ] Evaluation test case authoring guide: how to define inputs, expected outputs, and evaluation criteria
- [ ] Guide for running the evaluation suite locally and in CI

**Code Review Gate:**
- [ ] Reviewer confirms test cases exercise real LLM output, not mocked responses
- [ ] Reviewer confirms evaluation criteria are specific and verifiable, not subjective

## Notes
This story depends on STORY-055 (centralized prompts) because the evaluation harness needs to load prompts independently to test them. The harness should be designed to run in a dedicated evaluation environment with real LLM API access — it is not a unit test and should not be mocked. Consider marking evaluation tests with a pytest marker (e.g., `@pytest.mark.llm_eval`) so they can be run independently from the fast unit test suite. The initial 5 test cases should cover the most critical prompt: the core research analysis that produces company assessments.

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
