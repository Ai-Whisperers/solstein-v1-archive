"""
Real Data Pipeline Architecture - EPIC-008 Story 8.1
=====================================================

This module implements a real data pipeline to replace synthetic data generation.
The pipeline fetches company data from multiple external sources and validates
it before use in the ENEVE workflow.

Architecture Overview:
----------------------

┌─────────────────────────────────────────────────────────────────┐
│                    Real Data Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Source     │     │   Source     │     │   Source     │   │
│  │  Crunchbase  │     │   LinkedIn   │     │    Yahoo     │   │
│  │   Adapter    │     │   Adapter    │     │   Finance    │   │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│         │                    │                    │            │
│         └────────────────────┼────────────────────┘            │
│                              ▼                                  │
│                    ┌──────────────────┐                        │
│                    │  Data Aggregator │                        │
│                    │   (Merge & Dedu) │                        │
│                    └────────┬─────────┘                        │
│                             ▼                                   │
│                    ┌──────────────────┐                        │
│                    │  Data Validator  │                        │
│                    │ (Quality Checks) │                        │
│                    └────────┬─────────┘                        │
│                             ▼                                   │
│                    ┌──────────────────┐                        │
│                    │ Manual Curation  │                        │
│                    │   (Review UI)    │                        │
│                    └────────┬─────────┘                        │
│                             ▼                                   │
│                    ┌──────────────────┐                        │
│                    │  Output to ENEVE │                        │
│                    └──────────────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Pipeline Stages:
----------------

1. SOURCE ADAPTERS (Stories 8.2, 8.3)
   - Crunchbase Adapter: Funding, valuation, company info
   - LinkedIn Adapter: Employee count, company description
   - Yahoo Finance Adapter: Public company financials
   - Each adapter implements BaseDataSource interface

2. DATA AGGREGATOR
   - Merges data from multiple sources
   - Resolves conflicts (newest wins, or confidence-weighted)
   - Deduplicates entries
   - Tracks data provenance

3. DATA VALIDATOR (Story 8.4)
   - Validates data completeness
   - Checks for outliers and anomalies
   - Verifies data freshness
   - Assigns quality scores

4. MANUAL CURATION (Story 8.5)
   - Review UI for flagged entries
   - Human verification of critical data
   - Override capability for automated decisions

5. OUTPUT
   - Generates competitor_data.json format
   - Preserves all required fields
   - Includes metadata about data sources

Data Flow:
----------

Input: Company name (or list of names)
  ↓
[Source Adapters] → Fetch from Crunchbase, LinkedIn, Yahoo
  ↓
[Data Aggregator] → Merge, deduplicate, resolve conflicts
  ↓
[Data Validator] → Validate completeness, check quality
  ↓
[Manual Curation] → Review flagged entries (optional)
  ↓
Output: Enriched company data in ENEVE format

Usage:
------

    from scripts.real_data_pipeline import RealDataPipeline

    # Initialize pipeline
    pipeline = RealDataPipeline(
        crunchbase_api_key="...",
        linkedin_api_key="...",
    )

    # Fetch real data for companies
    companies = ["Tesla", "Rivian", "Lucid Motors"]
    enriched_data = await pipeline.fetch_companies(companies)

    # Save to ENEVE format
    pipeline.save_to_eneve_format(enriched_data, "data/input/competitor_data_real.json")

Configuration:
--------------

Environment variables:
- CRUNCHBASE_API_KEY: API key for Crunchbase
- LINKEDIN_API_KEY: API key for LinkedIn
- YAHOO_FINANCE_ENABLED: Enable Yahoo Finance (default: true)
- PIPELINE_CACHE_DIR: Cache directory (default: data/cache/pipeline)
- PIPELINE_CACHE_TTL: Cache TTL in hours (default: 24)

Implementation Status:
----------------------
- [x] Story 8.1: Design pipeline architecture
- [ ] Story 8.2: Crunchbase integration
- [ ] Story 8.3: LinkedIn integration
- [ ] Story 8.4: Data validation
- [ ] Story 8.5: Manual curation
- [ ] Story 8.6: Data refresh
"""

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class DataSourceResult:
    """Result from a single data source."""

    source_name: str
    company_name: str
    data: dict[str, Any]
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    raw_response: dict | None = None


