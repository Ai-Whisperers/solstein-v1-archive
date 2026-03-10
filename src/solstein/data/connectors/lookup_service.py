"""Unified identifier lookup service for company data.

EPIC-042: Identifier Resolution
EPIC-022: Refactored to use Strategy Pattern

Uses multiple lookup strategies (OpenCorporates, OpenFIGI, DuckDuckGo)
to resolve company identifiers with confidence scoring.

FREE tools used:
- OpenCorporates API (free tier)
- OpenFIGI API (free tier)
- DuckDuckGo web search (free)
"""

from __future__ import annotations

from typing import Any, Optional

from loguru import logger

from solstein.config import get_settings
from solstein.infrastructure.retry_policy import CircuitBreaker, RetryPolicy

from .contracts import ConnectorRequest, ConnectorResponse
from .lookup_strategies import (
    DuckDuckGoStrategy,
    OpenCorporatesStrategy,
    OpenFIGIStrategy,
)
from .runtime import ConnectorRuntime


class IdentifierLookupService:
    """Unified identifier lookup using Strategy Pattern.

    EPIC-022: Refactored to delegate to specialized lookup strategies.
    Each lookup provider (OpenCorporates, OpenFIGI, DuckDuckGo)
    implements its own strategy for finding identifiers.

    Confidence scoring:
    - High (0.9-1.0): Official API results
    - Medium (0.7-0.89): Search-based results
    - Low (0.5-0.69): Inferred results
    """

    def __init__(self):
        """Initialize lookup service with strategies."""
        # Initialize lookup strategies
        self._strategies = [
            OpenCorporatesStrategy(),
            OpenFIGIStrategy(),
            DuckDuckGoStrategy(),
        ]
        settings = get_settings()
        self._runtime = ConnectorRuntime(
            retry_policy=RetryPolicy(
                max_attempts=settings.connector_max_attempts,
                base_delay_seconds=settings.connector_retry_base_delay,
                max_delay_seconds=settings.connector_retry_max_delay,
            ),
            circuit_breaker=CircuitBreaker(
                failure_threshold=settings.connector_circuit_failure_threshold,
                cooldown_seconds=settings.connector_circuit_cooldown_seconds,
            ),
        )

        # Initialize cache
        self._cache: dict[str, dict[str, Any]] = {}

    @property
    def available_strategies(self) -> list[str]:
        """Get list of available strategy names."""
        return [s.name for s in self._strategies if s.is_available]

    async def resolve_identifiers(
        self,
        company_name: str,
        headquarters: Optional[str] = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """Resolve all identifiers for a company using all strategies.

        Args:
            company_name: Company name to lookup
            headquarters: Optional headquarters location
            use_cache: Whether to use cached results

        Returns:
            Dictionary with resolved identifiers and confidence scores
        """
        cache_key = f"{company_name}_{headquarters or ''}"

        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug("Using cached identifiers", company=company_name)
            return self._cache[cache_key]

        logger.info("Resolving identifiers", company=company_name)

        # Aggregate results from all strategies
        all_results: list[dict[str, Any]] = []

        for strategy in self._strategies:
            if not strategy.is_available:
                continue

            try:
                result = await strategy.lookup(company_name)
                if result:
                    all_results.append(result)
                    logger.debug(
                        "Strategy found identifiers",
                        strategy=strategy.name,
                        company=company_name,
                        identifiers=list(result.keys()),
                    )
            except Exception as exc:
                logger.warning(
                    "Strategy lookup failed",
                    strategy=strategy.name,
                    company=company_name,
                    error=str(exc),
                )

        # Merge results with confidence scoring
        merged = self._merge_results(all_results)

        # Add geography inference if not found
        if "geography" not in merged and headquarters:
            geography = self._infer_geography(company_name, headquarters)
            if geography:
                merged["geography"] = geography
                merged["geography_confidence"] = 0.6
                merged["geography_source"] = "heuristic"

        # Cache result
        if use_cache:
            self._cache[cache_key] = merged

        return merged

    async def resolve_identifiers_enveloped(
        self,
        company_name: str,
        headquarters: Optional[str] = None,
        use_cache: bool = True,
    ) -> ConnectorResponse[dict[str, Any]]:
        request = ConnectorRequest(
            connector="identifier_lookup_service",
            operation="resolve_identifiers",
            inputs={
                "company_name": company_name,
                "headquarters": headquarters,
                "use_cache": use_cache,
            },
        )

        async def _operation() -> dict[str, Any]:
            return await self.resolve_identifiers(
                company_name=company_name,
                headquarters=headquarters,
                use_cache=use_cache,
            )

        return await self._runtime.run(
            request=request,
            operation=_operation,
            retryable_exceptions=(RuntimeError, TimeoutError),
            empty_is_degraded=True,
            empty_error="No identifiers resolved",
            extra_metadata={"strategy_count": len(self._strategies)},
        )

    def _merge_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge results from multiple strategies with confidence scoring.

        Args:
            results: List of results from different strategies

        Returns:
            Merged dictionary with best identifiers
        """
        merged: dict[str, Any] = {}

        # Priority order for identifier sources
        source_priority = {
            "openfigi": 3,
            "opencorporates": 2,
            "duckduckgo_search": 1,
            "heuristic": 0,
        }

        # Fields to merge
        identifier_fields = [
            "ticker",
            "company_number",
            "isin",
            "jurisdiction",
            "legal_name",
            "exchange",
            "geography",
        ]

        for field in identifier_fields:
            best_value = None
            best_confidence = 0.0
            best_source = None

            for result in results:
                if field in result:
                    confidence = result.get(f"{field}_confidence", 0.5)
                    source = result.get(f"{field}_source", "unknown")

                    # Prefer higher confidence, then higher source priority
                    source_score = source_priority.get(source, 0)
                    current_score = confidence * 10 + source_score
                    best_score = best_confidence * 10 + source_priority.get(best_source or "", 0)

                    if current_score > best_score:
                        best_value = result[field]
                        best_confidence = confidence
                        best_source = source

            if best_value:
                merged[field] = best_value
                merged[f"{field}_confidence"] = best_confidence
                merged[f"{field}_source"] = best_source

        return merged

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

    def clear_cache(self) -> None:
        """Clear the identifier cache."""
        self._cache.clear()
        logger.info("Identifier cache cleared")


# Singleton instance for convenience
identifier_lookup_service = IdentifierLookupService()
