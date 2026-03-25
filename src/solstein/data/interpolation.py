"""
Task 4: NULL Handling Strategy with Interpolation

Implements strategies for handling missing data across different field types:
- Revenue: Linear or geometric interpolation from timeline
- Growth: Calculate from revenue timeline or use sector average
- Employees: Use last known value or estimate from revenue
- All interpolations are flagged with 'is_interpolated' for transparency

Key Principle: Never invent data without clear provenance.
All interpolations are explicitly marked and documented.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class InterpolationConfig:
    """Configuration for interpolation thresholds and strategies."""

    # Revenue interpolation
    revenue_min_timeline_points: int = 2  # Need at least 2 points to interpolate
    revenue_interpolation_method: str = "geometric"  # "linear" or "geometric"
    revenue_max_gap_years: int = 3  # Don't interpolate gaps > 3 years

    # Growth interpolation
    growth_min_timeline_points: int = 2
    growth_use_sector_average: bool = True
    growth_sector_average_fallback: float = 10.0  # % per year

    # Employee interpolation
    employee_min_timeline_points: int = 2
    employee_use_last_known: bool = True
    employee_estimate_from_revenue: bool = True
    employee_revenue_ratio: float = 0.0003  # Employees per EUR of revenue

    # General
    flag_all_interpolations: bool = True  # Always mark interpolated values


class InterpolationEngine:
    """Engine for interpolating missing financial data."""

    def __init__(self, config: InterpolationConfig | None = None):
        """Initialize with configuration."""
        self.config = config or InterpolationConfig()
        logger.info(f"InterpolationEngine initialized with config: {self.config}")

    def interpolate_revenue(
        self,
        revenue_timeline: list[dict] | None = None,
        current_revenue: float | None = None,
    ) -> tuple[float | None, bool]:
        """
        Interpolate missing revenue from timeline.

        Args:
            revenue_timeline: List of {year, revenue} dicts
            current_revenue: Current revenue value (if already known)

        Returns:
            Tuple of (interpolated_revenue, is_interpolated)
        """
        # If revenue is already known, return it
        if current_revenue is not None:
            return current_revenue, False

        # If no timeline, can't interpolate
        if not revenue_timeline or len(revenue_timeline) < self.config.revenue_min_timeline_points:
            return None, False

        # Sort timeline by year
        sorted_timeline = sorted(revenue_timeline, key=lambda x: x.get("year", 0))

        # Find gaps and interpolate
        for i in range(len(sorted_timeline) - 1):
            current_year = sorted_timeline[i].get("year")
            next_year = sorted_timeline[i + 1].get("year")
            current_revenue_val = sorted_timeline[i].get("revenue")
            next_revenue_val = sorted_timeline[i + 1].get("revenue")

            if current_revenue_val is None or next_revenue_val is None:
                continue

            gap = next_year - current_year
            if gap <= 0 or gap > self.config.revenue_max_gap_years:
                continue

            # Interpolate using configured method
            if self.config.revenue_interpolation_method == "geometric":
                # Geometric mean: (current * next) ^ (1/gap)
                interpolated = (current_revenue_val * next_revenue_val) ** (1 / gap)
            else:
                # Linear: current + (next - current) / gap
                interpolated = current_revenue_val + (next_revenue_val - current_revenue_val) / gap

            logger.info(f"Interpolated revenue: {current_revenue_val} -> {next_revenue_val} = {interpolated}")
            return interpolated, True

        # No interpolation possible
        return None, False

    def interpolate_growth_rate(
        self,
        revenue_timeline: list[dict] | None = None,
        current_growth: float | None = None,
    ) -> tuple[float | None, bool]:
        """
        Interpolate missing growth rate from revenue timeline.

        Args:
            revenue_timeline: List of {year, revenue} dicts
            current_growth: Current growth rate (if already known)

        Returns:
            Tuple of (interpolated_growth, is_interpolated)
        """
        # If growth is already known, return it
        if current_growth is not None:
            return current_growth, False

        # If no timeline, use sector average
        if not revenue_timeline or len(revenue_timeline) < self.config.growth_min_timeline_points:
            if self.config.growth_use_sector_average:
                logger.info(f"Using sector average growth: {self.config.growth_sector_average_fallback}%")
                return self.config.growth_sector_average_fallback, True
            return None, False

        # Calculate growth from most recent years
        sorted_timeline = sorted(revenue_timeline, key=lambda x: x.get("year", 0))

        if len(sorted_timeline) >= 2:
            recent = sorted_timeline[-1]
            previous = sorted_timeline[-2]

            recent_revenue = recent.get("revenue")
            previous_revenue = previous.get("revenue")
            recent_year = recent.get("year")
            previous_year = previous.get("year")

            if recent_revenue and previous_revenue and recent_year and previous_year:
                years_diff = recent_year - previous_year
                if years_diff > 0:
                    # Calculate CAGR
                    growth = ((recent_revenue / previous_revenue) ** (1 / years_diff) - 1) * 100
                    logger.info(f"Calculated growth from timeline: {growth}%")
                    return growth, True

        # Fallback to sector average
        if self.config.growth_use_sector_average:
            logger.info(f"Using sector average growth: {self.config.growth_sector_average_fallback}%")
            return self.config.growth_sector_average_fallback, True

        return None, False

    def interpolate_employees(
        self,
        employee_timeline: list[dict] | None = None,
        current_employees: int | None = None,
        revenue: float | None = None,
    ) -> tuple[int | None, bool]:
        """
        Interpolate missing employee count.

        Args:
            employee_timeline: List of {year, employees} dicts
            current_employees: Current employee count (if already known)
            revenue: Revenue for estimation fallback

        Returns:
            Tuple of (interpolated_employees, is_interpolated)
        """
        # If employees is already known, return it
        if current_employees is not None:
            return current_employees, False

        # Try to use last known value from timeline
        if employee_timeline and self.config.employee_use_last_known:
            sorted_timeline = sorted(employee_timeline, key=lambda x: x.get("year", 0))
            last_known = sorted_timeline[-1].get("employees")
            if last_known is not None:
                logger.info(f"Using last known employee count: {last_known}")
                return last_known, True

        # Try to estimate from revenue
        if revenue and self.config.employee_estimate_from_revenue:
            estimated = int(revenue * self.config.employee_revenue_ratio)
            logger.info(f"Estimated employees from revenue: {estimated}")
            return estimated, True

        return None, False

    def validate_interpolation(
        self,
        original_value: float | None,
        interpolated_value: float | None,
        is_interpolated: bool,
    ) -> bool:
        """
        Validate that interpolation is reasonable.

        Args:
            original_value: Original value (if any)
            interpolated_value: Interpolated value
            is_interpolated: Whether value was interpolated

        Returns:
            True if interpolation is valid
        """
        if not is_interpolated:
            return True

        if interpolated_value is None:
            return False

        # Check for reasonable ranges
        if interpolated_value < 0:
            logger.warning(f"Interpolated value is negative: {interpolated_value}")
            return False

        # If we have original value, check it's not wildly different
        if original_value is not None:
            ratio = interpolated_value / original_value if original_value != 0 else 0
            if ratio < 0.5 or ratio > 2.0:
                logger.warning(
                    f"Interpolated value differs significantly from original: "
                    f"{original_value} -> {interpolated_value} (ratio: {ratio})"
                )
                # Don't reject, just warn

        return True


# Global instance
interpolation_engine = InterpolationEngine()
