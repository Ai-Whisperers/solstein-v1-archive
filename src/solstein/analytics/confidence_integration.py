"""Confidence calibration integration for the research pipeline.

Integrates ConfidenceAdjuster into the scoring and aggregation pipeline
to provide calibrated confidence scores based on historical accuracy.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from solstein.infrastructure.confidence_adjustment import ConfidenceAdjuster


class CalibratedConfidenceProvider:
    """Provides calibrated confidence scores for data sources.

        Uses ConfidenceAdjuster to track source accuracy and provide
    time-weighted confidence calibration.
    """

    def __init__(
        self,
        smoothing_factor: float = 0.1,
        min_confidence: float = 0.3,
        max_confidence: float = 0.99,
    ):
        """Initialize the calibrated confidence provider.

        Args:
            smoothing_factor: How quickly to adjust confidence (0.1 = slow, 0.5 = fast)
            min_confidence: Minimum allowed confidence score
            max_confidence: Maximum allowed confidence score
        """
        self.adjuster = ConfidenceAdjuster(
            smoothing_factor=smoothing_factor,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
        )

        # Register all known data sources with their base confidences
        self._register_default_sources()

    def _register_default_sources(self) -> None:
        """Register all data sources with their base confidence levels."""
        default_confidences = {
            "sec_edgar": 0.95,
            "companies_house": 0.93,
            "yahoo_finance": 0.88,
            "global_market": 0.87,
            "github": 0.85,
            "website": 0.84,
            "patents": 0.80,
            "linkedin": 0.75,
            "funding": 0.73,
            "news": 0.72,
            "news_signal": 0.70,
            "web_search": 0.68,
            "static_catalog": 0.65,
            "competitor_json": 0.60,
        }

        for source_name, base_confidence in default_confidences.items():
            self.adjuster.register_source(source_name, base_confidence)

        logger.info(f"Registered {len(default_confidences)} sources for confidence calibration")

    def get_calibrated_confidence(
        self,
        source_name: str,
        base_confidence: float | None = None,
    ) -> float:
        """Get the calibrated confidence for a source.

        Args:
            source_name: Name of the data source
            base_confidence: Optional override for base confidence

        Returns:
            Calibrated confidence score (0.0-1.0)
        """
        return self.adjuster.get_adjusted_confidence(source_name, base_confidence)

    def record_prediction(
        self,
        source_name: str,
        predicted_confidence: float,
        was_correct: bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a prediction outcome for calibration.

        Args:
            source_name: Name of the data source
            predicted_confidence: Confidence that was predicted
            was_correct: Whether the prediction was correct/verified
            metadata: Optional additional context
        """
        self.adjuster.record_prediction(
            source_name=source_name,
            predicted_confidence=predicted_confidence,
            was_correct=was_correct,
            metadata=metadata,
        )

    def get_source_stats(self, source_name: str) -> dict[str, Any] | None:
        """Get calibration statistics for a source.

        Args:
            source_name: Name of the data source

        Returns:
            Statistics dict or None if source not registered
        """
        return self.adjuster.get_source_stats(source_name)

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get calibration statistics for all sources.

        Returns:
            Dict mapping source names to their statistics
        """
        return self.adjuster.get_all_stats()

    def auto_calibrate_from_conflicts(
        self,
        source_name: str,
        conflicts_resolved: list[dict[str, Any]],
    ) -> None:
        """Auto-calibrate based on conflict resolution outcomes.

        Args:
            source_name: Source to calibrate
            conflicts_resolved: List of conflict resolution results
        """
        self.adjuster.auto_calibrate_from_conflicts(source_name, conflicts_resolved)


# Global singleton instance
_calibrated_provider: CalibratedConfidenceProvider | None = None


def get_calibrated_confidence_provider() -> CalibratedConfidenceProvider:
    """Get the global calibrated confidence provider instance.

    Returns:
        CalibratedConfidenceProvider singleton
    """
    global _calibrated_provider
    if _calibrated_provider is None:
        _calibrated_provider = CalibratedConfidenceProvider()
    return _calibrated_provider


def reset_calibrated_provider() -> None:
    """Reset the global provider (useful for testing)."""
    global _calibrated_provider
    _calibrated_provider = None
