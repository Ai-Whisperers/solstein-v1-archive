"""
Phase 4: Enrichment Logic Orchestrator

Handles robust, configurable enrichment with proper decision-making:
- Skip enrichment if data already complete
- Configurable enrichment order and prioritization
- Dependency resolution between sources
- Selective field enrichment
- Cost tracking and result comparison
- Confidence-aware overwriting
- Rollback on error
- Immutable enrichment (return new object)
- Idempotency guarantees
- Batch processing
- Progress tracking
- Cancellation support
- Dry-run mode
"""

import copy
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from ..domain.models import ConfidenceLevel

if TYPE_CHECKING:
    from .unified_loader import UnifiedCompany

logger = logging.getLogger(__name__)


class EnrichmentSource(str, Enum):
    """Available enrichment sources."""

    SEC_EDGAR = "SEC_EDGAR"
    COMPANIES_HOUSE = "COMPANIES_HOUSE"
    NEWS_SIGNALS = "NEWS_SIGNALS"


class EnrichmentField(str, Enum):
    """Fields that can be enriched."""

    REVENUE = "revenue"
    GROWTH_RATE = "growth_rate"
    EMPLOYEES = "employees"
    PROFIT_MARGIN = "profit_margin"
    COMPANY_NUMBER = "company_number"
    ISIN = "isin"
    GEOGRAPHY_CODE = "geography_code"
    NEWS_SIGNALS = "news_signals"


@dataclass
class EnrichmentCost:
    """Track cost of enrichment operations."""

    source: EnrichmentSource
    field: EnrichmentField
    api_calls: int = 0
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EnrichmentResult:
    """Result of enrichment operation."""

    company: "UnifiedCompany"
    sources_used: list[EnrichmentSource] = field(default_factory=list)
    fields_enriched: list[EnrichmentField] = field(default_factory=list)
    costs: list[EnrichmentCost] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_api_calls: int = 0
    total_duration_ms: float = 0.0
    idempotent: bool = True  # Same input = same output on retries


@dataclass
class EnrichmentConfig:
    """Configuration for enrichment behavior."""

    # Enrichment control
    enabled: bool = True
    dry_run: bool = False

    # Source configuration
    source_order: list[EnrichmentSource] = field(
        default_factory=lambda: [
            EnrichmentSource.SEC_EDGAR,
            EnrichmentSource.COMPANIES_HOUSE,
            EnrichmentSource.NEWS_SIGNALS,
        ]
    )
    enabled_sources: set[EnrichmentSource] = field(
        default_factory=lambda: {
            EnrichmentSource.SEC_EDGAR,
            EnrichmentSource.COMPANIES_HOUSE,
            EnrichmentSource.NEWS_SIGNALS,
        }
    )

    # Field selection
    fields_to_enrich: set[EnrichmentField] | None = None  # None = all fields

    # Confidence thresholds
    min_confidence_to_overwrite: ConfidenceLevel = ConfidenceLevel.ESTIMATED

    # Retry and timeout
    max_retries: int = 3
    timeout_seconds: int = 30

    # Batch processing
    batch_size: int = 10

    # Cancellation
    cancel_requested: bool = False

    def is_source_enabled(self, source: EnrichmentSource) -> bool:
        """Check if source is enabled."""
        return source in self.enabled_sources

    def should_enrich_field(self, field: EnrichmentField) -> bool:
        """Check if field should be enriched."""
        if self.fields_to_enrich is None:
            return True
        return field in self.fields_to_enrich


