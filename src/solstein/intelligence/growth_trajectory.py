"""Growth trajectory analyzer for Epic 2.

Analyzes revenue trends, calculates CAGR, detects consistency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .financial_models import (
    ConfidenceLevel,
    RevenuePoint,
    TrajectoryDirection,
)


@dataclass
class TrajectoryAnalysis:
    """Result of trajectory analysis."""

    direction: TrajectoryDirection
    cagr_3yr: float | None
    cagr_5yr: float | None
    consistency_score: float
    volatility_index: float
    narrative: str


class GrowthTrajectoryAnalyzer:
    """Analyze company growth trajectory from revenue timeline."""

    def __init__(self):
        self.min_years_for_cagr = 2

    def analyze(
        self,
        revenue_timeline: list[RevenuePoint],
        current_growth_rate: float | None = None,
    ) -> TrajectoryAnalysis:
        """Analyze growth trajectory from revenue timeline.

        Args:
            revenue_timeline: List of revenue points over time
            current_growth_rate: Current year-over-year growth rate if known

        Returns:
            TrajectoryAnalysis with direction, CAGR, and narrative
        """
        if len(revenue_timeline) < 2:
            return TrajectoryAnalysis(
                direction=TrajectoryDirection.UNKNOWN,
                cagr_3yr=None,
                cagr_5yr=None,
                consistency_score=0.0,
                volatility_index=0.0,
                narrative="Insufficient revenue history for trajectory analysis.",
            )

        # Sort by year
        sorted_timeline = sorted(revenue_timeline, key=lambda x: x.year)

        # Calculate CAGR
        cagr_3yr = self._calculate_cagr(sorted_timeline, years=3)
        cagr_5yr = self._calculate_cagr(sorted_timeline, years=5)

        # Calculate consistency and volatility
        consistency_score = self._calculate_consistency_score(sorted_timeline)
        volatility_index = self._calculate_volatility(sorted_timeline)

        # Determine trajectory direction
        direction = self._determine_direction(sorted_timeline, cagr_3yr, current_growth_rate)

        # Generate narrative
        narrative = self._generate_narrative(direction, cagr_3yr, cagr_5yr, consistency_score, sorted_timeline)

        return TrajectoryAnalysis(
            direction=direction,
            cagr_3yr=cagr_3yr,
            cagr_5yr=cagr_5yr,
            consistency_score=consistency_score,
            volatility_index=volatility_index,
            narrative=narrative,
        )

    def _calculate_cagr(self, timeline: list[RevenuePoint], years: int) -> float | None:
        """Calculate compound annual growth rate.

        Args:
            timeline: Sorted revenue timeline
            years: Number of years for CAGR calculation

        Returns:
            CAGR as percentage, or None if insufficient data
        """
        if len(timeline) < 2:
            return None

        # Find start and end points within the year range
        end_point = timeline[-1]
        start_year = end_point.year - years

        # Find start point closest to but not before start_year
        start_point = None
        for point in timeline:
            if point.year >= start_year and point.revenue > 0:
                start_point = point
                break

        if start_point is None:
            # Use earliest available point
            for point in timeline:
                if point.revenue > 0:
                    start_point = point
                    break

        if start_point is None or start_point == end_point:
            return None

        if start_point.revenue <= 0:
            return None

        # Calculate actual years between points
        actual_years = end_point.year - start_point.year
        if actual_years < 1:
            return None

        # CAGR = (End Value / Start Value)^(1/n) - 1
        try:
            cagr = ((end_point.revenue / start_point.revenue) ** (1 / actual_years) - 1) * 100
            return round(cagr, 1)
        except (ValueError, ZeroDivisionError):
            return None

    def _calculate_consistency_score(self, timeline: list[RevenuePoint]) -> float:
        """Calculate growth consistency score (0-10).

        Measures how consistent growth has been year-over-year.
        Higher score = more consistent/predictable growth.

        Args:
            timeline: Sorted revenue timeline

        Returns:
            Consistency score from 0-10
        """
        if len(timeline) < 3:
            return 5.0  # Neutral score for insufficient data

        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(timeline)):
            if timeline[i - 1].revenue > 0:
                growth = ((timeline[i].revenue - timeline[i - 1].revenue) / timeline[i - 1].revenue) * 100
                growth_rates.append(growth)

        if len(growth_rates) < 2:
            return 5.0

        # Calculate standard deviation of growth rates
        mean_growth = sum(growth_rates) / len(growth_rates)
        variance = sum((r - mean_growth) ** 2 for r in growth_rates) / len(growth_rates)
        std_dev = math.sqrt(variance)

        # Convert to consistency score (lower std_dev = higher consistency)
        # Benchmark: std_dev of 50% = score of 0, std_dev of 0% = score of 10
        consistency = max(0, min(10, 10 - (std_dev / 5)))

        return round(consistency, 1)

    def _calculate_volatility(self, timeline: list[RevenuePoint]) -> float:
        """Calculate volatility index from revenue changes.

        Args:
            timeline: Sorted revenue timeline

        Returns:
            Volatility index (coefficient of variation)
        """
        if len(timeline) < 2:
            return 0.0

        revenues = [p.revenue for p in timeline if p.revenue > 0]
        if len(revenues) < 2:
            return 0.0

        mean_revenue = sum(revenues) / len(revenues)
        if mean_revenue == 0:
            return 0.0

        variance = sum((r - mean_revenue) ** 2 for r in revenues) / len(revenues)
        std_dev = math.sqrt(variance)

        # Coefficient of variation
        volatility = (std_dev / mean_revenue) * 100

        return round(volatility, 1)

    def _determine_direction(
        self,
        timeline: list[RevenuePoint],
        cagr_3yr: float | None,
        current_growth_rate: float | None,
    ) -> TrajectoryDirection:
        """Determine growth trajectory direction.

        Args:
            timeline: Sorted revenue timeline
            cagr_3yr: 3-year CAGR if available
            current_growth_rate: Current YoY growth rate if available

        Returns:
            TrajectoryDirection classification
        """
        if len(timeline) < 2:
            return TrajectoryDirection.UNKNOWN

        # Use recent growth trends
        recent_points = timeline[-3:]  # Last 3 years max
        if len(recent_points) < 2:
            recent_points = timeline

        # Calculate recent growth rates
        recent_growth_rates = []
        for i in range(1, len(recent_points)):
            if recent_points[i - 1].revenue > 0:
                growth = (
                    (recent_points[i].revenue - recent_points[i - 1].revenue) / recent_points[i - 1].revenue
                ) * 100
                recent_growth_rates.append(growth)

        if not recent_growth_rates:
            return TrajectoryDirection.UNKNOWN

        # Determine direction based on trend
        if len(recent_growth_rates) >= 2:
            # Check if growth is accelerating or decelerating
            first_growth = recent_growth_rates[0]
            last_growth = recent_growth_rates[-1]

            if last_growth < -10:
                return TrajectoryDirection.DECLINING
            elif last_growth > first_growth + 10:
                return TrajectoryDirection.ACCELERATING
            elif last_growth < first_growth - 10:
                return TrajectoryDirection.DECELERATING
            else:
                return TrajectoryDirection.STEADY
        else:
            # Single growth rate available
            growth = recent_growth_rates[0]
            if growth < -10:
                return TrajectoryDirection.DECLINING
            elif growth > 30:
                return TrajectoryDirection.ACCELERATING
            elif growth < 5:
                return TrajectoryDirection.DECELERATING
            else:
                return TrajectoryDirection.STEADY

    def _generate_narrative(
        self,
        direction: TrajectoryDirection,
        cagr_3yr: float | None,
        cagr_5yr: float | None,
        consistency_score: float,
        timeline: list[RevenuePoint],
    ) -> str:
        """Generate trajectory narrative.

        Args:
            direction: Trajectory direction
            cagr_3yr: 3-year CAGR
            cagr_5yr: 5-year CAGR
            consistency_score: Growth consistency score
            timeline: Revenue timeline

        Returns:
            Narrative description of trajectory
        """
        parts = []

        # Direction description
        direction_desc = {
            TrajectoryDirection.ACCELERATING: "accelerating growth trajectory",
            TrajectoryDirection.STEADY: "steady growth trajectory",
            TrajectoryDirection.DECELERATING: "decelerating growth trajectory",
            TrajectoryDirection.DECLINING: "declining revenue trajectory",
            TrajectoryDirection.UNKNOWN: "unclear growth trajectory",
        }
        parts.append(f"The company shows a {direction_desc[direction]}.")

        # CAGR information
        if cagr_3yr is not None:
            growth_desc = "strong" if cagr_3yr > 30 else "moderate" if cagr_3yr > 10 else "slow"
            if cagr_3yr < 0:
                growth_desc = "negative"
            parts.append(f"3-year CAGR of {cagr_3yr}% indicates {growth_desc} historical growth.")

        if cagr_5yr is not None and cagr_5yr != cagr_3yr:
            parts.append(f"5-year CAGR of {cagr_5yr}% shows longer-term trend.")

        # Consistency
        consistency_desc = (
            "highly consistent"
            if consistency_score >= 8
            else "moderately consistent"
            if consistency_score >= 5
            else "volatile"
        )
        parts.append(f"Growth consistency score of {consistency_score}/10 suggests {consistency_desc} performance.")

        # Recent revenue context
        if timeline:
            latest = timeline[-1]
            parts.append(f"Latest recorded revenue: €{latest.revenue:.1f}M ({latest.year}).")

        return " ".join(parts)

    def estimate_from_single_point(
        self,
        current_revenue: float,
        current_growth_rate: float,
        years_history: int = 3,
    ) -> TrajectoryAnalysis:
        """Estimate trajectory from single revenue point and growth rate.

        Used when full timeline is not available.

        Args:
            current_revenue: Current revenue in millions
            current_growth_rate: Current YoY growth rate (%)
            years_history: Estimated years of history

        Returns:
            Estimated trajectory analysis
        """
        # Estimate past revenue based on growth rate
        estimated_past = current_revenue / ((1 + current_growth_rate / 100) ** years_history)

        timeline = [
            RevenuePoint(
                year=2024 - years_history,
                revenue=estimated_past,
                source="estimated",
                confidence=ConfidenceLevel.LOW,
            ),
            RevenuePoint(
                year=2024,
                revenue=current_revenue,
                source="reported",
                confidence=ConfidenceLevel.MEDIUM,
            ),
        ]

        return self.analyze(timeline, current_growth_rate)
