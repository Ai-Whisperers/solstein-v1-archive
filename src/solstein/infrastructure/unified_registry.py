"""Unified registry for data source adapters and refresh connectors.

Combines Gestalt's adapter registry with Nyx's refresh connectors
for a unified data source management system.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from solstein.adapters.protocols import (
    DiscoverySource,
    EnrichmentSource,
    UnifiedDataSource,
)
from solstein.config import Settings
from solstein.infrastructure.refresh import BaseRefreshConnector


@dataclass
class UnifiedRegistry:
    """Central registry for all data sources including adapters and refresh connectors.

    This registry unifies Gestalt's adapter architecture with Nyx's refresh
    connector pattern, providing a single interface for managing all data
    sources in the Solstein system.

    Features:
    - Register adapters (DiscoverySource, EnrichmentSource)
    - Register refresh connectors (BaseRefreshConnector)
    - Retrieve by source name
    - List all registered sources
    - Backward compatible with existing SourceRegistry
    """

    _adapters: dict[str, UnifiedDataSource] = field(default_factory=dict)
    _refresh_connectors: dict[str, BaseRefreshConnector] = field(default_factory=dict)
    _discovery_sources: list[DiscoverySource] = field(default_factory=list)
    _enrichment_sources: list[EnrichmentSource] = field(default_factory=list)

    def register_adapter(self, adapter: UnifiedDataSource) -> None:
        """Register an adapter that implements UnifiedDataSource protocol.

        Args:
            adapter: An adapter implementing UnifiedDataSource protocol
        """
        source_name = adapter.source_name
        self._adapters[source_name] = adapter

        # Also register in legacy lists for backward compatibility
        if hasattr(adapter, "discover") and adapter.supports_discovery():
            self._discovery_sources.append(adapter)  # type: ignore

        if hasattr(adapter, "enrich"):
            self._enrichment_sources.append(adapter)  # type: ignore

    def register_refresh_connector(self, source_name: str, connector: BaseRefreshConnector) -> None:
        """Register a refresh connector for a data source.

        Args:
            source_name: Name of the data source
            connector: Refresh connector instance
        """
        self._refresh_connectors[source_name] = connector

    def get_adapter(self, source_name: str) -> UnifiedDataSource | None:
        """Get adapter by source name.

        Args:
            source_name: Name of the data source

        Returns:
            Adapter instance or None if not found
        """
        return self._adapters.get(source_name)

    def get_refresh_connector(self, source_name: str) -> BaseRefreshConnector | None:
        """Get refresh connector by source name.

        Args:
            source_name: Name of the data source

        Returns:
            Refresh connector instance or None if not found
        """
        return self._refresh_connectors.get(source_name)

    def list_sources(self) -> list[str]:
        """List all registered source names.

        Returns:
            List of source names from both adapters and refresh connectors
        """
        sources = set(self._adapters.keys())
        sources.update(self._refresh_connectors.keys())
        return sorted(list(sources))

    def list_adapters(self) -> list[str]:
        """List all registered adapter source names.

        Returns:
            List of adapter source names
        """
        return sorted(list(self._adapters.keys()))

    def list_refresh_connectors(self) -> list[str]:
        """List all registered refresh connector source names.

        Returns:
            List of refresh connector source names
        """
        return sorted(list(self._refresh_connectors.keys()))

    @property
    def discovery_sources(self) -> list[DiscoverySource]:
        """Get discovery sources (backward compatibility).

        Returns:
            List of DiscoverySource adapters
        """
        return list(self._discovery_sources)

    @property
    def enrichment_sources(self) -> list[EnrichmentSource]:
        """Get enrichment sources (backward compatibility).

        Returns:
            List of EnrichmentSource adapters
        """
        return list(self._enrichment_sources)

    def has_refresh_connector(self, source_name: str) -> bool:
        """Check if a refresh connector exists for a source.

        Args:
            source_name: Name of the data source

        Returns:
            True if refresh connector exists
        """
        return source_name in self._refresh_connectors

    def has_adapter(self, source_name: str) -> bool:
        """Check if an adapter exists for a source.

        Args:
            source_name: Name of the data source

        Returns:
            True if adapter exists
        """
        return source_name in self._adapters


def build_default_registry(settings: Settings) -> UnifiedRegistry:
    """Build a unified registry with all available sources.

    This factory function creates a UnifiedRegistry populated with:
    - All available adapters (discovery and enrichment)
    - All available refresh connectors

    Sources that require API keys are only registered when the
    corresponding key is present in settings.

    Args:
        settings: Application settings

    Returns:
        Configured UnifiedRegistry
    """
    registry = UnifiedRegistry()

    # Import adapters lazily so the registry module itself stays
    # lightweight and testable without requiring every dependency.
    from solstein.adapters.discovery.competitor_json import CompetitorJsonSource
    from solstein.adapters.discovery.static_catalog import StaticCatalogSource
    from solstein.adapters.enrichment.global_market import GlobalMarketEnrichment
    from solstein.adapters.enrichment.linkedin import LinkedInEnrichment
    from solstein.adapters.enrichment.patents import PatentEnrichment
    from solstein.adapters.enrichment.website import WebsiteEnrichment
    from solstein.adapters.enrichment.yahoo_finance import YahooFinanceEnrichment

    # -- Discovery: always available --
    registry.register_adapter(StaticCatalogSource())
    registry.register_adapter(CompetitorJsonSource())

    # -- Enrichment: always available (no API key needed) --
    registry.register_adapter(YahooFinanceEnrichment())
    registry.register_adapter(PatentEnrichment())
    registry.register_adapter(WebsiteEnrichment())
    registry.register_adapter(LinkedInEnrichment(news_api_key=settings.news_api_key))
    registry.register_adapter(GlobalMarketEnrichment())

    # -- Enrichment: conditional on API keys --
    # STORY-264: NewsEnrichment (NewsAPI) and WebSearchNewsEnrichment (Exa)
    # removed — replaceable by GDELT and SearXNG respectively.
    # WebSearchDiscoverySource (Exa) also removed.
    # Adapters moved to adapters/{enrichment,discovery}/_retired/.

    if settings.crunchbase_api_key:
        from solstein.adapters.enrichment.funding import FundingEnrichment

        registry.register_adapter(
            FundingEnrichment(
                crunchbase_api_key=settings.crunchbase_api_key,
                news_api_key=settings.news_api_key,
            )
        )

    # -- Refresh Connectors: will be added in subsequent tasks --
    # These will be registered as they are implemented:
    # - YahooFinanceRefreshConnector
    # - PatentRefreshConnector
    # - NewsRefreshConnector
    # - etc.

    return registry


# Global registry instance (initialized lazily)
_global_registry: UnifiedRegistry | None = None


def get_registry(settings: Settings | None = None) -> UnifiedRegistry:
    """Get the global unified registry instance.

    Args:
        settings: Optional settings to use for initialization

    Returns:
        UnifiedRegistry instance
    """
    global _global_registry

    if _global_registry is None:
        if settings is None:
            from solstein.config import get_settings

            settings = get_settings()
        _global_registry = build_default_registry(settings)

    return _global_registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _global_registry
    _global_registry = None
