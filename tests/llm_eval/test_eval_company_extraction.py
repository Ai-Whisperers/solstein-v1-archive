"""Tests for company extraction evaluation (STORY-074).

Runs the company_extraction evaluator against all cases in the dataset.
Each case must pass its minimum score thresholds.
"""

from __future__ import annotations

import pytest

from solstein.llm.evaluation import run_evaluation

from .datasets import COMPANY_EXTRACTION_DATASET


class TestCompanyExtractionEvaluation:
    """Evaluate company data extraction quality."""

    @pytest.fixture
    def results(self):
        return run_evaluation(COMPANY_EXTRACTION_DATASET)

    def test_all_cases_evaluated(self, results):
        assert len(results) == len(COMPANY_EXTRACTION_DATASET.cases)

    def test_stripe_extraction_passes(self, results):
        r = next(r for r in results if r.case_name == "stripe_extraction")
        assert r.passed, f"stripe_extraction failed: {r.scores}"

    def test_databricks_extraction_passes(self, results):
        r = next(r for r in results if r.case_name == "databricks_extraction")
        assert r.passed, f"databricks_extraction failed: {r.scores}"

    def test_figma_extraction_passes(self, results):
        r = next(r for r in results if r.case_name == "figma_extraction")
        assert r.passed, f"figma_extraction failed: {r.scores}"

    def test_sparse_startup_passes(self, results):
        r = next(r for r in results if r.case_name == "sparse_startup")
        assert r.passed, f"sparse_startup failed: {r.scores}"

    def test_public_company_passes(self, results):
        r = next(r for r in results if r.case_name == "public_company_extraction")
        assert r.passed, f"public_company_extraction failed: {r.scores}"

    def test_value_accuracy_meets_threshold(self, results):
        threshold = COMPANY_EXTRACTION_DATASET.min_scores.get("value_accuracy", 0)
        for r in results:
            assert r.scores.get("value_accuracy", 0) >= threshold, (
                f"{r.case_name} value_accuracy {r.scores.get('value_accuracy')} < {threshold}"
            )

    def test_field_presence_meets_threshold(self, results):
        threshold = COMPANY_EXTRACTION_DATASET.min_scores.get("field_presence", 0)
        for r in results:
            assert r.scores.get("field_presence", 0) >= threshold, (
                f"{r.case_name} field_presence {r.scores.get('field_presence')} < {threshold}"
            )
