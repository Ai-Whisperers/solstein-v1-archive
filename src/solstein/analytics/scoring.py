"""
Scoring algorithms for SolStein competitive intelligence.

Calculates growth scores, financial health scores, and competitive positioning.
"""

from typing import Dict, Any, Optional
from loguru import logger

from ..data.models import CompanyProfile, FinancialMetric


class GrowthScorer:
    """Calculate growth scores for companies."""
    
    def calculate_scores(self, profile: CompanyProfile) -> CompanyProfile:
        """Calculate all scores for a company profile."""
        logger.debug(f"Calculating scores for {profile.name}")
        
        # Calculate individual scores
        growth_score = self._calculate_growth_score(profile.financials)
        financial_health_score = self._calculate_financial_health_score(profile.financials)
        competitive_position_score = self._calculate_competitive_position_score(profile)
        
        # Update profile with scores
        profile.growth_score = growth_score
        profile.financial_health_score = financial_health_score
        profile.competitive_position_score = competitive_position_score
        
        return profile
    
    def _calculate_growth_score(self, financials: FinancialMetric) -> float:
        """Calculate growth score (0-10)."""
        score = 5.0  # Base score
        
        # Revenue growth (40% weight)
        if financials.growth_rate is not None:
            growth_factor = min(financials.growth_rate / 20, 4.0)  # Max 4 points
            score += growth_factor
        
        # Employee growth (20% weight)
        # Note: We don't have historical employee data, so we'll use revenue/employee ratio
        if financials.employees and financials.revenue:
            revenue_per_employee = financials.revenue / financials.employees
            if revenue_per_employee > 500_000:
                score += 2.0  # High productivity
            elif revenue_per_employee > 200_000:
                score += 1.0  # Good productivity
        
        # Funding momentum (20% weight)
        if financials.funding_raised:
            if financials.funding_raised > 50_000_000:
                score += 2.0  # Well-funded
            elif financials.funding_raised > 10_000_000:
                score += 1.0  # Adequately funded
        
        # Profitability growth (20% weight)
        if financials.profit_margin is not None:
            if financials.profit_margin > 20:
                score += 2.0  # Highly profitable
            elif financials.profit_margin > 10:
                score += 1.0  # Profitable
            elif financials.profit_margin < 0:
                score -= 1.0  # Losing money
        
        return max(0.0, min(score, 10.0))
    
    def _calculate_financial_health_score(self, financials: FinancialMetric) -> float:
        """Calculate financial health score (0-10)."""
        score = 5.0  # Base score
        
        # Revenue scale (25% weight)
        if financials.revenue:
            if financials.revenue > 100_000_000:
                score += 2.5  # Large company
            elif financials.revenue > 10_000_000:
                score += 1.25  # Medium company
            elif financials.revenue < 1_000_000:
                score -= 1.0  # Very small
        
        # Profitability (25% weight)
        if financials.profit_margin is not None:
            if financials.profit_margin > 15:
                score += 2.5  # Very profitable
            elif financials.profit_margin > 5:
                score += 1.25  # Profitable
            elif financials.profit_margin < 0:
                score -= 2.5  # Unprofitable
        
        # Employee efficiency (25% weight)
        if financials.employees and financials.revenue:
            revenue_per_employee = financials.revenue / financials.employees
            if revenue_per_employee > 1_000_000:
                score += 2.5  # Exceptional efficiency
            elif revenue_per_employee > 500_000:
                score += 1.25  # Good efficiency
            elif revenue_per_employee < 100_000:
                score -= 1.0  # Low efficiency
        
        # Funding cushion (25% weight)
        if financials.funding_raised and financials.revenue:
            funding_to_revenue = financials.funding_raised / financials.revenue
            if funding_to_revenue > 10:
                score += 2.5  # Well-cushioned
            elif funding_to_revenue > 2:
                score += 1.25  # Adequate cushion
            elif funding_to_revenue < 0.5 and financials.profit_margin is not None and financials.profit_margin < 5:
                score -= 1.0  # Thin cushion
        
        return max(0.0, min(score, 10.0))
    
    def _calculate_competitive_position_score(self, profile: CompanyProfile) -> float:
        """Calculate competitive position score (0-10)."""
        score = 5.0  # Base score
        
        # Tier positioning (30% weight)
        tier_scores = {
            "Tier 1": 3.0,
            "Tier 2": 1.5,
            "Tier 3": 0.0,
            "Tier 4": -1.0,
        }
        score += tier_scores.get(profile.tier, 0.0)
        
        # AI maturity (25% weight)
        ai_scores = {
            "Very Strong": 2.5,
            "Strong": 1.5,
            "Moderate": 0.5,
            "Low": -0.5,
            "None": -1.0,
        }
        score += ai_scores.get(profile.ai_maturity, 0.0)
        
        # SaaS maturity (20% weight)
        saas_score = (profile.saas_maturity - 1) / 9 * 2.0  # Scale 1-10 to 0-2
        score += saas_score
        
        # Geographic presence (15% weight)
        if len(profile.geographic_presence) > 10:
            score += 1.5  # Global presence
        elif len(profile.geographic_presence) > 3:
            score += 0.75  # Regional presence
        elif len(profile.geographic_presence) == 1:
            score -= 0.5  # Single market
        
        # Tech stack (10% weight)
        if len(profile.tech_stack) > 5:
            score += 0.5  # Diverse tech stack
        elif not profile.tech_stack:
            score -= 0.5  # No tech stack info
        
        return max(0.0, min(score, 10.0))


