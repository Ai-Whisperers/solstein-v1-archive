"""Tests for business analysis evaluation (STORY-074).

Runs the business_analysis evaluator against all cases in the dataset.
Each case must pass its minimum score thresholds.
"""

from __future__ import annotations

import pytest

from solstein.llm.evaluation import run_evaluation

from .datasets import BUSINESS_ANALYSIS_DATASET


class TestBusinessAnalysisEvaluation:
    """Evaluate business analysis output quality."""

    @pytest.fixture
    def results(self):
        return run_evaluation(BUSINESS_ANALYSIS_DATASET)

    def test_all_cases_evaluated(self, results):
        assert len(results) == len(BUSINESS_ANALYSIS_DATASET.cases)

    def test_stripe_analysis_passes(self, results):
        r = next(r for r in results if r.case_name == "stripe_analysis")
        assert r.passed, f"stripe_analysis failed: {r.scores}"

    def test_databricks_threat_passes(self, results):
        r = next(r for r in results if r.case_name == "databricks_competitive_threat")
        assert r.passed, f"databricks_competitive_threat failed: {r.scores}"

    def test_short_analysis_passes(self, results):
        r = next(r for r in results if r.case_name == "short_analysis")
        assert r.passed, f"short_analysis failed: {r.scores}"

    def test_signal_extraction_passes(self, results):
        r = next(r for r in results if r.case_name == "signal_extraction_analysis")
        assert r.passed, f"signal_extraction_analysis failed: {r.scores}"

    def test_empty_analysis_fails(self, results):
        """Empty analysis should fail - verifying the evaluator catches regressions."""
        r = next(r for r in results if r.case_name == "empty_analysis")
        assert not r.passed, "empty_analysis should fail but didn't"
        assert r.scores.get("content_length", 1) == 0.0

    def test_topic_coverage_good_cases(self, results):
        threshold = BUSINESS_ANALYSIS_DATASET.min_scores.get("topic_coverage", 0)
        for r in results:
            if r.case_name == "empty_analysis":
                continue  # Expected to fail
            assert r.scores.get("topic_coverage", 0) >= threshold, (
                f"{r.case_name} topic_coverage {r.scores.get('topic_coverage')} < {threshold}"
            )
