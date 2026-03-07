"""OpenFIGI lookup strategy.

EPIC-022: Extracted from IdentifierLookupService for modularity.
"""

import os
import re
from typing import Any

import requests
from loguru import logger

from .base import LookupStrategy


class OpenFIGIStrategy(LookupStrategy):
    """Lookup financial identifiers via OpenFIGI API."""

    def __init__(self) -> None:
        self._api_key = os.getenv("OPENFIGI_API_KEY")

    @property
    def name(self) -> str:
        return "openfigi"

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    async def lookup(self, company_name: str) -> dict[str, Any]:
        """Lookup financial identifiers via OpenFIGI API.

        Args:
            company_name: Company name to search

        Returns:
            Dictionary with ticker, company_number, isin, exchange
        """
        if not self.is_available:
            return {}

        headers = {
            "Content-Type": "application/json",
            "X-OPENFIGI-APIKEY": str(self._api_key),
        }
        payload = {"query": company_name}

        try:
            response = requests.post(
                "https://api.openfigi.com/v3/search",
                headers=headers,
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.warning("OpenFIGI lookup failed", company=company_name, error=str(exc))
            return {}

        if not isinstance(data, list) or not data:
            return {}

        first = data[0]
        if not isinstance(first, dict):
            return {}

        ticker = first.get("ticker")
        exch_code = first.get("exchCode")
        security_desc = first.get("securityDescription")

        # Try to infer company number from security description
        inferred_company_number = None
        if isinstance(security_desc, str):
            company_match = re.search(r"\b([0-9]{6,8})\b", security_desc)
            if company_match:
                inferred_company_number = company_match.group(1)

        return {
            "ticker": ticker if isinstance(ticker, str) and ticker else None,
            "company_number": inferred_company_number,
            "isin": first.get("securityID") if isinstance(first.get("securityID"), str) else None,
            "exchange": exch_code if isinstance(exch_code, str) else None,
            "openfigi_confidence": 0.92,
            "openfigi_source": "openfigi",
        }
