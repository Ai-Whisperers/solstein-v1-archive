"""Integration tests for real adapter chain — Phase 7.

Exercises actual enrichment and discovery adapters against live APIs.
Always-on adapters (no API key) always run. API-gated adapters are
skipped when the corresponding environment variable is absent.

Run with:
    PYTHONPATH=src python3 -m pytest tests/integration/test_full_pipeline.py -m integration -v --no-cov

These tests are NOT run in CI by default.
"""

from __future__ import annotations

import contextlib
import os
import time
from pathlib import Path

import pytest

from solstein.adapters.discovery.competitor_json import CompetitorJsonSource
from solstein.adapters.discovery.static_catalog import StaticCatalogSource
from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment
from solstein.adapters.enrichment.linkedin import LinkedInEnrichment
from solstein.adapters.enrichment.patents import PatentEnrichment
from solstein.adapters.enrichment.website import WebsiteEnrichment
from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment
from solstein.domain.models import DataSourceType, RawDataSource

# Test constants (matching conftest.py)
TEST_COMPANY_ID = "accenture"
TEST_COMPANY_NAME = "Accenture"
TEST_TICKER = "ACN"
TEST_MARKET = "Dutch Energy Software"
TEST_SEED = "Eneve"


# ---------------------------------------------------------------------------
# Discovery Adapter Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
class TestStaticCatalogDiscovery:
    """StaticCatalogSource: always available, no API key."""

    def test_discovers_companies_for_energy_market(self) -> None:
        source = StaticCatalogSource()
        candidates = source.discover(
            market=TEST_MARKET,
            seed_company=TEST_SEED,
            max_results=50,
        )
        assert len(candidates) > 0
        assert all(c.market == TEST_MARKET for c in candidates)

    def test_candidate_fields_populated(self) -> None:
        source = StaticCatalogSource()
        candidates = source.discover(market=TEST_MARKET, seed_company=TEST_SEED)
        for c in candidates[:5]:
            assert c.company_id
            assert c.name
            assert c.industry


@pytest.mark.integration
@pytest.mark.slow
class TestCompetitorJsonDiscovery:
    """CompetitorJsonSource: always available, reads local JSON."""

    def test_discovers_companies(self) -> None:
        source = CompetitorJsonSource()
        candidates = source.discover(
            market=TEST_MARKET,
            seed_company=TEST_SEED,
            max_results=50,
        )
        assert isinstance(candidates, list)


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get("EXA_API_KEY"),
    reason="EXA_API_KEY not set",
)
class TestWebSearchDiscovery:
    """WebSearchDiscoverySource: requires EXA_API_KEY."""

    def test_discovers_companies_via_web_search(self) -> None:
        from solstein.adapters.discovery.web_search import WebSearchDiscoverySource

        source = WebSearchDiscoverySource(exa_api_key=os.environ["EXA_API_KEY"])
        candidates = source.discover(
            market=TEST_MARKET,
            seed_company=TEST_SEED,
            max_results=5,
        )
        assert len(candidates) > 0


# ---------------------------------------------------------------------------
# Always-On Enrichment Adapter Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
class TestYahooFinanceEnrichment:
    """YahooFinanceEnrichment: always available, requires ticker."""

    def test_enriches_with_valid_ticker(self) -> None:
        adapter = YahooFinanceEnrichment()
        start = time.perf_counter()
        result = adapter.enrich(
            company_id=TEST_COMPANY_ID,
            company_name=TEST_COMPANY_NAME,
            ticker=TEST_TICKER,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert isinstance(result, RawDataSource)
        assert result.source_type == DataSourceType.YAHOO_FINANCE
        assert result.confidence == 0.8
        assert isinstance(result.raw_content, dict)
        assert elapsed_ms < 30_000, f"YahooFinance took {elapsed_ms:.0f}ms"

    def test_raises_without_ticker(self) -> None:
        adapter = YahooFinanceEnrichment()
        with pytest.raises(ValueError, match="requires a ticker"):
            adapter.enrich(
                company_id="eneve",
                company_name="Eneve",
                ticker=None,
            )


@pytest.mark.integration
@pytest.mark.slow
class TestGlobalMarketEnrichment:
    """GlobalMarketEnrichment: always available, requires ticker."""

    def test_enriches_with_valid_ticker(self) -> None:
        adapter = GlobalMarketEnrichment()
        result = adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, ticker=TEST_TICKER)

        assert isinstance(result, RawDataSource)
        assert result.source_type == DataSourceType.YAHOO_FINANCE
        assert result.confidence == 0.8
        content = result.raw_content
        assert isinstance(content, dict)
        assert "ticker" in content

    def test_raises_without_ticker(self) -> None:
        adapter = GlobalMarketEnrichment()
        with pytest.raises(ValueError, match="requires a ticker"):
            adapter.enrich("eneve", "Eneve", ticker=None)


