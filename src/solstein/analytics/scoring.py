"""
Scoring algorithms for SolStein competitive intelligence.

Calculates growth scores, financial health scores, and competitive positioning.
"""

from typing import Any
from datetime import datetime

from loguru import logger

from ..core.scoring_config import ScoringSettings
from ..domain.models import (
    Company,
    FinancialMetric,
    MarketAnalysis,
)


class GrowthScorer:
    """Calculate growth scores for companies."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()

    def calculate_scores(self, profile: Company) -> Company:
        """Calculate all scores for a company profile."""
        logger.debug(f"Calculating scores for {profile.name}")

        # Calculate individual scores
        growth_score = self._calculate_growth_score(profile.financials)
        financial_health_score = self._calculate_financial_health_score(
            profile.financials
        )
        competitive_position_score = self._calculate_competitive_position_score(profile)

        # Update profile with scores
        profile.growth_score = growth_score
        profile.financial_health_score = financial_health_score
        profile.competitive_position_score = competitive_position_score

        return profile

    def _calculate_growth_score(self, financials: FinancialMetric) -> float:
        """Calculate growth score (0-10)."""
        cfg = self.config.growth
        score = cfg.base_score

        # Revenue growth
        if financials.growth_rate is not None:
            growth_factor = min(
                financials.growth_rate / cfg.revenue_growth_divisor,
                cfg.revenue_growth_cap,
            )
            score += growth_factor

        # Employee productivity (Revenue per Employee)
        if financials.employees and financials.revenue:
            revenue_per_employee = financials.revenue / financials.employees
            if revenue_per_employee > cfg.efficiency_high_threshold:
                score += cfg.efficiency_high_bonus
            elif revenue_per_employee > cfg.efficiency_med_threshold:
                score += cfg.efficiency_med_bonus

        # Funding momentum
        if financials.funding_raised:
            if financials.funding_raised > cfg.funding_high_threshold:
                score += cfg.funding_high_bonus
            elif financials.funding_raised > cfg.funding_med_threshold:
                score += cfg.funding_med_bonus

        # Profitability growth
        if financials.profit_margin is not None:
            if financials.profit_margin > cfg.margin_high_threshold:
                score += cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                score += cfg.margin_med_bonus
            elif financials.profit_margin < 0:
                score += cfg.margin_negative_penalty

        return max(0.0, min(score, 10.0))

    def _calculate_financial_health_score(self, financials: FinancialMetric) -> float:
        """Calculate financial health score (0-10)."""
        cfg = self.config.financial
        score = cfg.base_score

        # Revenue scale
        if financials.revenue:
            if financials.revenue > cfg.revenue_large_threshold:
                score += cfg.revenue_large_bonus
            elif financials.revenue > cfg.revenue_med_threshold:
                score += cfg.revenue_med_bonus
            elif financials.revenue < cfg.revenue_small_threshold:
                score += cfg.revenue_small_penalty

        # Profitability
        if financials.profit_margin is not None:
            if financials.profit_margin > cfg.margin_high_threshold:
                score += cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                score += cfg.margin_med_bonus
            elif financials.profit_margin < 0:
                score += cfg.margin_negative_penalty

        # Employee efficiency
        if financials.employees and financials.revenue:
            revenue_per_employee = financials.revenue / financials.employees
            if revenue_per_employee > cfg.efficiency_exceptional_threshold:
                score += cfg.efficiency_exceptional_bonus
            elif revenue_per_employee > cfg.efficiency_good_threshold:
                score += cfg.efficiency_good_bonus
            elif revenue_per_employee < cfg.efficiency_low_threshold:
                score += cfg.efficiency_low_penalty

        # Funding cushion
        if financials.funding_raised and financials.revenue:
            funding_to_revenue = financials.funding_raised / financials.revenue
            if funding_to_revenue > cfg.cushion_high_ratio:
                score += cfg.cushion_high_bonus
            elif funding_to_revenue > cfg.cushion_med_ratio:
                score += cfg.cushion_med_bonus
            elif (
                funding_to_revenue < cfg.cushion_thin_ratio
                and financials.profit_margin is not None
                and financials.profit_margin < 5
            ):
                score += cfg.cushion_thin_penalty

        return max(0.0, min(score, 10.0))

    def _calculate_competitive_position_score(self, profile: Company) -> float:
        """Calculate competitive position score (0-10)."""
        cfg = self.config.competitive
        score = cfg.base_score

        # Tier positioning
        score += cfg.tier_scores.get(profile.tier, 0.0)

        # AI maturity
        score += cfg.ai_maturity_scores.get(profile.ai_maturity, 0.0)

        # SaaS maturity (Scale 1-10 to 0-2 normalized)
        saas_score = (profile.saas_maturity - 1) / 9 * 2.0
        score += saas_score

        # Geographic presence
        if len(profile.geographic_presence) > cfg.geo_global_count:
            score += cfg.geo_global_bonus
        elif len(profile.geographic_presence) > cfg.geo_regional_count:
            score += cfg.geo_regional_bonus
        elif len(profile.geographic_presence) == 1:
            score += cfg.geo_single_penalty

        # Tech stack
        if len(profile.tech_stack) > cfg.tech_diverse_count:
            score += cfg.tech_diverse_bonus
        elif not profile.tech_stack:
            score += cfg.tech_none_penalty

        return max(0.0, min(score, 10.0))


class MarketAnalyzer:
    """Analyze market-level metrics and trends."""

    def analyze_market(self, profiles: list[Company]) -> MarketAnalysis:
        """Analyze a market based on company profiles."""
        logger.info(f"Analyzing market with {len(profiles)} companies")

        # Calculate base metrics needed for return
        revenues = [p.financials.revenue for p in profiles if p.financials.revenue]
        market_size = sum(revenues) if revenues else 0.0
        
        growth_rates = [
            p.financials.growth_rate 
            for p in profiles 
            if p.financials.growth_rate is not None
        ]
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0
        
        # Calculate CR4
        cr4 = 0.0
        if revenues:
            sorted_revenues = sorted(revenues, reverse=True)
            top_4 = sorted_revenues[:4]
            if sum(revenues) > 0:
                cr4 = sum(top_4) / sum(revenues) * 100

        # Return Domain Entity
        return MarketAnalysis(
            market_name=profiles[0].industry if profiles else "Unknown Market",
            analysis_date=datetime.now(),
            companies=profiles,
            total_market_size=market_size,
            growth_rate=avg_growth,
            concentration_ratio=cr4,
            barriers_to_entry=self._determine_barriers(profiles),
            key_trends=self._determine_trends(profiles),
            regulatory_environment=["Industry Standard Compliance", "Data Privacy Regulations"],
            swot_analysis=self._calculate_swot(profiles),
            recommendations=self._generate_recommendations(profiles, avg_growth, cr4),
        )

    def _determine_barriers(self, profiles: list[Company]) -> list[str]:
        """Determine likely barriers to entry based on market state."""
        barriers = ["Capital Intensity"]
        if len(profiles) > 5:
            barriers.append("High Competitive Rivalry")
        return barriers

    def _determine_trends(self, profiles: list[Company]) -> list[str]:
        """Identify market trends from aggregate company data."""
        trends = ["Digital Transformation"]
        if any(p.ai_maturity in ["Strong", "Very Strong"] for p in profiles):
            trends.append("Advanced AI Integration")
        if any("Cloud" in str(p.tech_stack) for p in profiles):
            trends.append("Cloud-Native Infrastructure")
        return trends

    def _generate_recommendations(self, profiles: list[Company], avg_growth: float, cr4: float) -> list[str]:
        """Generate strategic recommendations based on market metrics."""
        recommendations = []
        if avg_growth > 15:
            recommendations.append("Aggressive expansion into high-growth verticals")
        if cr4 > 70:
            recommendations.append("Focus on niche differentiation to compete with market leaders")
        else:
            recommendations.append("Consolidation opportunities in a fragmented market")
        return recommendations

    def _calculate_tier_distribution(self, profiles: list[Company]) -> dict[str, int]:
        """Calculate distribution of companies across tiers."""
        distribution = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0, "Tier 4": 0}

        for profile in profiles:
            distribution[profile.tier] = distribution.get(profile.tier, 0) + 1

        return distribution

    def _calculate_growth_metrics(self, profiles: list[Company]) -> dict[str, float]:
        """Calculate market growth metrics."""
        growth_rates = [
            p.financials.growth_rate
            for p in profiles
            if p.financials.growth_rate is not None
        ]

        if not growth_rates:
            return {"average": 0.0, "median": 0.0, "high_growth_count": 0}

        sorted_rates = sorted(growth_rates)
        n = len(sorted_rates)

        return {
            "average": sum(growth_rates) / n,
            "median": sorted_rates[n // 2]
            if n % 2 == 1
            else (sorted_rates[n // 2 - 1] + sorted_rates[n // 2]) / 2,
            "high_growth_count": len([r for r in growth_rates if r > 20]),
            "declining_count": len([r for r in growth_rates if r < 0]),
        }

    def _calculate_financial_metrics(self, profiles: list[Company]) -> dict[str, Any]:
        """Calculate market financial metrics."""
        revenues = [p.financials.revenue for p in profiles if p.financials.revenue]
        profits = [
            p.financials.profit_margin
            for p in profiles
            if p.financials.profit_margin is not None
        ]

        metrics = {
            "total_revenue": sum(revenues) if revenues else 0,
            "average_revenue": sum(revenues) / len(revenues) if revenues else 0,
            "profitable_companies": len([p for p in profits if p > 0]),
            "unprofitable_companies": len([p for p in profits if p <= 0]),
            "average_profit_margin": sum(profits) / len(profits) if profits else 0,
        }

        # Calculate market concentration (CR4)
        if revenues:
            sorted_revenues = sorted(revenues, reverse=True)
            top_4 = sorted_revenues[:4]
            metrics["cr4"] = sum(top_4) / sum(revenues) * 100

        return metrics

    def _calculate_technology_metrics(self, profiles: list[Company]) -> dict[str, Any]:
        """Calculate technology adoption metrics."""
        ai_counts = {"None": 0, "Low": 0, "Moderate": 0, "Strong": 0, "Very Strong": 0}
        saas_scores = [p.saas_maturity for p in profiles]

        for profile in profiles:
            ai_counts[profile.ai_maturity] = ai_counts.get(profile.ai_maturity, 0) + 1

        # Count unique technologies
        all_tech = set()
        for profile in profiles:
            all_tech.update(profile.tech_stack)

        return {
            "ai_adoption": ai_counts,
            "average_saas_maturity": sum(saas_scores) / len(saas_scores)
            if saas_scores
            else 0,
            "unique_technologies": len(all_tech),
            "most_common_technologies": self._most_common_tech(profiles),
        }

    def _most_common_tech(
        self, profiles: list[Company], top_n: int = 5
    ) -> list[tuple[str, int]]:
        """Find most common technologies in the market."""
        tech_counts: dict[str, int] = {}

        for profile in profiles:
            for tech in profile.tech_stack:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        return sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def _calculate_competitive_intensity(
        self, profiles: list[Company]
    ) -> dict[str, Any]:
        """Calculate competitive intensity metrics."""
        threat_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

        for profile in profiles:
            threat_counts[profile.threat_level] = (
                threat_counts.get(profile.threat_level, 0) + 1
            )

        # Calculate Herfindahl-Hirschman Index (HHI) approximation
        revenues = [p.financials.revenue for p in profiles if p.financials.revenue]
        if revenues:
            total_revenue = sum(revenues)
            market_shares = [r / total_revenue * 100 for r in revenues]
            hhi = sum(share**2 for share in market_shares)
        else:
            hhi = 0.0

        return {
            "threat_distribution": threat_counts,
            "hhi": hhi,
            "market_concentration": self._interpret_hhi(hhi),
            "direct_competitors": len(
                [p for p in profiles if p.threat_level in ["High", "Critical"]]
            ),
        }

    def _interpret_hhi(self, hhi: float) -> str:
        """Interpret HHI score for market concentration."""
        if hhi > 2500:
            return "Highly Concentrated"
        elif hhi > 1500:
            return "Moderately Concentrated"
        elif hhi > 1000:
            return "Somewhat Concentrated"
        else:
            return "Competitive"

    def _calculate_swot(self, profiles: list[Company]) -> dict[str, Any]:
        """Generate basic SWOT analysis based on company data."""
        return {
            "strengths": ["Strong Growth"] if any(p.financials.growth_rate and p.financials.growth_rate > 20 for p in profiles) else ["Established Players"],
            "weaknesses": ["Fragmented Market"] if len(profiles) > 10 else ["Niche Market"],
            "opportunities": ["AI Adoption", "Regional Expansion"],
            "threats": ["High Barriers to Entry", "Regulatory Changes"],
        }


class CompetitiveOverlapCalculator:
    """Calculate competitive overlap between companies."""

    def calculate_overlap(self, profile1: Company, profile2: Company) -> float:
        """Calculate overlap score between two companies (0-1)."""
        scores = []

        # Industry overlap
        if profile1.industry == profile2.industry:
            scores.append(1.0)
        else:
            scores.append(0.0)

        # Geographic overlap
        geo_overlap = self._calculate_geographic_overlap(profile1, profile2)
        scores.append(geo_overlap)

        # Technology overlap
        tech_overlap = self._calculate_technology_overlap(profile1, profile2)
        scores.append(tech_overlap)

        # Customer segment overlap (simplified)
        if profile1.key_customers and profile2.key_customers:
            customer_overlap = self._calculate_customer_overlap(profile1, profile2)
            scores.append(customer_overlap)

        # Tier proximity
        tier_proximity = self._calculate_tier_proximity(profile1, profile2)
        scores.append(tier_proximity)

        # Average the scores
        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_geographic_overlap(self, p1: Company, p2: Company) -> float:
        """Calculate geographic overlap (0-1)."""
        if not p1.geographic_presence or not p2.geographic_presence:
            return 0.0

        set1 = set(p1.geographic_presence)
        set2 = set(p2.geographic_presence)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _calculate_technology_overlap(self, p1: Company, p2: Company) -> float:
        """Calculate technology stack overlap (0-1)."""
        if not p1.tech_stack or not p2.tech_stack:
            return 0.0

        set1 = set(p1.tech_stack)
        set2 = set(p2.tech_stack)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _calculate_customer_overlap(self, p1: Company, p2: Company) -> float:
        """Calculate customer overlap (0-1)."""
        # Simple implementation - could be enhanced with actual customer data
        if not p1.key_customers or not p2.key_customers:
            return 0.0

        # Count overlapping industries/sectors in customer lists
        common_terms = 0
        for cust1 in p1.key_customers:
            for cust2 in p2.key_customers:
                # Check for common words (very simplified)
                words1 = set(cust1.lower().split())
                words2 = set(cust2.lower().split())
                if words1.intersection(words2):
                    common_terms += 1

        max_customers = max(len(p1.key_customers), len(p2.key_customers))
        return common_terms / max_customers if max_customers > 0 else 0.0

    def _calculate_tier_proximity(self, p1: Company, p2: Company) -> float:
        """Calculate tier proximity score (0-1)."""
        tier_order = {"Tier 1": 4, "Tier 2": 3, "Tier 3": 2, "Tier 4": 1}

        tier1 = tier_order.get(p1.tier, 2)
        tier2 = tier_order.get(p2.tier, 2)

        distance = abs(tier1 - tier2)
        return 1.0 - (distance / 3.0)  # Normalize to 0-1
