"""
Repositories implementation for data access.
"""

from pathlib import Path

from loguru import logger

from ..config import get_settings
from ..core.repositories import CompanyRepository
from ..data.loaders import CompetitorDataLoader
from ..domain.models import Company, FinancialMetric


class JsonFileRepository(CompanyRepository):
    """
    Repository implementation that reads from JSON files.
    """

    def __init__(self, data_dir: Path | None = None):
        self.settings = get_settings()
        self.data_dir = data_dir or self.settings.data.data_dir
        self._loader = CompetitorDataLoader(data_dir=self.data_dir)

    def _to_domain(self, pydantic_model) -> Company:
        """Helper to convert legacy Pydantic model to Domain Entity."""
        # This is a bit ugly, but necessary during migration
        # In a real DB repo, this would map SQL Alchemy -> Domain
        data = pydantic_model.model_dump()

        # Convert financials dict to FinancialMetric domain object
        fin_data = data.pop('financials', {})
        financials = FinancialMetric(**fin_data)

        # Create domain object
        return Company(financials=financials, **data)

    def get_all(self, limit: int | None = None, filters: dict | None = None) -> list[Company]:
        """Retrieve all companies from JSON storage."""
        # Load Pydantic models
        pydantic_companies = self._loader.load_companies(limit=limit)

        # Convert to Domain
        companies = [self._to_domain(c) for c in pydantic_companies]

        if not filters:
            return companies

        # Apply filtering (Repository should handle this, not the Controller/API)
        filtered_results = []
        for company in companies:
            match = True

            # Tier filter
            if filters.get("tier") and company.tier != filters["tier"]:
                match = False

            # Industry filter
            if filters.get("industry") and filters["industry"].lower() not in company.industry.lower():
                match = False

            # Revenue filter
            if filters.get("min_revenue") and (not company.financials.revenue or company.financials.revenue < filters["min_revenue"]):
                match = False

            if match:
                filtered_results.append(company)

        return filtered_results

    def get_by_id(self, company_id: str) -> Company | None:
        """Retrieve a company by ID."""
        pydantic_companies = self._loader.load_companies()
        for c in pydantic_companies:
            if c.id == company_id:
                return self._to_domain(c)
        return None

    def save(self, company: Company) -> Company:
        """
        Save a company profile.
        """
        logger.warning("JsonFileRepository.save() is not fully implemented.")
        return company
