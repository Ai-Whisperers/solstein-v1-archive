"""Adapter layer for pluggable data sources."""

from .instrumented import (
    AdapterHealthRecord,
    InstrumentedDiscoverySource,
    InstrumentedEnrichmentSource,
    build_instrumented_registry,
)
from .protocols import DiscoverySource, EnrichmentSource, FactAggregator
from .registry import SourceRegistry, build_default_registry

__all__ = [
    "AdapterHealthRecord",
    "DiscoverySource",
    "EnrichmentSource",
    "FactAggregator",
    "InstrumentedDiscoverySource",
    "InstrumentedEnrichmentSource",
    "SourceRegistry",
    "build_default_registry",
    "build_instrumented_registry",
]
