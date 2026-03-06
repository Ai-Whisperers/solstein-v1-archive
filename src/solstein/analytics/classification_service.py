"""Unified classification service for EPIC-017.

This module consolidates classification logic from analytics/classification.py
and analytics/scoring.py into a single, deterministic service.
"""

from __future__ import annotations

from dataclasses import dataclass

from solstein.analytics.constants import (
    CLASSIFICATION_LEAD_MAX,
    CLASSIFICATION_LEAD_MIN,
    CLASSIFICATION_PHOENIX_MAX,
    CLASSIFICATION_PHOENIX_MIN,
    CLASSIFICATION_SALT_MAX,
    CLASSIFICATION_SALT_MIN,
    LEAD_SCORE_THRESHOLD,
    PHOENIX_SCORE_THRESHOLD,
    SALT_SCORE_THRESHOLD,
    derive_threat_level,
)
from solstein.domain.models import Company


@dataclass(frozen=True)
class ClassificationResult:
    """Result of classification with confidence and metadata."""

    label: str
    confidence: float
    threat_level: str
    composite_score: float
    data_completeness: float


class ClassificationService:
    """Unified classification service - single source of truth.

    This service consolidates classification logic that was previously
    scattered across analytics/classification.py and analytics/scoring.py.
    """

    # Thresholds for classification boundaries
    PHOENIX_THRESHOLD = PHOENIX_SCORE_THRESHOLD  # 7.0
    SALT_THRESHOLD = SALT_SCORE_THRESHOLD  # 4.5
    LEAD_THRESHOLD = LEAD_SCORE_THRESHOLD  # 4.49

    # Confidence calculation weights
    COMPLETENESS_WEIGHT = 0.7
    SCORE_CERTAINTY_WEIGHT = 0.3

    # Boundary uncertainty zones
    BOUNDARY_ZONES = [
        (4.4, 4.6),  # Near Lead/Salt boundary
        (6.9, 7.1),  # Near Salt/Phoenix boundary
    ]

    # Completeness mapping from data quality tier
    COMPLETENESS_MAP = {
        "COMPLETE": 90.0,
        "PARTIAL": 65.0,
        "MINIMAL": 35.0,
        "INSUFFICIENT": 15.0,
    }

    def classify(self, composite_score: float | None) -> str:
        """Classify company based on composite score.

        Args:
            composite_score: Composite score (0-10)

        Returns:
            Classification label: 'Phoenix', 'Salt', or 'Lead'
        """
        if composite_score is None:
            return "Lead"

        if composite_score >= self.PHOENIX_THRESHOLD:
            return "Phoenix"
        elif composite_score >= self.SALT_THRESHOLD:
            return "Salt"
        else:
            return "Lead"

    def calculate_confidence(
        self,
        composite_score: float | None,
        data_completeness: float | None,
    ) -> float:
        """Calculate confidence in classification.

        Args:
            composite_score: Composite score (0-10)
            data_completeness: Data completeness percentage (0-100)

        Returns:
            Confidence score (0-1)
        """
        if composite_score is None or data_completeness is None:
            return 0.3  # Low confidence for missing data

        # Normalize completeness to 0-1
        completeness_factor = data_completeness / 100.0

        # Score certainty: scores near boundaries are less certain
        score_certainty = 1.0
        for low, high in self.BOUNDARY_ZONES:
            if low <= composite_score <= high:
                score_certainty = 0.7
                break

        # Combine factors
        confidence = self.COMPLETENESS_WEIGHT * completeness_factor + self.SCORE_CERTAINTY_WEIGHT * score_certainty

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def get_completeness_from_tier(self, data_quality_tier: str | None) -> float:
        """Get estimated completeness from data quality tier.

        Args:
            data_quality_tier: Data quality tier string

        Returns:
            Estimated completeness percentage
        """
        if data_quality_tier is None:
            return 50.0
        return self.COMPLETENESS_MAP.get(data_quality_tier.upper(), 50.0)

    def classify_company(self, company: Company) -> ClassificationResult:
        """Classify a company with full result including confidence.

        Args:
            company: Company object with composite_score and data_quality_tier

        Returns:
            ClassificationResult with label, confidence, threat level, and metadata
        """
        composite_score = company.composite_score

        # Get classification label
        label = self.classify(composite_score)

        # Get data completeness
        data_completeness = self.get_completeness_from_tier(company.data_quality_tier)

        # Calculate confidence
        confidence = self.calculate_confidence(composite_score, data_completeness)

        # Derive threat level
        threat_level = derive_threat_level(label, composite_score or 0.0)

        return ClassificationResult(
            label=label,
            confidence=confidence,
            threat_level=threat_level,
            composite_score=composite_score or 0.0,
            data_completeness=data_completeness,
        )

    def get_distribution(self, companies: list[Company]) -> dict[str, int]:
        """Get distribution of classifications across companies.

        Args:
            companies: List of Company objects

        Returns:
            Dict with counts: {'Phoenix': N, 'Salt': N, 'Lead': N}
        """
        distribution = {"Phoenix": 0, "Salt": 0, "Lead": 0}

        for company in companies:
            classification = self.classify(company.composite_score)
            distribution[classification] += 1

        return distribution

    def validate_distribution(
        self,
        companies: list[Company],
    ) -> dict[str, object]:
        """Validate that classification distribution meets targets.

        Args:
            companies: List of Company objects

        Returns:
            Dict with validation results and statistics
        """
        dist = self.get_distribution(companies)
        total = len(companies)

        if total == 0:
            return {
                "phoenix_valid": False,
                "salt_valid": False,
                "lead_valid": False,
                "phoenix_pct": 0.0,
                "salt_pct": 0.0,
                "lead_pct": 0.0,
                "phoenix_count": 0,
                "salt_count": 0,
                "lead_count": 0,
                "total": 0,
            }

        phoenix_pct = dist["Phoenix"] / total
        salt_pct = dist["Salt"] / total
        lead_pct = dist["Lead"] / total

        return {
            "phoenix_valid": CLASSIFICATION_PHOENIX_MIN <= phoenix_pct <= CLASSIFICATION_PHOENIX_MAX,
            "salt_valid": CLASSIFICATION_SALT_MIN <= salt_pct <= CLASSIFICATION_SALT_MAX,
            "lead_valid": CLASSIFICATION_LEAD_MIN <= lead_pct <= CLASSIFICATION_LEAD_MAX,
            "phoenix_pct": phoenix_pct,
            "salt_pct": salt_pct,
            "lead_pct": lead_pct,
            "phoenix_count": dist["Phoenix"],
            "salt_count": dist["Salt"],
            "lead_count": dist["Lead"],
            "total": total,
        }

    def is_tentative(self, confidence: float, threshold: float = 0.7) -> bool:
        """Check if classification is tentative (low confidence).

        Args:
            confidence: Classification confidence (0-1)
            threshold: Confidence threshold for tentative classification

        Returns:
            True if confidence < threshold
        """
        return confidence < threshold


# Global singleton instance for convenience
classification_service = ClassificationService()


def classify_company(composite_score: float | None) -> str:
    """Convenience function for direct classification.

    DEPRECATED: Use ClassificationService.classify() for new code.
    This function is kept for backward compatibility.
    """
    return classification_service.classify(composite_score)
