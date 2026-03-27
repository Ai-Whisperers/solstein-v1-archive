"""Tests for the evaluation framework itself (STORY-074).

Verifies scoring functions, runner mechanics, and Langfuse integration.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from solstein.llm.evaluation import (
    EvalCase,
    EvalDataset,
    _score_field_presence,
    _score_list_coverage,
    _score_value_accuracy,
    evaluate_business_analysis,
    evaluate_company_extraction,
    evaluate_research_plan,
    run_evaluation,
)


class TestScoreHelpers:
    """Test individual scoring functions."""

    def test_field_presence_all_present(self):
        output = {"name": "Acme", "industry": "Tech", "revenue": 100}
        assert _score_field_presence(output, ["name", "industry", "revenue"]) == 1.0

    def test_field_presence_partial(self):
        output = {"name": "Acme", "industry": None}
        assert _score_field_presence(output, ["name", "industry"]) == 0.5

    def test_field_presence_none_present(self):
        output = {"name": None}
        assert _score_field_presence(output, ["name", "industry"]) == 0.0

    def test_field_presence_empty_required(self):
        assert _score_field_presence({}, []) == 1.0

    def test_value_accuracy_exact_match(self):
        output = {"name": "Acme", "year": 2020}
        expected = {"name": "Acme", "year": 2020}
        assert _score_value_accuracy(output, expected) == 1.0

    def test_value_accuracy_case_insensitive(self):
        output = {"name": "ACME CORP"}
        expected = {"name": "acme corp"}
        assert _score_value_accuracy(output, expected) == 1.0

    def test_value_accuracy_numeric_tolerance(self):
        output = {"revenue": 105.0}
        expected = {"revenue": 100.0}
        assert _score_value_accuracy(output, expected) == 1.0  # within 10%

    def test_value_accuracy_numeric_out_of_tolerance(self):
        output = {"revenue": 120.0}
        expected = {"revenue": 100.0}
        assert _score_value_accuracy(output, expected) == 0.0  # 20% off

    def test_value_accuracy_skip_none_expected(self):
        output = {"name": "Acme"}
        expected = {"name": "Acme", "optional": None}
        assert _score_value_accuracy(output, expected) == 1.0

    def test_list_coverage_full(self):
        output = ["Stripe Payments", "Stripe Connect", "Atlas"]
        expected = ["Stripe Payments", "Atlas"]
        assert _score_list_coverage(output, expected) == 1.0

    def test_list_coverage_partial(self):
        output = ["Payments"]
        expected = ["Payments", "Connect"]
        assert _score_list_coverage(output, expected) == 0.5

    def test_list_coverage_empty_output(self):
        assert _score_list_coverage(None, ["item"]) == 0.0

    def test_list_coverage_empty_expected(self):
        assert _score_list_coverage(["item"], []) == 1.0


class TestEvaluators:
    """Test task-specific evaluators directly."""

    def test_research_plan_perfect(self):
        output = {
            "queries": [
                {"query": "q1", "priority": 1, "intent": "website"},
                {"query": "q2", "priority": 2, "intent": "funding"},
                {"query": "q3", "priority": 3, "intent": "financials"},
                {"query": "q4", "priority": 1, "intent": "headcount"},
                {"query": "q5", "priority": 2, "intent": "news"},
                {"query": "q6", "priority": 3, "intent": "social"},
            ],
        }
        expected = {
            "min_queries": 6,
            "max_queries": 8,
            "required_intents": ["website", "funding", "financials"],
        }
        result = evaluate_research_plan(output, expected)
        assert result.passed
        assert result.scores["format_compliance"] == 1.0

    def test_research_plan_empty_queries(self):
        result = evaluate_research_plan({"queries": []}, {"min_queries": 6})
        assert not result.passed
        assert result.scores["query_count"] == 0.0

    def test_company_extraction_complete(self):
        output = {
            "company_name": "Acme",
            "industry": "Tech",
            "description": "A tech company",
            "website": "https://acme.com",
            "headquarters": "SF",
            "founded_year": 2020,
            "employees": 100,
            "revenue": 50.0,
            "funding_raised": 10.0,
            "products": ["Widget"],
        }
        expected = {
            "required_fields": ["company_name", "industry"],
            "expected_values": {"company_name": "Acme"},
        }
        result = evaluate_company_extraction(output, expected)
        assert result.passed
        assert result.scores["field_presence"] == 1.0
        assert result.scores["value_accuracy"] == 1.0

    def test_business_analysis_substantive(self):
        output = {
            "analysis": (
                "The company shows strong growth with revenue of $100 million. "
                "Competitive positioning is favorable in the market segment. "
                "Key risks include market saturation and regulatory changes."
            ),
        }
        expected = {
            "min_words": 20,
            "required_topics": ["revenue", "competitive", "risk"],
        }
        result = evaluate_business_analysis(output, expected)
        assert result.passed
        assert result.scores["topic_coverage"] == 1.0

    def test_business_analysis_empty_fails(self):
        result = evaluate_business_analysis(
            {"analysis": ""},
            {"min_words": 50, "required_topics": ["revenue"]},
        )
        assert not result.passed


class TestEvalRunner:
    """Test the evaluation runner."""

    def test_run_with_dataset(self):
        dataset = EvalDataset(
            name="test",
            task_type="company_extraction",
            cases=[
                EvalCase(
                    name="case1",
                    input_data={"company_name": "Acme", "industry": "Tech", "description": "A co"},
                    expected={"required_fields": ["company_name"]},
                ),
            ],
        )
        results = run_evaluation(dataset)
        assert len(results) == 1
        assert results[0].case_name == "case1"

    def test_run_applies_min_scores(self):
        dataset = EvalDataset(
            name="test",
            task_type="company_extraction",
            cases=[
                EvalCase(
                    name="case1",
                    input_data={"company_name": None},
                    expected={"required_fields": ["company_name", "industry", "description"]},
                ),
            ],
            min_scores={"field_presence": 0.9},
        )
        results = run_evaluation(dataset)
        assert not results[0].passed  # field_presence should be 0.0 < 0.9

    def test_run_unknown_task_type_raises(self):
        dataset = EvalDataset(name="bad", task_type="unknown", cases=[])
        with pytest.raises(ValueError, match="Unknown task type"):
            run_evaluation(dataset)

    def test_langfuse_score_push(self):
        mock_lf = MagicMock()
        dataset = EvalDataset(
            name="test",
            task_type="company_extraction",
            cases=[
                EvalCase(
                    name="c1",
                    input_data={"company_name": "Acme", "industry": "Tech", "description": "Co"},
                    expected={"required_fields": ["company_name"]},
                ),
            ],
        )
        run_evaluation(dataset, langfuse_client=mock_lf)
        assert mock_lf.score.called

    def test_langfuse_failure_swallowed(self):
        mock_lf = MagicMock()
        mock_lf.score.side_effect = ConnectionError("Langfuse down")
        dataset = EvalDataset(
            name="test",
            task_type="company_extraction",
            cases=[
                EvalCase(
                    name="c1",
                    input_data={"company_name": "Acme", "industry": "Tech", "description": "Co"},
                    expected={"required_fields": ["company_name"]},
                ),
            ],
        )
        # Should not raise
        results = run_evaluation(dataset, langfuse_client=mock_lf)
        assert len(results) == 1


class TestDegradedPromptDetection:
    """AC: A deliberately degraded prompt produces failing evaluation scores."""

    def test_degraded_research_plan_fails(self):
        """A plan with only 1 low-priority query should fail."""
        output = {
            "queries": [
                {"query": "random search", "priority": 3, "intent": "other"},
            ],
        }
        expected = {
            "min_queries": 6,
            "required_intents": ["website", "funding", "financials"],
        }
        result = evaluate_research_plan(output, expected)
        assert not result.passed

    def test_degraded_extraction_fails(self):
        """An extraction with all None values should fail."""
        output = {
            "company_name": None,
            "industry": None,
            "description": None,
        }
        expected = {
            "required_fields": ["company_name", "industry", "description"],
            "expected_values": {"company_name": "Stripe"},
        }
        result = evaluate_company_extraction(output, expected)
        assert not result.passed