@dataclass
class AggregatedCompany:
    """Company data aggregated from multiple sources."""

    company_name: str
    merged_data: dict[str, Any]
    sources: list[str]
    confidence_scores: dict[str, float]
    quality_score: float
    last_updated: datetime
    validation_errors: list[str] = field(default_factory=list)


class BaseDataSource(ABC):
    """Abstract base class for data source adapters."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.source_name = self.__class__.__name__

    @abstractmethod
    async def fetch_company(self, company_name: str) -> DataSourceResult | None:
        """Fetch company data from this source.

        Args:
            company_name: Name of the company to fetch

        Returns:
            DataSourceResult if successful, None if not found
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this data source is available (API key valid, etc.)."""
        pass


class DataAggregator:
    """Aggregates data from multiple sources."""

    def __init__(self):
        self.conflict_resolution_strategy = "newest"  # or "confidence_weighted"

    def aggregate(self, results: list[DataSourceResult]) -> AggregatedCompany:
        """Merge data from multiple sources.

        Args:
            results: List of results from different sources

        Returns:
            Aggregated company data
        """
        if not results:
            raise ValueError("No results to aggregate")

        company_name = results[0].company_name
        sources = [r.source_name for r in results]
        confidence_scores = {r.source_name: r.confidence for r in results}

        # Merge data (simple merge for now - last source wins for conflicts)
        merged_data = {}
        for result in sorted(results, key=lambda r: r.timestamp):
            merged_data.update(result.data)

        # Calculate overall quality score
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
        quality_score = min(1.0, avg_confidence * (1 + len(results) * 0.1))

        return AggregatedCompany(
            company_name=company_name,
            merged_data=merged_data,
            sources=sources,
            confidence_scores=confidence_scores,
            quality_score=quality_score,
            last_updated=datetime.now(),
        )


class DataValidator:
    """Validates aggregated company data."""

    def __init__(self):
        self.required_fields = ["company_name", "industry"]
        self.numeric_ranges = {
            "revenue": (0, 1_000_000),  # in millions
            "employees": (1, 500_000),
            "funding_raised": (0, 100_000),  # in millions
        }

    def validate(self, company: AggregatedCompany) -> AggregatedCompany:
        """Validate company data and flag issues.

        Args:
            company: Aggregated company data

        Returns:
            Company with validation_errors populated
        """
        errors = []
        data = company.merged_data

        # Check required fields
        for required_field in self.required_fields:
            if required_field not in data or not data[required_field]:
                errors.append(f"Missing required field: {required_field}")

        # Check numeric ranges
        for numeric_field, (min_val, max_val) in self.numeric_ranges.items():
            if numeric_field in data:
                value = data[numeric_field]
                if value is not None and (value < min_val or value > max_val):
                    errors.append(f"{numeric_field} out of range: {value}")

        # Check data freshness
        if datetime.now() - company.last_updated > timedelta(days=30):
            errors.append("Data may be stale (>30 days old)")

        company.validation_errors = errors
        return company


class RealDataPipeline:
    """Main pipeline for fetching real company data."""

    def __init__(
        self,
        crunchbase_api_key: str | None = None,
        linkedin_api_key: str | None = None,
        enable_yahoo_finance: bool = True,
    ):
        self.sources: list[BaseDataSource] = []
        self.aggregator = DataAggregator()
        self.validator = DataValidator()

        # Initialize sources (will be implemented in Stories 8.2, 8.3)
        # self.sources.append(CrunchbaseAdapter(crunchbase_api_key))
        # self.sources.append(LinkedInAdapter(linkedin_api_key))
        # if enable_yahoo_finance:
        #     self.sources.append(YahooFinanceAdapter())

        logger.info(f"Initialized RealDataPipeline with {len(self.sources)} sources")

    async def fetch_company(self, company_name: str) -> AggregatedCompany | None:
        """Fetch and aggregate data for a single company.

        Args:
            company_name: Name of the company

        Returns:
            Aggregated company data or None if no sources available
        """
        logger.info(f"Fetching data for {company_name}...")

        # Fetch from all available sources
        results = []
        for source in self.sources:
            if source.is_available():
                try:
                    result = await source.fetch_company(company_name)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Source {source.source_name} failed: {e}")

        if not results:
            logger.warning(f"No data found for {company_name}")
            return None

        # Aggregate and validate
        aggregated = self.aggregator.aggregate(results)
        validated = self.validator.validate(aggregated)

        logger.info(f"✅ Fetched {company_name} from {len(results)} sources")
        return validated

    async def fetch_companies(self, company_names: list[str]) -> list[AggregatedCompany]:
        """Fetch data for multiple companies.

        Args:
            company_names: List of company names

        Returns:
            List of aggregated company data
        """
        tasks = [self.fetch_company(name) for name in company_names]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    def to_eneve_format(self, companies: list[AggregatedCompany]) -> dict[str, Any]:
        """Convert aggregated data to ENEVE competitor_data.json format.

        Args:
            companies: List of aggregated companies

        Returns:
            Dictionary in competitor_data.json format
        """
        competitors = []

        for company in companies:
            data = company.merged_data

            # Map to ENEVE format
            eneve_company = {
                "company_name": company.company_name,
                "industry": data.get("industry", "Energy Software"),
                "description": data.get("description", ""),
                "website": data.get("website", ""),
                "country": data.get("country", "Unknown"),
                "founded_year": data.get("founded_year"),
                "employees": data.get("employees"),
                "employees_confidence": self._confidence_to_string(company.confidence_scores.get("employees", 0.5)),
                "funding_raised": data.get("funding_raised"),
                "funding_confidence": self._confidence_to_string(company.confidence_scores.get("funding", 0.5)),
                "valuation": data.get("valuation"),
                "valuation_confidence": self._confidence_to_string(company.confidence_scores.get("valuation", 0.5)),
                "revenue": {
                    "timeline": [
                        {
                            "year": datetime.now().year,
                            "eur_millions": data.get("revenue", 0),
                            "yoy_growth_pct": data.get("growth_rate", 0),
                            "confidence": self._confidence_to_string(company.confidence_scores.get("revenue", 0.5)),
                        }
                    ],
                    "cagr_3yr_pct": data.get("cagr_3yr"),
                    "cagr_5yr_pct": data.get("cagr_5yr"),
                },
                "profitability": {
                    "ebitda_margin_pct": data.get("ebitda_margin"),
                    "recurring_revenue_pct": data.get("recurring_revenue_pct"),
                    "revenue_per_employee_eur_k": data.get("revenue_per_employee"),
                },
                "geographic_presence": data.get("geographic_presence", []),
                "enrichment_source_count": len(company.sources),
                "enrichment_quality_metrics": {
                    "source_count": len(company.sources),
                    "quality_score": company.quality_score,
                    "sources": company.sources,
                    "validation_errors": company.validation_errors,
                },
                "source_links": [{"source": s, "confidence": "medium"} for s in company.sources],
            }

            competitors.append(eneve_company)

        return {"competitors": competitors}

    def _confidence_to_string(self, confidence: float) -> str:
        """Convert numeric confidence to string."""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"

    def save_to_eneve_format(
        self,
        companies: list[AggregatedCompany],
        output_path: str,
    ) -> None:
        """Save companies to ENEVE format JSON file.

        Args:
            companies: List of aggregated companies
            output_path: Path to output JSON file
        """
        data = self.to_eneve_format(companies)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"💾 Saved {len(companies)} companies to {output_path}")


# Placeholder adapters (to be implemented in Stories 8.2, 8.3)
class CrunchbaseAdapter(BaseDataSource):
    """Adapter for Crunchbase API."""

    async def fetch_company(self, company_name: str) -> DataSourceResult | None:
        """TODO: Implement in Story 8.2"""
        pass

    def is_available(self) -> bool:
        return self.api_key is not None


class LinkedInAdapter(BaseDataSource):
    """Adapter for LinkedIn API."""

    async def fetch_company(self, company_name: str) -> DataSourceResult | None:
        """TODO: Implement in Story 8.3"""
        pass

    def is_available(self) -> bool:
        return self.api_key is not None


class YahooFinanceAdapter(BaseDataSource):
    """Adapter for Yahoo Finance API."""

    async def fetch_company(self, company_name: str) -> DataSourceResult | None:
        """TODO: Implement"""
        pass

    def is_available(self) -> bool:
        return True  # No API key required for basic data
