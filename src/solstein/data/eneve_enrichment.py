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
        if not company.confidence_scores:
            company.confidence_scores = {}

        # Calculate confidence based on data availability
        metrics_present = 0
        total_metrics = 8

        if company.revenue is not None:
            metrics_present += 1
            company.confidence_scores['revenue'] = 0.9
        else:
            company.confidence_scores['revenue'] = 0.0

        if company.growth_rate is not None:
            metrics_present += 1
            company.confidence_scores['growth_rate'] = 0.85
        else:
            company.confidence_scores['growth_rate'] = 0.0

        if company.employees is not None:
            metrics_present += 1
            company.confidence_scores['employees'] = 0.95
        else:
            company.confidence_scores['employees'] = 0.0

        if company.profit_margin is not None:
            metrics_present += 1
            company.confidence_scores['profit_margin'] = 0.8
        else:
            company.confidence_scores['profit_margin'] = 0.0

        if company.funding is not None:
            metrics_present += 1
            company.confidence_scores['funding'] = 0.85
        else:
            company.confidence_scores['funding'] = 0.0

        if company.valuation is not None:
            metrics_present += 1
            company.confidence_scores['valuation'] = 0.75
        else:
            company.confidence_scores['valuation'] = 0.0

        if company.ai_maturity is not None:
            metrics_present += 1
            company.confidence_scores['ai_maturity'] = 0.7
        else:
            company.confidence_scores['ai_maturity'] = 0.0

        if company.threat_level is not None:
            metrics_present += 1
            company.confidence_scores['threat_level'] = 0.7
        else:
            company.confidence_scores['threat_level'] = 0.0

        # Overall data completeness score
        company.confidence_scores['data_completeness'] = metrics_present / total_metrics

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
        if not company.company_name:
            return False, "Company name is required"

        # Check for at least some data
        has_data = any([
            company.revenue is not None,
            company.employees is not None,
            company.growth_rate is not None,
            company.profit_margin is not None,
            company.funding is not None,
            company.valuation is not None,
            company.ai_maturity is not None,
            company.threat_level is not None,
        ])

        if not has_data:
            return False, f"No enrichment data found for {company.company_name}"

        # Validate numeric ranges
        if company.revenue is not None and company.revenue < 0:
            return False, f"Revenue cannot be negative: {company.revenue}"

        if company.employees is not None and company.employees < 0:
            return False, f"Employees cannot be negative: {company.employees}"

        if company.growth_rate is not None and (company.growth_rate < -100 or company.growth_rate > 1000):
            return False, f"Growth rate out of reasonable range: {company.growth_rate}%"

        if company.profit_margin is not None and (company.profit_margin < -100 or company.profit_margin > 100):
            return False, f"Profit margin out of range: {company.profit_margin}%"

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
        # Merge numeric fields (prefer non-None)
        if primary.revenue is None and secondary.revenue is not None:
            primary.revenue = secondary.revenue

        if primary.employees is None and secondary.employees is not None:
            primary.employees = secondary.employees

        if primary.growth_rate is None and secondary.growth_rate is not None:
            primary.growth_rate = secondary.growth_rate

        if primary.profit_margin is None and secondary.profit_margin is not None:
            primary.profit_margin = secondary.profit_margin

        if primary.funding is None and secondary.funding is not None:
            primary.funding = secondary.funding

        if primary.valuation is None and secondary.valuation is not None:
            primary.valuation = secondary.valuation

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
