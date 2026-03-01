"""
Task 2: Unified CompanyData Model with Conflict Resolution

Merges JSON and Markdown data sources with conflict resolution and data source tracking.
Priority: Markdown > JSON (when conflicts exist)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

from ..domain.models import Company, FinancialMetric, ConfidenceLevel, AIMaturity, ThreatLevel, CompanyTier
from .loaders import CompetitorDataLoader
from ..extractors.markdown_extractor import MarkdownExtractor
from ..analytics.confidence_weighting import populate_signal_confidences

from .connectors.sec_edgar_connector import SECEdgarConnector

from .connectors.companies_house_connector import CompaniesHouseConnector

from .connectors.news_signal_detector import NewsSignalDetector
from .enrichment_validators import (
    validate_revenue, validate_growth_rate, validate_employee_count,
    validate_profit_margin, validate_no_nan_inf, validate_data_freshness,
    validate_cross_field_consistency, validate_against_existing_data
)
from .enrichment_orchestrator import EnrichmentOrchestrator, EnrichmentConfig, EnrichmentSource, EnrichmentField
from .enrichment_config import UnifiedCompanyLoaderConfig, get_config, EnvValidator
from .enrichment_service import ConnectorFactory, DataValidationService, ErrorHandlingService, EnrichmentService, CacheService, MetricsService
from .security_hardening import audit_logger, InputValidator, security_headers

logger = logging.getLogger(__name__)

# Error message formatting helper
def format_enrichment_error(source: str, context: str, error: str) -> str:
    """Format enrichment error messages consistently.
    
    Args:
        source: Data source (e.g., 'SEC EDGAR', 'Companies House', 'News Signals')
        context: Context info (e.g., ticker, company_number, company name)
        error: Error message or exception
    
    Returns:
        Formatted error string: 'SOURCE [context]: error'
    """
    if context:
        return f"{source} [{context}]: {str(error)[:200]}"  # Truncate to 200 chars
    return f"{source}: {str(error)[:200]}"

def safe_append_source(sources: List[str], source: str) -> None:
    """Safely append to enrichment_sources, preventing duplicates.
    
    Args:
        sources: List of enrichment sources
        source: Source to append (e.g., 'SEC EDGAR')
    """
    if source not in sources:
        sources.append(source)


def categorize_error(error_type: str, error: Exception | str) -> str:
    """Categorize error into API_ERROR, DATA_ERROR, VALIDATION_ERROR, or UNKNOWN.
    
    Args:
        error_type: Type of error (e.g., 'API', 'DATA', 'VALIDATION')
        error: The error object or message
    
    Returns:
        Error category string
    """
    error_str = str(error).lower()
    
    if error_type.upper() == 'API':
        return 'API_ERROR'
    elif error_type.upper() == 'DATA':
        return 'DATA_ERROR'
    elif error_type.upper() == 'VALIDATION':
        return 'VALIDATION_ERROR'
    else:
        return 'UNKNOWN'


def add_error_severity(error_msg: str, severity: str) -> str:
    """Add severity prefix to error message.
    
    Args:
        error_msg: The error message
        severity: Severity level (CRITICAL, WARNING, INFO)
    
    Returns:
        Error message with severity prefix
    """
    severity_upper = severity.upper()
    if severity_upper not in ('CRITICAL', 'WARNING', 'INFO'):
        severity_upper = 'INFO'
    return f"[{severity_upper}] {error_msg}"


def build_error_context(ticker: str | None = None, company_number: str | None = None, year: int | None = None, attempt_count: int | None = None) -> str:
    """Build error context string from enrichment parameters.
    
    Args:
        ticker: Stock ticker symbol
        company_number: UK company number
        year: Year being enriched
        attempt_count: Number of attempts made
    
    Returns:
        Context string for error messages
    """
    parts = []
    if ticker:
        parts.append(f"ticker={ticker}")
    if company_number:
        parts.append(f"company_number={company_number}")
    if year:
        parts.append(f"year={year}")
    if attempt_count:
        parts.append(f"attempt={attempt_count}")
    return ', '.join(parts) if parts else 'unknown context'


# Phase 2.B: Error Tracking Infrastructure Helpers

def track_error_with_timestamp(company: 'UnifiedCompany', error_msg: str, field: str | None = None) -> None:
    """Track error with timestamp and optional field association.
    
    Args:
        company: Company object to track error on
        error_msg: Error message
        field: Optional field name if error is field-specific
    """
    # Append to main error list
    company.enrichment_errors.append(error_msg)
    
    # Track timestamp
    error_key = f"error_{len(company.enrichment_errors)}"
    company.enrichment_error_timestamps[error_key] = datetime.now(timezone.utc)
    
    # Track per-field if specified
    if field:
        if field not in company.enrichment_errors_per_field:
            company.enrichment_errors_per_field[field] = []
        company.enrichment_errors_per_field[field].append(error_msg)
    
    # Increment error count
    company.enrichment_error_count += 1
    
    # Limit error accumulation to 50 most recent
    if len(company.enrichment_errors) > 50:
        company.enrichment_errors = company.enrichment_errors[-50:]
        company.enrichment_error_timestamps = {k: v for k, v in list(company.enrichment_error_timestamps.items())[-50:]}


def categorize_and_track_error(company: 'UnifiedCompany', error_msg: str, category: str) -> None:
    """Track error with category for metrics.
    
    Args:
        company: Company object to track error on
        error_msg: Error message
        category: Error category (API_ERROR, DATA_ERROR, VALIDATION_ERROR, UNKNOWN)
    """
    track_error_with_timestamp(company, error_msg)
    
    # Track category count
    if category not in company.enrichment_error_categories:
        company.enrichment_error_categories[category] = 0
    company.enrichment_error_categories[category] += 1

class UnifiedCompany(Company):
    """Extended Company model with data source tracking and merge conflict documentation."""

    data_source_per_field: Dict[str, str] = {}  # Track where each field came from
    merge_conflicts: List[str] = []  # Fields where JSON and Markdown differed
    merge_priority: str = "Markdown > JSON"  # Document priority rules
    merge_timestamp: Optional[datetime] = None


class UnifiedCompanyLoader:
    """Load and merge company data from JSON and Markdown sources."""

    def __init__(self, sec_connector: Optional[SECEdgarConnector] = None, companies_house_connector: Optional[CompaniesHouseConnector] = None, news_detector: Optional[NewsSignalDetector] = None):

        self.json_loader = CompetitorDataLoader()

        self.markdown_extractor = MarkdownExtractor()


        # Initialize configuration system
        try:
            self.config = get_config()
            logger.info("✅ Enrichment configuration loaded successfully")
        except Exception as e:
            logger.warning(f"Configuration initialization failed: {e}, using defaults")
            self.config = UnifiedCompanyLoaderConfig()

        # Initialize connectors via factory
        factory = ConnectorFactory()
        
        try:
            self.sec_connector = sec_connector or factory.create_sec_connector(self.config)
            if self.sec_connector:
                logger.info("✅ SEC EDGAR connector initialized via factory")
        except Exception as e:
            logger.warning(f"SEC EDGAR connector initialization failed: {e}")
            self.sec_connector = None

        try:
            self.companies_house_connector = companies_house_connector or factory.create_companies_house_connector(self.config)
            if self.companies_house_connector:
                logger.info("✅ Companies House connector initialized via factory")
        except Exception as e:
            logger.warning(f"Companies House connector initialization failed: {e}")
            self.companies_house_connector = None

        try:
            self.news_detector = news_detector or factory.create_news_detector(self.config)
            if self.news_detector:
                logger.info("✅ News Signal detector initialized via factory")
        except Exception as e:
            logger.warning(f"News Signal Detector initialization failed: {e}")
            self.news_detector = None
        

        # EPIC-FIX-003: Configurable markdown directory (was hardcoded to 2026-02-23/dutch_market)
        # Use config if available, otherwise use environment variable, then fallback to default
        import os
        if hasattr(self.config, 'markdown_dir') and self.config.markdown_dir:
            self.markdown_dir = Path(self.config.markdown_dir)
        else:
            # Check for environment variable override
            env_market_dir = os.getenv('DUTCH_MARKET_DIR')
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
        

    def load_unified_companies(self) -> List[UnifiedCompany]:
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
                unified = self._merge_companies(json_company, markdown_company)
            else:
                # Use JSON only
                unified = self._convert_to_unified(json_company, source="JSON")

            unified_companies.append(unified)

        # Add Markdown-only companies (if any)
        json_ids = {c.id for c in json_companies}
        for markdown_company in markdown_companies:
            if markdown_company.id not in json_ids:
                unified = self._convert_to_unified(markdown_company, source="Markdown")
                unified_companies.append(unified)

        logger.info(f"Created {len(unified_companies)} unified companies")

        

        # Enrich companies from connectors (SEC EDGAR, Companies House, News Signals)

        logger.info("Starting connector enrichment...")

        enriched_companies = []

        for company in unified_companies:

            try:

                enriched = self.enrich_from_connectors(company)

                enriched_companies.append(enriched)

            except Exception as e:

                logger.warning(f"Enrichment failed for {company.name}: {e}")

                enriched_companies.append(company)  # Use original if enrichment fails

        

        logger.info(f"Enrichment complete. {len([c for c in enriched_companies if c.enrichment_sources])} companies enriched")

        

        # Populate signal confidences for scoring component weighting

        for company in enriched_companies:

            populate_signal_confidences(company)

        

        return enriched_companies


    def _load_markdown_companies(self) -> List[Company]:
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
            except Exception as e:
                logger.warning(f"Failed to load Markdown file {md_file}: {e}")

        return companies

    def _merge_companies(self, json_company: Company, markdown_company: Company) -> UnifiedCompany:
        """
        Merge JSON and Markdown companies with conflict resolution.
        Priority: Markdown > JSON
        """

        conflicts = []
        data_sources = {}

        # Start with JSON company as base
        merged = UnifiedCompany(**json_company.model_dump())

        # Merge financial metrics
        if json_company.financials and markdown_company.financials:
            merged_financials = self._merge_financials(
                json_company.financials, markdown_company.financials, conflicts, data_sources
            )
            merged.financials = merged_financials
        elif markdown_company.financials:
            merged.financials = markdown_company.financials
            data_sources["financials"] = "Markdown"

        # Merge other fields with Markdown priority
        if markdown_company.tier != json_company.tier:
            conflicts.append("tier")
            merged.tier = markdown_company.tier
            data_sources["tier"] = "Markdown"
        else:
            data_sources["tier"] = "JSON"

        if markdown_company.ai_maturity != json_company.ai_maturity:
            conflicts.append("ai_maturity")
            merged.ai_maturity = markdown_company.ai_maturity
            data_sources["ai_maturity"] = "Markdown"
            # Infer AI score from AI maturity when there's a conflict
            self._infer_ai_score_from_maturity(merged, markdown_company.ai_maturity)
        else:
            data_sources["ai_maturity"] = "JSON"
            # Also check if AI score is 0 but maturity is Strong/Very Strong - fix contradiction
            if merged.ai_score == 0 and merged.ai_maturity in ["Strong", "Very Strong"]:
                self._infer_ai_score_from_maturity(merged, merged.ai_maturity)

        if markdown_company.threat_level != json_company.threat_level:
            conflicts.append("threat_level")
            merged.threat_level = markdown_company.threat_level
            data_sources["threat_level"] = "Markdown"
        else:
            data_sources["threat_level"] = "JSON"

        if markdown_company.geographic_presence != json_company.geographic_presence:
            conflicts.append("geographic_presence")
            merged.geographic_presence = markdown_company.geographic_presence
            data_sources["geographic_presence"] = "Markdown"
        else:
            data_sources["geographic_presence"] = "JSON"

        # Set tracking fields
        merged.data_source_per_field = data_sources
        merged.merge_conflicts = conflicts
        merged.merge_timestamp = datetime.now(timezone.utc)

        if conflicts:
            logger.info(f"Merged {merged.name} with {len(conflicts)} conflicts: {conflicts}")

        return merged

    def _merge_financials(
        self,
        json_fin: FinancialMetric,
        markdown_fin: FinancialMetric,
        conflicts: List[str],
        data_sources: Dict[str, str],
    ) -> FinancialMetric:
        """Merge financial metrics with Markdown priority."""

        # Start with JSON
        merged = FinancialMetric(**json_fin.model_dump())

        # Apply Markdown values with priority
        if markdown_fin.revenue is not None and markdown_fin.revenue != json_fin.revenue:
            conflicts.append("revenue")
            merged.revenue = markdown_fin.revenue
            merged.revenue_confidence = markdown_fin.revenue_confidence
            data_sources["revenue"] = "Markdown"
        else:
            data_sources["revenue"] = "JSON"

        if markdown_fin.growth_rate is not None and markdown_fin.growth_rate != json_fin.growth_rate:
            conflicts.append("growth_rate")
            merged.growth_rate = markdown_fin.growth_rate
            merged.growth_confidence = markdown_fin.growth_confidence
            data_sources["growth_rate"] = "Markdown"
        else:
            data_sources["growth_rate"] = "JSON"

        if markdown_fin.employees is not None and markdown_fin.employees != json_fin.employees:
            conflicts.append("employees")
            merged.employees = markdown_fin.employees
            merged.employees_confidence = markdown_fin.employees_confidence
            data_sources["employees"] = "Markdown"
        else:
            data_sources["employees"] = "JSON"

        if markdown_fin.profit_margin is not None and markdown_fin.profit_margin != json_fin.profit_margin:
            conflicts.append("profit_margin")
            merged.profit_margin = markdown_fin.profit_margin
            merged.margin_confidence = markdown_fin.margin_confidence
            data_sources["profit_margin"] = "Markdown"
        else:
            data_sources["profit_margin"] = "JSON"

        if markdown_fin.funding_raised is not None and markdown_fin.funding_raised != json_fin.funding_raised:
            conflicts.append("funding_raised")
            merged.funding_raised = markdown_fin.funding_raised
            merged.funding_confidence = markdown_fin.funding_confidence
            data_sources["funding_raised"] = "Markdown"
        else:
            data_sources["funding_raised"] = "JSON"

        if markdown_fin.valuation is not None and markdown_fin.valuation != json_fin.valuation:
            conflicts.append("valuation")
            merged.valuation = markdown_fin.valuation
            merged.valuation_confidence = markdown_fin.valuation_confidence
            data_sources["valuation"] = "Markdown"
        else:
            data_sources["valuation"] = "JSON"

        return merged

    def _convert_to_unified(self, company: Company, source: str) -> UnifiedCompany:
        """Convert a Company to UnifiedCompany with source tracking."""

        unified = UnifiedCompany(**company.model_dump())

        # Track all fields as coming from single source
        unified.data_source_per_field = {
            "revenue": source,
            "growth_rate": source,
            "employees": source,
            "profit_margin": source,
            "funding_raised": source,
            "valuation": source,
            "tier": source,
            "ai_maturity": source,
            "threat_level": source,
            "geographic_presence": source,
        }
        unified.merge_conflicts = []
        unified.merge_timestamp = datetime.now(timezone.utc)

        return unified


    def _infer_ai_score_from_maturity(self, company: UnifiedCompany, ai_maturity: str) -> None:
        """Infer AI score from AI maturity level when there's a conflict.
        
        Maps AI maturity levels to scores using the CompetitivePositionConfig mapping.
        This fixes contradictions like 'Strong' maturity with 0/10 score.
        """
        from ..core.scoring_config import CompetitivePositionConfig
        
        config = CompetitivePositionConfig()
        ai_maturity_scores = config.ai_maturity_scores
        
        # Map AI maturity to score (0-10 scale)
        # CompetitivePositionConfig uses -1.0 to 2.5 scale, so we need to normalize to 0-10
        maturity_score = ai_maturity_scores.get(ai_maturity, 0.0)
        # Normalize: -1.0 to 2.5 range maps to 0-10 range
        # Formula: ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
        normalized_score = ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
        normalized_score = max(0, min(10, int(round(normalized_score))))  # Round to int and clamp to 0-10
        
        company.ai_score = normalized_score
        logger.info(f"Inferred AI score {normalized_score}/10 for {company.name} from AI maturity '{ai_maturity}'")


    def enrich_from_connectors(self, company: UnifiedCompany) -> UnifiedCompany:
        """Enrich company data from all available connectors.
        
        Uses EnrichmentOrchestrator to:
        - Skip enrichment if data already complete
        - Determine optimal source order
        - Handle confidence-aware overwriting
        - Ensure immutability (returns new object)
        - Track enrichment costs and errors
        
        Calls SEC EDGAR, Companies House, and News Signal Detector in sequence.
        Only fills NULL fields - never replaces existing data.
        """
        
        orchestrator = EnrichmentOrchestrator(EnrichmentConfig())
        
        if orchestrator.should_skip_enrichment(company):
            logger.debug(f"Skipping enrichment for {company.name} - data already complete or no identifiers")
            return company
        
        enriched = orchestrator.create_enrichment_copy(company)
        
        sources = orchestrator.get_enrichment_order(enriched)
        fields = orchestrator.get_fields_to_enrich(enriched)
        
        if not sources or not fields:
            logger.debug(f"No enrichment needed for {enriched.name}")
            return enriched
        
        for source in sources:
            try:
                if source == EnrichmentSource.SEC_EDGAR:
                    enriched = self.fill_nulls_from_sec_edgar(enriched)
                elif source == EnrichmentSource.COMPANIES_HOUSE:
                    enriched = self.fill_nulls_from_companies_house(enriched)
                elif source == EnrichmentSource.NEWS_SIGNALS:
                    enriched = self.attach_news_signals(enriched)
            except Exception as e:
                logger.error(f"Enrichment from {source} failed for {enriched.name}: {e}")
                enriched = orchestrator.rollback_on_error(company, enriched, str(e))
                break
        
        return enriched


    def enrich_batch(self, companies: List[UnifiedCompany], batch_size: int = 10) -> List[UnifiedCompany]:
        """Batch enrich companies with caching and performance tracking (Phase B).
        
        Args:
            companies: List of companies to enrich
            batch_size: Number of companies to process per batch (default: 10)
        
        Returns:
            List of enriched companies
        """
        import time
        
        enriched_companies = []
        total_batches = (len(companies) + batch_size - 1) // batch_size
        
        logger.info(f"✅ Starting batch enrichment: {len(companies)} companies in {total_batches} batches of {batch_size}")
        
        for batch_num, i in enumerate(range(0, len(companies), batch_size), 1):
            batch = companies[i:i + batch_size]
            batch_start = time.time()
            
            logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} companies)")
            
            for company in batch:
                try:
                    # Check cache first
                    cache_key = f"enriched_{company.id}_{company.ticker or company.company_number}"
                    cached_result = self.cache.get(cache_key)
                    
                    if cached_result:
                        logger.debug(f"Cache hit for {company.name}")
                        enriched_companies.append(cached_result)
                        self.metrics.record_enrichment(0, True)  # 0ms for cache
                        continue
                    
                    # Enrich company
                    enriched = self.enrich_from_connectors(company)
                    enriched_companies.append(enriched)
                    
                    # Cache result
                    self.cache.set(cache_key, enriched)
                    self.metrics.record_enrichment(0, True)
                    
                except Exception as e:
                    logger.warning(f"Batch enrichment failed for {company.name}: {e}")
                    enriched_companies.append(company)  # Use original if enrichment fails
                    self.metrics.record_enrichment(0, False)
            
            batch_duration = (time.time() - batch_start) * 1000  # Convert to ms
            logger.info(f"Batch {batch_num}/{total_batches} completed in {batch_duration:.2f}ms")
        
        # Log final metrics
        metrics_summary = self.metrics.get_summary()
        logger.info(f"✅ Batch enrichment complete: {metrics_summary['successful']} successful, {metrics_summary['failed']} failed, avg {metrics_summary['avg_duration_ms']:.2f}ms per company")
        
        return enriched_companies
    
    def get_enrichment_metrics(self) -> dict:
        """Get current enrichment metrics (Phase B).
        
        Returns:
            Dictionary of enrichment performance metrics
        """
        return self.metrics.get_summary()
    
    def clear_enrichment_cache(self) -> None:
        """Clear all cached enrichment results (Phase B)."""
        self.cache.clear()
        logger.info("✅ Enrichment cache cleared")



    def fill_nulls_from_sec_edgar(self, company: UnifiedCompany) -> UnifiedCompany:

        """Fill NULL financial fields from SEC EDGAR for US companies.

        

        Only fills: revenue, growth_rate, employees, profit_margin

        Only for companies with valid ticker symbols.

        Sets confidence to CONFIRMED for SEC-sourced data.

        """

        logger.info(f"[CONNECTOR-SEC-START] SEC EDGAR enrichment STARTED for {company.name} (ticker={company.ticker})")


        # Skip if no SEC connector available

        if not self.sec_connector:

            return company

        

        # Skip if no ticker

        if not company.ticker or not company.ticker.strip():

            return company

        

        # Skip if no financials object

        if not company.financials:

            return company

        

        try:

            # Try to fetch 10-K for current year first, then previous years

            current_year = datetime.now().year

            

            filing_data = None

            for year_offset in range(0, 3):  # Try current year and 2 previous years

                try:

                    year = current_year - year_offset

                    filing_data = self.sec_connector.fetch_filing(

                        ticker=company.ticker.upper().strip(),

                        year=year,

                        form_type="10-K"

                    )

                    if filing_data:

                        break

                except ValueError as e:

                    logger.debug(f"SEC EDGAR fetch failed for {company.ticker} year {year}: {e}")

                    continue

                except RuntimeError as e:

                    logger.debug(f"SEC EDGAR API error for {company.ticker} year {year}: {e}")

                    continue

            

            if not filing_data:

                logger.debug(f"No SEC EDGAR data found for {company.name} ({company.ticker})")

                # Track error: all retries failed

                error_context = build_error_context(ticker=company.ticker)
                error_msg = format_enrichment_error('SEC EDGAR', error_context, 'No data found after retrying 3 years')
                company.enrichment_errors.append(error_msg)

                return company

            

            # Fill NULL fields only - never replace existing data
            # VALIDATE data before filling to prevent garbage from APIs

            # Helper function to check if value is valid number (not NaN/Inf)
            def is_valid_number(val):
                if not isinstance(val, (int, float)):
                    return False
                if val != val:  # NaN check
                    return False
                if val == float('inf') or val == float('-inf'):
                    return False
                return True

            # Validate and fill revenue: must be positive, < 1 quadrillion
            if filing_data.get("revenue") is not None:
                revenue = filing_data["revenue"]
                if is_valid_number(revenue) and 0 < revenue < 1e15:
                    if company.financials.revenue is None:
                        company.financials.revenue = revenue
                        company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
                        company.data_source_per_field["revenue"] = "SEC EDGAR"
                        company.enrichment_sources.append("SEC EDGAR")
                        logger.debug(f"Filled revenue for {company.name} from SEC EDGAR: {revenue}")
                elif is_valid_number(revenue):
                    logger.warning(f"SEC EDGAR revenue out of range for {company.name}: {revenue}")
                else:
                    logger.warning(f"SEC EDGAR revenue invalid for {company.name}: {revenue}")

            # Validate and fill growth_rate: must be between -50% and 200%
            if filing_data.get("growth_rate") is not None:
                growth_rate = filing_data["growth_rate"]
                if is_valid_number(growth_rate) and -0.5 <= growth_rate <= 2.0:
                    if company.financials.growth_rate is None:
                        company.financials.growth_rate = growth_rate
                        company.financials.growth_confidence = ConfidenceLevel.CONFIRMED
                        company.data_source_per_field["growth_rate"] = "SEC EDGAR"
                        logger.debug(f"Filled growth_rate for {company.name} from SEC EDGAR: {growth_rate}")
                elif is_valid_number(growth_rate):
                    logger.warning(f"SEC EDGAR growth_rate out of range for {company.name}: {growth_rate}")
                else:
                    logger.warning(f"SEC EDGAR growth_rate invalid for {company.name}: {growth_rate}")

            # Validate and fill employees: must be positive integer, < 10 million
            if filing_data.get("employees") is not None:
                employees = filing_data["employees"]
                try:
                    employees_int = int(employees) if not isinstance(employees, int) else employees
                    if 0 < employees_int < 10_000_000:
                        if company.financials.employees is None:
                            company.financials.employees = employees_int
                            company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
                            company.data_source_per_field["employees"] = "SEC EDGAR"
                            logger.debug(f"Filled employees for {company.name} from SEC EDGAR: {employees_int}")
                    else:
                        logger.warning(f"SEC EDGAR employees out of range for {company.name}: {employees_int}")
                except (ValueError, TypeError):
                    logger.warning(f"SEC EDGAR employees invalid for {company.name}: {employees}")

            # Validate and fill profit_margin: must be between -100% and 100%
            if filing_data.get("profit_margin") is not None:
                profit_margin = filing_data["profit_margin"]
                if is_valid_number(profit_margin) and -1.0 <= profit_margin <= 1.0:
                    if company.financials.profit_margin is None:
                        company.financials.profit_margin = profit_margin
                        company.financials.margin_confidence = ConfidenceLevel.CONFIRMED
                        company.data_source_per_field["profit_margin"] = "SEC EDGAR"
                        logger.debug(f"Filled profit_margin for {company.name} from SEC EDGAR: {profit_margin}")
                elif is_valid_number(profit_margin):
                    logger.warning(f"SEC EDGAR profit_margin out of range for {company.name}: {profit_margin}")
                else:
                    logger.warning(f"SEC EDGAR profit_margin invalid for {company.name}: {profit_margin}")


            # Store additional metrics in profitability_raw_metrics for reference

            if filing_data.get("ebitda"):

                company.profitability_raw_metrics["ebitda_sec"] = filing_data["ebitda"]

            if filing_data.get("cash_position"):

                company.profitability_raw_metrics["cash_position_sec"] = filing_data["cash_position"]

            

            # Track enrichment timestamp

            company.enrichment_timestamps["SEC EDGAR"] = datetime.now(timezone.utc)

            logger.info(f"[CONNECTOR-SEC-END] SEC EDGAR enrichment COMPLETED for {company.name}. Revenue: {company.financials.revenue}")


            return company

            

        except ValueError as e:

            logger.warning(f"SEC EDGAR enrichment failed for {company.name}: {e}")

            error_context = build_error_context(ticker=company.ticker)
            error_msg = format_enrichment_error('SEC EDGAR', error_context, str(e))
            company.enrichment_errors.append(error_msg)

            return company

        except RuntimeError as e:

            logger.warning(f"SEC EDGAR API error for {company.name}: {e}")

            error_context = build_error_context(ticker=company.ticker)
            error_msg = format_enrichment_error('SEC EDGAR', error_context, str(e))
            company.enrichment_errors.append(error_msg)

            return company



    def fill_nulls_from_companies_house(self, company: UnifiedCompany) -> UnifiedCompany:

        """Fill NULL financial fields from Companies House for UK companies.

        

        Only fills: revenue, employees, profit_margin

        Only for companies with valid company_number.

        Sets confidence to CONFIRMED for Companies House data.

        """
        logger.info(f"[CONNECTOR-CH-START] Companies House enrichment STARTED for {company.name} (company_number={company.company_number})")

        if not self.companies_house_connector:

            return company

        

        # Skip if no company_number

        if not company.company_number or not company.company_number.strip():

            return company

        

        # Skip if no financials object

        if not company.financials:

            return company

        

        try:

            ch_data = self.companies_house_connector.get_company_metrics(

                company_number=company.company_number.strip()

            )

            

            if not ch_data:

                logger.debug(f"No Companies House data found for {company.name} ({company.company_number})")

                # Track error: API returned no data

                error_context = build_error_context(company_number=company.company_number)
                error_msg = format_enrichment_error('Companies House', error_context, 'No data found')
                company.enrichment_errors.append(error_msg)

                return company

            

            # Fill NULL fields only - never replace existing data
            # VALIDATE data before filling to prevent garbage from APIs

            # Helper function to check if value is valid number (not NaN/Inf)
            def is_valid_number(val):
                if not isinstance(val, (int, float)):
                    return False
                if val != val:  # NaN check
                    return False
                if val == float('inf') or val == float('-inf'):
                    return False
                return True

            # Validate and fill revenue: must be positive, < 1 quadrillion
            # Note: Companies House returns GBP, convert to EUR (1 GBP ≈ 1.17 EUR)
            if ch_data.get("revenue") is not None:
                revenue_gbp = ch_data["revenue"]
                if is_valid_number(revenue_gbp) and 0 < revenue_gbp < 1e15:
                    # Convert GBP to EUR (approximate: 1 GBP = 1.17 EUR)
                    revenue_eur = revenue_gbp * 1.17
                    if company.financials.revenue is None:
                        company.financials.revenue = revenue_eur
                        company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
                        company.data_source_per_field["revenue"] = "Companies House"
                        company.enrichment_sources.append("Companies House")
                        logger.debug(f"Filled revenue for {company.name} from Companies House: {revenue_eur} EUR (from {revenue_gbp} GBP)")
                elif is_valid_number(revenue_gbp):
                    logger.warning(f"Companies House revenue out of range for {company.name}: {revenue_gbp}")
                else:
                    logger.warning(f"Companies House revenue invalid for {company.name}: {revenue_gbp}")

            # Validate and fill employees: must be positive integer, < 10 million
            # Note: Companies House may return ranges like "10-50", parse to midpoint
            if ch_data.get("employees") is not None:
                employees = ch_data["employees"]
                employees_int = None
                try:
                    # Try direct int conversion first
                    if isinstance(employees, int):
                        employees_int = employees
                    elif isinstance(employees, str):
                        # Handle range format like "10-50"
                        if '-' in employees:
                            parts = employees.split('-')
                            if len(parts) == 2:
                                low = int(parts[0].strip())
                                high = int(parts[1].strip())
                                employees_int = (low + high) // 2  # Use midpoint
                            else:
                                employees_int = int(employees)
                        else:
                            employees_int = int(employees)
                    else:
                        employees_int = int(employees)
                    
                    if employees_int and 0 < employees_int < 10_000_000:
                        if company.financials.employees is None:
                            company.financials.employees = employees_int
                            company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
                            company.data_source_per_field["employees"] = "Companies House"
                            logger.debug(f"Filled employees for {company.name} from Companies House: {employees_int}")
                    elif employees_int:
                        logger.warning(f"Companies House employees out of range for {company.name}: {employees_int}")
                except (ValueError, TypeError):
                    logger.warning(f"Companies House employees invalid for {company.name}: {employees}")

            # Validate and fill profit_margin: must be between -100% and 100%
            if ch_data.get("profit_margin") is not None:
                profit_margin = ch_data["profit_margin"]
                if is_valid_number(profit_margin) and -1.0 <= profit_margin <= 1.0:
                    if company.financials.profit_margin is None:
                        company.financials.profit_margin = profit_margin
                        company.financials.margin_confidence = ConfidenceLevel.CONFIRMED
                        company.data_source_per_field["profit_margin"] = "Companies House"
                        logger.debug(f"Filled profit_margin for {company.name} from Companies House: {profit_margin}")
                elif is_valid_number(profit_margin):
                    logger.warning(f"Companies House profit_margin out of range for {company.name}: {profit_margin}")
                else:
                    logger.warning(f"Companies House profit_margin invalid for {company.name}: {profit_margin}")

            # Track enrichment timestamp

            company.enrichment_timestamps["Companies House"] = datetime.now(timezone.utc)

            
            logger.info(f"[CONNECTOR-CH-END] Companies House enrichment COMPLETED for {company.name}. Revenue: {company.financials.revenue}")
            return company

            

        except ValueError as e:

            logger.warning(f"Companies House enrichment failed for {company.name}: {e}")

            error_context = build_error_context(company_number=company.company_number)
            error_msg = format_enrichment_error('Companies House', error_context, str(e))
            company.enrichment_errors.append(error_msg)

            return company

        except RuntimeError as e:

            logger.warning(f"Companies House API error for {company.name}: {e}")

            error_context = build_error_context(company_number=company.company_number)
            error_msg = format_enrichment_error('Companies House', error_context, str(e))
            company.enrichment_errors.append(error_msg)

            return company



    def attach_news_signals(self, company: UnifiedCompany) -> UnifiedCompany:

        """Attach news-based signals from NewsSignalDetector.

        

        Detects: funding signals, partnership signals, key hire signals

        Appends to company.signals list with confidence scores.

        """
        logger.info(f"[CONNECTOR-NEWS-START] News Signals enrichment STARTED for {company.name}")

        # Skip if no news detector available

        if not self.news_detector:

            return company

        

        try:

            # Detect funding signals

            try:

                funding_signal = self.news_detector.detect_funding_signal(company.name)

                if funding_signal:

                    # Note: Company model doesn't have signals field, tracking via enrichment_sources instead


                    company.enrichment_sources.append("News Signals (Funding)")

                    logger.debug(f"Detected funding signal for {company.name}")

            except RuntimeError as e:

                logger.debug(f"Funding signal detection failed for {company.name}: {e}")

                error_context = build_error_context(ticker=company.ticker)
                error_msg = format_enrichment_error('News Signals', error_context, f'Funding detection: {str(e)}')
                company.enrichment_errors.append(error_msg)

            

            # Detect partnership signals

            try:

                partnership_signal = self.news_detector.detect_partnership_signal(company.name)

                if partnership_signal:

                    # Note: Company model doesn't have signals field, tracking via enrichment_sources instead


                    company.enrichment_sources.append("News Signals (Partnership)")

                    logger.debug(f"Detected partnership signal for {company.name}")

            except RuntimeError as e:

                logger.debug(f"Partnership signal detection failed for {company.name}: {e}")

                error_context = build_error_context(ticker=company.ticker)
                error_msg = format_enrichment_error('News Signals', error_context, f'Partnership detection: {str(e)}')
                company.enrichment_errors.append(error_msg)

            

            # Detect key hire signals

            try:

                key_hire_signal = self.news_detector.detect_key_hire_signal(company.name)

                if key_hire_signal:

                    # Note: Company model doesn't have signals field, tracking via enrichment_sources instead


                    company.enrichment_sources.append("News Signals (Key Hire)")

                    logger.debug(f"Detected key hire signal for {company.name}")

            except RuntimeError as e:

                logger.debug(f"Key hire signal detection failed for {company.name}: {e}")

                error_context = build_error_context(ticker=company.ticker)
                error_msg = format_enrichment_error('News Signals', error_context, f'Key hire detection: {str(e)}')
                company.enrichment_errors.append(error_msg)

            

            # Track enrichment timestamp

            company.enrichment_timestamps["News Signals"] = datetime.now(timezone.utc)

            
            logger.info(f"[CONNECTOR-NEWS-END] News Signals enrichment COMPLETED for {company.name}")
            return company

            

        except Exception as e:

            logger.warning(f"News signal enrichment failed for {company.name}: {e}")

            error_context = build_error_context(ticker=company.ticker)
            error_msg = format_enrichment_error('News Signals', error_context, str(e))
            company.enrichment_errors.append(error_msg)

            return company


# Global instance
unified_loader = UnifiedCompanyLoader()
