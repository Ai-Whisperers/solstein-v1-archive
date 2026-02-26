"""
Phase 7: Code Organization - Enrichment Service Layer

Separates enrichment logic from loading logic into focused service classes:
- EnrichmentService: Orchestrates enrichment operations
- DataValidationService: Encapsulates data validation
- ErrorHandlingService: Centralized error handling
- ConnectorFactory: Creates connector instances
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone

from ..domain.models import ConfidenceLevel
from .enrichment_config import UnifiedCompanyLoaderConfig, get_config
from .enrichment_orchestrator import (
    EnrichmentOrchestrator,
    EnrichmentConfig,
    EnrichmentSource,
)
from .enrichment_validators import (
    validate_revenue,
    validate_growth_rate,
    validate_employee_count,
    validate_profit_margin,
)

logger = logging.getLogger(__name__)


class ConnectorFactory:
    """Factory for creating connector instances (Phase 7 item 130)."""

    @staticmethod
    def create_sec_connector(config: UnifiedCompanyLoaderConfig):
        """Create SEC EDGAR connector with configuration."""
        if not config.sec_edgar_config.enabled:
            return None
        from .connectors.sec_edgar_connector import SECEdgarConnector

        return SECEdgarConnector()

    @staticmethod
    def create_companies_house_connector(config: UnifiedCompanyLoaderConfig):
        """Create Companies House connector with configuration."""
        if not config.companies_house_config.enabled:
            return None
        from .connectors.companies_house_connector import CompaniesHouseConnector

        return CompaniesHouseConnector()

    @staticmethod
    def create_news_detector(config: UnifiedCompanyLoaderConfig):
        """Create News Signal detector with configuration."""
        if not config.news_signals_config.enabled:
            return None
        from .connectors.news_signal_detector import NewsSignalDetector

        return NewsSignalDetector()


class DataValidationService:
    """Service for data validation (Phase 7 item 128)."""

    @staticmethod
    def validate_enrichment_data(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate enriched data before accepting.

        Args:
            data: Dictionary of enriched data

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not data:
            return False, "Empty data dictionary"

        # Validate revenue
        if "revenue" in data:
            is_valid, error = validate_revenue(data["revenue"])
            if not is_valid:
                return False, f"Revenue validation failed: {error}"

        # Validate growth rate
        if "growth_rate" in data:
            is_valid, error = validate_growth_rate(data["growth_rate"])
            if not is_valid:
                return False, f"Growth rate validation failed: {error}"

        # Validate employees
        if "employees" in data:
            is_valid, error = validate_employee_count(data["employees"])
            if not is_valid:
                return False, f"Employee count validation failed: {error}"

        # Validate profit margin
        if "profit_margin" in data:
            is_valid, error = validate_profit_margin(data["profit_margin"])
            if not is_valid:
                return False, f"Profit margin validation failed: {error}"

        return True, None

    @staticmethod
    def sanitize_data(data: dict) -> dict:
        """
        Sanitize enriched data for database storage.

        Args:
            data: Raw enriched data

        Returns:
            Sanitized data dictionary
        """
        sanitized = {}
        for key, value in data.items():
            # Skip None values
            if value is None:
                continue

            # Convert types as needed
            if key in ("revenue", "employees", "profit_margin", "growth_rate"):
                if value == 0:
                    continue  # Skip zero values
                sanitized[key] = value
            else:
                sanitized[key] = value

        return sanitized


class ErrorHandlingService:
    """Service for centralized error handling (Phase 7 item 129)."""

    @staticmethod
    def handle_enrichment_error(
        company_name: str,
        source: str,
        error: Exception,
        attempt: int = 1,
    ) -> str:
        """
        Handle enrichment error with standardized processing.

        Args:
            company_name: Name of company being enriched
            source: Data source that failed
            error: Exception that occurred
            attempt: Attempt number

        Returns:
            Formatted error message
        """
        error_msg = str(error)

        # Sanitize error message (remove secrets)
        error_msg = ErrorHandlingService._sanitize_error_message(error_msg)

        # Format with context
        formatted = f"{source} [attempt {attempt}]: {error_msg}"

        # Log with appropriate level
        if attempt >= 3:
            logger.warning(f"Enrichment failed for {company_name}: {formatted}")
        else:
            logger.debug(f"Enrichment attempt {attempt} failed for {company_name}: {formatted}")

        return formatted

    @staticmethod
    def _sanitize_error_message(message: str) -> str:
        """
        Remove sensitive information from error messages.

        Args:
            message: Original error message

        Returns:
            Sanitized error message
        """
        # Remove API keys
        import re

        message = re.sub(r"sk-[a-zA-Z0-9]+", "[API_KEY]", message)
        message = re.sub(r"api[_-]?key[=:]\s*[a-zA-Z0-9]+", "[API_KEY]", message, flags=re.IGNORECASE)
        message = re.sub(r"password[=:]\s*[a-zA-Z0-9]+", "[PASSWORD]", message, flags=re.IGNORECASE)
        message = re.sub(r"token[=:]\s*[a-zA-Z0-9]+", "[TOKEN]", message, flags=re.IGNORECASE)

        # Truncate if too long
        if len(message) > 200:
            message = message[:200] + "..."

        return message


class EnrichmentService:
    """
    Service for enrichment operations (Phase 7 item 127).

    Encapsulates all enrichment logic, separate from loading.
    """

    def __init__(self, config: Optional[UnifiedCompanyLoaderConfig] = None):
        """
        Initialize enrichment service.

        Args:
            config: Configuration (uses global if not provided)
        """
        self.config = config or get_config()
        self.orchestrator = EnrichmentOrchestrator(
            EnrichmentConfig(
                enabled=self.config.enrichment_enabled,
                dry_run=self.config.dry_run,
            )
        )
        self.validator = DataValidationService()
        self.error_handler = ErrorHandlingService()

    def enrich_company(self, company) -> tuple:
        """
        Enrich single company using orchestrator.

        Args:
            company: UnifiedCompany to enrich

        Returns:
            Tuple of (enriched_company, sources_used, errors)
        """
        if not self.config.enrichment_enabled:
            logger.debug(f"Enrichment disabled, skipping {company.name}")
            return company, [], []

        if self.orchestrator.should_skip_enrichment(company):
            logger.debug(f"Data already complete for {company.name}, skipping enrichment")
            return company, [], []

        # Create immutable copy
        enriched = self.orchestrator.create_enrichment_copy(company)

        sources = self.orchestrator.get_enrichment_order(enriched)
        fields = self.orchestrator.get_fields_to_enrich(enriched)

        if not sources or not fields:
            return enriched, sources, []

        errors = []

        for source in sources:
            try:
                if source == EnrichmentSource.SEC_EDGAR:
                    enriched = self._enrich_from_sec(enriched)
                elif source == EnrichmentSource.COMPANIES_HOUSE:
                    enriched = self._enrich_from_companies_house(enriched)
                elif source == EnrichmentSource.NEWS_SIGNALS:
                    enriched = self._enrich_from_news_signals(enriched)
            except Exception as e:
                error_msg = self.error_handler.handle_enrichment_error(
                    company.name,
                    str(source),
                    e,
                )
                errors.append(error_msg)

                if self.config.rollback_on_error:
                    enriched = self.orchestrator.rollback_on_error(company, enriched, str(e))
                    break

        return enriched, sources, errors

    def _enrich_from_sec(self, company):
        """Enrich from SEC EDGAR (placeholder)."""
        # This would call the actual SEC enrichment method
        return company

    def _enrich_from_companies_house(self, company):
        """Enrich from Companies House (placeholder)."""
        # This would call the actual Companies House enrichment method
        return company

    def _enrich_from_news_signals(self, company):
        """Enrich from News Signals (placeholder)."""
        # This would call the actual News Signals enrichment method
        return company


class CacheService:
    """Service for result caching (Phase 7 item 134)."""

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize cache service.

        Args:
            ttl_hours: Time-to-live in hours
        """
        self.ttl_hours = ttl_hours
        self.cache = {}

    def get(self, key: str) -> Optional[dict]:
        """Get cached value if not expired."""
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]
        age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600

        if age_hours > self.ttl_hours:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: dict) -> None:
        """Cache value with current timestamp."""
        self.cache[key] = (value, datetime.now(timezone.utc))

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()


class MetricsService:
    """Service for metrics collection (Phase 7 item 136)."""

    def __init__(self):
        """Initialize metrics service."""
        self.enrichment_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_duration_ms = 0.0

    def record_enrichment(self, duration_ms: float, success: bool) -> None:
        """Record enrichment operation."""
        self.enrichment_count += 1
        self.total_duration_ms += duration_ms
        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_summary(self) -> dict:
        """Get metrics summary."""
        avg_duration = self.total_duration_ms / self.enrichment_count if self.enrichment_count > 0 else 0

        return {
            "total_enrichments": self.enrichment_count,
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": (self.success_count / self.enrichment_count * 100 if self.enrichment_count > 0 else 0),
            "avg_duration_ms": avg_duration,
            "total_duration_ms": self.total_duration_ms,
        }
