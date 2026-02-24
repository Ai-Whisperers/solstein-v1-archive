"""Central registry for data source adapters.

The registry collects DiscoverySource and EnrichmentSource adapters
and provides them to the pipeline stages.  ``build_default_registry``
constructs a registry with all available sources based on the current
Settings (API keys present → adapter registered).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from solstein.adapters.protocols import (
    DiscoverySource,
    EnrichmentSource,
)
from solstein.config import Settings


@dataclass
class SourceRegistry:
    """Central registry for all data source adapters."""

    _discovery_sources: list[DiscoverySource] = field(default_factory=list)
    _enrichment_sources: list[EnrichmentSource] = field(default_factory=list)

    def register_discovery(self, source: DiscoverySource) -> None:
        self._discovery_sources.append(source)

    def register_enrichment(self, source: EnrichmentSource) -> None:
        self._enrichment_sources.append(source)

    @property
    def discovery_sources(self) -> list[DiscoverySource]:
        return list(self._discovery_sources)

    @property
    def enrichment_sources(self) -> list[EnrichmentSource]:
        return list(self._enrichment_sources)


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

    registry = SourceRegistry()

    # Always available — no external API keys needed
    registry.register_discovery(StaticCatalogSource())
    registry.register_discovery(CompetitorJsonSource())

    # Conditional on API keys being configured
    # (adapters added in Phase 2 will plug in here)

    return registry
