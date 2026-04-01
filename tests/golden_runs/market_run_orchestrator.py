"""Full-market golden run orchestrator.

STORY-268 / EPIC-070: Runs the EnrichmentPipeline for a benchmark
company set with mocked external dependencies, captures per-company
artifacts (raw sources + aggregated records), and supports diffing
against golden baselines for regression detection.

Usage::

    orchestrator = MarketRunOrchestrator(artifacts_dir)
    results = await orchestrator.run(BENCHMARK_COMPANIES, COMPANY_MOCK_DATA)
    report = orchestrator.diff_against_baseline("full_market_baseline")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment
from solstein.adapters.enrichment.patents import PatentEnrichment
from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment
from solstein.adapters.registry import SourceRegistry
from solstein.application.enrichment_pipeline import EnrichmentPipeline
from solstein.domain.models import AggregatedDataRecord

from .market_fixtures import COMPANY_MOCK_DATA, BenchmarkCompany


@dataclass
class CompanyRunResult:
    """Result of running the pipeline for a single company."""

    company_id: str
    company_name: str
    record: AggregatedDataRecord
    adapter_count: int
    successful_adapters: int
    failed_adapters: int


@dataclass
class MarketRunResult:
    """Aggregate result of a full-market golden run."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    company_results: list[CompanyRunResult] = field(default_factory=list)

    @property
    def total_companies(self) -> int:
        return len(self.company_results)

    @property
    def total_facts(self) -> int:
        return sum(r.record.total_facts for r in self.company_results)

    @property
    def average_completeness(self) -> float:
        if not self.company_results:
            return 0.0
        return sum(
            r.record.data_completeness_percentage for r in self.company_results
        ) / len(self.company_results)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict for artifact storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_companies": self.total_companies,
            "total_facts": self.total_facts,
            "average_completeness": round(self.average_completeness, 2),
            "companies": [
                {
                    "company_id": r.company_id,
                    "company_name": r.company_name,
                    "adapter_count": r.adapter_count,
                    "successful_adapters": r.successful_adapters,
                    "failed_adapters": r.failed_adapters,
                    "total_facts": r.record.total_facts,
                    "average_confidence": round(r.record.average_confidence, 4),
                    "data_completeness_percentage": round(
                        r.record.data_completeness_percentage, 2
                    ),
                    "fact_types": [f.fact_type for f in r.record.facts],
                }
                for r in self.company_results
            ],
        }


@dataclass
class RegressionViolation:
    """A single regression detected during baseline comparison."""

    company_id: str
    field_name: str
    expected: str
    actual: str
    severity: str = "error"


@dataclass
class RegressionReport:
    """Result of comparing a market run against a golden baseline."""

    violations: list[RegressionViolation] = field(default_factory=list)
    checked_companies: int = 0
    checked_fields: int = 0

    @property
    def passed(self) -> bool:
        return not any(v.severity == "error" for v in self.violations)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [
            f"[{status}] Market regression: "
            f"{self.checked_companies} companies, "
            f"{self.checked_fields} fields, "
            f"{len(self.violations)} violations"
        ]
        for v in self.violations:
            lines.append(
                f"  [{v.severity.upper()}] {v.company_id}.{v.field_name}: "
                f"expected {v.expected}, got {v.actual}"
            )
        return "\n".join(lines)


def _build_test_registry() -> SourceRegistry:
    """Build a minimal registry with the 3 always-available adapters."""
    registry = SourceRegistry()
    registry.register_enrichment(YahooFinanceEnrichment())
    registry.register_enrichment(GlobalMarketEnrichment())
    registry.register_enrichment(PatentEnrichment())
    return registry


