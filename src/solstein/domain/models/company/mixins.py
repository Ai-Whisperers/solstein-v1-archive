"""Company utility mixins.

EPIC-022: Extracted from Company model for modularity.
"""

from typing import Any

from solstein.domain.models.financial import FinancialMetric


class CompanyUtilityMixin:
    """Mixin providing utility methods for Company model.

    These methods provide standardized field access and manipulation.
    """

    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get any field by name.

        Args:
            field_name: Name of the field to get
            default: Default value if field doesn't exist

        Returns:
            Field value or default
        """
        try:
            return getattr(self, field_name, default)
        except AttributeError:
            return default

    def get_financial_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get a field from financials.

        Args:
            field_name: Name of the financial field
            default: Default value if field doesn't exist

        Returns:
            Financial field value or default
        """
        if self.financials is None:
            return default
        return getattr(self.financials, field_name, default)

    def set_field(self, field_name: str, value: Any) -> bool:
        """Safely set a field value.

        Args:
            field_name: Name of the field to set
            value: Value to set

        Returns:
            True if successful, False if field doesn't exist
        """
        try:
            if hasattr(self, field_name):
                setattr(self, field_name, value)
                return True
            return False
        except Exception:
            return False

    def has_field(self, field_name: str) -> bool:
        """Check if a field exists and has a value.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field exists and has non-None value
        """
        try:
            value = getattr(self, field_name, None)
            return value is not None
        except AttributeError:
            return False

    def get_data_completeness(self) -> float:
        """Calculate data completeness score (0.0 to 1.0).

        Returns:
            Completeness score based on required fields
        """
        required_fields = [
            "name",
            "industry",
            "revenue",
            "employees",
            "growth_rate",
            "headquarters",
        ]

        present_count = sum(1 for field in required_fields if self.has_field(field))
        return present_count / len(required_fields)


class CompanyPropertyMixin:
    """Mixin providing computed properties for Company model."""

    @property
    def is_large_cap(self) -> bool:
        """Check if company is large cap (revenue >= €100M)."""
        revenue = getattr(self, "revenue", None)
        return revenue is not None and revenue >= 100_000_000

    @property
    def is_high_growth(self) -> bool:
        """Check if company is high growth (growth rate >= 20%)."""
        growth = getattr(self, "growth_rate", None)
        return growth is not None and growth >= 0.20

    @property
    def is_profitable(self) -> bool:
        """Check if company is profitable (profit margin > 0%)."""
        margin = getattr(self, "profit_margin", None)
        return margin is not None and margin > 0


class CompanySyncMixin:
    """Mixin providing synchronization methods for Company model."""

    def sync_financial_fields(self) -> "Company":
        """Synchronize financial fields between top-level and financials object.

        Ensures consistency between:
        - self.revenue <-> self.financials.revenue
        - self.employees <-> self.financials.employees
        - self.growth_rate <-> self.financials.growth_rate
        - self.profit_margin <-> self.financials.profit_margin
        - self.valuation <-> self.financials.valuation
        - self.funding <-> self.financials.funding_raised
        """
        # Ensure company_name is set
        if self.company_name is None:
            self.company_name = self.name

        # Ensure financials object exists
        if self.financials is None:
            self.financials = FinancialMetric()

        # Sync fields bidirectionally
        self._sync_field("revenue", "revenue")
        self._sync_field("employees", "employees")
        self._sync_field("growth_rate", "growth_rate")
        self._sync_field("profit_margin", "profit_margin")
        self._sync_field("valuation", "valuation")

        # Special case for funding/funding_raised
        funding_value = self.funding
        financial_funding = self.financials.funding_raised
        if funding_value is None and financial_funding is not None:
            self.funding = financial_funding
        elif funding_value is not None and financial_funding is None:
            self.financials.funding_raised = funding_value

        # Sync confidence scores
        if not self.confidence_scores and self.signal_confidences:
            self.confidence_scores = dict(self.signal_confidences)
        elif self.confidence_scores and not self.signal_confidences:
            self.signal_confidences = dict(self.confidence_scores)

        return self

    def _sync_field(self, field_name: str, financial_name: str) -> None:
        """Sync a single field between top-level and financials.

        Args:
            field_name: Name of the top-level field
            financial_name: Name of the financials field
        """
        value = getattr(self, field_name)
        financial_value = getattr(self.financials, financial_name)

        if value is None and financial_value is not None:
            setattr(self, field_name, financial_value)
        elif value is not None and financial_value is None:
            setattr(self.financials, financial_name, value)
