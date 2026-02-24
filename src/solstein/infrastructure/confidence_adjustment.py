"""Confidence adjustment algorithm for data source calibration."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from loguru import logger


@dataclass
class ConfidenceMetrics:
    """Metrics for tracking confidence calibration."""

    source_name: str
    total_predictions: int = 0
    correct_predictions: int = 0
    current_confidence: float = 0.5
    base_confidence: float = 0.5
    calibration_factor: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    history: list[dict[str, Any]] = field(default_factory=list)


class ConfidenceAdjuster:
    """Adjusts confidence scores based on historical accuracy.

    Uses Bayesian-inspired calibration:
    - Tracks prediction accuracy over time
    - Adjusts confidence based on observed error rates
    - Applies time decay to older predictions
    - Maintains calibration history

    Confidence adjustment formula:
    - If accuracy > confidence: increase confidence (source is underconfident)
    - If accuracy < confidence: decrease confidence (source is overconfident)
    - Apply smoothing factor to prevent wild swings
    """

    def __init__(
        self,
        smoothing_factor: float = 0.1,
        min_confidence: float = 0.3,
        max_confidence: float = 0.99,
        history_window_days: int = 90,
    ):
        self.smoothing_factor = smoothing_factor
        self.min_confidence = min_confidence
        self.max_confidence = max_confidence
        self.history_window_days = history_window_days
        self.metrics: dict[str, ConfidenceMetrics] = {}

    def register_source(
        self,
        source_name: str,
        base_confidence: float,
    ) -> None:
        """Register a new data source for confidence tracking."""
        if source_name not in self.metrics:
            self.metrics[source_name] = ConfidenceMetrics(
                source_name=source_name,
                current_confidence=base_confidence,
                base_confidence=base_confidence,
            )
            logger.info(f"Registered source {source_name} with confidence {base_confidence}")

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
            predicted_confidence: Confidence score that was predicted
            was_correct: Whether the prediction was correct/verified
            metadata: Optional additional context
        """
        if source_name not in self.metrics:
            logger.warning(f"Unknown source {source_name}, skipping prediction record")
            return

        metrics = self.metrics[source_name]
        metrics.total_predictions += 1

        if was_correct:
            metrics.correct_predictions += 1

        # Record in history with time decay
        record = {
            "timestamp": datetime.now(),
            "predicted_confidence": predicted_confidence,
            "was_correct": was_correct,
            "metadata": metadata or {},
        }
        metrics.history.append(record)

        # Clean old history
        self._prune_history(metrics)

        # Recalculate confidence
        self._update_confidence(metrics)

        logger.debug(
            f"Recorded prediction for {source_name}: confidence={predicted_confidence:.2f}, correct={was_correct}"
        )

    def _prune_history(self, metrics: ConfidenceMetrics) -> None:
        """Remove history entries older than window."""
        cutoff = datetime.now() - timedelta(days=self.history_window_days)
        metrics.history = [h for h in metrics.history if h["timestamp"] > cutoff]

    def _update_confidence(self, metrics: ConfidenceMetrics) -> None:
        """Recalculate confidence based on recent history."""
        if metrics.total_predictions == 0:
            return

        # Calculate accuracy with time-weighting
        weighted_correct = 0.0
        weighted_total = 0.0

        now = datetime.now()
        max_age = timedelta(days=self.history_window_days)

        for record in metrics.history:
            age = now - record["timestamp"]
            weight = 1.0 - (age / max_age)  # Linear decay
            weight = max(0.1, weight)  # Minimum weight

            weighted_total += weight
            if record["was_correct"]:
                weighted_correct += weight

        if weighted_total == 0:
            observed_accuracy = metrics.base_confidence
        else:
            observed_accuracy = weighted_correct / weighted_total

        # Calculate calibration factor
        # If accuracy > confidence, source is underconfident (increase)
        # If accuracy < confidence, source is overconfident (decrease)
        calibration_error = observed_accuracy - metrics.current_confidence

        # Apply smoothing to prevent wild swings
        adjustment = calibration_error * self.smoothing_factor

        # Update confidence
        new_confidence = metrics.current_confidence + adjustment
        new_confidence = max(self.min_confidence, min(self.max_confidence, new_confidence))

        # Update calibration factor
        if metrics.current_confidence > 0:
            metrics.calibration_factor = new_confidence / metrics.current_confidence

        metrics.current_confidence = new_confidence
        metrics.last_updated = datetime.now()

        logger.info(
            f"Updated confidence for {metrics.source_name}: "
            f"{metrics.current_confidence:.3f} (accuracy={observed_accuracy:.3f}, "
            f"adjustment={adjustment:+.3f})"
        )

    def get_adjusted_confidence(
        self,
        source_name: str,
        base_confidence: float | None = None,
    ) -> float:
        """Get the calibrated confidence for a source.

        Args:
            source_name: Name of the data source
            base_confidence: Optional override base confidence

        Returns:
            Calibrated confidence score
        """
        if source_name not in self.metrics:
            # Return base confidence if source not registered
            return base_confidence or 0.5

        metrics = self.metrics[source_name]

        if base_confidence is not None:
            # Apply calibration factor to provided base confidence
            return max(self.min_confidence, min(self.max_confidence, base_confidence * metrics.calibration_factor))

        return metrics.current_confidence

    def get_source_stats(self, source_name: str) -> dict[str, Any] | None:
        """Get calibration statistics for a source."""
        if source_name not in self.metrics:
            return None

        metrics = self.metrics[source_name]

        accuracy = 0.0
        if metrics.total_predictions > 0:
            accuracy = metrics.correct_predictions / metrics.total_predictions

        return {
            "source_name": metrics.source_name,
            "total_predictions": metrics.total_predictions,
            "correct_predictions": metrics.correct_predictions,
            "accuracy": accuracy,
            "current_confidence": metrics.current_confidence,
            "base_confidence": metrics.base_confidence,
            "calibration_factor": metrics.calibration_factor,
            "last_updated": metrics.last_updated.isoformat(),
            "history_size": len(metrics.history),
        }

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get calibration statistics for all sources."""
        return {name: self.get_source_stats(name) for name in self.metrics.keys()}

    def reset_source(self, source_name: str) -> None:
        """Reset calibration for a source to base values."""
        if source_name in self.metrics:
            metrics = self.metrics[source_name]
            base = metrics.base_confidence
            self.metrics[source_name] = ConfidenceMetrics(
                source_name=source_name,
                current_confidence=base,
                base_confidence=base,
            )
            logger.info(f"Reset calibration for {source_name}")

    def auto_calibrate_from_conflicts(
        self,
        source_name: str,
        conflicts_resolved: list[dict[str, Any]],
    ) -> None:
        """Auto-calibrate based on conflict resolution outcomes.

        When a source loses conflicts frequently, it may be overconfident.
        When a source wins conflicts frequently, it may be underconfident.
        """
        if not conflicts_resolved:
            return

        wins = sum(1 for c in conflicts_resolved if c.get("winner_source") == source_name)
        total = len([c for c in conflicts_resolved if source_name in [c.get("existing_source"), c.get("new_source")]])

        if total == 0:
            return

        win_rate = wins / total

        # Record as predictions
        for conflict in conflicts_resolved:
            if conflict.get("existing_source") == source_name:
                was_correct = conflict.get("winner_source") == source_name
                self.record_prediction(
                    source_name=source_name,
                    predicted_confidence=self.metrics[source_name].current_confidence,
                    was_correct=was_correct,
                    metadata={"type": "conflict_resolution", "conflict_id": conflict.get("id")},
                )

        logger.info(f"Auto-calibrated {source_name} from {total} conflicts: win_rate={win_rate:.2f}")


class SourceConfidenceRegistry:
    """Registry for managing default confidence levels by source type."""

    DEFAULT_CONFIDENCES = {
        "sec_edgar": 0.95,
        "companies_house": 0.93,
        "github": 0.85,
        "news_signal": 0.72,
    }

    def __init__(self):
        self.confidences = dict(self.DEFAULT_CONFIDENCES)

    def get_confidence(self, source_name: str) -> float:
        """Get default confidence for a source."""
        return self.confidences.get(source_name, 0.5)

    def set_confidence(self, source_name: str, confidence: float) -> None:
        """Set default confidence for a source."""
        self.confidences[source_name] = confidence

    def register_source(self, source_name: str, confidence: float) -> None:
        """Register a new source with default confidence."""
        self.confidences[source_name] = confidence

    def get_all(self) -> dict[str, float]:
        """Get all registered source confidences."""
        return dict(self.confidences)
