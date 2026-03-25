"""Financial projection engine for Epic 2.

Projects 12-month revenue forecasts based on growth trajectories and vectors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .financial_models import (
    ConfidenceLevel,
    FinancialIntelligence,
    TrajectoryDirection,
)


@dataclass
class ProjectionResult:
    """Result of financial projection."""

    projected_revenue_12mo: float
    confidence: ConfidenceLevel
    rationale: str
    scenarios: dict[str, float]  # optimistic, base, pessimistic


class FinancialProjectionEngine:
    """Generate 12-month revenue projections."""

    def __init__(self):
        self.default_growth_rate = 0.15  # 15% default

    def project(
        self,
        current_revenue: float,
        financial_intelligence: FinancialIntelligence,
        market_growth_rate: Optional[float] = None,
    ) -> ProjectionResult:
        """Generate 12-month revenue projection.

        Args:
            current_revenue: Current annual revenue in millions EUR
            financial_intelligence: Financial intelligence data
            market_growth_rate: Market sector growth rate if known

        Returns:
            ProjectionResult with forecasts and confidence
        """
        # Determine base growth rate from trajectory
        base_growth = self._determine_base_growth_rate(financial_intelligence)

        # Adjust for growth vectors
        vector_adjustment = self._calculate_vector_adjustment(financial_intelligence)

        # Adjust for market context
        market_adjustment = 0.0
        if market_growth_rate is not None:
            # Blend company trajectory with market
            market_adjustment = (market_growth_rate - base_growth) * 0.3

        # Calculate scenarios
        base_rate = base_growth + vector_adjustment
        optimistic_rate = base_rate * 1.3
        pessimistic_rate = base_rate * 0.6

        # Apply adjustments
        base_rate += market_adjustment
        optimistic_rate += market_adjustment
        pessimistic_rate += market_adjustment

        # Ensure non-negative growth in pessimistic scenario
        pessimistic_rate = max(-0.3, pessimistic_rate)

        # Calculate projected revenues
        base_revenue = current_revenue * (1 + base_rate)
        optimistic_revenue = current_revenue * (1 + optimistic_rate)
        pessimistic_revenue = current_revenue * (1 + pessimistic_rate)

        # Determine confidence level
        confidence = self._determine_confidence(financial_intelligence, base_rate)

        # Generate rationale
        rationale = self._generate_rationale(
            financial_intelligence,
            base_rate,
            vector_adjustment,
            confidence,
        )

        return ProjectionResult(
            projected_revenue_12mo=round(base_revenue, 1),
            confidence=confidence,
            rationale=rationale,
            scenarios={
                "optimistic": round(optimistic_revenue, 1),
                "base": round(base_revenue, 1),
                "pessimistic": round(pessimistic_revenue, 1),
            },
        )

    def _determine_base_growth_rate(self, fi: FinancialIntelligence) -> float:
        """Determine base growth rate from trajectory analysis."""
        # Use CAGR if available
        if fi.cagr_3yr is not None and fi.cagr_3yr > 0:
            # Recent CAGR is strong predictor
            return fi.cagr_3yr / 100

        # Use trajectory direction
        direction_multipliers = {
            TrajectoryDirection.ACCELERATING: 0.35,
            TrajectoryDirection.STEADY: 0.15,
            TrajectoryDirection.DECELERATING: 0.05,
            TrajectoryDirection.DECLINING: -0.10,
            TrajectoryDirection.UNKNOWN: 0.15,
        }

        return direction_multipliers.get(fi.growth_trajectory, 0.15)

    def _calculate_vector_adjustment(self, fi: FinancialIntelligence) -> float:
        """Calculate growth adjustment from identified vectors."""
        adjustment = 0.0

        for vector in fi.primary_growth_vectors:
            # High-impact vectors add more to growth
            impact_multiplier = {
                "high": 0.10,
                "medium": 0.05,
                "low": 0.02,
            }.get(vector.estimated_impact, 0.03)

            # Confidence scales the impact
            adjustment += impact_multiplier * vector.confidence

        # Cap adjustment
        return min(0.25, adjustment)

    def _determine_confidence(
        self,
        fi: FinancialIntelligence,
        projected_growth_rate: float,
    ) -> ConfidenceLevel:
        """Determine confidence level in projection."""
        confidence_score = 0.0

        # More historical data = higher confidence
        if len(fi.revenue_timeline) >= 5:
            confidence_score += 0.3
        elif len(fi.revenue_timeline) >= 3:
            confidence_score += 0.2
        elif len(fi.revenue_timeline) >= 2:
            confidence_score += 0.1

        # Higher consistency = higher confidence
        confidence_score += (fi.growth_consistency_score / 10) * 0.3

        # Stable trajectory = higher confidence
        if fi.growth_trajectory == TrajectoryDirection.STEADY:
            confidence_score += 0.2
        elif fi.growth_trajectory == TrajectoryDirection.ACCELERATING:
            confidence_score += 0.15
        elif fi.growth_trajectory == TrajectoryDirection.DECELERATING:
            confidence_score += 0.05

        # Multiple growth vectors = higher confidence
        if len(fi.primary_growth_vectors) >= 3:
            confidence_score += 0.2
        elif len(fi.primary_growth_vectors) >= 2:
            confidence_score += 0.1
        elif len(fi.primary_growth_vectors) >= 1:
            confidence_score += 0.05

        # Moderate growth rates easier to predict than extreme
        growth_rate_abs = abs(projected_growth_rate)
        if 0.10 <= growth_rate_abs <= 0.30:
            confidence_score += 0.1
        elif growth_rate_abs > 0.50:
            confidence_score -= 0.1  # Extreme growth harder to predict

        # Map score to confidence level
        if confidence_score >= 0.7:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _generate_rationale(
        self,
        fi: FinancialIntelligence,
        base_rate: float,
        vector_adjustment: float,
        confidence: ConfidenceLevel,
    ) -> str:
        """Generate projection rationale."""
        parts = []

        # Base projection explanation
        parts.append(f"Base projection of {base_rate:.1%} growth driven by ")

        if fi.cagr_3yr:
            parts.append(f"historical 3-year CAGR of {fi.cagr_3yr}%.")
        elif fi.growth_trajectory != TrajectoryDirection.UNKNOWN:
            parts.append(f"{fi.growth_trajectory.value} growth trajectory.")
        else:
            parts.append("industry average benchmarks.")

        # Vector impact
        if vector_adjustment > 0:
            parts.append(f"Growth vectors add {vector_adjustment:.1%} to base rate.")

        # Primary vectors
        if fi.primary_growth_vectors:
            vector_names = [v.name for v in fi.primary_growth_vectors[:2]]
            parts.append(f"Key drivers: {', '.join(vector_names)}.")

        # Confidence explanation
        confidence_explanations = {
            ConfidenceLevel.HIGH: (
                "High confidence due to consistent historical performance and clear growth vectors."
            ),
            ConfidenceLevel.MEDIUM: (
                "Medium confidence based on available data; projection may vary with market conditions."
            ),
            ConfidenceLevel.LOW: (
                "Low confidence due to limited historical data or volatile growth patterns; treat as rough estimate."
            ),
        }
        parts.append(confidence_explanations.get(confidence, ""))

        return " ".join(parts)

    def quick_project(
        self,
        current_revenue: float,
        growth_rate: Optional[float] = None,
        confidence: Optional[ConfidenceLevel] = None,
    ) -> ProjectionResult:
        """Quick projection when full intelligence not available.

        Args:
            current_revenue: Current annual revenue
            growth_rate: Known growth rate
            confidence: Override confidence level

        Returns:
            Simplified projection
        """
        rate = (growth_rate / 100) if growth_rate is not None else self.default_growth_rate

        base_revenue = current_revenue * (1 + rate)
        optimistic = current_revenue * (1 + rate * 1.3)
        pessimistic = current_revenue * (1 + rate * 0.6)

        conf = confidence or (ConfidenceLevel.HIGH if growth_rate is not None else ConfidenceLevel.LOW)

        return ProjectionResult(
            projected_revenue_12mo=round(base_revenue, 1),
            confidence=conf,
            rationale=(
                f"Quick projection based on {rate:.1%} growth rate. "
                f"{'Historical data available.' if growth_rate is not None else 'Limited data - rough estimate.'}"
            ),
            scenarios={
                "optimistic": round(optimistic, 1),
                "base": round(base_revenue, 1),
                "pessimistic": round(pessimistic, 1),
            },
        )
