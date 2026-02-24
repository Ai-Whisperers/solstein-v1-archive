"""Discovery adapter wrapping CompetitorDataLoader.

Reads ``data/input/competitor_data.json`` and converts each entry
into a ``DiscoveryCandidate`` so the pipeline can merge them with
candidates from other discovery sources.
"""

from __future__ import annotations

from loguru import logger

from solstein.research.discovery import DiscoveryCandidate, _slugify


class CompetitorJsonSource:
    """Wraps ``CompetitorDataLoader`` as a DiscoverySource."""

    @property
    def source_name(self) -> str:
        return "competitor_json"

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        try:
            from solstein.data.loaders import CompetitorDataLoader

            loader = CompetitorDataLoader()
            companies = loader.load_companies()
        except Exception as exc:
            logger.warning("CompetitorJsonSource: failed to load competitor data: {}", exc)
            return []

        source_url = "https://github.com/ai-whisperers/solstein/blob/main/data/input/competitor_data.json"
        candidates: list[DiscoveryCandidate] = []
        for company in companies[:max_results]:
            region = ", ".join(company.geographic_presence) if company.geographic_presence else "Unknown"
            tags = company.tech_stack[:3] if company.tech_stack else []
            candidates.append(
                DiscoveryCandidate(
                    company_id=_slugify(company.name),
                    name=company.name,
                    market=market,
                    ticker=None,
                    industry=company.industry,
                    region=region,
                    tags=tags,
                    seed_relevance=0.0,
                    discovery_reason="competitor_data.json",
                    source_links=[source_url],
                )
            )
        return candidates
