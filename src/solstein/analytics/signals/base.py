"""Base signal classes.

Contains the core Signal and SignalCategory definitions.
Separated to avoid circular imports with definitions package.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SignalCategory(str, Enum):
    """Categories for business signals."""

    GROWTH = "growth"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    HIRING = "hiring"
    PRODUCT = "product"
    MARKET = "market"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"


class Signal(BaseModel):
    """A business signal definition."""

    name: str = Field(..., description="Signal name")
    category: SignalCategory = Field(..., description="Signal category")
    description: str = Field(..., description="What this signal measures")
    weight: float = Field(default=1.0, description="Importance weight (0.0-2.0)")
    data_sources: list[str] = Field(default_factory=list, description="Sources that provide this signal")
    validation_rules: dict[str, Any] = Field(default_factory=dict, description="Validation constraints")

    class Config:
        frozen = True
