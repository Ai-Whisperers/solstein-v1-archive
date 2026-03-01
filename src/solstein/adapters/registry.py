"""Central registry for data source adapters.

The registry collects DiscoverySource, EnrichmentSource, and
UnifiedDataSource adapters and provides them to the pipeline stages.
``build_default_registry`` constructs a registry with all available
sources based on the current Settings (API keys present → adapter registered).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from solstein.adapters.protocols import (
    DiscoverySource,
    EnrichmentSource,
    UnifiedDataSource,
)
from solstein.config import Settings


@dataclass
class SourceRegistry:
    """Central registry for all data source adapters."""

    _discovery_sources: list[DiscoverySource] = field(default_factory=list)
    _enrichment_sources: list[EnrichmentSource] = field(default_factory=list)
    _unified_sources: list[UnifiedDataSource] = field(default_factory=list)

    def register_discovery(self, source: DiscoverySource) -> None:
        self._discovery_sources.append(source)

    def register_enrichment(self, source: EnrichmentSource) -> None:
        self._enrichment_sources.append(source)

    def register_unified(self, source: UnifiedDataSource) -> None:
        """Register a full UnifiedDataSource adapter (discover+enrich+refresh)."""
        self._unified_sources.append(source)

    @property
    def discovery_sources(self) -> list[DiscoverySource]:
        return list(self._discovery_sources)

    @property
    def enrichment_sources(self) -> list[EnrichmentSource]:
        return list(self._enrichment_sources)

    @property
    def unified_sources(self) -> list[UnifiedDataSource]:
        """All registered UnifiedDataSource adapters."""
        return list(self._unified_sources)

    @property
    def all_enrichment_sources(self) -> list[EnrichmentSource]:
        """Combined legacy + unified enrichment sources.

        UnifiedDataSource structurally satisfies EnrichmentSource so the
        unified adapters are exposed here for backwards-compatible pipeline use.
        """
        combined: list[EnrichmentSource] = list(self._enrichment_sources)
        combined.extend(self._unified_sources)  # type: ignore[arg-type]
        return combined


def build_default_registry(settings: Settings) -> SourceRegistry:
    """Build a registry with all available sources based on config.

    Sources that require API keys are only registered when the
    corresponding key is present in *settings*.  Sources that work
    without external credentials (static catalog, competitor JSON,
    Yahoo Finance) are always registered.
    """
    # Import adapters lazily so the registry module itself stays
    # lightweight and testable without requiring every dependency.
    from solstein.adapters.discovery.competitor_json import CompetitorJsonSource
    from solstein.adapters.discovery.static_catalog import StaticCatalogSource
    from solstein.adapters.enrichment.patents import PatentEnrichment
    from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment

    registry = SourceRegistry()

    # -- Discovery: always available --
    registry.register_discovery(StaticCatalogSource())
    registry.register_discovery(CompetitorJsonSource())

    # -- Enrichment: always available (no API key needed) --
    registry.register_enrichment(YahooFinanceEnrichment())
    registry.register_enrichment(PatentEnrichment())

    # -- Enrichment: conditional on API keys --
    if settings.news_api_key:
        from solstein.adapters.enrichment.news import NewsEnrichment

        registry.register_enrichment(NewsEnrichment(news_api_key=settings.news_api_key))

    if settings.crunchbase_api_key:
        from solstein.adapters.enrichment.funding import FundingEnrichment

        registry.register_enrichment(
            FundingEnrichment(
                crunchbase_api_key=settings.crunchbase_api_key,
                news_api_key=settings.news_api_key,
            )
        )

    if settings.exa_api_key:
        from solstein.adapters.discovery.web_search import WebSearchDiscoverySource
        from solstein.adapters.enrichment.web_search_news import WebSearchNewsEnrichment

        registry.register_discovery(WebSearchDiscoverySource(exa_api_key=settings.exa_api_key))
        registry.register_enrichment(WebSearchNewsEnrichment())

    # LinkedIn and website enrichment are always available but lower quality
    from solstein.adapters.enrichment.linkedin import LinkedInEnrichment
    from solstein.adapters.enrichment.website import WebsiteEnrichment

    registry.register_enrichment(LinkedInEnrichment(news_api_key=settings.news_api_key))
    registry.register_enrichment(WebsiteEnrichment())

    # GlobalMarketEnrichment provides currency-normalized market data
    from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment

    registry.register_enrichment(GlobalMarketEnrichment())

    # Unified adapters — satisfy the full UnifiedDataSource protocol
    # (discover + enrich + refresh) and are also exposed via all_enrichment_sources.
    from solstein.adapters.enrichment.funding_unified import FundingUnifiedAdapter
    from solstein.adapters.enrichment.linkedin_unified import LinkedInUnifiedAdapter
    from solstein.adapters.enrichment.news_unified import NewsUnifiedAdapter
    from solstein.adapters.enrichment.patents_unified import PatentsUnifiedAdapter
    from solstein.adapters.enrichment.web_search_unified import WebSearchUnifiedAdapter
    from solstein.adapters.enrichment.website_unified import WebsiteUnifiedAdapter

    registry.register_enrichment(WebSearchUnifiedAdapter())
    registry.register_enrichment(NewsUnifiedAdapter(news_api_key=settings.news_api_key))
    registry.register_enrichment(FundingUnifiedAdapter(crunchbase_api_key=settings.crunchbase_api_key))
    registry.register_enrichment(LinkedInUnifiedAdapter(news_api_key=settings.news_api_key))
    registry.register_enrichment(WebsiteUnifiedAdapter())
    registry.register_enrichment(PatentsUnifiedAdapter())

    return registry
