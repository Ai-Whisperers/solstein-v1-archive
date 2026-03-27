"""Discovery adapter wrapping web_search_client.search_company_info().

Uses Exa search to discover companies related to a market by
searching for company information with market-relevant queries.
Requires the ``exa_py`` package and an Exa API key.
"""

from __future__ import annotations

from loguru import logger


class WebSearchDiscoverySource:
    """Wraps ``search_company_info()`` as a DiscoverySource."""

    def __init__(self, exa_api_key: str | None = None):
        self._exa_api_key = exa_api_key

    @property
    def source_name(self) -> str:
        return "exa_search"

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        from solstein.research.discovery import DiscoveryCandidate, _slugify

        try:
            from solstein.data.web_search_client import search_company_info

            results = search_company_info(seed_company, query_type="general")
        except Exception as exc:
            logger.warning("WebSearchDiscoverySource: search failed: {}", exc)
            return []

        candidates: list[DiscoveryCandidate] = []
        for item in results[:max_results]:
            title = item.get("title", "")
            if not title:
                continue
            candidates.append(
                DiscoveryCandidate(
                    company_id=_slugify(title),
                    name=title,
                    market=market,
                    ticker=None,
                    industry="Unknown",
                    region="Unknown",
                    tags=extra_keywords or [],
                    seed_relevance=0.0,
                    discovery_reason="exa web search",
                    source_links=[item.get("url", "")],
                )
            )
        return candidates
