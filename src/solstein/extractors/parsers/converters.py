"""Data converters for extracted markdown content.

EPIC-022: Extracted from MarkdownExtractor for modularity.
"""

import re

from ...domain.models import (
    AIMaturity,
    CompanyTier,
    ConfidenceLevel,
    ThreatLevel,
)


class DataConverter:
    """Convert extracted string data to typed values."""

    @staticmethod
    def parse_numeric(value: str | None) -> float | None:
        """Parse numeric value from string.

        Args:
            value: String value like "€100M" or "50.5"

        Returns:
            Parsed float or None
        """
        if not value:
            return None

        # Remove currency symbols and units
        cleaned = re.sub(r"[€$\s]", "", value)

        # Handle K, M, B, T suffixes
        multiplier = 1.0
        if cleaned.endswith("K"):
            multiplier = 1_000
            cleaned = cleaned[:-1]
        elif cleaned.endswith("M"):
            multiplier = 1_000_000
            cleaned = cleaned[:-1]
        elif cleaned.endswith("B"):
            multiplier = 1_000_000_000
            cleaned = cleaned[:-1]
        elif cleaned.endswith("T"):
            multiplier = 1_000_000_000_000
            cleaned = cleaned[:-1]

        try:
            return float(cleaned.replace(",", "")) * multiplier
        except ValueError:
            return None

    @staticmethod
    def parse_percentage(value: str | None) -> float | None:
        """Parse percentage value from string.

        Args:
            value: String value like "25.5%"

        Returns:
            Parsed float (0.0-1.0) or None
        """
        if not value:
            return None

        # Remove % and whitespace
        cleaned = value.replace("%", "").strip()

        try:
            return float(cleaned.replace(",", "")) / 100.0
        except ValueError:
            return None

    @staticmethod
    def parse_ai_maturity(value: str | None) -> AIMaturity:
        """Parse AI maturity from string.

        Args:
            value: String like "Advanced" or "Emerging"

        Returns:
            AIMaturity enum value
        """
        if not value:
            return AIMaturity.NONE

        value_lower = value.lower().strip()

        maturity_map = {
            "very strong": AIMaturity.VERY_STRONG,
            "advanced": AIMaturity.VERY_STRONG,
            "strong": AIMaturity.STRONG,
            "moderate": AIMaturity.MODERATE,
            "intermediate": AIMaturity.MODERATE,
            "emerging": AIMaturity.LOW,
            "low": AIMaturity.LOW,
            "none": AIMaturity.NONE,
        }

        return maturity_map.get(value_lower, AIMaturity.NONE)

    @staticmethod
    def parse_threat_level(value: str | None) -> ThreatLevel:
        """Parse threat level from string.

        Args:
            value: String like "High" or "Low"

        Returns:
            ThreatLevel enum value
        """
        if not value:
            return ThreatLevel.MEDIUM

        value_lower = value.lower().strip()

        threat_map = {
            "critical": ThreatLevel.CRITICAL,
            "high": ThreatLevel.HIGH,
            "medium": ThreatLevel.MEDIUM,
            "low": ThreatLevel.LOW,
        }

        if "low" in value_lower:
            return ThreatLevel.LOW
        return threat_map.get(value_lower, ThreatLevel.MEDIUM)

    @staticmethod
    def parse_tier(value: str | None) -> CompanyTier:
        """Parse company tier from string.

        Args:
            value: String like "Phoenix" or "Salt"

        Returns:
            CompanyTier enum value
        """
        if not value:
            return CompanyTier.TIER_3

        value_lower = value.lower().strip()

        tier_map = {
            "tier 1": CompanyTier.TIER_1,
            "tier 2": CompanyTier.TIER_2,
            "tier 3": CompanyTier.TIER_3,
            "tier 4": CompanyTier.TIER_4,
            "phoenix": CompanyTier.TIER_1,
            "salt": CompanyTier.TIER_2,
            "lead": CompanyTier.TIER_3,
        }

        return tier_map.get(value_lower, CompanyTier.TIER_3)

    @staticmethod
    def parse_confidence(value: str | None) -> ConfidenceLevel:
        """Parse confidence level from string.

        Args:
            value: String like "HIGH" or "MEDIUM"

        Returns:
            ConfidenceLevel enum value
        """
        if not value:
            return ConfidenceLevel.UNKNOWN

        value_upper = value.upper().strip()

        confidence_map = {
            "HIGH": ConfidenceLevel.CONFIRMED,
            "CONFIRMED": ConfidenceLevel.CONFIRMED,
            "MEDIUM": ConfidenceLevel.ESTIMATED,
            "ESTIMATED": ConfidenceLevel.ESTIMATED,
            "LOW": ConfidenceLevel.UNKNOWN,
            "UNVERIFIED": ConfidenceLevel.UNKNOWN,
            "UNKNOWN": ConfidenceLevel.UNKNOWN,
            "SYNTHETIC": ConfidenceLevel.SYNTHETIC,
        }

        return confidence_map.get(value_upper, ConfidenceLevel.UNKNOWN)

    @staticmethod
    def determine_tier_from_revenue(revenue: float | None) -> CompanyTier:
        """Determine company tier based on revenue.

        Args:
            revenue: Annual revenue in EUR

        Returns:
            CompanyTier based on revenue thresholds
        """
        if revenue is None:
            return CompanyTier.TIER_3

        if revenue >= 100_000_000:  # €100M+
            return CompanyTier.TIER_1
        elif revenue >= 10_000_000:  # €10M-€100M
            return CompanyTier.TIER_2
        else:
            return CompanyTier.TIER_3
