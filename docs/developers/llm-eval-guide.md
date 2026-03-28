# LLM Output Evaluation Guide

> STORY-056 — LLM Evaluation Harness

This guide explains how to author evaluation test cases, how to run the
evaluation suite locally, and how to integrate it into CI.

---

## Why an evaluation harness?

Without a systematic evaluation, prompt changes are assessed by running a
request and reading the output. A change that improves one case may silently
break ten others. The evaluation harness makes prompt regressions detectable
before deployment by:

1. Defining explicit test inputs and measurable pass criteria.
2. Scoring each dimension of the output (0.0–1.0) against the criteria.
3. Marking a test case as PASSED only when all scores meet their thresholds.
4. Surfacing per-dimension scores so you know exactly which dimension failed.

---

## Test layers

The evaluation suite has two layers:

| Layer | Marker | Needs API key? | Location |
|-------|--------|----------------|----------|
| Framework unit tests | _(none)_ | No — uses pre-built output | `tests/llm_eval/test_eval_framework.py` |
| Live LLM evaluation | `@pytest.mark.llm_eval` | Yes — calls real Anthropic API | `tests/llm_eval/test_eval_live_llm.py` |

Framework unit tests run in every CI build and take < 1 second. Live tests
run only when `ANTHROPIC_API_KEY` is set; they are skipped silently otherwise.

---

## Running the suite locally

```bash
# Run all evaluation tests (live tests skip if no API key)
pytest tests/llm_eval/ -v

# Run live tests only (requires ANTHROPIC_API_KEY)
pytest -m llm_eval tests/llm_eval/ -v

# Run framework unit tests only (no API key needed)
pytest -m "not llm_eval" tests/llm_eval/ -v

# Use a cheaper model for live runs (default: claude-haiku-4-5-20251001)
SOLSTEIN_EVAL_MODEL=claude-haiku-4-5-20251001 pytest -m llm_eval tests/llm_eval/ -v
```

Set the API key in your shell before running live tests:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

---

## CI integration

Add a dedicated evaluation job to your CI workflow:

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation
on:
  workflow_dispatch:    # Run on demand
  schedule:
    - cron: '0 6 * * 1'   # Weekly on Monday at 06:00 UTC

jobs:
  evaluate:
    runs-on: ubuntu-latest
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      SOLSTEIN_EVAL_MODEL: claude-haiku-4-5-20251001
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --dev
      - run: pytest -m llm_eval tests/llm_eval/ -v --tb=short
```

Keep live evaluation on a separate workflow (not the main PR check) to avoid
incurring API costs on every push. Run it weekly or on demand.

---

## Evaluation dimensions

The `evaluate_research_plan()` evaluator scores four dimensions:

| Dimension | Description | Threshold |
|-----------|-------------|-----------|
| `query_count` | Did the LLM produce the expected number of queries? | 0.6 |
| `priority_coverage` | Are all three priority levels (1, 2, 3) present? | 0.6 |
| `intent_coverage` | Do query intents cover the required research areas? | 0.6 |
| `format_compliance` | Does every query have `query`, `priority`, and `intent`? | 0.6 |

A test case passes when **all** dimension scores are ≥ 0.6.

---

## Authoring a new evaluation test case

### Step 1 — Choose the evaluator

| Prompt task | Evaluator function |
|-------------|-------------------|
| Research plan generation | `evaluate_research_plan()` |
| Company data extraction | `evaluate_company_extraction()` |
| Business analysis / narrative | `evaluate_business_analysis()` |

### Step 2 — Define the input

```python
# The input feeds into the prompt template.
company_name = "Acme Corp"
industry_context = "B2B SaaS security"
```

### Step 3 — Define expected criteria

For a research plan:

```python
expected = {
    "min_queries": 6,          # minimum number of search queries
    "max_queries": 10,         # maximum allowed queries
    "required_intents": [      # intents that must appear
        "website",
        "funding",
        "financials",
    ],
}
```

### Step 4 — Write the test

```python
@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_acme(anthropic_client, eval_model):
    """Case N — Acme Corp: describe what makes this case interesting."""
    from solstein.llm.evaluation import evaluate_research_plan
    from tests.llm_eval.test_eval_live_llm import _call_research_plan, _assert_result

    output = await _call_research_plan(
        anthropic_client, eval_model,
        company_name="Acme Corp",
        industry_context="B2B SaaS security",
    )
    expected = {
        "min_queries": 6,
        "max_queries": 10,
        "required_intents": ["website", "funding", "financials"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="acme_corp")
```

Place the test in `tests/llm_eval/test_eval_live_llm.py` (or a new
task-specific file under `tests/llm_eval/`).

### Step 5 — Add a negative test for your prompt

Always add at least one case that expects failure to confirm the evaluator
catches regressions:

```python
@pytest.mark.llm_eval
def test_my_prompt_degraded_output_fails():
    """Verify the evaluator catches a deliberately broken response."""
    malformed = {"queries": []}   # empty — should fail query_count
    result = evaluate_research_plan(malformed, {"min_queries": 6})
    assert not result.passed
    assert result.scores["query_count"] == 0.0
```

---

## Design principles

**Do not mock LLM calls in live tests.** The point of `@pytest.mark.llm_eval`
tests is to exercise real LLM output. Use mocks only in the framework unit
tests (`test_eval_framework.py`) where you want to test evaluator logic in
isolation.

**Keep evaluation criteria specific and verifiable.** Avoid subjective
criteria like "the response sounds professional". Define measurable checks:
required fields, word count, intent coverage, schema compliance.

**Use the cheapest sufficient model.** The default `SOLSTEIN_EVAL_MODEL` is
`claude-haiku-4-5-20251001` — fast and inexpensive. Upgrade to Sonnet or Opus
only when evaluating tasks that require more reasoning depth.

**Separate evaluation CI from unit CI.** Live tests cost money. Run them on
a schedule or on-demand, not on every PR push.

---

## File map

```
tests/llm_eval/
├── __init__.py                    # Package init (STORY-074)
├── conftest.py                    # Fixtures: anthropic_client, eval_model (STORY-056)
├── datasets.py                    # Pre-built EvalDataset instances (STORY-074)
├── test_eval_framework.py         # Framework unit tests — no API needed (STORY-074)
├── test_eval_research_plan.py     # Dataset-driven research plan tests (STORY-074)
├── test_eval_company_extraction.py  # Dataset-driven extraction tests (STORY-074)
├── test_eval_business_analysis.py   # Dataset-driven analysis tests (STORY-074)
└── test_eval_live_llm.py          # Live LLM tests — needs API key (STORY-056)

src/solstein/llm/
├── evaluation.py                  # Evaluators and EvalDataset / EvalResult (STORY-074)
└── prompts.py                     # Prompt registry loaded by live tests (STORY-055)
```
