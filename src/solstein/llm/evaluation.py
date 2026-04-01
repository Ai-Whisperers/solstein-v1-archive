"""LLM output evaluation framework with Langfuse integration.

STORY-074: Rule-based evaluators for core LLM tasks. Scores are computed
locally and optionally pushed to Langfuse for historical tracking.

Usage::

    from solstein.llm.evaluation import (
        EvalDataset, EvalCase, EvalResult,
        evaluate_research_plan, evaluate_company_extraction,
        evaluate_business_analysis, run_evaluation,
    )

    results = run_evaluation(dataset, evaluator_fn)
    assert all(r.passed for r in results)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class EvalCase:
    """A single evaluation test case."""

    name: str
    input_data: dict[str, Any]
    expected: dict[str, Any]
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    """Result of evaluating a single test case."""

    case_name: str
    scores: dict[str, float]  # score_name -> 0.0-1.0
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)
    latency_s: float = 0.0


@dataclass
class EvalDataset:
    """A named collection of evaluation cases for a specific LLM task."""

    name: str
    task_type: str  # "research_plan", "company_extraction", "business_analysis"
    cases: list[EvalCase]
    min_scores: dict[str, float] = field(default_factory=dict)  # threshold per score


# ---------------------------------------------------------------------------
# Score helpers
# ---------------------------------------------------------------------------


def _score_field_presence(output: dict[str, Any], required_fields: list[str]) -> float:
    """Score: fraction of required fields that are non-None in output."""
    if not required_fields:
        return 1.0
    present = sum(1 for f in required_fields if output.get(f) is not None)
    return present / len(required_fields)


def _score_value_accuracy(output: dict[str, Any], expected: dict[str, Any]) -> float:
    """Score: fraction of expected values that match output (case-insensitive for strings)."""
    if not expected:
        return 1.0
    matches = 0
    total = 0
    for key, exp_val in expected.items():
        if exp_val is None:
            continue  # Skip None expectations
        total += 1
        out_val = output.get(key)
        if out_val is None:
            continue
        if isinstance(exp_val, str) and isinstance(out_val, str):
            if exp_val.lower().strip() == out_val.lower().strip():
                matches += 1
        elif isinstance(exp_val, (int, float)) and isinstance(out_val, (int, float)):
            # Allow 10% tolerance for numeric values
            if exp_val == 0:
                if out_val == 0:
                    matches += 1
            elif abs(out_val - exp_val) / abs(exp_val) <= 0.1:
                matches += 1
        elif out_val == exp_val:
            matches += 1
    return matches / total if total > 0 else 1.0


def _score_list_coverage(output_list: list[str] | None, expected_items: list[str]) -> float:
    """Score: fraction of expected items found in output list (case-insensitive)."""
    if not expected_items:
        return 1.0
    if not output_list:
        return 0.0
    output_lower = {item.lower().strip() for item in output_list}
    found = sum(1 for item in expected_items if item.lower().strip() in output_lower)
    return found / len(expected_items)


# ---------------------------------------------------------------------------
# Task-specific evaluators
# ---------------------------------------------------------------------------


def evaluate_research_plan(output: dict[str, Any], expected: dict[str, Any]) -> EvalResult:
    """Evaluate a research plan response.

    Scores:
    - query_count: Were enough queries generated? (0 or 1)
    - priority_coverage: Do queries cover all 3 priority levels?
    - intent_coverage: Do query intents cover expected research areas?
    - format_compliance: Does output match schema structure?
    """
    scores: dict[str, float] = {}
    details: dict[str, Any] = {}

    queries = output.get("queries", [])
    min_queries = expected.get("min_queries", 6)
    max_queries = expected.get("max_queries", 8)

    # Query count
    count = len(queries)
    if min_queries <= count <= max_queries:
        scores["query_count"] = 1.0
    elif count > 0:
        scores["query_count"] = min(count / min_queries, 1.0)
    else:
        scores["query_count"] = 0.0
    details["query_count"] = count

    # Priority coverage
    priorities_found = {q.get("priority") for q in queries if isinstance(q, dict)}
    scores["priority_coverage"] = len(priorities_found & {1, 2, 3}) / 3.0
    details["priorities_found"] = sorted(priorities_found)

    # Intent coverage
    expected_intents = expected.get("required_intents", [])
    if expected_intents and queries:
        actual_intents = {q.get("intent", "").lower() for q in queries if isinstance(q, dict)}
        found = sum(
            1 for intent in expected_intents
            if any(intent.lower() in ai for ai in actual_intents)
        )
        scores["intent_coverage"] = found / len(expected_intents)
    else:
        scores["intent_coverage"] = 1.0 if queries else 0.0

    # Format compliance
    format_ok = all(
        isinstance(q, dict) and "query" in q and "priority" in q and "intent" in q
        for q in queries
    ) if queries else False
    scores["format_compliance"] = 1.0 if format_ok else 0.0

    passed = all(v >= 0.6 for v in scores.values())
    return EvalResult(case_name="", scores=scores, passed=passed, details=details)


def evaluate_company_extraction(output: dict[str, Any], expected: dict[str, Any]) -> EvalResult:
    """Evaluate a company extraction response.

    Scores:
    - field_presence: Were required fields populated?
    - value_accuracy: Do values match expected data?
    - completeness: Overall extraction completeness.
    """
    scores: dict[str, float] = {}

    required_fields = expected.get("required_fields", [
        "company_name", "industry", "description",
    ])
    scores["field_presence"] = _score_field_presence(output, required_fields)

    expected_values = expected.get("expected_values", {})
    scores["value_accuracy"] = _score_value_accuracy(output, expected_values)

    all_fields = [
        "company_name", "website", "description", "industry", "headquarters",
        "founded_year", "employees", "revenue", "funding_raised", "products",
    ]
    scores["completeness"] = _score_field_presence(output, all_fields)

    # Pass/fail determined by dataset-level min_scores in run_evaluation
    passed = scores["field_presence"] >= 0.5 and scores["value_accuracy"] >= 0.5
    return EvalResult(case_name="", scores=scores, passed=passed)


def evaluate_business_analysis(output: dict[str, Any], expected: dict[str, Any]) -> EvalResult:
    """Evaluate a business analysis response.

    Scores:
    - content_length: Is the analysis substantive? (word count check)
    - topic_coverage: Does it cover expected topics?
    - data_grounding: Does it reference specific data points?
    """
    scores: dict[str, float] = {}
    details: dict[str, Any] = {}

    text = output.get("analysis", output.get("text", ""))
    if isinstance(text, str):
        word_count = len(text.split())
    else:
        word_count = 0
    details["word_count"] = word_count

    min_words = expected.get("min_words", 50)
    max_words = expected.get("max_words", 2000)
    if min_words <= word_count <= max_words:
        scores["content_length"] = 1.0
    elif word_count > 0:
        scores["content_length"] = min(word_count / min_words, 1.0)
    else:
        scores["content_length"] = 0.0

    expected_topics = expected.get("required_topics", [])
    if expected_topics and isinstance(text, str):
        text_lower = text.lower()
        found = sum(1 for topic in expected_topics if topic.lower() in text_lower)
        scores["topic_coverage"] = found / len(expected_topics)
    else:
        scores["topic_coverage"] = 1.0 if not expected_topics else 0.0

    data_markers = expected.get("data_markers", [])
    if data_markers and isinstance(text, str):
        text_lower = text.lower()
        found = sum(1 for m in data_markers if m.lower() in text_lower)
        scores["data_grounding"] = found / len(data_markers)
    else:
        scores["data_grounding"] = 1.0 if not data_markers else 0.0

    passed = all(v >= 0.5 for v in scores.values())
    return EvalResult(case_name="", scores=scores, passed=passed, details=details)


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

EvaluatorFn = Callable[[dict[str, Any], dict[str, Any]], EvalResult]

EVALUATORS: dict[str, EvaluatorFn] = {
    "research_plan": evaluate_research_plan,
    "company_extraction": evaluate_company_extraction,
    "business_analysis": evaluate_business_analysis,
}


def run_evaluation(
    dataset: EvalDataset,
    output_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    langfuse_client: Any | None = None,
) -> list[EvalResult]:
    """Run evaluation over a dataset.

    Args:
        dataset: The evaluation dataset with cases and thresholds.
        output_fn: Optional function that generates LLM output from input_data.
                   If None, uses case.input_data as the "output" (for testing evaluators).
        langfuse_client: Optional Langfuse client for score tracking.

    Returns:
        List of EvalResult, one per case.
    """
    evaluator = EVALUATORS.get(dataset.task_type)
    if evaluator is None:
        raise ValueError(f"Unknown task type: {dataset.task_type}")

    results: list[EvalResult] = []
    run_id = f"eval-{dataset.name}-{int(time.time())}"

    for case in dataset.cases:
        start = time.monotonic()
        try:
            if output_fn is not None:
                output = output_fn(case.input_data)
            else:
                output = case.input_data  # Use input as output for evaluator testing
            result = evaluator(output, case.expected)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[Eval] Case '{case.name}' failed: {exc}")
            result = EvalResult(
                case_name=case.name,
                scores={},
                passed=False,
                details={"error": str(exc)},
            )
        result.case_name = case.name
        result.latency_s = time.monotonic() - start

        # Apply dataset-level minimum score thresholds
        if dataset.min_scores and result.scores:
            for score_name, threshold in dataset.min_scores.items():
                if score_name in result.scores and result.scores[score_name] < threshold:
                    result.passed = False

        results.append(result)

        # Push scores to Langfuse if available
        _push_to_langfuse(langfuse_client, run_id, dataset.name, case.name, result)

    return results


def _push_to_langfuse(
    client: Any | None,
    run_id: str,
    dataset_name: str,
    case_name: str,
    result: EvalResult,
) -> None:
    """Push evaluation scores to Langfuse. Failures are swallowed."""
    if client is None:
        return
    try:
        for score_name, score_value in result.scores.items():
            client.score(
                name=f"{dataset_name}/{score_name}",
                value=score_value,
                comment=f"run={run_id} case={case_name}",
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"[Eval] Langfuse score push failed: {exc}")
