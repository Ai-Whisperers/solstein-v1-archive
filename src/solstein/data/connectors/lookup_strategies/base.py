"""Base classes for identifier lookup strategies.

EPIC-022: Extracted from IdentifierLookupService for modularity.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class LookupStrategy(ABC):
    """Base class for identifier lookup strategies.

    Each lookup provider (OpenCorporates, OpenFIGI, DuckDuckGo)
    implements its own strategy for finding identifiers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this lookup strategy."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this strategy is available (API keys, dependencies)."""
        pass

    @abstractmethod
    async def lookup(self, company_name: str) -> dict[str, Any]:
        """Lookup identifiers for a company.

        Args:
            company_name: Company name to lookup

        Returns:
            Dictionary of found identifiers with confidence scores
        """
        pass
