"""Live LLM evaluation tests — STORY-056.

These tests call the real Anthropic API and evaluate the responses using
the rule-based evaluation framework (built in STORY-074).  They are marked
@pytest.mark.llm_eval and are automatically skipped when ANTHROPIC_API_KEY
is not set in the environment (see conftest.py).

Five test cases cover the core research-analysis prompt (research_planner +
system_research_planner).  Two additional negative-path cases verify that
the evaluator correctly flags malformed or degenerate LLM output.

Running live tests (requires ANTHROPIC_API_KEY):
    pytest -m llm_eval tests/llm_eval/test_eval_live_llm.py -v

Running framework + live:
    pytest tests/llm_eval/ -v

Design notes:
- Each live test invokes the LLM directly via AnthropicQuerier (no mocking).
- Prompts are loaded from the centralized registry (STORY-055).
- Responses are evaluated with evaluate_research_plan() — per-dimension
  scores (0.0–1.0) are emitted in EvalResult.scores.
- A test passes when all dimension scores meet the built-in threshold (0.6).
- Negative tests feed deliberately malformed output to verify failure paths.
"""

from __future__ import annotations

import json
import re
from typing import Any

import pytest

from solstein.llm.evaluation import EvalResult, evaluate_research_plan
from solstein.llm.prompts import get_prompt, get_system_prompt

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_research_plan(raw: str) -> dict[str, Any]:
    """Parse raw LLM text into the dict structure expected by the evaluator.

    Accepts:
    - A JSON object with a ``queries`` list.
    - A JSON array (treated as the queries list directly).
    - Falls back to an empty dict on parse failure.
    """
    cleaned = raw.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[-1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    try:
        parsed: Any = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    if isinstance(parsed, list):
        return {"queries": parsed, "estimated_sources": len(parsed)}
    return parsed if isinstance(parsed, dict) else {}


async def _call_research_plan(
    anthropic_client: Any,
    model: str,
    company_name: str,
    industry_context: str = "",
) -> dict[str, Any]:
    """Call the research_planner prompt and return parsed output dict."""
    from solstein.llm.query.anthropic_querier import AnthropicQuerier

    querier = AnthropicQuerier()
    prompt = get_prompt(
        "research_planner",
        company_name=company_name,
        industry_context=industry_context,
    )
    system = get_system_prompt("system_research_planner")

    raw: str = await querier.query(
        client=anthropic_client,
        model=model,
        prompt=prompt,
        system_prompt=system,
    )
    return _parse_research_plan(raw)


def _assert_result(result: EvalResult, *, case_name: str) -> None:
    """Assert EvalResult passed; print per-dimension scores on failure."""
    assert result.passed, (
        f"[{case_name}] live LLM evaluation failed.\n  scores:  {result.scores}\n  details: {result.details}"
    )


# ---------------------------------------------------------------------------
# Live evaluation — five test cases for the core research-analysis prompt
# ---------------------------------------------------------------------------


@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_fintech(anthropic_client: Any, eval_model: str) -> None:
    """Case 1 — Fintech (Stripe): well-known company, high data availability."""
    output = await _call_research_plan(
        anthropic_client,
        eval_model,
        company_name="Stripe",
        industry_context="fintech payment processing",
    )
    expected = {
        "min_queries": 6,
        "max_queries": 10,
        "required_intents": ["website", "funding", "financials"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="fintech_stripe")


@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_enterprise_saas(anthropic_client: Any, eval_model: str) -> None:
    """Case 2 — Enterprise SaaS (Salesforce): public company, rich public data."""
    output = await _call_research_plan(
        anthropic_client,
        eval_model,
        company_name="Salesforce",
        industry_context="enterprise CRM software",
    )
    expected = {
        "min_queries": 6,
        "max_queries": 10,
        "required_intents": ["website", "financials", "industry"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="enterprise_saas_salesforce")


@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_unknown_startup(anthropic_client: Any, eval_model: str) -> None:
    """Case 3 — Unknown startup: sparse public data forces broader search strategy."""
    output = await _call_research_plan(
        anthropic_client,
        eval_model,
        company_name="NovaTech AI",
        industry_context="B2B AI automation startup",
    )
    expected = {
        "min_queries": 5,
        "max_queries": 10,
        "required_intents": ["website", "funding"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="unknown_startup_novatech")


@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_energy_company(anthropic_client: Any, eval_model: str) -> None:
    """Case 4 — Energy sector (Orsted): domain-specific intent coverage."""
    output = await _call_research_plan(
        anthropic_client,
        eval_model,
        company_name="Orsted",
        industry_context="offshore wind energy infrastructure",
    )
    expected = {
        "min_queries": 5,
        "max_queries": 10,
        "required_intents": ["website", "financials"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="energy_orsted")


@pytest.mark.llm_eval
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_research_plan_biotech(anthropic_client: Any, eval_model: str) -> None:
    """Case 5 — Biotech (Moderna): research-heavy domain, pipeline queries expected."""
    output = await _call_research_plan(
        anthropic_client,
        eval_model,
        company_name="Moderna",
        industry_context="mRNA therapeutics and vaccines biotech",
    )
    expected = {
        "min_queries": 5,
        "max_queries": 10,
        "required_intents": ["website", "financials", "products"],
    }
    result = evaluate_research_plan(output, expected)
    _assert_result(result, case_name="biotech_moderna")


# ---------------------------------------------------------------------------
# Negative-path tests — evaluator must flag malformed / degenerate output
# ---------------------------------------------------------------------------


@pytest.mark.llm_eval
def test_missing_required_field_fails_evaluation() -> None:
    """A response with an empty queries list must produce a failing EvalResult.

    This case does NOT call the LLM — it feeds a deliberately malformed
    payload directly to the evaluator to confirm the failure-detection path
    works correctly before any live API call is made.
    """
    malformed_output: dict[str, Any] = {
        "queries": [],  # empty — violates min_queries constraint
        "estimated_sources": 0,
    }
    expected = {
        "min_queries": 6,
        "required_intents": ["website", "funding", "financials"],
    }
    result = evaluate_research_plan(malformed_output, expected)
    assert not result.passed, (
        f"Expected evaluation to FAIL for an empty queries list, but it passed.\n  scores: {result.scores}"
    )
    assert result.scores.get("query_count", 1.0) == 0.0, (
        f"query_count should be 0.0, got {result.scores.get('query_count')}"
    )


@pytest.mark.llm_eval
def test_missing_intent_field_causes_format_failure() -> None:
    """Queries missing the 'intent' field must fail the format_compliance check.

    Verifies that the evaluator is strict about required fields — a real LLM
    that omits 'intent' from its output would be caught here.  No API call.
    """
    output_missing_intent: dict[str, Any] = {
        "queries": [
            {"query": "Acme Corp website", "priority": 1},  # intent absent
            {"query": "Acme Corp funding", "priority": 1},  # intent absent
            {"query": "Acme Corp revenue", "priority": 1},  # intent absent
            {"query": "Acme Corp headcount", "priority": 2},  # intent absent
            {"query": "Acme Corp news", "priority": 2},  # intent absent
            {"query": "Acme Corp LinkedIn", "priority": 3},  # intent absent
        ],
    }
    expected: dict[str, Any] = {
        "min_queries": 6,
        "required_intents": ["website", "funding"],
    }
    result = evaluate_research_plan(output_missing_intent, expected)
    assert not result.passed, (
        f"Expected evaluation to FAIL for queries missing 'intent', but it passed.\n  scores: {result.scores}"
    )
    assert result.scores.get("format_compliance", 1.0) < 1.0, (
        f"format_compliance should be < 1.0 when intent field is absent, got {result.scores.get('format_compliance')}"
    )
