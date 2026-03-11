"""Financial intelligence models for Epic 2.

Growth trajectory tracking, funding intelligence, and growth vector identification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional


class TrajectoryDirection(str, Enum):
    """Growth trajectory direction."""

    ACCELERATING = "accelerating"
    STEADY = "steady"
    DECELERATING = "decelerating"
    DECLINING = "declining"
    UNKNOWN = "unknown"


class FundingVelocity(str, Enum):
    """Funding velocity classification."""

    RAPID = "rapid"  # Multiple rounds per year
    STEADY = "steady"  # Annual rounds
    SPARSE = "sparse"  # Sporadic or none


class GrowthVectorType(str, Enum):
    """Types of growth vectors."""

    AI_ML = "ai_ml"
    SAAS_SCALING = "saas_scaling"
    GEOGRAPHIC_EXPANSION = "geographic_expansion"
    M_A = "mergers_acquisitions"
    PRODUCT_LINE = "product_line_expansion"
    CHANNEL = "channel_expansion"


class ConfidenceLevel(str, Enum):
    """Confidence level for projections and analysis."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class RevenuePoint:
    """A single revenue data point in time."""

    year: int
    revenue: float  # In millions EUR
    source: str = "unknown"
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN


@dataclass
class FundingRound:
    """Detailed funding round information."""

    round_name: str  # Series A, B, Seed, etc.
    amount: Optional[float] = None  # In millions EUR
    date: Optional[date] = None
    lead_investor: Optional[str] = None
    co_investors: list[str] = field(default_factory=list)
    valuation: Optional[float] = None  # Post-money in millions EUR
    valuation_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    source: str = "unknown"


@dataclass
class GrowthVector:
    """Identified growth vector with evidence."""

    vector_type: GrowthVectorType
    name: str
    confidence: float  # 0-1
    evidence: list[str] = field(default_factory=list)
    estimated_impact: str = "unknown"  # "high", "medium", "low"


