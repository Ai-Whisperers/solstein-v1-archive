"""Central registry for data source adapters.

The registry collects DiscoverySource, EnrichmentSource, and
UnifiedDataSource adapters and provides them to the pipeline stages.
``build_default_registry`` constructs a registry with all available
sources based on the current Settings (API keys present → adapter registered).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from solstein.adapters.protocols import (
    DiscoverySource,
    EnrichmentSource,
    UnifiedDataSource,
)
from solstein.config import Settings


def _empty_object_list() -> list[object]:
    return []


@dataclass
class SourceRegistry:
    """Central registry for all data source adapters."""

    _discovery_sources: list[object] = field(default_factory=_empty_object_list)
    _enrichment_sources: list[object] = field(default_factory=_empty_object_list)
    _unified_sources: list[object] = field(default_factory=_empty_object_list)

    def register_discovery(self, source: DiscoverySource) -> None:
        self._discovery_sources.append(source)

    def register_enrichment(self, source: EnrichmentSource) -> None:
        self._enrichment_sources.append(source)

    def register_unified(self, source: UnifiedDataSource) -> None:
        """Register a full UnifiedDataSource adapter (discover+enrich+refresh)."""
        self._unified_sources.append(source)

    @property
    def discovery_sources(self) -> list[DiscoverySource]:
        return [cast(DiscoverySource, source) for source in self._discovery_sources]

    @property
    def enrichment_sources(self) -> list[EnrichmentSource]:
        return [cast(EnrichmentSource, source) for source in self._enrichment_sources]

    @property
    def unified_sources(self) -> list[UnifiedDataSource]:
        """All registered UnifiedDataSource adapters."""
        return [cast(UnifiedDataSource, source) for source in self._unified_sources]

    @property
    def all_enrichment_sources(self) -> list[EnrichmentSource]:
        """Combined legacy + unified enrichment sources.

        UnifiedDataSource structurally satisfies EnrichmentSource so the
        unified adapters are exposed here for backwards-compatible pipeline use.
        """
        combined = [cast(EnrichmentSource, source) for source in self._enrichment_sources]
        combined.extend(cast(EnrichmentSource, source) for source in self._unified_sources)
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
    from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment
    from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment

    registry = SourceRegistry()

    # -- Discovery: always available --
    registry.register_discovery(StaticCatalogSource())
    registry.register_discovery(CompetitorJsonSource())

    # -- Enrichment: always available (no API key needed) --
    registry.register_enrichment(YahooFinanceEnrichment())
    registry.register_enrichment(GlobalMarketEnrichment())

    use_unified_enrichment = settings.feature_new_unified_loader

    if settings.exa_api_key:
        from solstein.adapters.discovery.web_search import WebSearchDiscoverySource

        registry.register_discovery(WebSearchDiscoverySource(exa_api_key=settings.exa_api_key))

    if use_unified_enrichment:
        from solstein.adapters.enrichment.funding_unified import FundingUnifiedAdapter
        from solstein.adapters.enrichment.linkedin_unified import LinkedInUnifiedAdapter
        from solstein.adapters.enrichment.news_unified import NewsUnifiedAdapter
        from solstein.adapters.enrichment.patents_unified import PatentsUnifiedAdapter
        from solstein.adapters.enrichment.web_search_unified import WebSearchUnifiedAdapter
        from solstein.adapters.enrichment.website_unified import WebsiteUnifiedAdapter

        registry.register_enrichment(PatentsUnifiedAdapter())
        registry.register_enrichment(NewsUnifiedAdapter(news_api_key=settings.news_api_key))
        registry.register_enrichment(FundingUnifiedAdapter(crunchbase_api_key=settings.crunchbase_api_key))
        registry.register_enrichment(LinkedInUnifiedAdapter(news_api_key=settings.news_api_key))
        registry.register_enrichment(WebsiteUnifiedAdapter())
        registry.register_enrichment(WebSearchUnifiedAdapter())
    else:
        from solstein.adapters.enrichment.linkedin import LinkedInEnrichment
        from solstein.adapters.enrichment.patents import PatentEnrichment
        from solstein.adapters.enrichment.website import WebsiteEnrichment

        registry.register_enrichment(PatentEnrichment())

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
            from solstein.adapters.enrichment.web_search_news import WebSearchNewsEnrichment

            registry.register_enrichment(WebSearchNewsEnrichment())

        registry.register_enrichment(LinkedInEnrichment(news_api_key=settings.news_api_key))
        registry.register_enrichment(WebsiteEnrichment())

    return registry
