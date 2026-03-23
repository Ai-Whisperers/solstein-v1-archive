"""
Scoring algorithms for SolStein competitive intelligence.

Calculates growth scores, financial health scores, and competitive positioning.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from loguru import logger

_TIER_PROXIMITY_NORMALIZER: float = 3.0
from ..core.scoring_config import ScoringSettings
from ..domain.models import (
    Company,
    CompanyClassification,
    MarketAnalysis,
    ScoringExplanation,
    ThreatLevel,
)
from .constants import (
    LEAD_SCORE_THRESHOLD,
    MAX_SCORE,
    MIN_SCORE,
    PHOENIX_SCORE_THRESHOLD,
    derive_threat_level,
)
from .scorers.competitive_position import CompetitivePositionScorer
from .scorers.financial_health import FinancialHealthScorer
from .scorers.growth_momentum import GrowthMomentumScorer

# ---------------------------------------------------------------------------
# Signal → scoring component mapping for confidence weighting
# ---------------------------------------------------------------------------

_COMPONENT_SIGNAL_MAP: dict[str, list[str]] = {
    "Revenue Growth": ["growth_rate"],
    "Employee Efficiency": ["revenue", "employees", "revenue_level", "company_size"],
    "Funding Momentum": ["funding", "funding_raised"],
    "Profitability Profile": ["profitability", "profit_margin"],
    "Revenue Scale": ["revenue", "revenue_level"],
    "Profitability Health": ["profitability", "profit_margin"],
    "Operating Efficiency": ["revenue", "employees", "revenue_level", "company_size"],
    "Funding Cushion": ["funding", "funding_raised", "revenue", "revenue_level"],
    "Market Tier": ["company_size", "employees", "valuation"],
    "AI Maturity": ["ai_maturity", "ai_score"],
    "SaaS Maturity": [],
    "Geographic Footprint": [],
    "Stack Diversity": [],
}


@dataclass(frozen=True)
class CompositeScoreResult:
    composite_score: float
    classification: CompanyClassification
    breakdown: dict[str, float | str]


def _confidence_weight(
    component_name: str,
    signal_confidences: dict[str, float],
) -> float:
    """Look up the average signal confidence for a scoring component.

    Returns 1.0 when the component has no mapped signals or none of the
    mapped signals have confidence data (preserves original score).
    """
    signal_names = _COMPONENT_SIGNAL_MAP.get(component_name, [])
    if not signal_names:
        return 1.0
    confidences = [signal_confidences[s] for s in signal_names if s in signal_confidences]
    if not confidences:
        return 1.0
    return sum(confidences) / len(confidences)


def _apply_confidence_weights(
    explanation: ScoringExplanation,
    signal_confidences: dict[str, float],
) -> tuple[float, ScoringExplanation]:
    """Re-weight score components by signal confidence.

    Each component's value is multiplied by the average confidence of
    the signals that inform it.  The base score is left untouched.
    """
    score = explanation.base_score
    for component in explanation.components:
        weight = _confidence_weight(component.name, signal_confidences)
        component.confidence_weight = weight
        component.value = round(component.value * weight, 4)
        score += component.value
    final = max(MIN_SCORE, min(score, MAX_SCORE))
    explanation.final_score = final
    return final, explanation


def classify_company(score: float | None) -> CompanyClassification:
    """Central logic to classify a company based on its composite or growth score."""
    if score is None:
        return CompanyClassification.SALT
    if score >= PHOENIX_SCORE_THRESHOLD:
        return CompanyClassification.PHOENIX
    if score <= LEAD_SCORE_THRESHOLD:
        return CompanyClassification.LEAD
    return CompanyClassification.SALT


def calculate_composite_score(
    growth_score: float,
    financial_health_score: float,
    competitive_position_score: float,
    config: ScoringSettings | None = None,
) -> CompositeScoreResult:
    settings = config or ScoringSettings()
    composite = settings.composite
    if not composite.validate_weights():
        composite.normalize_weights()

    composite_score = round(
        (growth_score * composite.growth_weight)
        + (financial_health_score * composite.financial_weight)
        + (competitive_position_score * composite.competitive_weight),
        2,
    )
    classification = classify_company(composite_score)
    breakdown: dict[str, float | str] = {
        "growth_score": growth_score,
        "financial_health_score": financial_health_score,
        "competitive_position_score": competitive_position_score,
        "composite_score": composite_score,
        "classification": classification.value,
    }
    return CompositeScoreResult(
        composite_score=composite_score,
        classification=classification,
        breakdown=breakdown,
    )


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

        growth_base = self.config.growth.base_score or 0.0
        financial_base = self.config.financial.base_score or 0.0
        competitive_base = self.config.competitive.base_score or 0.0

        try:
            growth_score, growth_expl = self.growth_momentum_scorer.score(profile.financials)
        except Exception as exc:
            logger.warning(f"[EPIC-059] Growth scoring degraded for {profile.name}: {exc}")
            growth_score = growth_base
            growth_expl = ScoringExplanation(base_score=growth_base, final_score=growth_base)
            profile.scoring_breakdown["growth_degraded"] = str(exc)

        try:
            financial_health_score, fin_expl = self.financial_health_scorer.score(profile.financials)
        except Exception as exc:
            logger.warning(f"[EPIC-059] Financial scoring degraded for {profile.name}: {exc}")
            financial_health_score = financial_base
            fin_expl = ScoringExplanation(base_score=financial_base, final_score=financial_base)
            profile.scoring_breakdown["financial_degraded"] = str(exc)

        try:
            competitive_position_score, comp_expl = self.competitive_position_scorer.score(profile)
        except Exception as exc:
            logger.warning(f"[EPIC-059] Competitive scoring degraded for {profile.name}: {exc}")
            competitive_position_score = competitive_base
            comp_expl = ScoringExplanation(base_score=competitive_base, final_score=competitive_base)
            profile.scoring_breakdown["competitive_degraded"] = str(exc)

        # Apply confidence weighting when signal confidences are available
        if profile.signal_confidences:
            growth_score, growth_expl = _apply_confidence_weights(growth_expl, profile.signal_confidences)
            financial_health_score, fin_expl = _apply_confidence_weights(fin_expl, profile.signal_confidences)
            competitive_position_score, comp_expl = _apply_confidence_weights(comp_expl, profile.signal_confidences)

        profile.growth_score = growth_score
        profile.financial_health_score = financial_health_score
        profile.competitive_position_score = competitive_position_score

        composite = self.config.composite
        if not composite.validate_weights():
            composite.normalize_weights()

        profile.composite_score = round(
            (growth_score * composite.growth_weight)
            + (financial_health_score * composite.financial_weight)
            + (competitive_position_score * composite.competitive_weight),
            2,
        )

        # Always calculate classification
        profile.classification = classify_company(profile.composite_score)

        # Derive threat level from classification and score
        profile.threat_level = ThreatLevel(derive_threat_level(profile.classification, profile.composite_score))

        profile.scoring_breakdown = {
            "growth": growth_expl,
            "financial": fin_expl,
            "competitive": comp_expl,
        }

        return profile


# NOTE: The following private methods were removed as dead code:
# - _calculate_growth_score (lines ~153-241)
# - _calculate_financial_health_score (lines ~243-339)
# - _calculate_competitive_position_score (lines ~341-434)
#
# These methods were never called. The live scoring path uses:
# - GrowthMomentumScorer (scorers/growth_momentum.py)
# - FinancialHealthScorer (scorers/financial_health.py)
# - CompetitivePositionScorer (scorers/competitive_position.py)


class MarketAnalyzer:
    """Analyze market-level metrics and trends."""

    def analyze_market(self, profiles: list[Company]) -> MarketAnalysis:
        """Analyze a market based on company profiles."""
        logger.info(f"Analyzing market with {len(profiles)} companies")

        # Calculate base metrics needed for return
        revenues = [p.financials.revenue for p in profiles if p.financials and p.financials.revenue]
        market_size = sum(revenues) if revenues else 0.0

        growth_rates = [p.financials.growth_rate for p in profiles if p.financials and p.financials.growth_rate is not None]
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

    def _generate_recommendations(self, profiles: list[Company], avg_growth: float, cr4: float) -> list[str]:  # noqa: E501
        """Generate strategic recommendations based on market metrics."""
        recommendations: list[str] = []
        if avg_growth > 15:
            recommendations.append("Aggressive expansion into high-growth verticals")
        if cr4 > 70:
            recommendations.append("Focus on niche differentiation to compete with market leaders")  # noqa: E501
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
        growth_rates = [p.financials.growth_rate for p in profiles if p.financials and p.financials.growth_rate is not None]

        if not growth_rates:
            return {"average": 0.0, "median": 0.0, "high_growth_count": 0}

        sorted_rates = sorted(growth_rates)
        n = len(sorted_rates)

        return {
            "average": sum(growth_rates) / n,
            "median": sorted_rates[n // 2] if n % 2 == 1 else (sorted_rates[n // 2 - 1] + sorted_rates[n // 2]) / 2,
            "high_growth_count": len([r for r in growth_rates if r > 20]),
            "declining_count": len([r for r in growth_rates if r < 0]),
        }

    def _calculate_financial_metrics(self, profiles: list[Company]) -> dict[str, Any]:
        """Calculate market financial metrics."""
        revenues = [p.financials.revenue for p in profiles if p.financials and p.financials.revenue]
        profits = [p.financials.profit_margin for p in profiles if p.financials and p.financials.profit_margin is not None]

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
        all_tech: set[str] = set()
        for profile in profiles:
            all_tech.update(profile.tech_stack)

        return {
            "ai_adoption": ai_counts,
            "average_saas_maturity": sum(saas_scores) / len(saas_scores) if saas_scores else 0,
            "unique_technologies": len(all_tech),
            "most_common_technologies": self._most_common_tech(profiles),
        }

    def _most_common_tech(self, profiles: list[Company], top_n: int = 5) -> list[tuple[str, int]]:
        """Find most common technologies in the market."""
        tech_counts: dict[str, int] = {}

        for profile in profiles:
            for tech in profile.tech_stack:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        return sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def _calculate_competitive_intensity(self, profiles: list[Company]) -> dict[str, Any]:
        """Calculate competitive intensity metrics."""
        threat_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

        for profile in profiles:
            threat_counts[profile.threat_level] = threat_counts.get(profile.threat_level, 0) + 1

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
            "direct_competitors": len([p for p in profiles if p.threat_level in ["High", "Critical"]]),
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
            if any(p.financials.growth_rate and p.financials.growth_rate > 20 for p in profiles)
            else ["Established Players"],  # noqa: E501
            "Weaknesses": ["Fragmented Market"] if len(profiles) > 10 else ["Niche Market"],  # noqa: E501
            "Opportunities": ["AI Adoption", "Regional Expansion"],
            "Threats": ["High Barriers to Entry", "Regulatory Changes"],
        }


class CompetitiveOverlapCalculator:
    """Calculate competitive overlap between companies."""

    def calculate_overlap(self, profile1: Company, profile2: Company) -> float:
        """Calculate overlap score between two companies (0-1)."""
        scores: list[float] = []

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
        return 1.0 - (distance / _TIER_PROXIMITY_NORMALIZER)
