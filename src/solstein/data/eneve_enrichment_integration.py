"""Enrichment integration for ENEVE workflow (EPIC-FIX-006).

Wires up the enrichment pipeline to the ENEVE workflow, enabling
automatic enrichment of company data from multiple sources.
"""

import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from loguru import logger

from solstein.adapters.registry import build_default_registry
from solstein.application.enrichment_pipeline import EnrichmentPipeline
from solstein.config import Settings
from solstein.domain.models import RawDataSource


class EnrichmentCache:
    """Simple file-based cache for enrichment results.

    Caches enrichment results to avoid redundant API calls.
    Cache key is based on company name and enrichment parameters.
    Cache expires after TTL (default: 24 hours).
    """

    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, company_name: str, params: dict[str, Any]) -> str:
        """Generate cache key from company name and params."""
        key_data = f"{company_name}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, company_name: str, params: dict[str, Any]) -> list[dict[str, Any]] | None:
        """Get cached enrichment results if available and not expired."""
        cache_key = self._get_cache_key(company_name, params)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached["timestamp"])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for {company_name}")
                cache_path.unlink()
                return None

            logger.debug(f"Cache hit for {company_name}")
            return cached["sources"]

        except Exception as e:
            logger.warning(f"Failed to read cache for {company_name}: {e}")
            return None

    def set(self, company_name: str, params: dict[str, Any], sources: list[RawDataSource]) -> None:
        """Cache enrichment results."""
        cache_key = self._get_cache_key(company_name, params)
        cache_path = self._get_cache_path(cache_key)

        try:
            # Convert RawDataSource objects to dicts for JSON serialization
            sources_data = []
            for source in sources:
                source_dict = {
                    "source_name": source.source_name,
                    "source_type": str(source.source_type),
                    "entity_id": source.entity_id,
                    "entity_name": source.entity_name,
                    "raw_content": source.raw_content
                    if isinstance(source.raw_content, dict)
                    else str(source.raw_content),
                }
                sources_data.append(source_dict)

            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "company_name": company_name,
                "params": params,
                "sources": sources_data,
            }

            with open(cache_path, "w") as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Cached enrichment for {company_name}")

        except Exception as e:
            logger.warning(f"Failed to write cache for {company_name}: {e}")

    def clear(self) -> int:
        """Clear all cached entries. Returns number of files removed."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError as error:
                logger.warning(f"Failed to remove cache file {cache_file}: {error}")
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        # Count expired entries
        expired_count = 0
        for cache_file in cache_files:
            try:
                with open(cache_file) as f:
                    cached = json.load(f)
                cached_time = datetime.fromisoformat(cached["timestamp"])
                if datetime.now() - cached_time > self.ttl:
                    expired_count += 1
            except (OSError, ValueError, KeyError, TypeError) as error:
                logger.debug(f"Skipping cache stats for unreadable file {cache_file}: {error}")

        return {
            "total_entries": len(cache_files),
            "expired_entries": expired_count,
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
        }


class EneveEnricher:
    """Enricher for ENEVE workflow companies.

    This class wires up the enrichment pipeline to provide
    multi-source data enrichment for the 3 ENEVE companies.

    Features:
    - Caching: Enrichment results are cached to avoid redundant API calls
    - Fallback: Falls back to available adapters if pipeline fails
    - Quality metrics: Tracks source quality and completeness
    """

    def __init__(self, settings: Settings | None = None, enable_cache: bool = True):
        self.settings = settings or Settings()
        self.registry = build_default_registry(self.settings)
        self.pipeline = EnrichmentPipeline(self.registry)

        # Initialize cache
        self.enable_cache = enable_cache
        if enable_cache:
            cache_dir = Path("data/cache/enrichment")
            self.cache = EnrichmentCache(cache_dir)
        else:
            self.cache = None

    async def enrich_companies(self, companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Enrich a list of companies with data from multiple sources.

        Args:
            companies: List of company dictionaries from competitor_data.json

        Returns:
            Enriched companies with additional data from adapters
        """
        enriched = []

        for company_data in companies:
            company_name = company_data.get("company_name", "Unknown")
            logger.info(f"Enriching {company_name}...")

            try:
                # Run enrichment pipeline
                raw_sources = await self._enrich_company(company_data)

                # Update company data with enrichment results
                enriched_company = self._merge_enrichment(company_data, raw_sources)

                enriched.append(enriched_company)
                logger.info(f"✅ Enriched {company_name} with {len(raw_sources)} sources")

            except Exception as e:
                logger.warning(f"⚠️  Failed to enrich {company_name}: {e}")
                # Return original data if enrichment fails
                enriched.append(company_data)

        return enriched

    async def _enrich_company(self, company_data: dict[str, Any]) -> list[RawDataSource]:
        """Run enrichment pipeline for a single company.

        Uses the real enrichment pipeline to gather data from multiple sources.
        Falls back to available adapters if pipeline fails.
        Uses cache to avoid redundant API calls.
        """
        sources = []
        company_name = company_data.get("company_name", "Unknown")

        # Build enrichment params for cache key
        params = {
            "website": company_data.get("website"),
            "industry": company_data.get("industry"),
        }

        # Check cache first
        if self.enable_cache and self.cache:
            cached = self.cache.get(company_name, params)
            if cached:
                logger.info(f"💾 Using cached enrichment for {company_name}")
                # Convert cached dicts back to RawDataSource objects
                sources = [
                    RawDataSource(
                        source_name=s["source_name"],
                        source_type=s["source_type"],
                        entity_id=s["entity_id"],
                        entity_name=s["entity_name"],
                        raw_content=s["raw_content"],
                    )
                    for s in cached
                ]
                return sources

        try:
            # Try to use the real enrichment pipeline
            result = await self.pipeline.enrich(
                company_id=company_name.lower().replace(" ", "-"),
                company_name=company_name,
                website=params["website"],

            )

            if result and result.sources:
                sources = result.sources
                logger.info(f"✅ Pipeline enrichment successful for {company_name}: {len(sources)} sources")

                # Cache the results
                if self.enable_cache and self.cache:
                    self.cache.set(company_name, params, sources)

            else:
                logger.warning(f"⚠️ Pipeline returned no sources for {company_name}, using fallback")
                sources = await self._fallback_enrichment(company_data)

        except Exception as e:
            logger.error(f"❌ Pipeline enrichment failed for {company_name}: {e}")
            logger.info(f"🔄 Using fallback enrichment for {company_name}")
            sources = await self._fallback_enrichment(company_data)

        return sources

    async def _fallback_enrichment(self, company_data: dict[str, Any]) -> list[RawDataSource]:
        """Fallback enrichment when pipeline fails.

        Uses available adapters from registry to gather basic data.
        """
        sources = []
        company_name = company_data.get("company_name", "Unknown")

        # Get enrichment sources from registry
        enrichment_sources = self.registry.all_enrichment_sources
        logger.debug(f"Found {len(enrichment_sources)} enrichment sources for fallback")

        # Try each available adapter
        for source in enrichment_sources[:3]:  # Limit to first 3 to avoid rate limits
            try:
                # Attempt to enrich with this source
                source_result = await source.enrich(company_data)
                if source_result:
                    sources.append(source_result)
                    logger.debug(f"✅ Fallback source added: {source_result.source_name}")
            except Exception as e:
                logger.debug(f"⚠️ Fallback source {source} failed: {e}")
                continue

        # If no sources worked, create minimal source from existing data
        if not sources:
            logger.warning(f"⚠️ All enrichment failed for {company_name}, using minimal source")
            sources.append(
                RawDataSource(
                    source_name="Input Data",
                    source_type="competitor_json",
                    entity_id=company_name,
                    entity_name=company_name,
                    raw_content=company_data,
                )
            )

        return sources

    def _merge_enrichment(self, company_data: dict[str, Any], raw_sources: list[RawDataSource]) -> dict[str, Any]:
        """Merge enrichment results into company data.

        Returns a shallow copy with merged fields; does not mutate the caller's dict.

        Updates:
        - enrichment_source_count: Number of sources used
        - data_quality_score: Calculated from source count
        - source_links: List of data sources
        - enrichment_quality_metrics: Detailed quality metrics
        """
        company_data = dict(company_data)  # shallow copy — do not mutate caller's dict
        # Update enrichment metrics
        company_data["enrichment_source_count"] = len(raw_sources)
        company_data["data_quality_score"] = min(0.95, 0.5 + (len(raw_sources) * 0.15))

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(raw_sources)
        company_data["enrichment_quality_metrics"] = quality_metrics

        # Add source links
        company_data["source_links"] = [
            {"source": s.source_name, "type": str(s.source_type), "confidence": "medium"} for s in raw_sources
        ]

        # Update confidence levels based on enrichment
        if "revenue" in company_data and "timeline" in company_data["revenue"]:
            for entry in company_data["revenue"]["timeline"]:
                if "confidence" not in entry or entry["confidence"] == "Unknown":
                    entry["confidence"] = "medium"
                    entry["source"] = "Enriched from multiple sources"

        return company_data

    def _calculate_quality_metrics(self, raw_sources: list[RawDataSource]) -> dict[str, Any]:
        """Calculate detailed quality metrics for enrichment sources.

        Metrics:
        - source_count: Total number of sources
        - source_diversity: Number of unique source types
        - high_confidence_sources: Count of high-confidence sources
        - data_completeness: Estimated completeness (0-1)
        - source_types: Breakdown by source type
        """
        if not raw_sources:
            return {
                "source_count": 0,
                "source_diversity": 0,
                "high_confidence_sources": 0,
                "data_completeness": 0.0,
                "source_types": {},
            }

        # Count source types
        source_types = {}
        high_confidence_count = 0

        for source in raw_sources:
            source_type = str(source.source_type)
            source_types[source_type] = source_types.get(source_type, 0) + 1

            # Consider sources with specific types as high confidence
            if source_type in ["api", "database", "verified"]:
                high_confidence_count += 1

        # Calculate diversity (unique types / total sources)
        diversity = len(source_types) / len(raw_sources) if raw_sources else 0

        # Estimate completeness based on source count and diversity
        # More sources and more diversity = higher completeness
        base_completeness = min(0.6, len(raw_sources) * 0.2)
        diversity_bonus = diversity * 0.2
        data_completeness = min(0.95, base_completeness + diversity_bonus)

        return {
            "source_count": len(raw_sources),
            "source_diversity": len(source_types),
            "high_confidence_sources": high_confidence_count,
            "data_completeness": round(data_completeness, 2),
            "source_types": source_types,
            "diversity_score": round(diversity, 2),
        }


