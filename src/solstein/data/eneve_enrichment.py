"""Enrichment utilities for eneve competitive intelligence pipeline."""

from typing import Optional
from loguru import logger

from ..domain.models import Company


class EnveEnrichmentService:
    """Service for enriching company data in the eneve pipeline."""

    @staticmethod
    def enrich_company_with_confidence(company: Company) -> Company:
        """Add confidence scores to company metrics based on data completeness.

        Args:
            company: Company object to enrich

        Returns:
            Company object with confidence scores added
        """
        if not company.signal_confidences:
            company.signal_confidences = {}

        # Calculate confidence based on data availability
        metrics_present = 0
        total_metrics = 8

        if company.financials and company.financials.revenue is not None:
            metrics_present += 1
            company.signal_confidences["revenue"] = 0.9
        else:
            company.signal_confidences["revenue"] = 0.0

        if company.financials and company.financials.growth_rate is not None:
            metrics_present += 1
            company.signal_confidences["growth_rate"] = 0.85
        else:
            company.signal_confidences["growth_rate"] = 0.0

        if company.financials and company.financials.employees is not None:
            metrics_present += 1
            company.signal_confidences["employees"] = 0.95
        else:
            company.signal_confidences["employees"] = 0.0

        if company.financials and company.financials.profit_margin is not None:
            metrics_present += 1
            company.signal_confidences["profit_margin"] = 0.8
        else:
            company.signal_confidences["profit_margin"] = 0.0

        if company.financials and company.financials.funding_raised is not None:
            metrics_present += 1
            company.signal_confidences["funding"] = 0.85
        else:
            company.signal_confidences["funding"] = 0.0

        if company.financials and company.financials.valuation is not None:
            metrics_present += 1
            company.signal_confidences["valuation"] = 0.75
        else:
            company.signal_confidences["valuation"] = 0.0

        if company.ai_maturity is not None:
            metrics_present += 1
            company.signal_confidences["ai_maturity"] = 0.7
        else:
            company.signal_confidences["ai_maturity"] = 0.0

        if company.threat_level is not None:
            metrics_present += 1
            company.signal_confidences["threat_level"] = 0.7
        else:
            company.signal_confidences["threat_level"] = 0.0

        # Overall data completeness score
        company.signal_confidences["data_completeness"] = metrics_present / total_metrics

        company.confidence_scores = dict(company.signal_confidences)

        return company

    @staticmethod
    def calculate_enrichment_source_count(company: Company) -> int:
        """Calculate number of enrichment sources for a company.

        Args:
            company: Company object

        Returns:
            Count of unique enrichment sources
        """
        sources = set()

        # Count sources from metric_sources
        if company.metric_sources:
            for metric_sources_list in company.metric_sources.values():
                if isinstance(metric_sources_list, list):
                    sources.update(metric_sources_list)

        # Count sources from source_links
        if company.source_links:
            sources.update(company.source_links)

        return len(sources)

    @staticmethod
    def validate_enriched_data(company: Company) -> tuple[bool, Optional[str]]:
        """Validate enriched company data.

        Args:
            company: Company object to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not company.name:
            return False, "Company name is required"

        # Check for at least some data
        has_data = False
        if company.financials:
            has_data = any(
                [
                    company.financials.revenue is not None,
                    company.financials.employees is not None,
                    company.financials.growth_rate is not None,
                    company.financials.profit_margin is not None,
                    company.financials.funding_raised is not None,
                    company.financials.valuation is not None,
                ]
            )

        has_data = has_data or any(
            [
                company.ai_maturity is not None,
                company.threat_level is not None,
            ]
        )

        if not has_data:
            return False, f"No enrichment data found for {company.name}"

        # Validate numeric ranges
        if company.financials:
            if company.financials.revenue is not None and company.financials.revenue < 0:
                return False, f"Revenue cannot be negative: {company.financials.revenue}"

            if company.financials.employees is not None and company.financials.employees < 0:
                return False, f"Employees cannot be negative: {company.financials.employees}"

            if company.financials.growth_rate is not None and (
                company.financials.growth_rate < -100 or company.financials.growth_rate > 1000
            ):
                return False, f"Growth rate out of reasonable range: {company.financials.growth_rate}%"

            if company.financials.profit_margin is not None and (
                company.financials.profit_margin < -100 or company.financials.profit_margin > 100
            ):
                return False, f"Profit margin out of range: {company.financials.profit_margin}%"

        return True, None

    @staticmethod
    def merge_enrichment_data(primary: Company, secondary: Company) -> Company:
        """Merge enrichment data from secondary company into primary.

        Args:
            primary: Primary company object
            secondary: Secondary company object with additional data

        Returns:
            Merged company object
        """
        # Merge financials
        if primary.financials and secondary.financials:
            if primary.financials.revenue is None and secondary.financials.revenue is not None:
                primary.financials.revenue = secondary.financials.revenue

            if primary.financials.employees is None and secondary.financials.employees is not None:
                primary.financials.employees = secondary.financials.employees

            if primary.financials.growth_rate is None and secondary.financials.growth_rate is not None:
                primary.financials.growth_rate = secondary.financials.growth_rate

            if primary.financials.profit_margin is None and secondary.financials.profit_margin is not None:
                primary.financials.profit_margin = secondary.financials.profit_margin

            if primary.financials.funding is None and secondary.financials.funding is not None:
                primary.financials.funding = secondary.financials.funding

            if primary.financials.valuation is None and secondary.financials.valuation is not None:
                primary.financials.valuation = secondary.financials.valuation

        if primary.financials:
            if primary.revenue is None and primary.financials.revenue is not None:
                primary.revenue = primary.financials.revenue
            if primary.employees is None and primary.financials.employees is not None:
                primary.employees = primary.financials.employees
            if primary.growth_rate is None and primary.financials.growth_rate is not None:
                primary.growth_rate = primary.financials.growth_rate
            if primary.profit_margin is None and primary.financials.profit_margin is not None:
                primary.profit_margin = primary.financials.profit_margin
            if primary.funding is None and primary.financials.funding_raised is not None:
                primary.funding = primary.financials.funding_raised
            if primary.valuation is None and primary.financials.valuation is not None:
                primary.valuation = primary.financials.valuation

        # Merge source links
        if secondary.source_links:
            primary.source_links = list(set((primary.source_links or []) + secondary.source_links))

        # Merge metric sources
        if secondary.metric_sources:
            for metric, sources in secondary.metric_sources.items():
                if metric not in primary.metric_sources:
                    primary.metric_sources[metric] = []
                primary.metric_sources[metric] = list(set(primary.metric_sources[metric] + sources))

        return primary
