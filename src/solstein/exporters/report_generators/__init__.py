"""Report generation strategies.

EPIC-022: Modularized LLM report generation.

Each report type has its own generator class for clean separation of concerns.
"""

from .base import ReportGenerator, SWOTAnalysis, StrategicRecommendations
from .competitive_narrative import CompetitiveNarrativeGenerator
from .executive_summary import ExecutiveSummaryGenerator
from .market_insights import MarketInsightsGenerator
from .recommendations import RecommendationsGenerator
from .swot import SWOTGenerator

__all__ = [
    "ReportGenerator",
    "SWOTAnalysis",
    "StrategicRecommendations",
    "ExecutiveSummaryGenerator",
    "SWOTGenerator",
    "RecommendationsGenerator",
    "CompetitiveNarrativeGenerator",
    "MarketInsightsGenerator",
]