@pytest.mark.integration
@pytest.mark.slow
class TestPatentEnrichment:
    """PatentEnrichment: always available, no API key or ticker required."""

    def test_enriches_known_company(self) -> None:
        adapter = PatentEnrichment()
        start = time.perf_counter()
        result = adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert isinstance(result, RawDataSource)
        assert result.confidence >= 0.4
        content = result.raw_content
        assert isinstance(content, dict)
        assert "total_patents" in content
        assert elapsed_ms < 30_000

    def test_enriches_company_without_ticker(self) -> None:
        adapter = PatentEnrichment()
        result = adapter.enrich("eneve", "Eneve")
        assert isinstance(result, RawDataSource)
        assert "total_patents" in result.raw_content


@pytest.mark.integration
@pytest.mark.slow
class TestLinkedInEnrichment:
    """LinkedInEnrichment: always available (news_api_key optional)."""

    def test_enriches_known_company(self) -> None:
        adapter = LinkedInEnrichment(news_api_key=os.environ.get("NEWS_API_KEY"))
        result = adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME)

        assert isinstance(result, RawDataSource)
        assert result.source_type == DataSourceType.LINKEDIN
        assert result.confidence == 0.3
        assert isinstance(result.raw_content, dict)


@pytest.mark.integration
@pytest.mark.slow
class TestWebsiteEnrichment:
    """WebsiteEnrichment: requires a website URL."""

    def test_raises_without_website(self) -> None:
        adapter = WebsiteEnrichment()
        with pytest.raises(ValueError, match="requires a website URL"):
            adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, website=None)


# ---------------------------------------------------------------------------
# API-Gated Enrichment Adapter Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get("NEWS_API_KEY"),
    reason="NEWS_API_KEY not set",
)
class TestNewsEnrichment:
    """NewsEnrichment: requires NEWS_API_KEY."""

    def test_enriches_known_company(self) -> None:
        from solstein.adapters.enrichment.news import NewsEnrichment

        adapter = NewsEnrichment(news_api_key=os.environ["NEWS_API_KEY"])
        result = adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME)

        assert isinstance(result, RawDataSource)
        assert result.confidence >= 0.4
        assert result.raw_content


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get("CRUNCHBASE_API_KEY"),
    reason="CRUNCHBASE_API_KEY not set",
)
class TestFundingEnrichment:
    """FundingEnrichment: requires CRUNCHBASE_API_KEY."""

    def test_enriches_known_company(self) -> None:
        from solstein.adapters.enrichment.funding import FundingEnrichment

        adapter = FundingEnrichment(
            crunchbase_api_key=os.environ["CRUNCHBASE_API_KEY"],
            news_api_key=os.environ.get("NEWS_API_KEY"),
        )
        result = adapter.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME)

        assert isinstance(result, RawDataSource)
        assert result.confidence >= 0.3


# ---------------------------------------------------------------------------
# Multi-Source Aggregation Quality
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
class TestAggregationWithRealData:
    """Test aggregation and signal extraction using real adapter output."""

    def test_multi_source_aggregation_produces_facts(self, real_settings) -> None:
        from solstein.adapters.registry import build_default_registry
        from solstein.domain.models import RawDataRecord
        from solstein.research.aggregate import DefaultFactAggregator

        registry = build_default_registry(real_settings)
        raw_sources = []
        for source in registry.enrichment_sources:
            try:
                raw = source.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, ticker=TEST_TICKER)
                raw_sources.append(raw)
            except Exception:
                pass  # expected for adapters that need website, etc.

        assert len(raw_sources) >= 2, f"Expected at least 2 successful sources, got {len(raw_sources)}"

        raw_record = RawDataRecord(
            company_id=TEST_COMPANY_ID,
            gathering_batch_id="integration-test",
            sources=raw_sources,
            total_sources_found=len(raw_sources),
        )

        aggregator = DefaultFactAggregator()
        aggregated = aggregator.aggregate(TEST_COMPANY_ID, raw_record)

        assert len(aggregated.facts) > 0
        assert aggregated.data_completeness_percentage > 0.0

    def test_signal_extraction_from_real_aggregated_data(self, real_settings) -> None:
        from solstein.adapters.registry import build_default_registry
        from solstein.domain.models import RawDataRecord
        from solstein.research.aggregate import DefaultFactAggregator
        from solstein.research.signals import extract_signals

        registry = build_default_registry(real_settings)
        raw_sources = []
        for source in registry.enrichment_sources:
            try:
                raw = source.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, ticker=TEST_TICKER)
                raw_sources.append(raw)
            except Exception:
                pass

        raw_record = RawDataRecord(
            company_id=TEST_COMPANY_ID,
            gathering_batch_id="integration-test",
            sources=raw_sources,
            total_sources_found=len(raw_sources),
        )

        aggregated = DefaultFactAggregator().aggregate(TEST_COMPANY_ID, raw_record)
        signal_record = extract_signals(aggregated, batch_id="integration-test")

        assert len(signal_record.signals) >= 2
        signal_names = {s.signal_name for s in signal_record.signals}
        assert signal_names & {"revenue_level", "company_size", "valuation"}


