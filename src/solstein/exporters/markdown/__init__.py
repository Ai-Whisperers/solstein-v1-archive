"""Markdown Report Generation Module

EPIC-021: Modularized report generation with specialized generators.
"""

from .base import BaseReportGenerator, ReportFormatter, ScoreInterpreter
from .client import ClientReportGenerator
from .company import CompanyReportGenerator
from .generator import ReportGenerator, generate_enhanced_report

# Helper functions
from .helpers import (
    calculate_3yr_growth,
    classify_trajectory,
    format_funding_detail,
    format_funding_rounds,
    generate_strategic_assessment,
    generate_strengths,
    generate_weaknesses,
    interpret_employee_growth,
    interpret_funding,
    interpret_geographic,
    interpret_ma,
    interpret_saas,
    score_employee_growth,
    score_funding,
    score_geographic,
    score_ma,
)
from .llm_enhanced import LLMEnhancedReportGenerator
from .market import MarketReportGenerator

__all__ = [
    # Main generators
    "ReportGenerator",
    "ClientReportGenerator",
    "LLMEnhancedReportGenerator",
    "CompanyReportGenerator",
    "MarketReportGenerator",
    "BaseReportGenerator",
    # Utilities
    "ReportFormatter",
    "ScoreInterpreter",
    "generate_enhanced_report",
    # Helper functions
    "classify_trajectory",
    "calculate_3yr_growth",
    "generate_strengths",
    "generate_weaknesses",
    "generate_strategic_assessment",
    "format_funding_rounds",
    "format_funding_detail",
    "score_funding",
    "score_employee_growth",
    "score_geographic",
    "score_ma",
    "interpret_funding",
    "interpret_employee_growth",
    "interpret_geographic",
    "interpret_ma",
    "interpret_saas",
]
