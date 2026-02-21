"""
Core repository interfaces.

Defines the contract for data access, allowing us to swap implementations (JSON -> SQL).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..domain.models import Company, CompanyTier


@dataclass
class CompanyFilter:
    """Type-safe filters for company queries."""

    tier: CompanyTier | None = None
    industry: str | None = None
    min_revenue: float | None = None
    classification: str | None = None
    min_growth_score: float | None = None
    max_growth_score: float | None = None


class CompanyRepository(ABC):
    """Abstract interface for Company data access."""

    @abstractmethod
    def get_all(
        self,
        limit: int | None = None,
        offset: int = 0,
        filters: CompanyFilter | None = None,
    ) -> list[Company]:
        """Retrieve all companies, optionally filtered."""
        pass

    @abstractmethod
    def get_by_id(self, company_id: str) -> Company | None:
        """Retrieve a single company by ID."""
        pass

    @abstractmethod
    def save(self, company: Company) -> Company:
        """Persist a company profile."""
        pass

    @abstractmethod
    def delete(self, company_id: str) -> bool:
        """Remove a company profile."""
        pass

    @abstractmethod
    def search(self, query: str, field: str = "name") -> list[Company]:
        """Search companies by a specific field."""
        pass
