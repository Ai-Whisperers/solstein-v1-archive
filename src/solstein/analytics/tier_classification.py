"""Enhanced tier classification with UX improvements (EPIC-FIX-007).

Provides more granular tier classification and user-friendly explanations
to address the "all Tier 4" UX issue.
"""

from dataclasses import dataclass
from typing import Optional

from solstein.domain.models import Company, CompanyTier


@dataclass
class TierClassification:
    """Detailed tier classification result."""

    tier: CompanyTier
    sub_tier: str  # e.g., "4A", "4B", "4C" for granularity
    display_name: str  # e.g., "Tier 4A - Growth Stage"
    explanation: str  # Why this tier was assigned
    revenue_range: str  # e.g., "€5M - €10M"
    trajectory: str  # "↑ Growing", "→ Stable", "↓ Declining"
    next_tier_threshold: Optional[str]  # What it takes to reach next tier


class EnhancedTierClassifier:
    """Enhanced tier classifier with sub-tiers and explanations."""

    TIER_THRESHOLDS = {
        CompanyTier.TIER_1: (1000, None),  # €1B+
        CompanyTier.TIER_2: (100, 1000),  # €100M - €1B
        CompanyTier.TIER_3: (10, 100),  # €10M - €100M
        CompanyTier.TIER_4: (0, 10),  # €0 - €10M
    }

    SUB_TIER_RANGES = {
        # Tier 4 sub-tiers (most common for startups)
        CompanyTier.TIER_4: [
            (7, "4A", "€7M - €10M", "Approaching Tier 3"),
            (5, "4B", "€5M - €7M", "Established Growth"),
            (3, "4C", "€3M - €5M", "Proven Product-Market Fit"),
            (1, "4D", "€1M - €3M", "Early Growth"),
            (0, "4E", "< €1M", "Seed/Startup"),
        ],
        # Tier 3 sub-tiers
        CompanyTier.TIER_3: [
            (50, "3A", "€50M - €100M", "Scale-Up Leader"),
            (25, "3B", "€25M - €50M", "Rapid Expansion"),
            (10, "3C", "€10M - €25M", "Growth Stage"),
        ],
        # Tier 2 sub-tiers
        CompanyTier.TIER_2: [
            (500, "2A", "€500M - €1B", "Market Leader"),
            (250, "2B", "€250M - €500M", "Established Leader"),
            (100, "2C", "€100M - €250M", "Growth Leader"),
        ],
        # Tier 1 sub-tiers
        CompanyTier.TIER_1: [
            (5000, "1A", "€5B+", "Enterprise Giant"),
            (1000, "1B", "€1B - €5B", "Large Enterprise"),
        ],
    }

    def classify(self, company: Company) -> TierClassification:
        """Classify a company with detailed tier information."""
        revenue = self._get_revenue(company)
        growth = self._get_growth(company)

        # Determine base tier
        tier = self._determine_base_tier(revenue)

        # Determine sub-tier
        sub_tier, revenue_range, description = self._determine_sub_tier(tier, revenue)

        # Determine trajectory
        trajectory = self._determine_trajectory(growth)

        # Build display name
        display_name = f"{sub_tier} - {description}"

        # Build explanation
        explanation = self._build_explanation(tier, revenue, growth, trajectory)

        # Determine next tier threshold
        next_threshold = self._get_next_tier_threshold(tier, revenue)

        return TierClassification(
            tier=tier,
            sub_tier=sub_tier,
            display_name=display_name,
            explanation=explanation,
            revenue_range=revenue_range,
            trajectory=trajectory,
            next_tier_threshold=next_threshold,
        )

    def _get_revenue(self, company: Company) -> float:
        """Extract revenue from company."""
        if company.financials and company.financials.revenue:
            return company.financials.revenue
        return 0.0

    def _get_growth(self, company: Company) -> float:
        """Extract growth rate from company."""
        if company.financials and company.financials.growth_rate:
            return company.financials.growth_rate
        return 0.0

    def _determine_base_tier(self, revenue: float) -> CompanyTier:
        """Determine base tier from revenue."""
        if revenue >= 1000:
            return CompanyTier.TIER_1
        elif revenue >= 100:
            return CompanyTier.TIER_2
        elif revenue >= 10:
            return CompanyTier.TIER_3
        else:
            return CompanyTier.TIER_4

    def _determine_sub_tier(self, tier: CompanyTier, revenue: float) -> tuple:
        """Determine sub-tier within base tier."""
        sub_tiers = self.SUB_TIER_RANGES.get(tier, [])

        for threshold, code, range_str, desc in sub_tiers:
            if revenue >= threshold:
                return code, range_str, desc

        # Fallback to lowest sub-tier
        return f"{tier.value}E", "< €1M", "Early Stage"

    def _determine_trajectory(self, growth: float) -> str:
        """Determine growth trajectory."""
        if growth >= 30:
            return "↑ Hypergrowth"
        elif growth >= 10:
            return "↑ Growing"
        elif growth >= 0:
            return "→ Stable"
        else:
            return "↓ Declining"

    def _build_explanation(self, tier: CompanyTier, revenue: float, growth: float, trajectory: str) -> str:
        """Build human-readable tier explanation."""
        tier_names = {
            CompanyTier.TIER_1: "Enterprise Leaders",
            CompanyTier.TIER_2: "Growth Leaders",
            CompanyTier.TIER_3: "Scale-ups",
            CompanyTier.TIER_4: "Growth Stage",
        }

        base = f"Classified as {tier_names.get(tier, 'Unknown')} based on €{revenue:.1f}M revenue"

        if growth > 0:
            base += f" with {trajectory.lower()} trajectory"

        return base

    def _get_next_tier_threshold(self, tier: CompanyTier, revenue: float) -> Optional[str]:
        """Get description of what it takes to reach next tier."""
        thresholds = {
            CompanyTier.TIER_4: f"Reach €{10 - revenue:.1f}M more revenue for Tier 3",
            CompanyTier.TIER_3: f"Reach €{100 - revenue:.1f}M more revenue for Tier 2",
            CompanyTier.TIER_2: f"Reach €{1000 - revenue:.1f}M more revenue for Tier 1",
            CompanyTier.TIER_1: None,  # Already at top
        }
        return thresholds.get(tier)


def classify_company_tier(company: Company) -> TierClassification:
    """Convenience function to classify a single company."""
    classifier = EnhancedTierClassifier()
    return classifier.classify(company)
