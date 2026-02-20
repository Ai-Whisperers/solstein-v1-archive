"""
Domain models for market simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class MarketConditionType(StrEnum):
    """Types of market conditions."""

    INTEREST_RATE = "interest_rate"
    INFLATION = "inflation"
    SECTOR_GROWTH = "sector_growth"
    COMPETITOR_ACTIVITY = "competitor_activity"
    REGULATORY_CHANGE = "regulatory_change"


@dataclass
class MarketCondition:
    """A specific market condition modifier."""

    type: MarketConditionType
    name: str
    impact_factor: float  # Multiplier or additive factor depending on logic
    description: str | None = None
    affected_industries: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """A simulation scenario composed of multiple market conditions."""

    id: str
    name: str
    description: str
    conditions: list[MarketCondition]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SimulationResult:
    """Result of a simulation for a single company."""

    company_id: str
    company_name: str
    base_valuation: float | None
    simulated_valuation: float | None
    valuation_change_pct: float

    base_growth_score: float
    simulated_growth_score: float
    growth_score_change: float

    notes: list[str] = field(default_factory=list)
