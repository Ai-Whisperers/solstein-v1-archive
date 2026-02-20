"""
Core repository interfaces.

Defines the contract for data access, allowing us to swap implementations (JSON -> SQL).
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any

from ..domain.models import Company, CompanyTier


@dataclass
class CompanyFilter:
    """Type-safe filters for company queries."""

    tier: CompanyTier | None = None
    industry: str | None = None
    min_revenue: float | None = None


class CompanyRepository(ABC):
    """Abstract interface for Company data access."""

    @abstractmethod
    def get_all(
        self, limit: int | None = None, filters: CompanyFilter | None = None
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
