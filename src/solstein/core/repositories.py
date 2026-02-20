"""
Core repository interfaces.

Defines the contract for data access, allowing us to swap implementations (JSON -> SQL).
"""

from abc import ABC, abstractmethod

from ..domain.models import Company


class CompanyRepository(ABC):
    """Abstract interface for Company data access."""

    @abstractmethod
    def get_all(self, limit: int | None = None, filters: dict | None = None) -> list[Company]:
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
