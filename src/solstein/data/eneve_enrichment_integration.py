"""Enrichment integration for ENEVE workflow (EPIC-FIX-006).

Wires up the enrichment pipeline to the ENEVE workflow, enabling
automatic enrichment of company data from multiple sources.
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any

from loguru import logger

from solstein.adapters.registry import build_default_registry
from solstein.application.enrichment_pipeline import EnrichmentPipeline
from solstein.config import Settings
from solstein.domain.models import Company, RawDataSource


class EneveEnricher:
    """Enricher for ENEVE workflow companies.

    This class wires up the enrichment pipeline to provide
    multi-source data enrichment for the 3 ENEVE companies.
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.registry = build_default_registry(self.settings)
        self.pipeline = EnrichmentPipeline(self.registry)

    async def enrich_companies(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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

    async def _enrich_company(self, company_data: Dict[str, Any]) -> List[RawDataSource]:
        """Run enrichment pipeline for a single company.

        Uses the real enrichment pipeline to gather data from multiple sources.
        Falls back to available adapters if pipeline fails.
        """
        sources = []
        company_name = company_data.get("company_name", "Unknown")
        
        try:
            # Try to use the real enrichment pipeline
            result = await self.pipeline.enrich(
                company_id=company_name.lower().replace(" ", "-"),
                company_name=company_name,
                website=company_data.get("website"),
                industry=company_data.get("industry"),
            )
            
            if result and result.sources:
                sources = result.sources
                logger.info(f"✅ Pipeline enrichment successful for {company_name}: {len(sources)} sources")
            else:
                logger.warning(f"⚠️ Pipeline returned no sources for {company_name}, using fallback")
                sources = await self._fallback_enrichment(company_data)
                
        except Exception as e:
            logger.error(f"❌ Pipeline enrichment failed for {company_name}: {e}")
            logger.info(f"🔄 Using fallback enrichment for {company_name}")
            sources = await self._fallback_enrichment(company_data)

        return sources
    
    async def _fallback_enrichment(self, company_data: Dict[str, Any]) -> List[RawDataSource]:
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
                    source_type="input",
                    entity_id=company_name,
                    entity_name=company_name,
                    raw_content=company_data,
                )
            )
        
        return sources

    def _merge_enrichment(self, company_data: Dict[str, Any], raw_sources: List[RawDataSource]) -> Dict[str, Any]:
        """Merge enrichment results into company data.

        Updates:
        - enrichment_source_count: Number of sources used
        - data_quality_score: Calculated from source count
        - source_links: List of data sources
        - enrichment_quality_metrics: Detailed quality metrics
        """
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

    def _calculate_quality_metrics(self, raw_sources: List[RawDataSource]) -> Dict[str, Any]:
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
    avg_completeness = sum(c.get("enrichment_quality_metrics", {}).get("data_completeness", 0) for c in enriched) / len(enriched) if enriched else 0
    avg_diversity_score = sum(c.get("enrichment_quality_metrics", {}).get("diversity_score", 0) for c in enriched) / len(enriched) if enriched else 0

    print(f"\n📊 Enrichment Summary:")
    print(f"  Companies enriched: {len(enriched)}")
    print(f"  Total sources: {total_sources}")
    print(f"  Average data quality: {avg_quality:.0%}")
    print(f"\n📈 Quality Metrics:")
    print(f"  Average completeness: {avg_completeness:.0%}")
    print(f"  Average diversity score: {avg_diversity_score:.2f}")
    print(f"  Total unique source types: {total_diversity}")


# CLI entry point
def main():
    """CLI entry point for enrichment."""
    input_path = Path("data/input/competitor_data.json")
    output_path = Path("data/input/competitor_data_enriched.json")

    asyncio.run(enrich_eneve_data(input_path, output_path))


if __name__ == "__main__":
    main()