@dataclass
class FinancialIntelligence:
    """Rich financial analysis container.

    This is the main output of Epic 2 - Financial Growth Intelligence Module.
    """

    # Growth Trajectory
    revenue_timeline: list[RevenuePoint] = field(default_factory=list)
    growth_trajectory: TrajectoryDirection = TrajectoryDirection.UNKNOWN
    growth_consistency_score: float = 0.0  # 0-10 volatility measure
    cagr_3yr: Optional[float] = None  # 3-year compound annual growth rate
    cagr_5yr: Optional[float] = None  # 5-year compound annual growth rate
    trajectory_narrative: str = ""

    # Funding Intelligence
    funding_rounds_enhanced: list[FundingRound] = field(default_factory=list)
    total_funding_raised: Optional[float] = None  # In millions EUR
    investor_quality_score: float = 0.0  # 0-10 based on lead investors
    funding_velocity: FundingVelocity = FundingVelocity.SPARSE
    runway_estimate_months: Optional[int] = None  # Calculated from burn rate
    last_funding_date: Optional[date] = None
    funding_narrative: str = ""

    # Growth Vectors
    primary_growth_vectors: list[GrowthVector] = field(default_factory=list)
    growth_vector_confidence: dict[str, float] = field(default_factory=dict)

    # Trajectory Projection
    projected_revenue_12mo: Optional[float] = None  # LLM-assisted projection
    projection_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    projection_rationale: str = ""

    # Financial Health Summary
    financial_health_score: Optional[float] = None  # 0-10
    health_assessment: str = ""
    key_strengths: list[str] = field(default_factory=list)
    key_risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "revenue_timeline": [
                {
                    "year": rp.year,
                    "revenue": rp.revenue,
                    "source": rp.source,
                    "confidence": rp.confidence.value,
                }
                for rp in self.revenue_timeline
            ],
            "growth_trajectory": self.growth_trajectory.value,
            "growth_consistency_score": self.growth_consistency_score,
            "cagr_3yr": self.cagr_3yr,
            "cagr_5yr": self.cagr_5yr,
            "trajectory_narrative": self.trajectory_narrative,
            "funding_rounds_enhanced": [
                {
                    "round_name": fr.round_name,
                    "amount": fr.amount,
                    "date": fr.date.isoformat() if fr.date else None,
                    "lead_investor": fr.lead_investor,
                    "co_investors": fr.co_investors,
                    "valuation": fr.valuation,
                    "valuation_confidence": fr.valuation_confidence.value,
                    "source": fr.source,
                }
                for fr in self.funding_rounds_enhanced
            ],
            "total_funding_raised": self.total_funding_raised,
            "investor_quality_score": self.investor_quality_score,
            "funding_velocity": self.funding_velocity.value,
            "runway_estimate_months": self.runway_estimate_months,
            "last_funding_date": self.last_funding_date.isoformat() if self.last_funding_date else None,
            "funding_narrative": self.funding_narrative,
            "primary_growth_vectors": [
                {
                    "vector_type": gv.vector_type.value,
                    "name": gv.name,
                    "confidence": gv.confidence,
                    "evidence": gv.evidence,
                    "estimated_impact": gv.estimated_impact,
                }
                for gv in self.primary_growth_vectors
            ],
            "projected_revenue_12mo": self.projected_revenue_12mo,
            "projection_confidence": self.projection_confidence.value,
            "projection_rationale": self.projection_rationale,
            "financial_health_score": self.financial_health_score,
            "health_assessment": self.health_assessment,
            "key_strengths": self.key_strengths,
            "key_risks": self.key_risks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FinancialIntelligence":
        """Create from dictionary."""
        fi = cls()

        # Revenue timeline
        if "revenue_timeline" in data:
            fi.revenue_timeline = [
                RevenuePoint(
                    year=rp["year"],
                    revenue=rp["revenue"],
                    source=rp.get("source", "unknown"),
                    confidence=ConfidenceLevel(rp.get("confidence", "unknown")),
                )
                for rp in data["revenue_timeline"]
            ]

        # Growth trajectory
        fi.growth_trajectory = TrajectoryDirection(data.get("growth_trajectory", "unknown"))
        fi.growth_consistency_score = data.get("growth_consistency_score", 0.0)
        fi.cagr_3yr = data.get("cagr_3yr")
        fi.cagr_5yr = data.get("cagr_5yr")
        fi.trajectory_narrative = data.get("trajectory_narrative", "")

        # Funding
        if "funding_rounds_enhanced" in data:
            fi.funding_rounds_enhanced = [
                FundingRound(
                    round_name=fr["round_name"],
                    amount=fr.get("amount"),
                    date=datetime.fromisoformat(fr["date"]).date() if fr.get("date") else None,
                    lead_investor=fr.get("lead_investor"),
                    co_investors=fr.get("co_investors", []),
                    valuation=fr.get("valuation"),
                    valuation_confidence=ConfidenceLevel(fr.get("valuation_confidence", "unknown")),
                    source=fr.get("source", "unknown"),
                )
                for fr in data["funding_rounds_enhanced"]
            ]

        fi.total_funding_raised = data.get("total_funding_raised")
        fi.investor_quality_score = data.get("investor_quality_score", 0.0)
        fi.funding_velocity = FundingVelocity(data.get("funding_velocity", "sparse"))
        fi.runway_estimate_months = data.get("runway_estimate_months")
        if data.get("last_funding_date"):
            fi.last_funding_date = datetime.fromisoformat(data["last_funding_date"]).date()
        fi.funding_narrative = data.get("funding_narrative", "")

        # Growth vectors
        if "primary_growth_vectors" in data:
            fi.primary_growth_vectors = [
                GrowthVector(
                    vector_type=GrowthVectorType(gv["vector_type"]),
                    name=gv["name"],
                    confidence=gv["confidence"],
                    evidence=gv.get("evidence", []),
                    estimated_impact=gv.get("estimated_impact", "unknown"),
                )
                for gv in data["primary_growth_vectors"]
            ]

        # Projection
        fi.projected_revenue_12mo = data.get("projected_revenue_12mo")
        fi.projection_confidence = ConfidenceLevel(data.get("projection_confidence", "unknown"))
        fi.projection_rationale = data.get("projection_rationale", "")

        # Health
        fi.financial_health_score = data.get("financial_health_score")
        fi.health_assessment = data.get("health_assessment", "")
        fi.key_strengths = data.get("key_strengths", [])
        fi.key_risks = data.get("key_risks", [])

        return fi
