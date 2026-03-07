"""Enrichment models for Solstein."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone

from ...domain.models import ConfidenceLevel
from ..source_policy import SourceTier, default_source_policy_catalog
from ..enrichment_types import EnrichableCompany

logger = logging.getLogger(__name__)


class EnrichmentSource(str, Enum):
    """Available enrichment sources."""

    SEC_EDGAR = "SEC_EDGAR"
    COMPANIES_HOUSE = "COMPANIES_HOUSE"
    NEWS_SIGNALS = "NEWS_SIGNALS"


class EnrichmentField(str, Enum):
    """Fields that can be enriched."""

    REVENUE = "revenue"
    GROWTH_RATE = "growth_rate"
    EMPLOYEES = "employees"
    PROFIT_MARGIN = "profit_margin"
    COMPANY_NUMBER = "company_number"
    ISIN = "isin"
    GEOGRAPHY_CODE = "geography_code"
    NEWS_SIGNALS = "news_signals"


@dataclass
class EnrichmentCost:
    """Track cost of enrichment operations."""

    source: EnrichmentSource
    field: EnrichmentField
    api_calls: int = 0
    duration_ms: float = 0.0
    success: bool = False
    error: Optional[str] = None
    timestamp: datetime = dataclass_field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EnrichmentResult:
    """Result of enrichment operation."""

    company: "EnrichableCompany"
    sources_used: List[EnrichmentSource] = dataclass_field(default_factory=list)
    fields_enriched: List[EnrichmentField] = dataclass_field(default_factory=list)
    costs: List[EnrichmentCost] = dataclass_field(default_factory=list)
    errors: List[str] = dataclass_field(default_factory=list)
    total_api_calls: int = 0
    total_duration_ms: float = 0.0
    idempotent: bool = True  # Same input = same output on retries


@dataclass
class EnrichmentConfig:
    """Configuration for enrichment behavior."""

    # Enrichment control
    enabled: bool = True
    dry_run: bool = False

    # Source configuration
    source_order: List[EnrichmentSource] = dataclass_field(
        default_factory=lambda: [
            EnrichmentSource.SEC_EDGAR,
            EnrichmentSource.COMPANIES_HOUSE,
            EnrichmentSource.NEWS_SIGNALS,
        ]
    )
    enabled_sources: Set[EnrichmentSource] = dataclass_field(
        default_factory=lambda: {
            EnrichmentSource.SEC_EDGAR,
            EnrichmentSource.COMPANIES_HOUSE,
            EnrichmentSource.NEWS_SIGNALS,
        }
    )

    # Field selection
    fields_to_enrich: Optional[Set[EnrichmentField]] = None  # None = all fields

    # Confidence thresholds
    min_confidence_to_overwrite: ConfidenceLevel = ConfidenceLevel.ESTIMATED

    # Retry and timeout
    max_retries: int = 3
    timeout_seconds: int = 30

    # Batch processing
    batch_size: int = 10

    # Cancellation
    cancel_requested: bool = False

    def is_source_enabled(self, source: EnrichmentSource) -> bool:
        """Check if source is enabled."""
        return source in self.enabled_sources

    def should_enrich_field(self, field: EnrichmentField) -> bool:
        """Check if field should be enriched."""
        if self.fields_to_enrich is None:
            return True
        return field in self.fields_to_enrich
