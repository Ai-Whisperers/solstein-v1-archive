"""Enrichment orchestrator for Solstein.

EPIC-022: Refactored to use modular policies for decision-making.

Uses policy classes for:
- Enrichment decisions (should skip, is complete, overwrite)
- Source ordering (enrichment order, paid escalation)
"""

from __future__ import annotations

import copy
import logging
from collections.abc import Callable
from typing import Any

from ...domain.models import ConfidenceLevel
from ..source_policy import SourceTier, default_source_policy_catalog
from .models import (
    EnrichmentConfig,
    EnrichmentCost,
    EnrichmentField,
    EnrichmentResult,
    EnrichmentSource,
)
from .policies import EnrichmentPolicy, SourceOrderingPolicy

logger = logging.getLogger(__name__)


class EnrichmentOrchestrator:
    """Orchestrates enrichment operations using Policy Pattern.

    EPIC-022: Refactored to delegate decision-making to policy classes.
    Policies handle enrichment decisions and source ordering.
    """

    def __init__(self, config: EnrichmentConfig | None = None):
        """Initialize orchestrator with configuration and policies.

        Args:
            config: Enrichment configuration
        """
        self.config = config or EnrichmentConfig()
        self.source_policies = default_source_policy_catalog()
        self._progress_callbacks: list[Callable[[str, int, int], None]] = []

        # Initialize policies
        self._decision_policy = EnrichmentPolicy(self.config)
        self._ordering_policy = SourceOrderingPolicy(self.config, self.source_policies)

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

    # Delegate to decision policy
    def should_skip_enrichment(self, company: EnrichableCompany) -> bool:
        """Determine if enrichment should be skipped."""
        return self._decision_policy.should_skip_enrichment(company)

    def _is_data_complete(self, company: EnrichableCompany) -> bool:
        """Check if company data is already complete."""
        return self._decision_policy.is_data_complete(company)

    def get_fields_to_enrich(self, company: EnrichableCompany) -> list[EnrichmentField]:
        """Get list of fields that need enrichment."""
        return self._decision_policy.get_fields_to_enrich(company)

    def should_overwrite_field(
        self,
        field: EnrichmentField,
        existing_value: Any,
        existing_confidence: ConfidenceLevel,
        new_value: Any,
        new_confidence: ConfidenceLevel,
    ) -> bool:
        """Determine if existing field should be overwritten."""
        return self._decision_policy.should_overwrite_field(
            field,
            existing_value,
            new_value,
            existing_confidence,
            new_confidence,
        )

    # Delegate to ordering policy
    def get_enrichment_order(
        self,
        company: EnrichableCompany,
        stage: SourceTier = SourceTier.FREE,
    ) -> list[EnrichmentSource]:
        """Get prioritized enrichment order for company."""
        return self._ordering_policy.get_enrichment_order(company, stage)

    def get_paid_escalation_order(self, company: EnrichableCompany) -> list[EnrichmentSource]:
        """Get order for paid escalation."""
        return self._ordering_policy.get_paid_escalation_order(company)

    # Utility methods
    def create_enrichment_copy(self, company: EnrichableCompany) -> EnrichableCompany:
        """Create a deep copy of company for enrichment."""
        return copy.deepcopy(company)

    def rollback_on_error(
        self,
        original: EnrichableCompany,
        modified: EnrichableCompany,
        error: str,
    ) -> EnrichableCompany:
        """Rollback enrichment on error."""
        logger.error(f"Enrichment error for {original.name}: {error}. Rolling back.")
        return original

    # Execution methods
    def enrich_batch(
        self,
        companies: list[EnrichableCompany],
        enrichment_fn: Callable[
            [EnrichableCompany, EnrichmentSource, list[EnrichmentField]],
            EnrichableCompany,
        ],
    ) -> list[EnrichmentResult]:
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
        company: EnrichableCompany,
        enrichment_fn: Callable[
            [EnrichableCompany, EnrichmentSource, list[EnrichmentField]],
            EnrichableCompany,
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

    # Control methods
    def request_cancellation(self) -> None:
        """Request cancellation of ongoing enrichment."""
        logger.info("Enrichment cancellation requested")
        self.config.cancel_requested = True

    def reset_cancellation(self) -> None:
        """Reset cancellation flag."""
        self.config.cancel_requested = False

    # Tracking methods
    def track_cost(
        self,
        source: EnrichmentSource,
        field: EnrichmentField,
        api_calls: int = 1,
        duration_ms: float = 0.0,
        success: bool = True,
        error: str | None = None,
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
