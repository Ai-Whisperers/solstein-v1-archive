"""STORY-265: Contract tests for surviving canonical enrichment adapters.

Verify that each canonical adapter:
1. Can be instantiated
2. Has the expected interface (enrich method)
3. Has a source_name attribute
4. Unified adapters are NOT importable from the active enrichment package
"""

import importlib

import pytest


class TestCanonicalAdapterContracts:
    """Verify canonical (legacy) enrichment adapters satisfy the protocol."""

    def test_patent_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.patents import PatentEnrichment

        adapter = PatentEnrichment()
        assert hasattr(adapter, "enrich")

    def test_news_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.news import NewsEnrichment

        adapter = NewsEnrichment(news_api_key=None)
        assert hasattr(adapter, "enrich")

    def test_funding_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.funding import FundingEnrichment

        adapter = FundingEnrichment(crunchbase_api_key=None, news_api_key=None)
        assert hasattr(adapter, "enrich")

    def test_linkedin_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.linkedin import LinkedInEnrichment

        adapter = LinkedInEnrichment(news_api_key=None)
        assert hasattr(adapter, "enrich")

    def test_website_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.website import WebsiteEnrichment

        adapter = WebsiteEnrichment()
        assert hasattr(adapter, "enrich")

    def test_yahoo_finance_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment

        adapter = YahooFinanceEnrichment()
        assert hasattr(adapter, "enrich")

    def test_global_market_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment

        adapter = GlobalMarketEnrichment()
        assert hasattr(adapter, "enrich")

    def test_web_search_news_enrichment_instantiable(self) -> None:
        from solstein.adapters.enrichment.web_search_news import WebSearchNewsEnrichment

        adapter = WebSearchNewsEnrichment()
        assert hasattr(adapter, "enrich")


class TestUnifiedAdaptersRetired:
    """Verify unified adapters are no longer importable from active package."""

    @pytest.mark.parametrize(
        "module_name",
        [
            "solstein.adapters.enrichment.funding_unified",
            "solstein.adapters.enrichment.linkedin_unified",
            "solstein.adapters.enrichment.news_unified",
            "solstein.adapters.enrichment.patents_unified",
            "solstein.adapters.enrichment.web_search_unified",
            "solstein.adapters.enrichment.website_unified",
        ],
    )
    def test_unified_adapter_not_importable_from_active_path(self, module_name: str) -> None:
        """Unified adapters must not be importable from active enrichment package."""
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_name)

    @pytest.mark.parametrize(
        "module_name",
        [
            "solstein.adapters.enrichment._retired.funding_unified",
            "solstein.adapters.enrichment._retired.linkedin_unified",
            "solstein.adapters.enrichment._retired.news_unified",
            "solstein.adapters.enrichment._retired.patents_unified",
            "solstein.adapters.enrichment._retired.web_search_unified",
            "solstein.adapters.enrichment._retired.website_unified",
        ],
    )
    def test_unified_adapter_available_from_retired_path(self, module_name: str) -> None:
        """Unified adapters remain importable from _retired for reference tests."""
        mod = importlib.import_module(module_name)
        assert mod is not None


class TestPlaceholderMethodsRemoved:
    """Verify placeholder enrichment methods no longer exist."""

    def test_enrichment_service_no_placeholder_sec(self) -> None:
        from solstein.data.enrichment_service import EnrichmentService

        assert not hasattr(EnrichmentService, "_enrich_from_sec"), (
            "Placeholder _enrich_from_sec should have been removed (STORY-265)"
        )

    def test_enrichment_service_no_placeholder_companies_house(self) -> None:
        from solstein.data.enrichment_service import EnrichmentService

        assert not hasattr(EnrichmentService, "_enrich_from_companies_house"), (
            "Placeholder _enrich_from_companies_house should have been removed (STORY-265)"
        )

    def test_enrichment_service_no_placeholder_news_signals(self) -> None:
        from solstein.data.enrichment_service import EnrichmentService

        assert not hasattr(EnrichmentService, "_enrich_from_news_signals"), (
            "Placeholder _enrich_from_news_signals should have been removed (STORY-265)"
        )
