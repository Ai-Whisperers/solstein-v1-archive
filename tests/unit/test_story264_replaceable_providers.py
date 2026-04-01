"""STORY-264: Verify replaceable providers removed from canonical runtime.

Acceptance criteria:
1. Deprecated/replaceable provider surfaces removed from canonical runtime
2. Registry construction updated (no NewsAPI, no Exa)
3. Tests prove canonical path works without replaceable providers
4. Retained exceptions documented with rationale
"""

import importlib

import pytest

from solstein.adapters.registry import build_default_registry
from solstein.config import Settings

# -- Registry construction: replaceable providers excluded --


class TestReplaceableProvidersExcluded:
    """Verify replaceable providers are NOT in the canonical registry."""

    def test_no_newsapi_enrichment_without_key(self) -> None:
        """NewsEnrichment must not appear even with default settings."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "NewsEnrichment" not in names

    def test_no_newsapi_enrichment_with_key(self) -> None:
        """NewsEnrichment must not appear even when news_api_key is set."""
        registry = build_default_registry(Settings(news_api_key="test_key"))
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "NewsEnrichment" not in names

    def test_no_exa_enrichment_without_key(self) -> None:
        """WebSearchNewsEnrichment must not appear with default settings."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "WebSearchNewsEnrichment" not in names

    def test_no_exa_enrichment_with_key(self) -> None:
        """WebSearchNewsEnrichment must not appear even when exa_api_key is set."""
        registry = build_default_registry(Settings(exa_api_key="test_key"))
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "WebSearchNewsEnrichment" not in names

    def test_no_exa_discovery_without_key(self) -> None:
        """WebSearchDiscoverySource must not appear with default settings."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.discovery_sources}
        assert "WebSearchDiscoverySource" not in names

    def test_no_exa_discovery_with_key(self) -> None:
        """WebSearchDiscoverySource must not appear even when exa_api_key is set."""
        registry = build_default_registry(Settings(exa_api_key="test_key"))
        names = {s.__class__.__name__ for s in registry.discovery_sources}
        assert "WebSearchDiscoverySource" not in names


# -- Retained providers: documented justification --


class TestRetainedProvidersWithJustification:
    """Verify retained providers are still in the canonical registry."""

    def test_yahoo_finance_retained(self) -> None:
        """YahooFinanceEnrichment retained: sole financial data source."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "YahooFinanceEnrichment" in names

    def test_global_market_retained(self) -> None:
        """GlobalMarketEnrichment retained: no-key-needed market data."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "GlobalMarketEnrichment" in names

    def test_funding_retained_with_key(self) -> None:
        """FundingEnrichment retained: Crunchbase non-negotiable for privates."""
        registry = build_default_registry(Settings(crunchbase_api_key="test_key"))
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "FundingEnrichment" in names

    def test_linkedin_retained(self) -> None:
        """LinkedInEnrichment retained: news_api_key is internal fallback."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "LinkedInEnrichment" in names

    def test_website_retained(self) -> None:
        """WebsiteEnrichment retained: no external API dependency."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "WebsiteEnrichment" in names

    def test_patent_retained(self) -> None:
        """PatentEnrichment retained: PatentsView is government-backed, free."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        assert "PatentEnrichment" in names


# -- Module import paths: retired adapters moved --


class TestRetiredImportPaths:
    """Verify retired adapters are not importable from active paths."""

    @pytest.mark.parametrize(
        "module_path",
        [
            "solstein.adapters.enrichment.news",
            "solstein.adapters.enrichment.web_search_news",
            "solstein.adapters.discovery.web_search",
        ],
    )
    def test_active_path_import_fails(self, module_path: str) -> None:
        """Replaceable adapter must not be importable from active package."""
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(module_path)

    @pytest.mark.parametrize(
        "module_path",
        [
            "solstein.adapters.enrichment._retired.news",
            "solstein.adapters.enrichment._retired.web_search_news",
            "solstein.adapters.discovery._retired.web_search",
        ],
    )
    def test_retired_path_import_succeeds(self, module_path: str) -> None:
        """Retired adapters remain available from _retired path for reference."""
        mod = importlib.import_module(module_path)
        assert mod is not None


# -- Canonical registry completeness --


class TestCanonicalRegistryCompleteness:
    """Verify the canonical registry has exactly the expected adapter set."""

    def test_default_enrichment_count(self) -> None:
        """Default settings (no API keys) produce exactly 5 enrichment adapters."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        expected = {
            "YahooFinanceEnrichment",
            "GlobalMarketEnrichment",
            "PatentEnrichment",
            "LinkedInEnrichment",
            "WebsiteEnrichment",
        }
        assert names == expected

    def test_default_discovery_count(self) -> None:
        """Default settings produce exactly 2 discovery sources."""
        registry = build_default_registry(Settings())
        names = {s.__class__.__name__ for s in registry.discovery_sources}
        expected = {
            "StaticCatalogSource",
            "CompetitorJsonSource",
        }
        assert names == expected

    def test_full_keys_enrichment_count(self) -> None:
        """All API keys set produces exactly 6 enrichment adapters (no NewsAPI/Exa)."""
        registry = build_default_registry(
            Settings(
                news_api_key="test",
                crunchbase_api_key="test",
                exa_api_key="test",
            )
        )
        names = {s.__class__.__name__ for s in registry.enrichment_sources}
        expected = {
            "YahooFinanceEnrichment",
            "GlobalMarketEnrichment",
            "PatentEnrichment",
            "LinkedInEnrichment",
            "WebsiteEnrichment",
            "FundingEnrichment",
        }
        assert names == expected