class MarketAnalyzer:
    """Analyze market-level metrics and trends."""
    
    def analyze_market(self, profiles: list[CompanyProfile]) -> Dict[str, Any]:
        """Analyze a market based on company profiles."""
        logger.info(f"Analyzing market with {len(profiles)} companies")
        
        analysis = {
            "company_count": len(profiles),
            "tier_distribution": self._calculate_tier_distribution(profiles),
            "growth_metrics": self._calculate_growth_metrics(profiles),
            "financial_metrics": self._calculate_financial_metrics(profiles),
            "technology_metrics": self._calculate_technology_metrics(profiles),
            "competitive_intensity": self._calculate_competitive_intensity(profiles),
        }
        
        return analysis
    
    def _calculate_tier_distribution(self, profiles: list[CompanyProfile]) -> Dict[str, int]:
        """Calculate distribution of companies across tiers."""
        distribution = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0, "Tier 4": 0}
        
        for profile in profiles:
            distribution[profile.tier] = distribution.get(profile.tier, 0) + 1
        
        return distribution
    
    def _calculate_growth_metrics(self, profiles: list[CompanyProfile]) -> Dict[str, float]:
        """Calculate market growth metrics."""
        growth_rates = [
            p.financials.growth_rate for p in profiles 
            if p.financials.growth_rate is not None
        ]
        
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
    
    def _calculate_financial_metrics(self, profiles: list[CompanyProfile]) -> Dict[str, Any]:
        """Calculate market financial metrics."""
        revenues = [p.financials.revenue for p in profiles if p.financials.revenue]
        profits = [p.financials.profit_margin for p in profiles if p.financials.profit_margin is not None]
        
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
    
    def _calculate_technology_metrics(self, profiles: list[CompanyProfile]) -> Dict[str, Any]:
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
            "average_saas_maturity": sum(saas_scores) / len(saas_scores) if saas_scores else 0,
            "unique_technologies": len(all_tech),
            "most_common_technologies": self._most_common_tech(profiles),
        }
    
    def _most_common_tech(self, profiles: list[CompanyProfile], top_n: int = 5) -> list[tuple[str, int]]:
        """Find most common technologies in the market."""
        tech_counts = {}
        
        for profile in profiles:
            for tech in profile.tech_stack:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        return sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def _calculate_competitive_intensity(self, profiles: list[CompanyProfile]) -> Dict[str, Any]:
        """Calculate competitive intensity metrics."""
        threat_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        
        for profile in profiles:
            threat_counts[profile.threat_level] = threat_counts.get(profile.threat_level, 0) + 1
        
        # Calculate Herfindahl-Hirschman Index (HHI) approximation
        revenues = [p.financials.revenue for p in profiles if p.financials.revenue]
        if revenues:
            total_revenue = sum(revenues)
            market_shares = [r / total_revenue * 100 for r in revenues]
            hhi = sum(share ** 2 for share in market_shares)
        else:
            hhi = 0
        
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


class CompetitiveOverlapCalculator:
    """Calculate competitive overlap between companies."""
    
    def calculate_overlap(self, profile1: CompanyProfile, profile2: CompanyProfile) -> float:
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
    
    def _calculate_geographic_overlap(self, p1: CompanyProfile, p2: CompanyProfile) -> float:
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
    
    def _calculate_technology_overlap(self, p1: CompanyProfile, p2: CompanyProfile) -> float:
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
    
    def _calculate_customer_overlap(self, p1: CompanyProfile, p2: CompanyProfile) -> float:
        """Calculate customer overlap (0-1)."""
        # Simple implementation - could be enhanced with actual customer data
        if not p1.key_customers or not p2.key_customers:
            return 0.0
        
        # Count overlapping industries/sectors in customer lists
        # This is a simplified approach
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
    
    def _calculate_tier_proximity(self, p1: CompanyProfile, p2: CompanyProfile) -> float:
        """Calculate tier proximity score (0-1)."""
        tier_order = {"Tier 1": 4, "Tier 2": 3, "Tier 3": 2, "Tier 4": 1}
        
        tier1 = tier_order.get(p1.tier, 2)
        tier2 = tier_order.get(p2.tier, 2)
        
        distance = abs(tier1 - tier2)
        return 1.0 - (distance / 3.0)  # Normalize to 0-1