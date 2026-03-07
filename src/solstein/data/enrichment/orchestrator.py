"""Enrichment orchestrator for Solstein."""

from __future__ import annotations

import copy
import logging
from typing import Any, Callable, List, Optional

from ...domain.models import ConfidenceLevel
from ..source_policy import SourceTier, default_source_policy_catalog
from .models import (
    EnrichmentConfig,
    EnrichmentCost,
    EnrichmentField,
    EnrichmentResult,
    EnrichmentSource,
)

logger = logging.getLogger(__name__)


class EnrichmentOrchestrator:
    """Orchestrates enrichment operations with proper decision-making."""

    def __init__(self, config: Optional[EnrichmentConfig] = None):
        """Initialize orchestrator with configuration."""
        self.config = config or EnrichmentConfig()
        self.source_policies = default_source_policy_catalog()
        self._progress_callbacks: List[Callable[[str, int, int], None]] = []

    def get_source_policy_tier(self, source: EnrichmentSource) -> SourceTier:
        policy = self.source_policies.get(source.value)
        if not policy:
            return SourceTier.FREE
        return policy.tier

    def register_progress_callback(self, callback: Callable[[str, int, int], None]) -> None:
        """Register callback for progress tracking."""
        self._progress_callbacks.append(callback)

    def _notify_progress(self, message: str, current: int, total: int) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(message, current, total)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def should_skip_enrichment(self, company: "EnrichableCompany") -> bool:
        """Determine if enrichment should be skipped."""
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

    def _is_data_complete(self, company: "EnrichableCompany") -> bool:
        """Check if company data is already complete."""
        financials = company.financials
        if not financials:
            return False

        has_revenue = financials.revenue is not None and financials.revenue > 0
        has_growth = financials.growth_rate is not None
        has_employees = financials.employees is not None and financials.employees > 0
        has_margin = financials.profit_margin is not None

        return has_revenue and has_growth and has_employees and has_margin

    def get_enrichment_order(
        self, company: "EnrichableCompany", stage: SourceTier = SourceTier.FREE
    ) -> List[EnrichmentSource]:
        """Get prioritized enrichment order for company."""
        order = []

        for source in self.config.source_order:
            if not self.config.is_source_enabled(source):
                continue

            if self.get_source_policy_tier(source) != stage:
                continue

            # Check if we have required identifier for this source
            if source == EnrichmentSource.SEC_EDGAR:
                if not (company.ticker and company.ticker.strip()):
                    continue
            elif source == EnrichmentSource.COMPANIES_HOUSE:
                if not (company.company_number and company.company_number.strip()):
                    continue

            order.append(source)

        return order

    def get_paid_escalation_order(self, company: "EnrichableCompany") -> List[EnrichmentSource]:
        return self.get_enrichment_order(company, stage=SourceTier.PAID)

    def get_fields_to_enrich(self, company: "EnrichableCompany") -> List[EnrichmentField]:
        """Get list of fields that need enrichment."""
        fields = []
        financials = company.financials

        if not financials:
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
        """Determine if existing field should be overwritten."""
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

    def create_enrichment_copy(self, company: "EnrichableCompany") -> "EnrichableCompany":
        """Create a deep copy of company for enrichment."""
        return copy.deepcopy(company)

    def rollback_on_error(
        self,
        original: "EnrichableCompany",
        modified: "EnrichableCompany",
        error: str,
    ) -> "EnrichableCompany":
        """Rollback enrichment on error."""
        logger.error(f"Enrichment error for {original.name}: {error}. Rolling back.")
        return original

    def enrich_batch(
        self,
        companies: List["EnrichableCompany"],
        enrichment_fn: Callable[
            ["EnrichableCompany", EnrichmentSource, List[EnrichmentField]],
            "EnrichableCompany",
        ],
    ) -> List[EnrichmentResult]:
        """Enrich multiple companies efficiently."""
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
        company: "EnrichableCompany",
        enrichment_fn: Callable[
            ["EnrichableCompany", EnrichmentSource, List[EnrichmentField]],
            "EnrichableCompany",
        ],
    ) -> EnrichmentResult:
        """Enrich single company with orchestration logic."""
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
        error: Optional[str] = None,
    ) -> EnrichmentCost:
        """Track cost of enrichment operation."""
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
        """Compare two enrichment results and pick the best."""
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
