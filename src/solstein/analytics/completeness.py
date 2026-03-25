"""
Task 3: Data Completeness Scoring

Calculates a 0-100 completeness score for each company based on field availability.
Assigns data quality tiers: COMPLETE, PARTIAL, MINIMAL, INSUFFICIENT.

Completeness Score Calculation:
- Counts non-NULL fields across all tracked fields
- Divides by total tracked fields
- Multiplies by 100 to get 0-100 score

Tier Assignment:
- COMPLETE: 80-100% completeness
- PARTIAL: 50-79% completeness
- MINIMAL: 20-49% completeness
- INSUFFICIENT: 0-19% completeness

Tracked Fields (19 total):
Financial: revenue, growth_rate, employees, profit_margin, funding_raised, valuation, ebitda_margin
Operational: recurring_revenue_pct, revenue_per_employee_eur_k, employee_cagr_3yr, open_positions
Scoring: ai_score, ai_maturity, threat_level, tier
Geographic: geographic_presence
Classification: ai_signal_level, ai_key_capabilities, ai_in_production
"""

import logging
from enum import Enum
from typing import Any

from ..domain.models import Company

logger = logging.getLogger(__name__)


class DataQualityTier(str, Enum):
    """Data quality tier classification."""

    COMPLETE = "COMPLETE"  # 80-100% completeness
    PARTIAL = "PARTIAL"  # 50-79% completeness
    MINIMAL = "MINIMAL"  # 20-49% completeness
    INSUFFICIENT = "INSUFFICIENT"  # 0-19% completeness


class CompletenessCalculator:
    """Calculate data completeness scores and assign quality tiers."""

    # Fields tracked for completeness scoring (19 total)
    TRACKED_FIELDS = [
        # Financial metrics (7)
        "revenue",
        "growth_rate",
        "employees",
        "profit_margin",
        "funding_raised",
        "valuation",
        "ebitda_margin",
        # Operational metrics (4)
        "recurring_revenue_pct",
        "revenue_per_employee_eur_k",
        "employee_cagr_3yr",
        "open_positions",
        # Scoring fields (4)
        "ai_score",
        "ai_maturity",
        "threat_level",
        "tier",
        # Geographic (1)
        "geographic_presence",
        # Classification (3)
        "ai_signal_level",
        "ai_key_capabilities",
        "ai_in_production",
    ]

    # Tier thresholds (inclusive lower bound, exclusive upper bound)
    TIER_THRESHOLDS = {
        DataQualityTier.COMPLETE: (80, 101),  # 80-100%
        DataQualityTier.PARTIAL: (50, 80),  # 50-79%
        DataQualityTier.MINIMAL: (20, 50),  # 20-49%
        DataQualityTier.INSUFFICIENT: (0, 20),  # 0-19%
    }

    def __init__(self):
        """Initialize calculator."""
        self.total_tracked_fields = len(self.TRACKED_FIELDS)
        logger.info(f"CompletenessCalculator initialized with {self.total_tracked_fields} tracked fields")

    def calculate_completeness_score(self, company: Company) -> float:
        """
        Calculate completeness score for a company (0-100).

        Args:
            company: Company to score

        Returns:
            Completeness score 0-100
        """
        non_null_count = 0

        # Fields whose default value does not represent actual data
        ENUM_DEFAULT_FIELDS = {
            "ai_maturity": "NONE",        # AIMaturity.NONE is the default
            "threat_level": "MEDIUM",     # ThreatLevel.MEDIUM is the default
            "tier": "TIER_3",             # CompanyTier.TIER_3 is the default
        }

        # Check each tracked field
        for field in self.TRACKED_FIELDS:
            value = self._get_field_value(company, field)
            if value is None:
                continue
            # Empty lists do not represent actual data
            if isinstance(value, list) and len(value) == 0:
                continue
            # Enum default sentinel values do not represent actual enriched data
            default_sentinel = ENUM_DEFAULT_FIELDS.get(field)
            if default_sentinel is not None:
                value_str = value.value if hasattr(value, "value") else str(value)
                if value_str == default_sentinel:
                    continue
            non_null_count += 1

        # Calculate percentage
        score = (non_null_count / self.total_tracked_fields) * 100
        return round(score, 1)

    def assign_tier(self, completeness_score: float) -> DataQualityTier:
        """
        Assign data quality tier based on completeness score.

        Args:
            completeness_score: Score from 0-100

        Returns:
            DataQualityTier enum value
        """
        for tier, (lower, upper) in self.TIER_THRESHOLDS.items():
            if lower <= completeness_score < upper:
                return tier

        # Fallback (should not reach here)
        return DataQualityTier.INSUFFICIENT

    def get_completeness_report(self, company: Company) -> dict:
        """
        Get detailed completeness report for a company.

        Args:
            company: Company to analyze

        Returns:
            Dictionary with score, tier, and field-level details
        """
        score = self.calculate_completeness_score(company)
        tier = self.assign_tier(score)

        # Fields whose default value does not represent actual data
        ENUM_DEFAULT_FIELDS = {
            "ai_maturity": "NONE",
            "threat_level": "MEDIUM",
            "tier": "TIER_3",
        }

        # Get field-level details
        field_details = {}
        for field in self.TRACKED_FIELDS:
            value = self._get_field_value(company, field)
            filled = value is not None
            if filled and isinstance(value, list) and len(value) == 0:
                filled = False
            default_sentinel = ENUM_DEFAULT_FIELDS.get(field)
            if filled and default_sentinel is not None:
                value_str = value.value if hasattr(value, "value") else str(value)
                if value_str == default_sentinel:
                    filled = False
            field_details[field] = {
                "present": filled,
                "value": value,
            }

        return {
            "company_id": company.id,
            "company_name": company.name,
            "completeness_score": score,
            "data_quality_tier": tier.value,
            "total_tracked_fields": self.total_tracked_fields,
            "non_null_fields": sum(1 for d in field_details.values() if d["present"]),
            "field_details": field_details,
        }

    def _get_field_value(self, company: Company, field: str) -> Any | None:
        """
        Get field value from company, handling nested fields.

        Args:
            company: Company object
            field: Field name (may be nested like "financials.revenue")

        Returns:
            Field value or None if not present
        """
        # Handle nested fields in financials
        financial_fields = [
            "revenue",
            "growth_rate",
            "employees",
            "profit_margin",
            "funding_raised",
            "valuation",
            "ebitda_margin",
            "recurring_revenue_pct",
            "revenue_per_employee_eur_k",
            "employee_cagr_3yr",
        ]

        if field in financial_fields:
            if company.financials is None:
                return None
            return getattr(company.financials, field, None)

        # Handle direct company attributes
        return getattr(company, field, None)


# Global instance
completeness_calculator = CompletenessCalculator()
