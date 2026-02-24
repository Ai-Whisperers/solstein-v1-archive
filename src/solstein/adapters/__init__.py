"""Adapter layer for pluggable data sources."""

from .protocols import DiscoverySource, EnrichmentSource, FactAggregator
from .registry import SourceRegistry, build_default_registry

__all__ = [
    "DiscoverySource",
    "EnrichmentSource",
    "FactAggregator",
    "SourceRegistry",
    "build_default_registry",
]
