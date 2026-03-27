"""
Web search agent for the AI research orchestrator.

Extracted from research_agents.py to reduce file size.
Performs web searches via SearXNG (primary) and DuckDuckGo (fallback).
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from .research_types import SearchResult

# Optional: DuckDuckGo search backend (loaded at import time)
_ddgs_class: Any | None = None
_duckduckgo_available = False

try:
    if importlib.util.find_spec("duckduckgo_search") is not None:
        _ddgs_module = importlib.import_module("duckduckgo_search")
        _ddgs_class = getattr(_ddgs_module, "DDGS", None)
        _duckduckgo_available = _ddgs_class is not None
    else:
        logger.warning("duckduckgo_search not installed. Web search will be disabled.")
except (ImportError, AttributeError) as error:
    logger.warning(f"duckduckgo_search failed to initialize: {error}")


class WebSearchAgent:
    """Performs web searches and relevance ranking.

    Primary backend: SearXNG (local instance, aggregates Brave+DDG+Google).
    Fallback: direct DuckDuckGo library.
    """

    SEARXNG_URL = "http://localhost:8889/search"

    def __init__(self) -> None:
        self.ddgs = _ddgs_class() if _duckduckgo_available and _ddgs_class is not None else None
        self.cache: dict[str, list[SearchResult]] = {}
        self._cache_max_size: int = 256

    async def search(self, query: str, intent: str, max_results: int = 10) -> list[SearchResult]:
        """Execute search and return ranked results."""
        cache_key = f"{query}_{intent}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        results: list[SearchResult] = []

        # Primary: SearXNG (aggregates Brave, DDG, Google, Wikipedia)
        try:
            searxng_results = await self._search_searxng(query, max_results)
            results.extend(searxng_results)
            if searxng_results:
                logger.info(f"SearXNG returned {len(searxng_results)} results for '{query}'")
        except (httpx.HTTPError, ConnectionError) as error:
            logger.warning(f"SearXNG search failed for '{query}': {error}")

        # Fallback: direct DuckDuckGo library
        if not results and self.ddgs is not None:
            try:
                ddg_results = await asyncio.to_thread(self._search_duckduckgo, query, max_results)
                results.extend(ddg_results)
                if ddg_results:
                    logger.info(f"DDG fallback returned {len(ddg_results)} results for '{query}'")
            except (RuntimeError, ValueError, ConnectionError) as error:
                logger.warning(f"DuckDuckGo fallback failed for '{query}': {error}")

        if not results:
            logger.warning(f"All search backends returned 0 results for '{query}'")

        ranked = self._rank_by_relevance(results, intent)
        if len(self.cache) >= self._cache_max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[cache_key] = ranked
        return ranked

    async def _search_searxng(self, query: str, max_results: int) -> list[SearchResult]:
        """Search using local SearXNG instance (aggregates multiple engines)."""
        results: list[SearchResult] = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.get(
                    self.SEARXNG_URL,
                    params={"q": query, "format": "json", "language": "en"},
                )

                if response.status_code == 403:
                    logger.debug(f"SearXNG JSON returned 403, falling back to HTML for: {query}")
                    return await self._search_searxng_html(client, query, max_results)

                response.raise_for_status()
                data = response.json()

                for item in data.get("results", [])[:max_results]:
                    url = item.get("url", "")
                    if not url:
                        continue
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=url,
                            snippet=item.get("content", ""),
                            source=urlparse(url).netloc,
                        )
                    )

                for infobox in data.get("infoboxes", []):
                    ib_url = infobox.get("id", "")
                    if ib_url and ib_url.startswith("http"):
                        results.append(
                            SearchResult(
                                title=infobox.get("infobox", ""),
                                url=ib_url,
                                snippet=infobox.get("content", ""),
                                source=urlparse(ib_url).netloc,
                            )
                        )
            except (httpx.HTTPError, KeyError, ValueError) as e:
                logger.warning(f"SearXNG search failed: {e}")

        return results

    async def _search_searxng_html(
        self, client: httpx.AsyncClient, query: str, max_results: int
    ) -> list[SearchResult]:
        """Fallback: Parse SearXNG HTML results when JSON is unavailable."""
        results: list[SearchResult] = []
        try:
            response = await client.get(
                self.SEARXNG_URL,
                params={"q": query, "language": "en"},
                headers={"Accept": "text/html"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article", class_="result")[:max_results]:
                link_elem = article.find("a", href=True)
                if not link_elem:
                    continue

                url = link_elem.get("href", "")
                title_elem = article.find("h3")
                title = title_elem.get_text(strip=True) if title_elem else ""
                content_elem = article.find("p", class_="content")
                if not content_elem:
                    content_elem = article.find("p")
                snippet = content_elem.get_text(strip=True) if content_elem else ""

                if url:
                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=urlparse(url).netloc,
                        )
                    )
        except (httpx.HTTPError, KeyError, ValueError, AttributeError) as e:
            logger.warning(f"SearXNG HTML parsing failed: {e}")

        return results

    def _search_duckduckgo(self, query: str, max_results: int) -> list[SearchResult]:
        """Fallback: search using DuckDuckGo library."""
        if self.ddgs is None:
            return []

        results: list[SearchResult] = []
        for result in self.ddgs.text(query, max_results=max_results):
            href = result.get("href", "")
            results.append(
                SearchResult(
                    title=result.get("title", ""),
                    url=href,
                    snippet=result.get("body", ""),
                    source=urlparse(href).netloc,
                )
            )
        return results

    def _rank_by_relevance(self, results: list[SearchResult], intent: str) -> list[SearchResult]:
        """Rank search results by intent relevance and source quality."""
        intent_keywords: dict[str, list[str]] = {
            "website": ["official", "about", "company", "home"],
            "funding": ["funding", "investment", "raised", "series", "valuation"],
            "financials": ["revenue", "financial", "sales", "growth", "profit"],
            "employees": ["employees", "headcount", "team", "hiring", "jobs"],
            "news": ["news", "press", "announces", "launches"],
            "social": ["linkedin", "twitter", "social", "media"],
        }
        keywords = intent_keywords.get(intent, [])

        for result in results:
            text = f"{result.title} {result.snippet}".lower()
            score = 0.0

            for keyword in keywords:
                if keyword in text:
                    score += 0.2

            if any(domain in result.source for domain in ["crunchbase.com", "linkedin.com", "bloomberg.com"]):
                score += 0.3
            elif any(domain in result.source for domain in ["techcrunch.com", "forbes.com", "reuters.com"]):
                score += 0.25
            elif ".gov" in result.source:
                score += 0.2

            if any(year in text for year in ["2024", "2025", "2026"]):
                score += 0.1

            result.relevance_score = min(score, 1.0)
            result.intent_match = intent

        return sorted(results, key=lambda item: item.relevance_score, reverse=True)


__all__ = ["WebSearchAgent"]
