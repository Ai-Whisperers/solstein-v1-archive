"""Base class for enrichment strategies.

EPIC-022: Extracted from EnrichmentOrchestrator for modularity.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..models import EnrichmentResult, EnrichmentSource


class EnrichmentStrategy(ABC):
    """Base class for enrichment strategies.

    Each enrichment source (SEC EDGAR, Companies House, etc.)
    implements its own strategy for enriching company data.
    """

    def __init__(self, source: EnrichmentSource) -> None:
        self.source = source

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this enrichment strategy."""
        pass

    @abstractmethod
    def can_enrich(self, company: "EnrichableCompany") -> bool:
        """Check if this strategy can enrich the given company.

        Args:
            company: Company to potentially enrich

        Returns:
            True if strategy can enrich this company
        """
        pass

    @abstractmethod
    async def enrich(self, company: "EnrichableCompany") -> EnrichmentResult:
        """Execute enrichment for the company.

        Args:
            company: Company to enrich

        Returns:
            Enrichment result
        """
        pass
