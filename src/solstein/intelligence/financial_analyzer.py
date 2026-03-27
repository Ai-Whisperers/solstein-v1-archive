"""Financial growth intelligence analyzer for Epic 2.

Main orchestrator that combines trajectory, funding, vectors, and projections.
"""

from __future__ import annotations

from typing import Any

from .financial_models import FinancialIntelligence
from .funding_intelligence import FundingIntelligenceAnalyzer
from .growth_trajectory import GrowthTrajectoryAnalyzer
from .growth_vectors import GrowthVectorDetector
from .projection_engine import FinancialProjectionEngine


class FinancialGrowthAnalyzer:
    """Generate comprehensive financial growth intelligence.

    This is the main entry point for Epic 2 - Financial Growth Intelligence Module.
    """

    def __init__(self):
        self.trajectory_analyzer = GrowthTrajectoryAnalyzer()
        self.funding_analyzer = FundingIntelligenceAnalyzer()
        self.vector_detector = GrowthVectorDetector()
        self.projection_engine = FinancialProjectionEngine()

    def analyze(
        self,
        company_data: dict[str, Any],
    ) -> FinancialIntelligence:
        """Generate complete financial intelligence for a company.

        Args:
            company_data: Dictionary with company information including:
                - name: Company name
                - revenue: Current revenue (millions EUR)
                - growth_rate: Current YoY growth rate (%)
                - employees: Employee count
                - funding_raised: Total funding raised (millions EUR)
                - funding_rounds: List of funding round dicts
                - description: Company description
                - ai_score: AI maturity score (0-10)
                - saas_maturity: SaaS maturity score (0-10)
                - recent_news: List of recent news headlines
                - revenue_timeline: List of {year, revenue} dicts

        Returns:
            FinancialIntelligence with complete analysis
        """
        fi = FinancialIntelligence()

        # Extract basic data
        revenue = company_data.get("revenue")
        growth_rate = company_data.get("growth_rate")
        employees = company_data.get("employees")
        funding_raised = company_data.get("funding_raised")
        funding_rounds = company_data.get("funding_rounds", [])

        # Build revenue timeline
        revenue_timeline = self._build_revenue_timeline(
            company_data.get("revenue_timeline", []),
            revenue,
            growth_rate,
        )
        fi.revenue_timeline = revenue_timeline

        # Analyze growth trajectory
        trajectory = self.trajectory_analyzer.analyze(revenue_timeline, growth_rate)
        fi.growth_trajectory = trajectory.direction
        fi.cagr_3yr = trajectory.cagr_3yr
        fi.cagr_5yr = trajectory.cagr_5yr
        fi.growth_consistency_score = trajectory.consistency_score
        fi.trajectory_narrative = trajectory.narrative

        # Analyze funding intelligence
        funding = self.funding_analyzer.analyze(
            funding_rounds=funding_rounds,
            total_funding=funding_raised,
            current_revenue=revenue,
            employee_count=employees,
        )
        fi.funding_rounds_enhanced = funding.rounds
        fi.total_funding_raised = funding.total_raised
        fi.investor_quality_score = funding.investor_quality_score
        fi.funding_velocity = funding.funding_velocity
        fi.runway_estimate_months = funding.runway_estimate_months
        fi.last_funding_date = funding.last_funding_date
        fi.funding_narrative = funding.narrative

        # Detect growth vectors
        vectors = self.vector_detector.detect(
            company_description=company_data.get("description", ""),
            recent_news=company_data.get("recent_news", []),
            funding_rounds=funding_rounds,
            employees=employees,
            growth_rate=growth_rate,
            ai_score=company_data.get("ai_score"),
            saas_maturity=company_data.get("saas_maturity"),
        )
        fi.primary_growth_vectors = vectors.vectors
        fi.growth_vector_confidence = vectors.confidence_scores

        # Generate projection
        if revenue and revenue > 0:
            projection = self.projection_engine.project(
                current_revenue=revenue,
                financial_intelligence=fi,
            )
            fi.projected_revenue_12mo = projection.projected_revenue_12mo
            fi.projection_confidence = projection.confidence
            fi.projection_rationale = projection.rationale

        # Generate health assessment
        fi = self._generate_health_assessment(fi)

        return fi

    def _build_revenue_timeline(
        self,
        timeline_data: list[dict],
        current_revenue: float | None,
        growth_rate: float | None,
    ) -> list:
        """Build revenue timeline from available data."""
        from .financial_models import ConfidenceLevel, RevenuePoint

        timeline = []

        # Add historical points
        for point in timeline_data:
            if isinstance(point, dict) and "year" in point and "revenue" in point:
                timeline.append(
                    RevenuePoint(
                        year=point["year"],
                        revenue=point["revenue"],
                        source=point.get("source", "reported"),
                        confidence=ConfidenceLevel(point.get("confidence", "medium")),
                    )
                )

        # Add current point if not in timeline
        if current_revenue and timeline:
            latest_year = max(t.year for t in timeline)
            if latest_year < 2024:
                timeline.append(
                    RevenuePoint(
                        year=2024,
                        revenue=current_revenue,
                        source="current",
                        confidence=ConfidenceLevel.MEDIUM,
                    )
                )
        elif current_revenue and not timeline:
            # Estimate past revenue
            if growth_rate and growth_rate > 0:
                past_revenue = current_revenue / ((1 + growth_rate / 100) ** 3)
                timeline = [
                    RevenuePoint(
                        year=2021,
                        revenue=past_revenue,
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
            else:
                timeline = [
                    RevenuePoint(
                        year=2024,
                        revenue=current_revenue,
                        source="reported",
                        confidence=ConfidenceLevel.MEDIUM,
                    ),
                ]

        return timeline

    def _generate_health_assessment(self, fi: FinancialIntelligence) -> FinancialIntelligence:
        """Generate financial health assessment and identify strengths/risks."""
        strengths = []
        risks = []

        # Assess trajectory
        if fi.growth_trajectory.value == "accelerating":
            strengths.append("Accelerating revenue growth trajectory")
        elif fi.growth_trajectory.value == "declining":
            risks.append("Declining revenue trend")

        # Assess CAGR
        if fi.cagr_3yr and fi.cagr_3yr >= 30:
            strengths.append("Exceptional 3-year CAGR (>30%)")
        elif fi.cagr_3yr and fi.cagr_3yr >= 15:
            strengths.append("Strong historical growth (CAGR 15-30%)")
        elif fi.cagr_3yr and fi.cagr_3yr < 0:
            risks.append("Negative historical growth rate")

        # Assess consistency
        if fi.growth_consistency_score >= 7:
            strengths.append("Highly consistent growth patterns")
        elif fi.growth_consistency_score <= 3:
            risks.append("Volatile growth - unpredictability risk")

        # Assess funding
        if fi.total_funding_raised and fi.total_funding_raised >= 50:
            strengths.append("Well-capitalized with significant funding")

        if fi.investor_quality_score >= 7:
            strengths.append("Strong investor backing (Tier 1/2 VCs)")

        if fi.runway_estimate_months:
            if fi.runway_estimate_months >= 24:
                strengths.append(f"Strong runway ({fi.runway_estimate_months}+ months)")
            elif fi.runway_estimate_months <= 12:
                risks.append(f"Limited runway (~{fi.runway_estimate_months} months) - funding risk")

        # Assess growth vectors
        high_impact_vectors = [v for v in fi.primary_growth_vectors if v.estimated_impact == "high"]
        if len(high_impact_vectors) >= 2:
            strengths.append("Multiple high-impact growth vectors identified")

        # Generate narrative
        if strengths and not risks:
            fi.health_assessment = (
                "Strong financial health with clear growth drivers and "
                "adequate capitalization. Well-positioned for continued expansion."
            )
            fi.financial_health_score = 8.0
        elif strengths and risks:
            fi.health_assessment = (
                "Mixed financial picture with both strengths and concerns. "
                "Growth potential balanced by execution risks."
            )
            fi.financial_health_score = 6.0
        elif risks and not strengths:
            fi.health_assessment = (
                "Challenging financial position with significant risks. "
                "Requires strategic intervention or capital infusion."
            )
            fi.financial_health_score = 4.0
        else:
            fi.health_assessment = "Insufficient data for comprehensive financial health assessment."
            fi.financial_health_score = 5.0

        fi.key_strengths = strengths[:5]  # Top 5
        fi.key_risks = risks[:5]  # Top 5

        return fi

    def analyze_from_company_object(self, company: Any) -> FinancialIntelligence:
        """Analyze from a Company domain object.

        Args:
            company: Company domain model instance

        Returns:
            FinancialIntelligence
        """
        # Extract data from company object
        company_data = {
            "name": getattr(company, "name", "Unknown"),
            "revenue": None,
            "growth_rate": None,
            "employees": None,
            "funding_raised": None,
            "funding_rounds": [],
            "description": getattr(company, "description", ""),
            "ai_score": getattr(company, "ai_score", None),
            "saas_maturity": getattr(company, "saas_maturity", None),
        }

        # Extract from financials
        if hasattr(company, "financials") and company.financials:
            fin = company.financials
            company_data["revenue"] = getattr(fin, "revenue", None)
            company_data["growth_rate"] = getattr(fin, "growth_rate", None)
            company_data["employees"] = getattr(fin, "employees", None)
            company_data["funding_raised"] = getattr(fin, "funding_raised", None)

        # Extract funding rounds
        if hasattr(company, "funding_rounds"):
            company_data["funding_rounds"] = company.funding_rounds or []

        return self.analyze(company_data)
