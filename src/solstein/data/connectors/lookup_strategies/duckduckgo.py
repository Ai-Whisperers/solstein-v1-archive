"""DuckDuckGo lookup strategy.

EPIC-022: Extracted from IdentifierLookupService for modularity.
"""

import asyncio
import importlib
import re
from typing import Any, Optional

from loguru import logger

from .base import LookupStrategy


class DuckDuckGoStrategy(LookupStrategy):
    """Lookup identifiers via DuckDuckGo web search."""

    def __init__(self) -> None:
        self._ddg_available = False
        self._ddg_client: Any = None

        # Try to import DDGS
        try:
            ddgs_module = importlib.import_module("ddgs")
            self._ddg_client = getattr(ddgs_module, "DDGS")
            self._ddg_available = True
        except Exception:
            try:
                ddgs_module = importlib.import_module("duckduckgo_search")
                self._ddg_client = getattr(ddgs_module, "DDGS")
                self._ddg_available = True
            except Exception as exc:
                logger.warning("DDG search client unavailable", error=str(exc))

    @property
    def name(self) -> str:
        return "duckduckgo"

    @property
    def is_available(self) -> bool:
        return self._ddg_available

    def _search_text(self, query: str) -> str:
        """Search and return concatenated text results."""
        if not self._ddg_available:
            return ""
        try:
            with self._ddg_client() as ddgs:
                results = list(ddgs.text(query, max_results=8))
        except Exception as exc:
            logger.warning("Lookup query failed", query=query, error=str(exc))
            return ""
        return " ".join((item.get("title", "") + " " + item.get("body", "")) for item in results)

    async def lookup(self, company_name: str) -> dict[str, Any]:
        """Lookup identifiers via DuckDuckGo search.

        Args:
            company_name: Company name to search

        Returns:
            Dictionary with ticker, company_number, isin
        """
        if not self.is_available:
            return {}

        return await asyncio.to_thread(self._lookup_sync, company_name)

    def _lookup_sync(self, company_name: str) -> dict[str, Any]:
        """Sync implementation of DuckDuckGo lookup (run via to_thread)."""
        result: dict[str, Any] = {}

        # Lookup ticker
        ticker = self._lookup_ticker(company_name)
        if ticker:
            result["ticker"] = ticker
            result["ticker_confidence"] = 0.85
            result["ticker_source"] = "duckduckgo_search"

        # Lookup company number
        company_number = self._lookup_company_number(company_name)
        if company_number:
            result["company_number"] = company_number
            result["company_number_confidence"] = 0.8
            result["company_number_source"] = "duckduckgo_search"

        # Lookup ISIN
        isin = self._lookup_isin(company_name)
        if isin:
            result["isin"] = isin
            result["isin_confidence"] = 0.75
            result["isin_source"] = "duckduckgo_search"

        # Infer geography
        geography = self._infer_geography(company_name)
        if geography:
            result["geography"] = geography
            result["geography_confidence"] = 0.6
            result["geography_source"] = "heuristic"

        return result

    def _lookup_ticker(self, company_name: str) -> Optional[str]:
        """Lookup ticker symbol."""
        text = self._search_text(f"{company_name} ticker symbol")
        if not text:
            return None

        # Try exchange pattern first
        exchange_pattern = re.compile(r"\b(?:NASDAQ|NYSE|AMEX|LSE|OTC)\s*[:\-]\s*([A-Z]{1,6})\b")
        match = exchange_pattern.search(text)
        if match:
            return match.group(1)

        # Try alternative pattern
        alt = re.search(r"\b\(([A-Z]{1,5})\)\s*(?:Stock|NASDAQ|NYSE)\b", text)
        if alt:
            return alt.group(1)

        return None

    def _lookup_company_number(self, company_name: str) -> Optional[str]:
        """Lookup company number."""
        text = self._search_text(f"{company_name} company number Companies House")
        if not text:
            return None

        match = re.search(r"company number\s*([0-9]{6,8})", text, flags=re.IGNORECASE)
        if match:
            return match.group(1)

        generic = re.search(r"\b([0-9]{6,8})\b", text)
        if generic:
            return generic.group(1)

        return None

    def _lookup_isin(self, company_name: str) -> Optional[str]:
        """Lookup ISIN."""
        text = self._search_text(f"{company_name} ISIN")
        if not text:
            return None

        match = re.search(r"\b([A-Z]{2}[A-Z0-9]{9}[0-9])\b", text)
        if match:
            return match.group(1)

        return None

    def _infer_geography(self, company_name: str, headquarters: Optional[str] = None) -> Optional[str]:
        """Infer geography from company name and headquarters."""
        haystack = f"{company_name} {headquarters or ''}".lower()

        if any(token in haystack for token in ["uk", "united kingdom", "london"]):
            return "UK"
        elif any(token in haystack for token in ["us", "united states", "california", "new york"]):
            return "US"
        elif any(token in haystack for token in ["china", "beijing", "shanghai"]):
            return "CN"
        elif any(token in haystack for token in ["india", "bangalore", "delhi"]):
            return "IN"
        elif any(token in haystack for token in ["germany", "france", "sweden", "eu", "europe"]):
            return "EU"

        return None
