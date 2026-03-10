"""Unified company loader main class.

Extracted from unified_loader.py as part of EPIC-021 file splitting.
Orchestrates loading and merging of company data from multiple sources.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from solstein.core.scoring_utils import populate_signal_confidences
from solstein.data.connectors.lookup_service import IdentifierLookupService
from solstein.data.loaders import CompetitorDataLoader
from solstein.extractors.markdown_extractor import MarkdownExtractor

from ..enrichment_config import UnifiedCompanyLoaderConfig, get_config
from ..enrichment_service import CacheService, ConnectorFactory, MetricsService
from .company import UnifiedCompany
from .enrichment import enrich_batch as _enrich_batch
from .enrichment import enrich_from_connectors
from .merger import merge_companies, convert_to_unified

logger = logging.getLogger(__name__)


class UnifiedCompanyLoader:
    """Load and merge company data from JSON and Markdown sources."""

    def __init__(
        self,
        sec_connector=None,
        companies_house_connector=None,
        news_detector=None,
        lookup_service=None,
    ):
        self.json_loader = CompetitorDataLoader()
        self.markdown_extractor = MarkdownExtractor()

        # Initialize configuration system
        try:
            self.config = get_config()
            logger.info("✅ Enrichment configuration loaded successfully")
        except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
            logger.warning(f"Configuration initialization failed: {e}, using defaults")
            self.config = UnifiedCompanyLoaderConfig()

        # Initialize connectors via factory
        factory = ConnectorFactory()
        try:
            self.sec_connector = sec_connector or factory.create_sec_connector(self.config)
            if self.sec_connector:
                logger.info("✅ SEC EDGAR connector initialized via factory")
        except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
            logger.warning(f"SEC EDGAR connector initialization failed: {e}")
            self.sec_connector = None

        try:
            self.companies_house_connector = companies_house_connector or factory.create_companies_house_connector(
                self.config
            )
            if self.companies_house_connector:
                logger.info("✅ Companies House connector initialized via factory")
        except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
            logger.warning(f"Companies House connector initialization failed: {e}")
            self.companies_house_connector = None

        try:
            self.news_detector = news_detector or factory.create_news_detector(self.config)
            if self.news_detector:
                logger.info("✅ News Signal detector initialized via factory")
        except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
            logger.warning(f"News Signal Detector initialization failed: {e}")
            self.news_detector = None

        try:
            self.lookup_service = lookup_service or IdentifierLookupService()
            logger.info("✅ Identifier lookup service initialized")
        except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
            logger.warning(f"Identifier lookup service initialization failed: {e}")
            self.lookup_service = None

        # EPIC-FIX-003: Configurable markdown directory (was hardcoded to 2026-02-23/dutch_market)
        # Use config if available, otherwise use environment variable, then fallback to default
        if hasattr(self.config, "markdown_dir") and self.config.markdown_dir:
            self.markdown_dir = Path(self.config.markdown_dir)
        else:
            # Check for environment variable override
            env_market_dir = os.getenv("DUTCH_MARKET_DIR")
            if env_market_dir:
                self.markdown_dir = Path(env_market_dir)
            else:
                # Fallback: use 'latest' instead of hardcoded date
                self.markdown_dir = (
                    Path(__file__).parent.parent.parent.parent
                    / "data"
                    / "input"
                    / "custom_market_runs"
                    / "latest"
                    / "dutch_market"
                )

        # Log the configured path for debugging
        logger.info(f"📁 Dutch market directory configured: {self.markdown_dir}")

        # Initialize caching and metrics for Phase B (Performance)
        self.cache = CacheService(ttl_hours=24)  # 24-hour TTL for enrichment results
        self.metrics = MetricsService()  # Track enrichment performance
        logger.info("✅ Performance services (CacheService, MetricsService) initialized")

    def load_unified_companies(self) -> list[UnifiedCompany]:
        """Load all companies with unified data from both sources."""
        # Load JSON companies
        json_companies = self.json_loader.load_companies()
        logger.info(f"Loaded {len(json_companies)} companies from JSON")

        # Load Markdown companies
        markdown_companies = self._load_markdown_companies()
        logger.info(f"Loaded {len(markdown_companies)} companies from Markdown")

        # Create mapping for quick lookup
        markdown_map = {c.id: c for c in markdown_companies}

        # Merge companies
        unified_companies = []
        for json_company in json_companies:
            markdown_company = markdown_map.get(json_company.id)

            if markdown_company:
                # Merge with conflict resolution
                unified = merge_companies(json_company, markdown_company)
            else:
                # Use JSON only
                unified = convert_to_unified(json_company, source="JSON")

            unified_companies.append(unified)

        # Add Markdown-only companies (if any)
        json_ids = {c.id for c in json_companies}
        for markdown_company in markdown_companies:
            if markdown_company.id not in json_ids:
                unified = convert_to_unified(markdown_company, source="Markdown")
                unified_companies.append(unified)

        logger.info(f"Created {len(unified_companies)} unified companies")

        # Enrich companies from connectors (SEC EDGAR, Companies House, News Signals)
        logger.info("Starting connector enrichment...")

        enriched_companies = []

        for company in unified_companies:
            try:
                enriched = enrich_from_connectors(self, company)
                enriched_companies.append(enriched)

            except (ValueError, RuntimeError, TypeError, AttributeError) as e:
                logger.warning(f"Enrichment failed for {company.name}: {e}")
                enriched_companies.append(company)  # Use original if enrichment fails

        logger.info(
            f"Enrichment complete. {len([c for c in enriched_companies if c.enrichment_sources])} companies enriched"
        )

        # Populate signal confidences for scoring component weighting
        for company in enriched_companies:
            populate_signal_confidences(company)

        return enriched_companies

    def _load_markdown_companies(self):
        """Load companies from Markdown files in dutch_market directory."""
        companies = []

        if not self.markdown_dir.exists():
            logger.warning(f"Markdown directory not found: {self.markdown_dir}")
            return companies

        # Find all .md files
        for md_file in self.markdown_dir.glob("*.md"):
            try:
                extracted_data = self.markdown_extractor.extract_from_file(md_file)
                if extracted_data:
                    company = self.markdown_extractor.to_company_profile(extracted_data)
                    companies.append(company)
                    logger.debug(f"Loaded Markdown company: {company.name}")
            except (ValueError, RuntimeError, TypeError, AttributeError, OSError) as e:
                logger.warning(f"Failed to load Markdown file {md_file}: {e}")

        return companies

    def enrich_batch(self, companies: list[UnifiedCompany], batch_size: int = 10) -> list[UnifiedCompany]:
        """Batch enrich companies with caching and performance tracking."""
        return _enrich_batch(self, companies, batch_size)

    def get_enrichment_metrics(self) -> dict:
        """Get current enrichment metrics."""
        return self.metrics.get_summary()

    def clear_enrichment_cache(self) -> None:
        """Clear all cached enrichment results."""
        self.cache.clear()
        logger.info("✅ Enrichment cache cleared")
