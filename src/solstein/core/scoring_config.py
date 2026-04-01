"""
Scoring Configuration Schemas.

Defines the tunable parameters for the scoring algorithms.

EPIC-009: Scoring Config Improvements
- Story 9.2: Make weights configurable via environment variables
- Story 9.3: Harmonize thresholds across scorers
- Story 9.4: SaaS formula configuration
"""

import os

from pydantic import BaseModel, Field


class GrowthScoringConfig(BaseModel):
    """Configuration for growth score calculation."""

    base_score: float | None = None

    # Weights & Factors
    revenue_growth_divisor: float = 20.0
    revenue_growth_cap: float = 4.0

    # Revenue per Employee thresholds (in EUR)
    efficiency_high_threshold: float = 500_000.0
    efficiency_high_bonus: float = 2.0
    efficiency_med_threshold: float = 200_000.0
    efficiency_med_bonus: float = 1.0

    # Funding thresholds (in Millions EUR - matches data format)
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

    base_score: float | None = 2.5

    # Revenue Scale (in Millions EUR - matches data format)
    # Data stores revenue as 5.0 for €5M, so thresholds must be in millions
    revenue_large_threshold: float = 100.0  # €100M
    revenue_large_bonus: float = 2.5
    revenue_med_threshold: float = 10.0  # €10M
    revenue_med_bonus: float = 1.25
    revenue_small_threshold: float = 1.0  # €1M
    revenue_small_penalty: float = -1.0

    # Profitability
    margin_high_threshold: float = 15.0
    margin_high_bonus: float = 2.5
    margin_med_threshold: float = 5.0
    margin_med_bonus: float = 1.25
    margin_negative_penalty: float = -2.5

    # Efficiency (Rev/Emp - in EUR per employee)
    # Revenue is in millions, so rev_per_emp = (revenue * 1_000_000) / employees
    efficiency_exceptional_threshold: float = 1_000_000.0  # €1M per employee
    efficiency_exceptional_bonus: float = 2.5
    efficiency_good_threshold: float = 500_000.0  # €500K per employee
    efficiency_good_bonus: float = 1.25
    efficiency_low_threshold: float = 100_000.0  # €100K per employee
    efficiency_low_penalty: float = -1.0

    # Funding Cushion (ratio - funding_raised / revenue)
    # Both in millions, so ratio is unitless
    cushion_high_ratio: float = 10.0
    cushion_high_bonus: float = 2.5
    cushion_med_ratio: float = 3.0
    cushion_med_bonus: float = 1.25
    cushion_thin_ratio: float = 0.5
    cushion_thin_penalty: float = -1.0


class CompetitivePositionConfig(BaseModel):
    """Configuration for competitive position score."""

    base_score: float | None = 5.0

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


class CompositeScoringConfig(BaseModel):
    """Configuration for composite score calculation.

    EPIC-009 Story 9.2: Make weights configurable.
    Weights can be set via environment variables or config file.
    """

    # Default weights (must sum to 1.0)
    growth_weight: float = Field(default_factory=lambda: float(os.getenv("SCORING_GROWTH_WEIGHT", "0.40")))
    financial_weight: float = Field(default_factory=lambda: float(os.getenv("SCORING_FINANCIAL_WEIGHT", "0.30")))
    competitive_weight: float = Field(default_factory=lambda: float(os.getenv("SCORING_COMPETITIVE_WEIGHT", "0.30")))

    # SaaS-specific adjustments (EPIC-009 Story 9.4)
    saas_recurring_revenue_bonus: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_SAAS_RECURRING_BONUS", "0.5"))
    )
    saas_high_margin_threshold: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_SAAS_MARGIN_THRESHOLD", "20.0"))
    )
    saas_high_margin_bonus: float = Field(default_factory=lambda: float(os.getenv("SCORING_SAAS_MARGIN_BONUS", "1.0")))

    def validate_weights(self) -> bool:
        """Validate that weights sum to approximately 1.0."""
        total = self.growth_weight + self.financial_weight + self.competitive_weight
        return 0.99 <= total <= 1.01

    def normalize_weights(self) -> None:
        """Normalize weights to sum to 1.0."""
        total = self.growth_weight + self.financial_weight + self.competitive_weight
        if total > 0:
            self.growth_weight /= total
            self.financial_weight /= total
            self.competitive_weight /= total


class AIReadinessScoringConfig(BaseModel):
    """Configuration for AI readiness scoring (EPIC-038, STORY-145).

    Dimension weights must sum to 1.0.
    classification_influence_weight controls how much AI readiness
    affects the overall composite score (0.0 = no influence).
    """

    data_infrastructure_weight: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_AI_DATA_INFRA_WEIGHT", "0.25"))
    )
    technical_debt_weight: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_AI_TECH_DEBT_WEIGHT", "0.25"))
    )
    ai_literacy_weight: float = Field(default_factory=lambda: float(os.getenv("SCORING_AI_LITERACY_WEIGHT", "0.30")))
    process_automation_weight: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_AI_AUTOMATION_WEIGHT", "0.20"))
    )
    classification_influence_weight: float = Field(
        default_factory=lambda: float(os.getenv("SCORING_AI_INFLUENCE_WEIGHT", "0.0"))
    )


class ScoringSettings(BaseModel):
    """Root configuration for all scoring.

    EPIC-009: All scoring parameters can be configured via:
    1. Environment variables (SCORING_* prefix)
    2. Config file (scoring_config.json)
    3. Direct instantiation
    """

    growth: GrowthScoringConfig = Field(default_factory=GrowthScoringConfig)
    financial: FinancialHealthConfig = Field(default_factory=FinancialHealthConfig)
    competitive: CompetitivePositionConfig = Field(default_factory=CompetitivePositionConfig)
    composite: CompositeScoringConfig = Field(default_factory=CompositeScoringConfig)
    ai_readiness: AIReadinessScoringConfig = Field(default_factory=AIReadinessScoringConfig)

    @classmethod
    def from_env(cls) -> "ScoringSettings":
        """Create settings from environment variables.

        Environment variables:
        - SCORING_GROWTH_WEIGHT: Weight for growth score (default: 0.40)
        - SCORING_FINANCIAL_WEIGHT: Weight for financial score (default: 0.30)
        - SCORING_COMPETITIVE_WEIGHT: Weight for competitive score (default: 0.30)
        - SCORING_*: Various other scoring parameters
        """
        return cls()

    @classmethod
    def from_file(cls, path: str) -> "ScoringSettings":
        """Load settings from JSON config file."""
        import json

        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    def save_to_file(self, path: str) -> None:
        """Save current settings to JSON config file."""
        import json

        with open(path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)
