"""
Domain models for market simulation.
"""

import sys
from datetime import datetime, timezone

if sys.version_info >= (3, 11):  # noqa: UP036
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


from pydantic import BaseModel, ConfigDict, Field


class MarketConditionType(StrEnum):
    """Types of market conditions."""

    INTEREST_RATE = "interest_rate"
    INFLATION = "inflation"
    SECTOR_GROWTH = "sector_growth"
    COMPETITOR_ACTIVITY = "competitor_activity"
    REGULATORY_CHANGE = "regulatory_change"


class MarketCondition(BaseModel):
    """A specific market condition modifier."""

    model_config = ConfigDict(validate_assignment=True)

    type: MarketConditionType
    name: str
    impact_factor: float  # Multiplier or additive factor depending on logic
    description: str | None = None
    affected_industries: list[str] = Field(default_factory=list)


class Scenario(BaseModel):
    """A simulation scenario composed of multiple market conditions."""

    model_config = ConfigDict(validate_assignment=True)

    id: str
    name: str
    description: str
    conditions: list[MarketCondition]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SimulationResult(BaseModel):
    """Result of a simulation for a single company."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    company_name: str
    base_valuation: float | None = None
    simulated_valuation: float | None = None
    valuation_change_pct: float

    base_growth_score: float
    simulated_growth_score: float
    growth_score_change: float

    notes: list[str] = Field(default_factory=list)
