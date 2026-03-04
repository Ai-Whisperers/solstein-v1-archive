"""Identifier lookup service for connector enrichment."""


class IdentifierLookupService:
    """Look up company identifiers (ticker, company_number, isin, geography)."""

    def __init__(self):
        """Initialize the lookup service."""
        pass

    def lookup_ticker(self, company_name: str) -> str | None:
        """
        Look up US stock ticker for a company by name.

        Args:
            company_name: Name of the company (e.g., "Apple Inc")

        Returns:
            Ticker symbol (e.g., "AAPL") or None if not found.
        """
        return None  # Stub - will be implemented in Phase 5

    def lookup_company_number(self, company_name: str) -> str | None:
        """
        Look up UK Companies House registration number.

        Args:
            company_name: Name of the company

        Returns:
            Company number (e.g., "01234567") or None if not found.
        """
        return None  # Stub - will be implemented in Phase 5

    def infer_geography(self, company_name: str, headquarters: str | None = None) -> str | None:
        """
        Infer company geography (US, UK, EU, etc) from name/HQ.

        Args:
            company_name: Name of the company
            headquarters: Headquarters location (e.g., "San Francisco, USA")

        Returns:
            Geography code (e.g., "US", "UK", "EU") or None if indeterminate.
        """
        return None  # Stub - will be implemented in Phase 5
