"""OpenCorporates lookup strategy.

EPIC-022: Extracted from IdentifierLookupService for modularity.
"""

import os
from typing import Any

import requests
from loguru import logger

from .base import LookupStrategy


class OpenCorporatesStrategy(LookupStrategy):
    """Lookup company identifiers via OpenCorporates API."""

    def __init__(self) -> None:
        self._api_key = os.getenv("OPENCORPORATES_API_KEY")

    @property
    def name(self) -> str:
        return "opencorporates"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    async def lookup(self, company_name: str) -> dict[str, Any]:
        """Lookup company via OpenCorporates API.

        Args:
            company_name: Company name to search

        Returns:
            Dictionary with company_number, jurisdiction, legal_name
        """
        if not self.is_available:
            return {}

        params = {
            "q": company_name,
            "api_token": self._api_key,
            "per_page": 3,
        }

        try:
            response = requests.get(
                "https://api.opencorporates.com/v0.4/companies/search",
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("OpenCorporates lookup failed", company=company_name, error=str(exc))
            return {}

        companies_block = payload.get("results", {}).get("companies", []) if isinstance(payload, dict) else []
        if not companies_block:
            return {}

        first = companies_block[0]
        company_data = first.get("company", {}) if isinstance(first, dict) else {}
        company_number = company_data.get("company_number")
        jurisdiction = company_data.get("jurisdiction_code")
        legal_name = company_data.get("name")

        if not isinstance(company_number, str) or not company_number:
            return {}

        return {
            "company_number": company_number,
            "jurisdiction": jurisdiction if isinstance(jurisdiction, str) else None,
            "legal_name": legal_name if isinstance(legal_name, str) else None,
            "opencorporates_confidence": 0.9,
            "opencorporates_source": "opencorporates",
        }
