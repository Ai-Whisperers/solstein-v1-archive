"""
Scoring algorithms for SolStein competitive intelligence.

Calculates growth scores, financial health scores, and competitive positioning.
"""

from datetime import datetime
from typing import Any

from loguru import logger

from ..core.scoring_config import ScoringSettings
from ..domain.models import (
    Company,
    FinancialMetric,
    MarketAnalysis,
    ScoreComponent,
    ScoringExplanation,
)
from .scorers.competitive_position import CompetitivePositionScorer
from .scorers.financial_health import FinancialHealthScorer
from .scorers.growth_momentum import GrowthMomentumScorer


def classify_company(score: float | None) -> str:
    """Central logic to classify a company based on its composite or growth score."""
    if score is None:
        return "Salt"
    if score >= 7.0:
        return "Phoenix"
    elif score <= 3.9:
        return "Lead"
    return "Salt"


class GrowthScorer:
    """Calculate growth scores for companies using composed scorers."""

    def __init__(self, config: ScoringSettings | None = None):
        self.config = config or ScoringSettings()
        self.growth_momentum_scorer = GrowthMomentumScorer(self.config)
        self.financial_health_scorer = FinancialHealthScorer(self.config)
        self.competitive_position_scorer = CompetitivePositionScorer(self.config)

    def calculate_scores(self, profile: Company) -> Company:
        """Calculate all scores for a company profile."""
        logger.debug(f"Calculating scores for {profile.name}")

        profile.scoring_breakdown = {}

        growth_score, growth_expl = self.growth_momentum_scorer.score(
            profile.financials
        )
        financial_health_score, fin_expl = self.financial_health_scorer.score(
            profile.financials
        )
        competitive_position_score, comp_expl = self.competitive_position_scorer.score(
            profile
        )

        profile.growth_score = growth_score
        profile.financial_health_score = financial_health_score
        profile.competitive_position_score = competitive_position_score

        if all(
            s is not None
            for s in [growth_score, financial_health_score, competitive_position_score]
        ):
            profile.composite_score = round(
                (growth_score * 0.4)
                + (financial_health_score * 0.3)
                + (competitive_position_score * 0.3),
                2,
            )
        else:
            profile.composite_score = growth_score

        # Always calculate classification
        profile.classification = classify_company(profile.composite_score)

        profile.scoring_breakdown["growth"] = growth_expl
        profile.scoring_breakdown["financial"] = fin_expl
        profile.scoring_breakdown["competitive"] = comp_expl

        return profile

    def _calculate_growth_score(
        self, financials: FinancialMetric
    ) -> tuple[float, ScoringExplanation]:  # noqa: E501
        """Calculate growth score (0-10) with explanation."""
        cfg = self.config.growth
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)

        # Revenue growth
        if financials.growth_rate is not None:
            growth_factor = min(
                financials.growth_rate / cfg.revenue_growth_divisor,
                cfg.revenue_growth_cap,
            )
            score += growth_factor
            explanation.components.append(
                ScoreComponent(
                    name="Revenue Growth",
                    value=growth_factor,
                    formula=f"min({financials.growth_rate}% / {cfg.revenue_growth_divisor}, {cfg.revenue_growth_cap})",  # noqa: E501
                    reasoning=f"High growth rate of {financials.growth_rate}% identified."
                    if financials.growth_rate > 15
                    else "Moderate growth rate identified.",  # noqa: E501
                )
            )

        # Employee productivity (Revenue per Employee)
        if financials.employees and financials.revenue:
            rev_per_emp = financials.revenue / financials.employees
            bonus = 0.0
            if rev_per_emp > cfg.efficiency_high_threshold:
                bonus = cfg.efficiency_high_bonus
            elif rev_per_emp > cfg.efficiency_med_threshold:
                bonus = cfg.efficiency_med_bonus

            if bonus > 0:
                score += bonus
                explanation.components.append(
                    ScoreComponent(
                        name="Employee Efficiency",
                        value=bonus,
                        formula=f"rev_per_emp({rev_per_emp:,.0f} EUR) > threshold",
                        reasoning="Revenue per employee is above efficiency benchmarks.",
                    )
                )

        # Funding momentum
        if financials.funding_raised:
            bonus = 0.0
            if financials.funding_raised > cfg.funding_high_threshold:
                bonus = cfg.funding_high_bonus
            elif financials.funding_raised > cfg.funding_med_threshold:
                bonus = cfg.funding_med_bonus

            if bonus > 0:
                score += bonus
                explanation.components.append(
                    ScoreComponent(
                        name="Funding Momentum",
                        value=bonus,
                        formula=f"funding({financials.funding_raised:,.0f} EUR) > threshold",  # noqa: E501
                        reasoning="Significant capital injection signals strong market confidence.",  # noqa: E501
                    )
                )

        # Profitability growth
        if financials.profit_margin is not None:
            adj = 0.0
            if financials.profit_margin > cfg.margin_high_threshold:
                adj = cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                adj = cfg.margin_med_bonus
            elif financials.profit_margin < 0:
                adj = cfg.margin_negative_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Profitability Profile",
                        value=adj,
                        formula=f"margin({financials.profit_margin}%) -> adjustment",
                        reasoning="Healthy margins contribute to growth score."
                        if adj > 0
                        else "Negative margins penalize growth score.",  # noqa: E501
                    )
                )

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation

    def _calculate_financial_health_score(
        self, financials: FinancialMetric
    ) -> tuple[float, ScoringExplanation]:  # noqa: E501
        """Calculate financial health score (0-10) with explanation."""
        cfg = self.config.financial
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)

        # Revenue scale
        if financials.revenue:
            adj = 0.0
            if financials.revenue > cfg.revenue_large_threshold:
                adj = cfg.revenue_large_bonus
            elif financials.revenue > cfg.revenue_med_threshold:
                adj = cfg.revenue_med_bonus
            elif financials.revenue < cfg.revenue_small_threshold:
                adj = cfg.revenue_small_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Revenue Scale",
                        value=adj,
                        formula=f"revenue({financials.revenue:,.0f} EUR) -> adjustment",
                        reasoning="Scale impacts financial stability scores.",
                    )
                )

        # Profitability
        if financials.profit_margin is not None:
            adj = 0.0
            if financials.profit_margin > cfg.margin_high_threshold:
                adj = cfg.margin_high_bonus
            elif financials.profit_margin > cfg.margin_med_threshold:
                adj = cfg.margin_med_bonus
            elif financials.profit_margin < 0:
                adj = cfg.margin_negative_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Profitability Health",
                        value=adj,
                        formula=f"margin({financials.profit_margin}%) -> adjustment",
                        reasoning="Operating margin is a key indicator of financial health.",
                    )
                )

        # Employee efficiency
        if financials.employees and financials.revenue:
            rev_per_emp = financials.revenue / financials.employees
            adj = 0.0
            if rev_per_emp > cfg.efficiency_exceptional_threshold:
                adj = cfg.efficiency_exceptional_bonus
            elif rev_per_emp > cfg.efficiency_good_threshold:
                adj = cfg.efficiency_good_bonus
            elif rev_per_emp < cfg.efficiency_low_threshold:
                adj = cfg.efficiency_low_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Operating Efficiency",
                        value=adj,
                        formula=f"rev_per_emp({rev_per_emp:,.0f} EUR) -> adjustment",
                        reasoning="Resource utilization efficiency.",
                    )
                )

        # Funding cushion
        if financials.funding_raised and financials.revenue:
            ratio = financials.funding_raised / financials.revenue
            adj = 0.0
            if ratio > cfg.cushion_high_ratio:
                adj = cfg.cushion_high_bonus
            elif ratio > cfg.cushion_med_ratio:
                adj = cfg.cushion_med_bonus
            elif (
                ratio < cfg.cushion_thin_ratio
                and financials.profit_margin is not None
                and financials.profit_margin < 5
            ):  # noqa: E501
                adj = cfg.cushion_thin_penalty

            if adj != 0:
                score += adj
                explanation.components.append(
                    ScoreComponent(
                        name="Funding Cushion",
                        value=adj,
                        formula=f"funding_ratio({ratio:.2f}) -> adjustment",
                        reasoning="Capital reserves relative to revenue scale.",
                    )
                )

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation

    def _calculate_competitive_position_score(
        self, profile: Company
    ) -> tuple[float, ScoringExplanation]:  # noqa: E501
        """Calculate competitive position score (0-10) with explanation."""
        cfg = self.config.competitive
        score = cfg.base_score
        explanation = ScoringExplanation(base_score=score)

        # Tier positioning
        tier_adj = cfg.tier_scores.get(profile.tier, 0.0)
        score += tier_adj
        explanation.components.append(
            ScoreComponent(
                name="Market Tier",
                value=tier_adj,
                formula=f"tier({profile.tier})",
                reasoning=f"Positioned as a {profile.tier} player in the market.",
            )
        )

        # AI maturity
        ai_adj = cfg.ai_maturity_scores.get(profile.ai_maturity, 0.0)
        score += ai_adj
        explanation.components.append(
            ScoreComponent(
                name="AI Maturity",
                value=ai_adj,
                formula=f"ai_maturity({profile.ai_maturity})",
                reasoning=f"Technological advantage: AI maturity is {profile.ai_maturity}.",
            )
        )

        # SaaS maturity
        saas_adj = (profile.saas_maturity - 1) / 9 * 2.0
        score += saas_adj
        explanation.components.append(
            ScoreComponent(
                name="SaaS Maturity",
                value=saas_adj,
                formula=f"({profile.saas_maturity}-1)/9 * 2.0",
                reasoning=f"SaaS transformation index: {profile.saas_maturity}/10.",
            )
        )

        # Geographic presence
        if len(profile.geographic_presence) > cfg.geo_global_count:
            adj = cfg.geo_global_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Geographic Footprint",
                    value=adj,
                    formula=f"regions({len(profile.geographic_presence)}) > {cfg.geo_global_count}",  # noqa: E501
                    reasoning="Global presence identified.",
                )
            )
        elif len(profile.geographic_presence) > cfg.geo_regional_count:
            adj = cfg.geo_regional_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Geographic Footprint",
                    value=adj,
                    formula=f"regions({len(profile.geographic_presence)}) > {cfg.geo_regional_count}",  # noqa: E501
                    reasoning="Regional presence identified.",
                )
            )

        # Tech stack
        if len(profile.tech_stack) > cfg.tech_diverse_count:
            adj = cfg.tech_diverse_bonus
            score += adj
            explanation.components.append(
                ScoreComponent(
                    name="Stack Diversity",
                    value=adj,
                    formula=f"tech_count({len(profile.tech_stack)}) > {cfg.tech_diverse_count}",  # noqa: E501
                    reasoning="Diverse technical capabilities identified.",
                )
            )

        final_score = max(0.0, min(score, 10.0))
        explanation.final_score = final_score
        return final_score, explanation


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
            regulatory_environment=[
                "Industry Standard Compliance",
                "Data Privacy Regulations",
            ],  # noqa: E501
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

    def _generate_recommendations(
        self, profiles: list[Company], avg_growth: float, cr4: float
    ) -> list[str]:  # noqa: E501
        """Generate strategic recommendations based on market metrics."""
        recommendations = []
        if avg_growth > 15:
            recommendations.append("Aggressive expansion into high-growth verticals")
        if cr4 > 70:
            recommendations.append(
                "Focus on niche differentiation to compete with market leaders"
            )  # noqa: E501
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

    def _calculate_swot(self, profiles: list[Company]) -> dict[str, list[str]]:
        """Generate basic SWOT analysis based on company data."""
        return {
            "Strengths": ["Strong Growth"]
            if any(
                p.financials.growth_rate and p.financials.growth_rate > 20
                for p in profiles
            )
            else ["Established Players"],  # noqa: E501
            "Weaknesses": ["Fragmented Market"]
            if len(profiles) > 10
            else ["Niche Market"],  # noqa: E501
            "Opportunities": ["AI Adoption", "Regional Expansion"],
            "Threats": ["High Barriers to Entry", "Regulatory Changes"],
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

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _calculate_technology_overlap(self, p1: Company, p2: Company) -> float:
        """Calculate technology stack overlap (0-1)."""
        if not p1.tech_stack or not p2.tech_stack:
            return 0.0

        set1 = set(p1.tech_stack)
        set2 = set(p2.tech_stack)

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
