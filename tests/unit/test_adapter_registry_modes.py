"""STORY-256 / STORY-264: Registry uses the canonical legacy enrichment path
with replaceable provider surfaces removed.

STORY-256: ``feature_new_unified_loader`` branching removed.
STORY-264: Replaceable providers (NewsAPI, Exa) removed from build path.
"""

from solstein.adapters.registry import build_default_registry
from solstein.config import Settings


def _enrichment_class_names(settings: Settings) -> set[str]:
    registry = build_default_registry(settings)
    return {source.__class__.__name__ for source in registry.enrichment_sources}


def test_registry_canonical_path_registers_legacy_adapters() -> None:
    """Default settings produce legacy enrichment adapters."""
    names = _enrichment_class_names(Settings())

    assert "LinkedInEnrichment" in names
    assert "WebsiteEnrichment" in names
    assert "PatentEnrichment" in names
    # Unified adapters must NOT appear in the canonical registry
    assert "LinkedInUnifiedAdapter" not in names
    assert "WebsiteUnifiedAdapter" not in names
    assert "PatentsUnifiedAdapter" not in names


def test_registry_ignores_deprecated_unified_loader_flag() -> None:
    """Setting feature_new_unified_loader=True no longer changes enrichment set.

    STORY-256: The flag is deprecated and the registry always uses the
    legacy path.
    """
    names = _enrichment_class_names(Settings(feature_new_unified_loader=True))

    # Same adapters as default — flag is ignored
    assert "LinkedInEnrichment" in names
    assert "WebsiteEnrichment" in names
    assert "PatentEnrichment" in names
    assert "LinkedInUnifiedAdapter" not in names
    assert "WebsiteUnifiedAdapter" not in names
    assert "PatentsUnifiedAdapter" not in names


def test_registry_always_registers_discovery_sources() -> None:
    """Static discovery sources are always registered."""
    registry = build_default_registry(Settings())
    discovery_names = {s.__class__.__name__ for s in registry.discovery_sources}

    assert "StaticCatalogSource" in discovery_names
    assert "CompetitorJsonSource" in discovery_names


def test_registry_always_registers_base_enrichment() -> None:
    """YahooFinance and GlobalMarket enrichment are always registered."""
    names = _enrichment_class_names(Settings())

    assert "YahooFinanceEnrichment" in names
    assert "GlobalMarketEnrichment" in names


# -- STORY-264: Replaceable providers removed from canonical build path --


def test_registry_excludes_newsapi_enrichment() -> None:
    """STORY-264: NewsEnrichment (NewsAPI) no longer registered even with key."""
    names = _enrichment_class_names(Settings(news_api_key="test_key"))
    assert "NewsEnrichment" not in names


def test_registry_excludes_exa_enrichment() -> None:
    """STORY-264: WebSearchNewsEnrichment (Exa) no longer registered even with key."""
    names = _enrichment_class_names(Settings(exa_api_key="test_key"))
    assert "WebSearchNewsEnrichment" not in names


def test_registry_excludes_exa_discovery() -> None:
    """STORY-264: WebSearchDiscoverySource (Exa) no longer registered even with key."""
    registry = build_default_registry(Settings(exa_api_key="test_key"))
    discovery_names = {s.__class__.__name__ for s in registry.discovery_sources}
    assert "WebSearchDiscoverySource" not in discovery_names


def test_registry_retains_yahoo_finance_with_justification() -> None:
    """STORY-264: YahooFinanceEnrichment retained — sole financial data source."""
    names = _enrichment_class_names(Settings())
    assert "YahooFinanceEnrichment" in names


def test_registry_retains_funding_enrichment() -> None:
    """STORY-264: FundingEnrichment (Crunchbase) retained — non-negotiable for privates."""
    names = _enrichment_class_names(Settings(crunchbase_api_key="test_key"))
    assert "FundingEnrichment" in names
