from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class SourceQualityScores:
    reliability: float
    freshness: float
    coverage: float
    accuracy: float
    overall: float
    reliability_factors: dict[str, Any] = field(default_factory=dict)
    freshness_factors: dict[str, Any] = field(default_factory=dict)
    coverage_factors: dict[str, Any] = field(default_factory=dict)
    accuracy_factors: dict[str, Any] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sample_size: int = 0
    calculation_period_days: int = 7


class QualityScorer:
    WEIGHTS = {
        "reliability": 0.35,
        "freshness": 0.25,
        "coverage": 0.25,
        "accuracy": 0.15,
    }

    def calculate_overall(self, scores: SourceQualityScores) -> float:
        weighted = (
            scores.reliability * self.WEIGHTS["reliability"]
            + scores.freshness * self.WEIGHTS["freshness"]
            + scores.coverage * self.WEIGHTS["coverage"]
            + scores.accuracy * self.WEIGHTS["accuracy"]
        )
        return round(max(0.0, min(weighted, 1.0)), 4)

    def with_computed_overall(
        self,
        *,
        reliability: float,
        freshness: float,
        coverage: float,
        accuracy: float,
        reliability_factors: dict[str, Any] | None = None,
        freshness_factors: dict[str, Any] | None = None,
        coverage_factors: dict[str, Any] | None = None,
        accuracy_factors: dict[str, Any] | None = None,
        sample_size: int = 0,
        calculation_period_days: int = 7,
    ) -> SourceQualityScores:
        bounded = {
            "reliability": max(0.0, min(reliability, 1.0)),
            "freshness": max(0.0, min(freshness, 1.0)),
            "coverage": max(0.0, min(coverage, 1.0)),
            "accuracy": max(0.0, min(accuracy, 1.0)),
        }

        provisional = SourceQualityScores(
            reliability=bounded["reliability"],
            freshness=bounded["freshness"],
            coverage=bounded["coverage"],
            accuracy=bounded["accuracy"],
            overall=0.0,
            reliability_factors=reliability_factors or {},
            freshness_factors=freshness_factors or {},
            coverage_factors=coverage_factors or {},
            accuracy_factors=accuracy_factors or {},
            sample_size=sample_size,
            calculation_period_days=calculation_period_days,
        )

        return SourceQualityScores(
            reliability=provisional.reliability,
            freshness=provisional.freshness,
            coverage=provisional.coverage,
            accuracy=provisional.accuracy,
            overall=self.calculate_overall(provisional),
            reliability_factors=provisional.reliability_factors,
            freshness_factors=provisional.freshness_factors,
            coverage_factors=provisional.coverage_factors,
            accuracy_factors=provisional.accuracy_factors,
            calculated_at=provisional.calculated_at,
            sample_size=provisional.sample_size,
            calculation_period_days=provisional.calculation_period_days,
        )
