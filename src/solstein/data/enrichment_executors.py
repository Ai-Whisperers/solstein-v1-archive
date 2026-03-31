"""Enrichment orchestration helpers.

EPIC-020: Extracted from EnrichmentService.enrich_company method.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .source_policy import SourceTier

if TYPE_CHECKING:
    from .enrichment_orchestrator import EnrichmentOrchestrator
    from .enrichment_service import EnrichmentService
    from .enrichment_types import EnrichableCompany


class FreeEnrichmentExecutor:
    """Execute enrichment from free sources."""

    def __init__(self, service: EnrichmentService, orchestrator: EnrichmentOrchestrator):
        self.service = service
        self.orchestrator = orchestrator

    def execute(
        self,
        company: EnrichableCompany,
        enriched: EnrichableCompany,
        fields: list,
        sources_free: list,
    ) -> tuple[EnrichableCompany, list, list[str], list]:
        """Execute free source enrichment.

        Returns:
            Tuple of (enriched_company, sources_used, errors, remaining_fields)
        """
        from .enrichment_orchestrator import EnrichmentSource

        sources_used = []
        errors = []

        for source in sources_free:
            try:
                if source == EnrichmentSource.SEC_EDGAR:
                    enriched = self.service._enrich_from_sec(enriched)
                elif source == EnrichmentSource.COMPANIES_HOUSE:
                    enriched = self.service._enrich_from_companies_house(enriched)
                elif source == EnrichmentSource.NEWS_SIGNALS:
                    enriched = self.service._enrich_from_news_signals(enriched)

                sources_used.append(source)
                fields = self.orchestrator.get_fields_to_enrich(enriched)

                if not fields:
                    break
            except Exception as e:
                error_msg = self.service.error_handler.handle_enrichment_error(
                    company.name,
                    str(source),
                    e,
                )
                errors.append(error_msg)

                if self.service.config.rollback_on_error:
                    enriched = self.orchestrator.rollback_on_error(company, enriched, str(e))
                    break

        return enriched, sources_used, errors, fields


class PaidEscalationExecutor:
    """Execute paid escalation enrichment."""

    def __init__(self, service: EnrichmentService, orchestrator: EnrichmentOrchestrator):
        self.service = service
        self.orchestrator = orchestrator

    def execute(
        self,
        company: EnrichableCompany,
        enriched: EnrichableCompany,
        fields: list,
        sources_used: list,
        errors: list,
    ) -> tuple[EnrichableCompany, list, list[str], list]:
        """Execute paid escalation enrichment.

        Returns:
            Tuple of (enriched_company, sources_used, errors, remaining_fields)
        """
        from .enrichment_orchestrator import EnrichmentSource
        from .enrichment_service import _append_enrichment_audit

        unresolved_fields = [field.value for field in fields]

        # Add justifications for unresolved fields
        if hasattr(enriched, "metric_justifications"):
            for field_name in unresolved_fields:
                justification_key = f"paid_escalation:{field_name}"
                enriched.metric_justifications.setdefault(
                    justification_key,
                    "unresolved after free pass",
                )

        paid_sources = self.orchestrator.get_enrichment_order(enriched, stage=SourceTier.PAID)
        paid_attempts = 0

        for source in paid_sources:
            if paid_attempts >= self.service.config.paid_escalation_max_attempts:
                errors.append("Paid escalation attempt budget exceeded")
                _append_enrichment_audit(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "company": company.name,
                        "operation": "paid_escalation",
                        "status": "blocked",
                        "reason": "budget_exceeded",
                        "unresolved_fields": unresolved_fields,
                        "max_attempts": self.service.config.paid_escalation_max_attempts,
                    }
                )
                break

            policy = self.orchestrator.source_policies.get(source.value)
            if policy and policy.field_coverage:
                if not set(unresolved_fields).intersection(policy.field_coverage):
                    continue

            try:
                if source == EnrichmentSource.SEC_EDGAR:
                    enriched = self.service._enrich_from_sec(enriched)
                elif source == EnrichmentSource.COMPANIES_HOUSE:
                    enriched = self.service._enrich_from_companies_house(enriched)
                elif source == EnrichmentSource.NEWS_SIGNALS:
                    enriched = self.service._enrich_from_news_signals(enriched)

                sources_used.append(source)
                paid_attempts += 1

                _append_enrichment_audit(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "company": company.name,
                        "operation": "paid_escalation",
                        "status": "attempted",
                        "source": source.value,
                        "unresolved_fields": unresolved_fields,
                        "attempt": paid_attempts,
                    }
                )

                if hasattr(enriched, "enrichment_sources"):
                    enriched.enrichment_sources.append(f"paid-escalation:{source.value}")
                if hasattr(enriched, "enrichment_timestamps"):
                    enriched.enrichment_timestamps[source.value] = datetime.now(timezone.utc)

                fields = self.orchestrator.get_fields_to_enrich(enriched)
                if not fields:
                    break
            except Exception as e:
                error_msg = self.service.error_handler.handle_enrichment_error(
                    company.name,
                    str(source),
                    e,
                )
                errors.append(error_msg)

                _append_enrichment_audit(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "company": company.name,
                        "operation": "paid_escalation",
                        "status": "failed",
                        "source": source.value,
                        "error": str(e),
                    }
                )

                if self.service.config.rollback_on_error:
                    enriched = self.orchestrator.rollback_on_error(company, enriched, str(e))
                    break

        return enriched, sources_used, errors, fields


class PaidEscalationSkipHandler:
    """Handle case when paid escalation is disabled but fields remain."""

    def __init__(self, service: EnrichmentService):
        self.service = service

    def handle(
        self,
        company: EnrichableCompany,
        fields: list,
    ) -> None:
        """Log and audit skipped paid escalation."""
        import logging

        from .enrichment_service import _append_enrichment_audit

        logger = logging.getLogger(__name__)

        logger.info(
            "Paid escalation disabled; unresolved enrichment fields remain for %s: %s",
            company.name,
            [field.value for field in fields],
        )

        _append_enrichment_audit(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "company": company.name,
                "operation": "paid_escalation",
                "status": "skipped",
                "reason": "disabled",
                "unresolved_fields": [field.value for field in fields],
            }
        )
