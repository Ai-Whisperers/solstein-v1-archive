"""Source ordering policies.

EPIC-022: Extracted from EnrichmentOrchestrator for modularity.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import EnrichableCompany


class SourceOrderingPolicy:
    """Policy for determining enrichment source order."""

    def __init__(self, config: "EnrichmentConfig", source_policies: dict):
        self.config = config
        self.source_policies = source_policies

    def get_source_policy_tier(self, source: "EnrichmentSource") -> "SourceTier":
        """Get policy tier for a source."""
        from ...source_policy import SourceTier

        policy = self.source_policies.get(source.value)
        if not policy:
            return SourceTier.FREE
        return policy.tier

    def get_enrichment_order(
        self,
        company: "EnrichableCompany",
        stage: "SourceTier" = None,
    ) -> list["EnrichmentSource"]:
        """Get prioritized enrichment order for company.

        Args:
            company: Company to enrich
            stage: Optional tier filter

        Returns:
            Ordered list of sources
        """
        from ...source_policy import SourceTier

        order = []
        stage = stage or SourceTier.FREE

        for source in self.config.source_order:
            if not self.config.is_source_enabled(source):
                continue

            if self.get_source_policy_tier(source) != stage:
                continue

            # Check if we have required identifier for this source
            if source.value == "sec_edgar":
                if not (company.ticker and company.ticker.strip()):
                    continue
            elif source.value == "companies_house":
                if not (company.company_number and company.company_number.strip()):
                    continue

            order.append(source)

        return order

    def get_paid_escalation_order(self, company: "EnrichableCompany") -> list["EnrichmentSource"]:
        """Get order for paid escalation.

        Args:
            company: Company to enrich

        Returns:
            Ordered list of paid sources
        """
        from ...source_policy import SourceTier

        return self.get_enrichment_order(company, stage=SourceTier.PAID)
