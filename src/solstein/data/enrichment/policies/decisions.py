"""Enrichment decision policies.

EPIC-022: Extracted from EnrichmentOrchestrator for modularity.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..models import EnrichableCompany, EnrichmentField


class EnrichmentPolicy:
    """Policy for making enrichment decisions."""

    def __init__(self, config: "EnrichmentConfig"):
        self.config = config

    def should_skip_enrichment(self, company: "EnrichableCompany") -> bool:
        """Determine if enrichment should be skipped.

        Args:
            company: Company to check

        Returns:
            True if enrichment should be skipped
        """
        if not self.config.enabled:
            return True

        # Check if we have any valid identifiers
        has_ticker = company.ticker and company.ticker.strip()
        has_company_number = company.company_number and company.company_number.strip()

        if not has_ticker and not has_company_number:
            return True

        return False

    def is_data_complete(self, company: "EnrichableCompany") -> bool:
        """Check if company data is already complete.

        Args:
            company: Company to check

        Returns:
            True if data is complete
        """
        financials = company.financials
        if not financials:
            return False

        has_revenue = financials.revenue is not None and financials.revenue > 0
        has_growth = financials.growth_rate is not None
        has_employees = financials.employees is not None and financials.employees > 0
        has_margin = financials.profit_margin is not None

        return has_revenue and has_growth and has_employees and has_margin

    def get_fields_to_enrich(self, company: "EnrichableCompany") -> list["EnrichmentField"]:
        """Get list of fields that need enrichment.

        Args:
            company: Company to check

        Returns:
            List of fields needing enrichment
        """
        from ..models import EnrichmentField

        fields = []
        financials = company.financials

        if not financials:
            # All fields needed
            return list(EnrichmentField)

        if financials.revenue is None or financials.revenue <= 0:
            fields.append(EnrichmentField.REVENUE)
        if financials.growth_rate is None:
            fields.append(EnrichmentField.GROWTH_RATE)
        if financials.employees is None or financials.employees <= 0:
            fields.append(EnrichmentField.EMPLOYEES)
        if financials.profit_margin is None:
            fields.append(EnrichmentField.PROFIT_MARGIN)

        return fields

    def should_overwrite_field(
        self,
        field: "EnrichmentField",
        current_value: Any,
        new_value: Any,
        current_confidence: "ConfidenceLevel",
        new_confidence: "ConfidenceLevel",
    ) -> bool:
        """Determine if a field should be overwritten.

        Args:
            field: Field being considered
            current_value: Current field value
            new_value: New field value
            current_confidence: Current confidence level
            new_confidence: New confidence level

        Returns:
            True if field should be overwritten
        """

        # Never overwrite with null
        if new_value is None:
            return False

        # Always fill empty fields
        if current_value is None:
            return True

        # Higher confidence wins
        if new_confidence.value > current_confidence.value:
            return True

        # Same confidence: prefer non-zero values
        if new_confidence == current_confidence:
            if current_value == 0 and new_value != 0:
                return True

        return False
