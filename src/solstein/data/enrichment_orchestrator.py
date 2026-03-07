"""Phase 4: Enrichment Logic Orchestrator.

⚠️ DEPRECATED: This module has been split into solstein.data.enrichment package.
For new code, use: from solstein.data.enrichment import EnrichmentOrchestrator, EnrichmentConfig

This file is kept for backward compatibility and re-exports all symbols.
"""

from __future__ import annotations

# Re-export everything from the new modular package
from solstein.data.enrichment import (
    EnrichmentConfig,
    EnrichmentCost,
    EnrichmentField,
    EnrichmentOrchestrator,
    EnrichmentResult,
    EnrichmentSource,
)

__all__ = [
    "EnrichmentConfig",
    "EnrichmentCost",
    "EnrichmentField",
    "EnrichmentOrchestrator",
    "EnrichmentResult",
    "EnrichmentSource",
]