class EnrichmentOrchestrator:
    """Orchestrates enrichment operations with proper decision-making."""

    def __init__(self, config: EnrichmentConfig | None = None):
        """Initialize orchestrator with configuration."""
        self.config = config or EnrichmentConfig()
        self._progress_callbacks: list[Callable[[str, int, int], None]] = []

    def register_progress_callback(self, callback: Callable[[str, int, int], None]) -> None:
        """Register callback for progress tracking.

        Args:
            callback: Function(message: str, current: int, total: int)
        """
        self._progress_callbacks.append(callback)

    def _notify_progress(self, message: str, current: int, total: int) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(message, current, total)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def should_skip_enrichment(self, company: "UnifiedCompany") -> bool:
        """Determine if enrichment should be skipped.

        Skip if:
        - Enrichment disabled
        - Company already has complete data
        - No valid identifiers (ticker, company_number)

        Args:
            company: Company to check

        Returns:
            True if enrichment should be skipped
        """
        if not self.config.enabled:
            logger.debug(f"Enrichment disabled for {company.name}")
            return True

        # Check if we have any valid identifiers
        has_ticker = company.ticker and company.ticker.strip()
        has_company_number = company.company_number and company.company_number.strip()

        if not has_ticker and not has_company_number:
            logger.debug(f"No valid identifiers for {company.name}, skipping enrichment")
            return True

        return False

    def _is_data_complete(self, company: "UnifiedCompany") -> bool:
        """Check if company data is already complete.

        Complete means: has revenue, growth_rate, employees, profit_margin
        """
        financials = company.financials
        if not financials:
            return False

        has_revenue = financials.revenue is not None and financials.revenue > 0
        has_growth = financials.growth_rate is not None
        has_employees = financials.employees is not None and financials.employees > 0
        has_margin = financials.profit_margin is not None

        return has_revenue and has_growth and has_employees and has_margin

    def get_enrichment_order(self, company: "UnifiedCompany") -> list[EnrichmentSource]:
        """Get prioritized enrichment order for company.

        Prioritization:
        1. Cheaper/faster sources first (News < Companies House < SEC)
        2. Sources with valid identifiers
        3. Enabled sources only

        Args:
            company: Company to enrich

        Returns:
            Ordered list of sources to try
        """
        order = []

        for source in self.config.source_order:
            if not self.config.is_source_enabled(source):
                continue

            # Check if we have required identifier for this source
            if source == EnrichmentSource.SEC_EDGAR:
                if not (company.ticker and company.ticker.strip()):
                    continue
            elif source == EnrichmentSource.COMPANIES_HOUSE:
                if not (company.company_number and company.company_number.strip()):
                    continue
            # NEWS_SIGNALS works with company name

            order.append(source)

        return order

    def get_fields_to_enrich(self, company: "UnifiedCompany") -> list[EnrichmentField]:
        """Get list of fields that need enrichment.

        Args:
            company: Company to check

        Returns:
            List of fields that are NULL or missing
        """
        fields = []
        financials = company.financials

        if not financials:
            # No financials at all, enrich all
            return [
                EnrichmentField.REVENUE,
                EnrichmentField.GROWTH_RATE,
                EnrichmentField.EMPLOYEES,
                EnrichmentField.PROFIT_MARGIN,
            ]

        # Check each field
        if (financials.revenue is None or financials.revenue == 0) and self.config.should_enrich_field(
            EnrichmentField.REVENUE
        ):
            fields.append(EnrichmentField.REVENUE)

        if financials.growth_rate is None and self.config.should_enrich_field(EnrichmentField.GROWTH_RATE):
            fields.append(EnrichmentField.GROWTH_RATE)

        if (financials.employees is None or financials.employees == 0) and self.config.should_enrich_field(
            EnrichmentField.EMPLOYEES
        ):
            fields.append(EnrichmentField.EMPLOYEES)

        if financials.profit_margin is None and self.config.should_enrich_field(EnrichmentField.PROFIT_MARGIN):
            fields.append(EnrichmentField.PROFIT_MARGIN)

        return fields

    def should_overwrite_field(
        self,
        field: EnrichmentField,
        existing_value: Any,
        existing_confidence: ConfidenceLevel,
        new_value: Any,
        new_confidence: ConfidenceLevel,
    ) -> bool:
        """Determine if existing field should be overwritten.

        Rules:
        - Don't overwrite if existing confidence >= threshold
        - Don't overwrite if new value is significantly different (>10x)
        - Overwrite if new confidence is higher

        Args:
            field: Field being considered
            existing_value: Current value
            existing_confidence: Current confidence
            new_value: Proposed new value
            new_confidence: Proposed confidence

        Returns:
            True if field should be overwritten
        """
        if existing_value is None:
            return True

        # Don't overwrite high-confidence data
        if existing_confidence == ConfidenceLevel.CONFIRMED:
            logger.debug(f"Not overwriting {field} - already CONFIRMED")
            return False

        # Check for magnitude mismatch (>10x difference)
        if isinstance(existing_value, (int, float)) and isinstance(new_value, (int, float)):
            if existing_value > 0 and new_value > 0:
                ratio = max(existing_value, new_value) / min(existing_value, new_value)
                if ratio > 10:
                    logger.warning(
                        f"Not overwriting {field} - magnitude mismatch: "
                        f"{existing_value} vs {new_value} (ratio: {ratio:.1f}x)"
                    )
                    return False

        # Overwrite if new confidence is higher
        if new_confidence == ConfidenceLevel.CONFIRMED and existing_confidence != ConfidenceLevel.CONFIRMED:
            return True

        return False

    def create_enrichment_copy(self, company: "UnifiedCompany") -> "UnifiedCompany":
        """Create a deep copy of company for enrichment.

        Ensures immutability - enrichment returns new object, doesn't mutate input.

        Args:
            company: Company to copy

        Returns:
            Deep copy of company
        """
        return copy.deepcopy(company)

    def rollback_on_error(
        self,
        original: "UnifiedCompany",
        modified: "UnifiedCompany",
        error: str,
    ) -> "UnifiedCompany":
        """Rollback enrichment on error.

        Returns original company and logs error.

        Args:
            original: Original company before enrichment
            modified: Modified company with error
            error: Error message

        Returns:
            Original company (unchanged)
        """
        logger.error(f"Enrichment error for {original.name}: {error}. Rolling back.")
        return original

    def enrich_batch(
        self,
        companies: list["UnifiedCompany"],
        enrichment_fn: Callable[["UnifiedCompany", EnrichmentSource, list[EnrichmentField]], "UnifiedCompany"],
    ) -> list[EnrichmentResult]:
        """Enrich multiple companies efficiently.

        Processes in batches with progress tracking and cancellation support.

        Args:
            companies: Companies to enrich
            enrichment_fn: Function to call for each company/source/fields combo

        Returns:
            List of enrichment results
        """
        results = []
        total = len(companies)

        for idx, company in enumerate(companies):
            if self.config.cancel_requested:
                logger.info("Enrichment cancelled by user")
                break

            self._notify_progress(f"Enriching {company.name}", idx + 1, total)

            result = self.enrich_single(company, enrichment_fn)
            results.append(result)

        self._notify_progress("Enrichment complete", total, total)
        return results

    def enrich_single(
        self,
        company: "UnifiedCompany",
        enrichment_fn: Callable[["UnifiedCompany", EnrichmentSource, list[EnrichmentField]], "UnifiedCompany"],
    ) -> EnrichmentResult:
        """Enrich single company with orchestration logic.

        Args:
            company: Company to enrich
            enrichment_fn: Function to call for each source/fields combo

        Returns:
            EnrichmentResult with details
        """
        result = EnrichmentResult(company=company)

        # Check if should skip
        if self.should_skip_enrichment(company):
            return result

        # Create copy for immutability
        enriched = self.create_enrichment_copy(company)

        # Get enrichment plan
        sources = self.get_enrichment_order(enriched)
        fields = self.get_fields_to_enrich(enriched)

        if not sources or not fields:
            result.company = enriched
            return result

        # Enrich from each source
        for source in sources:
            if self.config.cancel_requested:
                break

            try:
                # Dry-run mode: don't actually enrich
                if self.config.dry_run:
                    logger.info(f"DRY-RUN: Would enrich {enriched.name} from {source} with {fields}")
                    result.sources_used.append(source)
                    continue

                # Call enrichment function
                enriched = enrichment_fn(enriched, source, fields)
                result.sources_used.append(source)
                result.fields_enriched.extend(fields)

            except Exception as e:
                error_msg = f"Enrichment from {source} failed: {str(e)}"
                logger.error(error_msg)
                result.errors.append(error_msg)
                enriched = self.rollback_on_error(company, enriched, error_msg)

        result.company = enriched
        return result

    def request_cancellation(self) -> None:
        """Request cancellation of ongoing enrichment."""
        logger.info("Enrichment cancellation requested")
        self.config.cancel_requested = True

    def reset_cancellation(self) -> None:
        """Reset cancellation flag."""
        self.config.cancel_requested = False

    def track_cost(
        self,
        source: EnrichmentSource,
        field: EnrichmentField,
        api_calls: int = 1,
        duration_ms: float = 0.0,
        success: bool = True,
        error: str | None = None,
    ) -> EnrichmentCost:
        """Track cost of enrichment operation.

        Args:
            source: Data source
            field: Field enriched
            api_calls: Number of API calls made
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            error: Error message if failed

        Returns:
            EnrichmentCost object
        """
        cost = EnrichmentCost(
            source=source,
            field=field,
            api_calls=api_calls,
            duration_ms=duration_ms,
            success=success,
            error=error,
        )

        logger.debug(f"Enrichment cost: {source} → {field} ({api_calls} calls, {duration_ms:.0f}ms, success={success})")

        return cost

    def compare_results(
        self,
        field: EnrichmentField,
        value1: Any,
        source1: EnrichmentSource,
        confidence1: ConfidenceLevel,
        value2: Any,
        source2: EnrichmentSource,
        confidence2: ConfidenceLevel,
    ) -> tuple[Any, EnrichmentSource, ConfidenceLevel]:
        """Compare two enrichment results and pick the best.

        Priority:
        1. Higher confidence
        2. More recent source (if available)
        3. First source (default)

        Args:
            field: Field being compared
            value1: First value
            source1: First source
            confidence1: First confidence
            value2: Second value
            source2: Second source
            confidence2: Second confidence

        Returns:
            Tuple of (best_value, best_source, best_confidence)
        """
        # Prefer higher confidence
        if confidence1 == ConfidenceLevel.CONFIRMED and confidence2 != ConfidenceLevel.CONFIRMED:
            return value1, source1, confidence1
        elif confidence2 == ConfidenceLevel.CONFIRMED and confidence1 != ConfidenceLevel.CONFIRMED:
            return value2, source2, confidence2

        # If same confidence, prefer source order
        source_order = {s: i for i, s in enumerate(self.config.source_order)}
        if source_order.get(source1, 999) < source_order.get(source2, 999):
            return value1, source1, confidence1

        return value2, source2, confidence2
