# STORY-074: Migrate LLM Evaluation to Langfuse Evaluation Framework

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-021: Modern LLM Stack Migration](../README.md) |
| Created | 2026-02-28 |
| Supersedes | STORY-056 (LLM evaluation harness) |
| Dependencies | [STORY-073: Integrate Langfuse for Cost Tracking and Prompt Management](STORY-073-langfuse-integration.md) |

---

## The Audit Verdict

> No LLM output evaluation exists (see STORY-056). Prompt changes are assessed by running a request and reading the output — the "looks good to me" methodology. Langfuse provides a built-in evaluation framework that scores LLM outputs against defined criteria using either rule-based or LLM-as-judge evaluation, eliminating the need to build a custom harness from scratch.

## Problem Statement

STORY-056 proposed building a custom evaluation harness for LLM outputs. That story has remained open because building a custom eval framework is a significant engineering effort — dataset management, evaluation runner, scoring logic, result storage, and comparison tooling.

Langfuse's evaluation framework provides all of this: dataset management (input/expected output pairs), evaluation runs against those datasets, scoring using rule-based or LLM-as-judge evaluators, and historical tracking of scores over time. The marginal effort to use Langfuse's eval framework (once Langfuse is integrated via STORY-073) is a fraction of building one from scratch.

The practical consequence of no evaluation is that prompt changes are untested. An engineer edits a prompt, runs one request, decides the output "looks right," and ships it. There is no regression detection. A prompt change that improves financial analysis but degrades competitive threat extraction goes unnoticed until a client complains.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Quality** | No automated evaluation means prompt changes are assessed by vibes, not metrics — regressions are discovered by clients, not engineers |
| **Velocity** | Engineers avoid changing prompts because there is no safe way to verify the change did not break something — prompt improvement stalls |
| **Confidence** | The team cannot answer "did the last prompt update improve or degrade output quality?" with data |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| New `tests/llm_eval/` | Add | Langfuse evaluation dataset definitions, evaluation runner scripts, and pytest integration |
| `src/solstein/llm/` | Modify | Evaluation runner integration for CI pipeline execution |
| Langfuse project configuration | Configure | Evaluation criteria definitions, scoring rubrics, and dataset uploads |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Langfuse evaluation datasets must be defined for each core LLM task: company research summarization, competitive threat analysis, and financial signal extraction
- **REQ-2**: Each dataset must have at least 5 test cases with defined input (company data, prompt context), expected output characteristics (required fields, value ranges, quality criteria), and evaluation criteria (accuracy, completeness, format compliance)
- **REQ-3**: Evaluation runs must be executable from CI — `pytest tests/llm_eval/` must produce pass/fail results based on minimum score thresholds
- **REQ-4**: Evaluation scores must be tracked in Langfuse over time — prompt changes must produce a visible score delta, enabling before/after comparison
- **REQ-5**: STORY-056 (LLM evaluation harness) must be marked as superseded once evaluation datasets are live in Langfuse and CI integration is functional

## Acceptance Criteria

- [ ] `pytest tests/llm_eval/` runs and produces pass/fail results against defined minimum score thresholds
- [ ] At least 5 evaluation test cases exist per core LLM task (research summarization, threat analysis, signal extraction)
- [ ] A prompt change produces a measurable score delta visible in the Langfuse evaluation dashboard
- [ ] Evaluation results are tracked historically — scores from previous runs are preserved and comparable
- [ ] STORY-056 is marked as superseded

## Definition of Done

**Tests Required:**
- [ ] Evaluation run completes successfully and scores are visible in the Langfuse dashboard
- [ ] A deliberately degraded prompt produces failing evaluation scores — confirming the evaluation actually catches regressions
- [ ] CI pipeline runs `pytest tests/llm_eval/` and fails if scores drop below threshold

**Documentation Required:**
- [ ] Evaluation dataset creation guide: how to add new test cases
- [ ] Evaluation criteria reference: what each score measures and what thresholds mean
- [ ] CI integration guide: how evaluation fits into the deployment pipeline

**Code Review Gate:**
- [ ] Minimum 5 test cases per core LLM task verified
- [ ] Evaluation thresholds are reasonable (not set to always pass)
- [ ] Evaluation tests are deterministic enough for CI (allowance for LLM non-determinism documented)

## Notes

This story supersedes **STORY-056** (LLM evaluation harness). The original story proposed building a custom evaluation framework. Langfuse's built-in evaluation capabilities make this unnecessary.

A key risk with LLM evaluation in CI is non-determinism — the same prompt can produce different quality outputs across runs. The evaluation framework must account for this, likely using score thresholds with tolerance rather than exact match criteria. The evaluation criteria and thresholds should be calibrated during initial dataset creation.

This is a P2 story because it depends on Langfuse being operational (STORY-073) and its value is preventive (catching regressions) rather than corrective (fixing existing failures). It should be prioritized after the P1 foundation stories are complete.