class MarketRunOrchestrator:
    """Orchestrates a full-market golden run with mocked dependencies."""

    def __init__(self, artifacts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir
        self._last_result: MarketRunResult | None = None

    async def run(
        self,
        companies: list[BenchmarkCompany],
        mock_data: dict[str, dict[str, Any]] | None = None,
    ) -> MarketRunResult:
        """Run the pipeline for all benchmark companies.

        External dependencies (yfinance, patent search, global market)
        are patched with deterministic mock data from the fixtures.
        """
        if mock_data is None:
            mock_data = COMPANY_MOCK_DATA

        registry = _build_test_registry()
        pipeline = EnrichmentPipeline(registry, timeout_s=10.0)
        result = MarketRunResult()

        for company in companies:
            company_result = await self._run_single(
                pipeline, registry, company, mock_data.get(company.company_id, {})
            )
            result.company_results.append(company_result)

        self._last_result = result
        return result

    async def _run_single(
        self,
        pipeline: EnrichmentPipeline,
        registry: SourceRegistry,
        company: BenchmarkCompany,
        mocks: dict[str, Any],
    ) -> CompanyRunResult:
        """Run the pipeline for a single company with appropriate mocks."""
        adapter_count = len(registry.all_enrichment_sources)

        patches = self._build_patches(mocks)
        with _ApplyPatches(patches):
            record = await pipeline.enrich(
                company_id=company.company_id,
                company_name=company.company_name,
                ticker=company.ticker,
                website=company.website,
            )

        successful = record.total_facts
        return CompanyRunResult(
            company_id=company.company_id,
            company_name=company.company_name,
            record=record,
            adapter_count=adapter_count,
            successful_adapters=successful,
            failed_adapters=adapter_count - successful,
        )

    def _build_patches(self, mocks: dict[str, Any]) -> dict[str, Any]:
        """Build patch targets from mock data dict."""
        patches: dict[str, Any] = {}

        if "company_research" in mocks:
            patches["solstein.data.company_research.CompanyResearcher"] = (
                _make_researcher_mock(mocks["company_research"])
            )

        if "stock_data" in mocks:
            patches["solstein.data.fetchers.GlobalMarketLoader"] = (
                _make_loader_mock(mocks["stock_data"])
            )

        if "patent_result" in mocks:
            patches["solstein.data.patent_client.search_company_patents"] = (
                mocks["patent_result"]()
            )

        return patches

    def store_result(self, scenario: str) -> Path:
        """Store the last run result as a JSON artifact."""
        if self._last_result is None:
            raise RuntimeError("No run result to store; call run() first")

        actual_dir = self.artifacts_dir / "actual_runs"
        actual_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = actual_dir / f"market_run_{scenario}_{ts}.json"
        path.write_text(
            json.dumps(self._last_result.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        return path

    def diff_against_baseline(
        self,
        baseline: dict[str, Any],
    ) -> RegressionReport:
        """Compare the last run against a golden baseline."""
        if self._last_result is None:
            raise RuntimeError("No run result to diff; call run() first")

        return _diff_market_results(self._last_result, baseline)


def _make_researcher_mock(factory: Any) -> Any:
    """Create a mock class that returns the factory result on .research()."""
    mock_cls = MagicMock()
    mock_cls.return_value.research.return_value = factory()
    return mock_cls


def _make_loader_mock(factory: Any) -> Any:
    """Create a mock class that returns the factory result on .get_stock_data()."""
    mock_cls = MagicMock()
    mock_cls.return_value.get_stock_data.return_value = factory()
    return mock_cls


class _ApplyPatches:
    """Context manager that applies multiple unittest.mock.patch calls."""

    def __init__(self, patches: dict[str, Any]) -> None:
        self._patchers: list[Any] = []
        for target, replacement in patches.items():
            if target == "solstein.data.patent_client.search_company_patents":
                self._patchers.append(
                    patch(target, return_value=replacement)
                )
            else:
                self._patchers.append(patch(target, replacement))

    def __enter__(self) -> None:
        for p in self._patchers:
            p.start()

    def __exit__(self, *args: Any) -> None:
        for p in self._patchers:
            p.stop()


def _diff_market_results(
    actual: MarketRunResult,
    baseline: dict[str, Any],
) -> RegressionReport:
    """Compare a MarketRunResult against a baseline artifact."""
    report = RegressionReport()
    baseline_companies = {
        c["company_id"]: c for c in baseline.get("companies", [])
    }

    for company_result in actual.company_results:
        cid = company_result.company_id
        report.checked_companies += 1

        if cid not in baseline_companies:
            report.violations.append(RegressionViolation(
                company_id=cid,
                field_name="presence",
                expected="present in baseline",
                actual="missing from baseline",
                severity="warning",
            ))
            continue

        expected = baseline_companies[cid]
        _diff_company(report, cid, company_result, expected)

    # Check for companies in baseline but missing from actual
    actual_ids = {r.company_id for r in actual.company_results}
    for cid in baseline_companies:
        if cid not in actual_ids:
            report.violations.append(RegressionViolation(
                company_id=cid,
                field_name="presence",
                expected="present in run",
                actual="missing from run",
                severity="error",
            ))

    return report


def _diff_company(
    report: RegressionReport,
    cid: str,
    actual: CompanyRunResult,
    expected: dict[str, Any],
) -> None:
    """Compare a single company's result against its baseline entry."""
    # Check total_facts (no silent field loss)
    report.checked_fields += 1
    if actual.record.total_facts < expected.get("total_facts", 0):
        report.violations.append(RegressionViolation(
            company_id=cid,
            field_name="total_facts",
            expected=f">= {expected['total_facts']}",
            actual=str(actual.record.total_facts),
        ))

    # Check data completeness doesn't drop
    report.checked_fields += 1
    expected_completeness = expected.get("data_completeness_percentage", 0)
    if actual.record.data_completeness_percentage < expected_completeness * 0.9:
        report.violations.append(RegressionViolation(
            company_id=cid,
            field_name="data_completeness_percentage",
            expected=f">= {expected_completeness * 0.9:.1f}%",
            actual=f"{actual.record.data_completeness_percentage:.1f}%",
        ))

    # Check average confidence doesn't drop significantly
    report.checked_fields += 1
    expected_confidence = expected.get("average_confidence", 0)
    if expected_confidence > 0 and actual.record.average_confidence < expected_confidence * 0.8:
        report.violations.append(RegressionViolation(
            company_id=cid,
            field_name="average_confidence",
            expected=f">= {expected_confidence * 0.8:.4f}",
            actual=f"{actual.record.average_confidence:.4f}",
        ))

    # Check fact types are preserved (no silent source loss)
    report.checked_fields += 1
    expected_types = set(expected.get("fact_types", []))
    actual_types = {f.fact_type for f in actual.record.facts}
    missing_types = expected_types - actual_types
    if missing_types:
        report.violations.append(RegressionViolation(
            company_id=cid,
            field_name="fact_types",
            expected=f"includes {sorted(missing_types)}",
            actual=f"missing {sorted(missing_types)}",
        ))
