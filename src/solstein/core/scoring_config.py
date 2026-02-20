"""
Scoring Configuration Schemas.

Defines the tunable parameters for the scoring algorithms.
"""

from pydantic import BaseModel, Field


class GrowthScoringConfig(BaseModel):
    """Configuration for growth score calculation."""

    base_score: float = 5.0

    # Weights & Factors
    revenue_growth_divisor: float = 20.0
    revenue_growth_cap: float = 4.0

    # Revenue per Employee thresholds (in EUR)
    efficiency_high_threshold: float = 500_000.0
    efficiency_high_bonus: float = 2.0
    efficiency_med_threshold: float = 200_000.0
    efficiency_med_bonus: float = 1.0

    # Funding thresholds (in Millions)
    funding_high_threshold: float = 50.0
    funding_high_bonus: float = 2.0
    funding_med_threshold: float = 10.0
    funding_med_bonus: float = 1.0

    # Profitability thresholds
    margin_high_threshold: float = 20.0
    margin_high_bonus: float = 2.0
    margin_med_threshold: float = 10.0
    margin_med_bonus: float = 1.0
    margin_negative_penalty: float = -1.0


class FinancialHealthConfig(BaseModel):
    """Configuration for financial health score calculation."""

    base_score: float = 5.0

    # Revenue Scale (in Millions)
    revenue_large_threshold: float = 100.0
    revenue_large_bonus: float = 2.5
    revenue_med_threshold: float = 10.0
    revenue_med_bonus: float = 1.25
    revenue_small_threshold: float = 1.0
    revenue_small_penalty: float = -1.0

    # Profitability
    margin_high_threshold: float = 15.0
    margin_high_bonus: float = 2.5
    margin_med_threshold: float = 5.0
    margin_med_bonus: float = 1.25
    margin_negative_penalty: float = -2.5

    # Efficiency (Rev/Emp - Absolute EUR)
    efficiency_exceptional_threshold: float = 1_000_000.0
    efficiency_exceptional_bonus: float = 2.5
    efficiency_good_threshold: float = 500_000.0
    efficiency_good_bonus: float = 1.25
    efficiency_low_threshold: float = 100_000.0
    efficiency_low_penalty: float = -1.0

    # Funding Cushion
    cushion_high_ratio: float = 10.0
    cushion_high_bonus: float = 2.5
    cushion_med_ratio: float = 2.0
    cushion_med_bonus: float = 1.25
    cushion_thin_ratio: float = 0.5
    cushion_thin_penalty: float = -1.0


class CompetitivePositionConfig(BaseModel):
    """Configuration for competitive position score."""

    base_score: float = 5.0

    # Tier Scores
    tier_scores: dict[str, float] = Field(
        default_factory=lambda: {
            "Tier 1": 3.0,
            "Tier 2": 1.5,
            "Tier 3": 0.0,
            "Tier 4": -1.0,
        }
    )

    # AI Maturity Scores
    ai_maturity_scores: dict[str, float] = Field(
        default_factory=lambda: {
            "Very Strong": 2.5,
            "Strong": 1.5,
            "Moderate": 0.5,
            "Low": -0.5,
            "None": -1.0,
        }
    )

    # Geographic Presence
    geo_global_count: int = 10
    geo_global_bonus: float = 1.5
    geo_regional_count: int = 3
    geo_regional_bonus: float = 0.75
    geo_single_penalty: float = -0.5

    # Tech Stack
    tech_diverse_count: int = 5
    tech_diverse_bonus: float = 0.5
    tech_none_penalty: float = -0.5


class ScoringSettings(BaseModel):
    """Root configuration for all scoring."""

    growth: GrowthScoringConfig = Field(default_factory=GrowthScoringConfig)
    financial: FinancialHealthConfig = Field(default_factory=FinancialHealthConfig)
    competitive: CompetitivePositionConfig = Field(
        default_factory=CompetitivePositionConfig
    )
