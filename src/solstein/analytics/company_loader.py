"""
Task 5: Company Loader with Unified Data

Ensures companies are loaded with merged JSON + Markdown data before scoring.
This fixes the revenue per employee bug by using unified financials.
"""

import logging

from ..data.unified_loader import UnifiedCompanyLoader
from ..domain.models import Company

logger = logging.getLogger(__name__)


class UnifiedCompanyScoreLoader:
    """Loads companies with unified data for scoring."""

    def __init__(self):
        """Initialize with unified loader."""
        self.unified_loader = UnifiedCompanyLoader()
        self._unified_companies_cache: dict[str, Company] | None = None

    def load_company_for_scoring(self, company_id: str) -> Company | None:
        """
        Load a company with unified data for scoring.

        Args:
            company_id: Company ID to load

        Returns:
            Company with merged JSON + Markdown data, or None if not found
        """
        # Load all unified companies (cached)
        if self._unified_companies_cache is None:
            self._load_unified_companies()

        if self._unified_companies_cache is None:
            return None

        company = self._unified_companies_cache.get(company_id)
        if company:
            logger.debug(f"Loaded unified company for scoring: {company_id}")
        else:
            logger.warning(f"Company not found in unified data: {company_id}")

        return company

    def _load_unified_companies(self):
        """Load all unified companies and cache them."""
        try:
            unified_companies = self.unified_loader.load_unified_companies()
            self._unified_companies_cache = {c.id: c for c in unified_companies}
            logger.info(f"Loaded {len(self._unified_companies_cache)} unified companies for scoring")
        except Exception as e:
            logger.error(f"Failed to load unified companies: {e}")
            self._unified_companies_cache = {}

    def clear_cache(self):
        """Clear the unified companies cache."""
        self._unified_companies_cache = None
        logger.debug("Cleared unified companies cache")


# Global instance
unified_score_loader = UnifiedCompanyScoreLoader()