# ---------------------------------------------------------------------------
# Full Pipeline Integration
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
class TestFullPipelineIntegration:
    """Run the complete pipeline with real adapters, limited company set."""

    def test_pipeline_produces_all_artifacts(self, tmp_path: Path) -> None:
        from solstein.research.pipeline import run_market_intelligence

        summary = run_market_intelligence(
            seed_company=TEST_SEED,
            market=TEST_MARKET,
            output_dir=tmp_path,
            max_companies=3,
            strict_provenance=False,
        )

        assert summary["profiles"] >= 1
        assert summary["discovered"] >= 1

        expected_files = [
            "discovery_candidates.json",
            "extracted.json",
            "stage_report.json",
            "provenance_report.json",
            "contradictions_report.json",
            "evidence_readiness.json",
            "scored.json",
            "market_analysis.json",
            "dashboard.xlsx",
        ]
        for filename in expected_files:
            assert (tmp_path / filename).exists(), f"Missing artifact: {filename}"

    def test_audit_report_generation(self, tmp_path: Path) -> None:
        """Run pipeline, collect adapter health, generate audit report."""
        from solstein.adapters.instrumented import build_instrumented_registry
        from solstein.config import Settings
        from solstein.exporters.audit_report import PipelineAuditReportGenerator
        from solstein.research.pipeline import run_market_intelligence

        # Step 1: Run standard pipeline for artifacts
        run_market_intelligence(
            seed_company=TEST_SEED,
            market=TEST_MARKET,
            output_dir=tmp_path,
            max_companies=3,
            strict_provenance=False,
        )

        # Step 2: Collect adapter health via instrumented wrappers
        settings = Settings.load()
        registry, enrichment_wrappers, discovery_wrappers = build_instrumented_registry(settings)

        for source in registry.discovery_sources:
            with contextlib.suppress(Exception):
                source.discover(market=TEST_MARKET, seed_company=TEST_SEED, max_results=3)

        for source in registry.enrichment_sources:
            with contextlib.suppress(Exception):
                source.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, ticker=TEST_TICKER)

        all_health: list[dict] = []
        for w in discovery_wrappers:
            all_health.extend([vars(r) for r in w.health_records])
        for w in enrichment_wrappers:
            all_health.extend([vars(r) for r in w.health_records])

        # Step 3: Generate audit report
        generator = PipelineAuditReportGenerator()
        audit_path = generator.generate(
            artifacts_dir=tmp_path,
            output_dir=tmp_path,
            adapter_health=all_health,
        )

        assert audit_path.exists()
        content = audit_path.read_text()
        assert "# Pipeline Audit Report" in content
        assert "## Discovery" in content
        assert "## Enrichment" in content
        assert "## Scoring" in content
        assert "## Adapter Health" in content


# ---------------------------------------------------------------------------
# Adapter Health Smoke Test
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.slow
class TestAdapterHealthSmoke:
    """Quick health check: every registered adapter responds."""

    def test_all_registered_enrichment_adapters_respond(self, real_registry) -> None:
        results: dict[str, dict] = {}
        for source in real_registry.enrichment_sources:
            start = time.perf_counter()
            try:
                source.enrich(TEST_COMPANY_ID, TEST_COMPANY_NAME, ticker=TEST_TICKER)
                status = "success"
            except Exception as exc:
                status = f"error: {exc}"
            elapsed = (time.perf_counter() - start) * 1000
            results[source.source_name] = {"status": status, "ms": round(elapsed)}

        # At least YahooFinance, GlobalMarket, Patents should succeed
        successful = [name for name, r in results.items() if r["status"] == "success"]
        assert len(successful) >= 3, f"Only {len(successful)} adapters succeeded: {results}"
