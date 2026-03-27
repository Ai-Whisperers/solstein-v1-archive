"""Tests for research plan evaluation (STORY-074).

Runs the research_plan evaluator against all cases in the dataset.
Each case must pass its minimum score thresholds.
"""

from __future__ import annotations

import pytest

from solstein.llm.evaluation import run_evaluation

from .datasets import RESEARCH_PLAN_DATASET


class TestResearchPlanEvaluation:
    """Evaluate research plan generation quality."""

    @pytest.fixture
    def results(self):
        return run_evaluation(RESEARCH_PLAN_DATASET)

    def test_all_cases_evaluated(self, results):
        assert len(results) == len(RESEARCH_PLAN_DATASET.cases)

    def test_stripe_fintech_passes(self, results):
        r = next(r for r in results if r.case_name == "stripe_fintech")
        assert r.passed, f"stripe_fintech failed: {r.scores}"

    def test_unknown_startup_passes(self, results):
        r = next(r for r in results if r.case_name == "unknown_startup")
        assert r.passed, f"unknown_startup failed: {r.scores}"

    def test_enterprise_saas_passes(self, results):
        r = next(r for r in results if r.case_name == "enterprise_saas")
        assert r.passed, f"enterprise_saas failed: {r.scores}"

    def test_biotech_company_passes(self, results):
        r = next(r for r in results if r.case_name == "biotech_company")
        assert r.passed, f"biotech_company failed: {r.scores}"

    def test_european_fintech_passes(self, results):
        r = next(r for r in results if r.case_name == "european_fintech")
        assert r.passed, f"european_fintech failed: {r.scores}"

    def test_format_compliance_all_pass(self, results):
        for r in results:
            assert r.scores.get("format_compliance", 0) == 1.0, (
                f"{r.case_name} format_compliance: {r.scores.get('format_compliance')}"
            )

    def test_query_count_meets_threshold(self, results):
        threshold = RESEARCH_PLAN_DATASET.min_scores.get("query_count", 0)
        for r in results:
            assert r.scores.get("query_count", 0) >= threshold, (
                f"{r.case_name} query_count {r.scores.get('query_count')} < {threshold}"
            )