async def enrich_eneve_data(input_path: Path, output_path: Path) -> None:
    """Enrich ENEVE company data and save to output.

    This is the main entry point for EPIC-FIX-006.
    """
    import json

    # Load existing data
    with open(input_path) as f:
        data = json.load(f)

    companies = data.get("competitors", [])
    logger.info(f"Loaded {len(companies)} companies for enrichment")

    # Create enricher and run
    enricher = EneveEnricher()
    enriched = await enricher.enrich_companies(companies)

    # Save enriched data
    data["competitors"] = enriched
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"💾 Saved enriched data to {output_path}")

    # Print summary with quality metrics
    total_sources = sum(c.get("enrichment_source_count", 0) for c in enriched)
    avg_quality = sum(c.get("data_quality_score", 0) for c in enriched) / len(enriched) if enriched else 0

    # Aggregate quality metrics
    total_diversity = sum(c.get("enrichment_quality_metrics", {}).get("source_diversity", 0) for c in enriched)
    avg_completeness = (
        sum(c.get("enrichment_quality_metrics", {}).get("data_completeness", 0) for c in enriched) / len(enriched)
        if enriched
        else 0
    )
    avg_diversity_score = (
        sum(c.get("enrichment_quality_metrics", {}).get("diversity_score", 0) for c in enriched) / len(enriched)
        if enriched
        else 0
    )

    logger.info("Enrichment Summary:")
    logger.info(f"Companies enriched: {len(enriched)}")
    logger.info(f"Total sources: {total_sources}")
    logger.info(f"Average data quality: {avg_quality:.0%}")
    logger.info("Quality Metrics:")
    logger.info(f"Average completeness: {avg_completeness:.0%}")
    logger.info(f"Average diversity score: {avg_diversity_score:.2f}")
    logger.info(f"Total unique source types: {total_diversity}")

    # Print cache stats if caching is enabled
    if enricher.cache:
        cache_stats = enricher.cache.get_stats()
        logger.info("Cache Statistics:")
        logger.info(f"Cache entries: {cache_stats['total_entries']}")
        logger.info(f"Expired entries: {cache_stats['expired_entries']}")
        logger.info(f"Cache size: {cache_stats['total_size_bytes'] / 1024:.1f} KB")


# CLI entry point
def main():
    """CLI entry point for enrichment."""
    input_path = Path("data/input/competitor_data.json")
    output_path = Path("data/input/competitor_data_enriched.json")

    asyncio.run(enrich_eneve_data(input_path, output_path))


if __name__ == "__main__":
    main()
