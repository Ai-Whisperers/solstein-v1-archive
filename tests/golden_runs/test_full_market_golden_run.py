"""Full-market golden run tests with artifact diffing.

STORY-268 / EPIC-070: Runs the EnrichmentPipeline for a 5-company
benchmark set and verifies pipeline completeness, artifact shapes,
regression gates, and no silent field loss against golden baselines.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from solstein.domain.models import AggregatedDataRecord

from .conftest import ARTIFACTS_DIR, load_artifact
from .market_fixtures import BENCHMARK_COMPANIES, COMPANY_MOCK_DATA
from .market_run_orchestrator import (
    MarketRunOrchestrator,
    MarketRunResult,
)


@pytest.fixture()
def baseline() -> dict[str, Any]:
    return load_artifact("full_market_baseline")


@pytest.fixture()
def orchestrator() -> MarketRunOrchestrator:
    return MarketRunOrchestrator(ARTIFACTS_DIR)


@pytest.fixture()
def market_result(orchestrator: MarketRunOrchestrator) -> MarketRunResult:
    """Run the full-market golden run once and cache the result."""
    return asyncio.get_event_loop().run_until_complete(
        orchestrator.run(BENCHMARK_COMPANIES, COMPANY_MOCK_DATA)
    )


# ---------------------------------------------------------------------------
# Pipeline Execution Tests
# ---------------------------------------------------------------------------


class TestFullMarketExecution:
    """Verify the pipeline executes correctly for all benchmark companies."""

    def test_all_companies_processed(self, market_result: MarketRunResult) -> None:
        """Pipeline must process all 5 benchmark companies."""
        assert market_result.total_companies == 5

    def test_total_facts_produced(self, market_result: MarketRunResult) -> None:
        """Pipeline must produce the expected total fact count."""
        assert market_result.total_facts == 13

    def test_each_company_returns_aggregated_record(
        self, market_result: MarketRunResult
    ) -> None:
        """Each company result must contain an AggregatedDataRecord."""
        for cr in market_result.company_results:
            assert isinstance(cr.record, AggregatedDataRecord)
            assert cr.record.company_id == cr.company_id

    def test_ticker_companies_have_full_coverage(
        self, market_result: MarketRunResult
    ) -> None:
        """Companies with tickers must have 100% data completeness."""
        ticker_companies = ["bench-001", "bench-002", "bench-004", "bench-005"]
        for cr in market_result.company_results:
            if cr.company_id in ticker_companies:
                assert cr.record.data_completeness_percentage == 100.0, (
                    f"{cr.company_id} expected 100% completeness, "
                    f"got {cr.record.data_completeness_percentage}%"
                )

    def test_private_company_has_partial_coverage(
        self, market_result: MarketRunResult
    ) -> None:
        """Private company (no ticker) must have partial coverage."""
        for cr in market_result.company_results:
            if cr.company_id == "bench-003":
                assert cr.record.data_completeness_percentage < 50.0
                assert cr.record.total_facts == 1
                return
        pytest.fail("bench-003 not found in results")

    def test_average_completeness_above_threshold(
        self, market_result: MarketRunResult
    ) -> None:
        """Market-wide average completeness must exceed 80%."""
        assert market_result.average_completeness >= 80.0


# ---------------------------------------------------------------------------
# Artifact Shape Tests
# ---------------------------------------------------------------------------


class TestArtifactShapes:
    """Verify output artifact structure matches expected shape."""

    def test_result_serializes_to_dict(self, market_result: MarketRunResult) -> None:
        """MarketRunResult must serialize to a complete dict."""
        data = market_result.to_dict()
        assert "timestamp" in data
        assert "total_companies" in data
        assert "total_facts" in data
        assert "average_completeness" in data
        assert "companies" in data
        assert len(data["companies"]) == 5

    def test_company_entries_have_required_fields(
        self, market_result: MarketRunResult
    ) -> None:
        """Each company entry must have all required fields."""
        required = [
            "company_id", "company_name", "adapter_count",
            "successful_adapters", "failed_adapters", "total_facts",
            "average_confidence", "data_completeness_percentage", "fact_types",
        ]
        for entry in market_result.to_dict()["companies"]:
            for field in required:
                assert field in entry, f"Missing field: {field} in {entry['company_id']}"

    def test_fact_types_are_valid_data_source_types(
        self, market_result: MarketRunResult
    ) -> None:
        """All fact_type values must be valid DataSourceType values."""
        from solstein.domain.models import DataSourceType

        valid_types = {t.value for t in DataSourceType}
        for cr in market_result.company_results:
            for fact in cr.record.facts:
                assert fact.fact_type in valid_types, (
                    f"Invalid fact_type '{fact.fact_type}' "
                    f"for {cr.company_id}"
                )

    def test_confidence_scores_in_range(
        self, market_result: MarketRunResult
    ) -> None:
        """All confidence scores must be in [0, 1]."""
        for cr in market_result.company_results:
            for fact in cr.record.facts:
                assert 0.0 <= fact.confidence <= 1.0, (
                    f"Confidence {fact.confidence} out of range "
                    f"for {cr.company_id}"
                )


# ---------------------------------------------------------------------------
# Regression Gate Tests
# ---------------------------------------------------------------------------


class TestRegressionGates:
    """Verify the market run passes regression gates against golden baseline."""

    def test_regression_report_passes(
        self,
        orchestrator: MarketRunOrchestrator,
        market_result: MarketRunResult,
        baseline: dict[str, Any],
    ) -> None:
        """Full regression diff against baseline must pass."""
        orchestrator._last_result = market_result
        report = orchestrator.diff_against_baseline(baseline)
        assert report.passed, report.summary()

    def test_no_company_lost(
        self,
        orchestrator: MarketRunOrchestrator,
        market_result: MarketRunResult,
        baseline: dict[str, Any],
    ) -> None:
        """No company from the baseline should be missing in the run."""
        orchestrator._last_result = market_result
        report = orchestrator.diff_against_baseline(baseline)
        missing = [
            v for v in report.violations
            if v.field_name == "presence" and v.severity == "error"
        ]
        assert len(missing) == 0, f"Companies missing from run: {missing}"

    def test_no_silent_fact_loss(
        self,
        market_result: MarketRunResult,
        baseline: dict[str, Any],
    ) -> None:
        """No company should silently lose facts vs the baseline."""
        baseline_companies = {
            c["company_id"]: c for c in baseline["companies"]
        }
        for cr in market_result.company_results:
            expected = baseline_companies.get(cr.company_id, {})
            expected_facts = expected.get("total_facts", 0)
            assert cr.record.total_facts >= expected_facts, (
                f"{cr.company_id}: expected >= {expected_facts} facts, "
                f"got {cr.record.total_facts}"
            )

    def test_no_silent_source_type_loss(
        self,
        market_result: MarketRunResult,
        baseline: dict[str, Any],
    ) -> None:
        """No company should lose source types that were in the baseline."""
        thresholds = baseline.get("regression_thresholds", {})
        required_types = thresholds.get("required_fact_types_per_company", {})

        for cr in market_result.company_results:
            required = set(required_types.get(cr.company_id, []))
            actual = {f.fact_type for f in cr.record.facts}
            missing = required - actual
            assert not missing, (
                f"{cr.company_id}: missing required fact types {sorted(missing)}"
            )

    def test_total_facts_above_minimum(
        self,
        market_result: MarketRunResult,
        baseline: dict[str, Any],
    ) -> None:
        """Total facts across all companies must meet minimum threshold."""
        min_facts = baseline.get("regression_thresholds", {}).get(
            "min_total_facts", 0
        )
        assert market_result.total_facts >= min_facts, (
            f"Total facts {market_result.total_facts} < minimum {min_facts}"
        )


# ---------------------------------------------------------------------------
# Artifact Storage Tests
# ---------------------------------------------------------------------------


class TestArtifactStorage:
    """Verify artifact storage and retrieval work correctly."""

    def test_store_result_creates_file(
        self,
        orchestrator: MarketRunOrchestrator,
        market_result: MarketRunResult,
        tmp_path: Any,
    ) -> None:
        """store_result must create a JSON file in the artifacts directory."""
        orchestrator.artifacts_dir = tmp_path
        orchestrator._last_result = market_result
        path = orchestrator.store_result("test_scenario")
        assert path.exists()
        assert path.suffix == ".json"

    def test_store_result_roundtrips(
        self,
        orchestrator: MarketRunOrchestrator,
        market_result: MarketRunResult,
        tmp_path: Any,
    ) -> None:
        """Stored artifact must deserialize back to the same data."""
        import json

        orchestrator.artifacts_dir = tmp_path
        orchestrator._last_result = market_result
        path = orchestrator.store_result("roundtrip")

        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["total_companies"] == market_result.total_companies
        assert loaded["total_facts"] == market_result.total_facts
        assert len(loaded["companies"]) == len(market_result.company_results)
