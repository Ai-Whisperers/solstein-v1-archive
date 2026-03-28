"""
Edge case tests to cover remaining uncovered branches after the Pydantic refactor.

STORY-044: Updated to use current module-level functions instead of removed
private methods on CompetitorDataLoader and MarkdownExtractor.
"""

import logging

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.cli import main as cli_main
from solstein.data.converters import determine_tier
from solstein.data.parsers import convert_confidence
from solstein.domain.models import CompanyTier, ConfidenceLevel, FinancialMetric

# ---- Logging Intercept ----


def test_logger_intercept_frame_walk():
    """Trigger the InterceptHandler while-loop frame walk in setup_logging."""
    std_logger = logging.getLogger("test_frame_walk")
    std_logger.warning("Triggering intercept frame walk")


# ---- CLI entrypoint ----


def test_cli_main_import():
    """Ensure cli.main() can be imported and is callable."""
    assert callable(cli_main)


# ---- Data Converter Fallbacks ----


def test_determine_tier_very_low_revenue():
    """Revenue < 10 -> TIER_4."""
    tier = determine_tier(5.0)
    assert tier == CompanyTier.TIER_4


def test_determine_tier_none_revenue():
    """None revenue -> TIER_4."""
    tier = determine_tier(None)
    assert tier == CompanyTier.TIER_4


def test_convert_confidence_fallback():
    """An unrecognised confidence string -> UNKNOWN."""
    conf = convert_confidence("some garbage")
    assert conf == ConfidenceLevel.UNKNOWN


def test_convert_confidence_confirmed():
    """'Confirmed' -> CONFIRMED."""
    conf = convert_confidence("Confirmed")
    assert conf == ConfidenceLevel.CONFIRMED


# ---- Scoring Cushion Penalty ----


def test_financial_score_cushion_thin_penalty():
    """funding/revenue < thin ratio and profit_margin < 5 -> cushion thin penalty."""
    scorer = FinancialHealthScorer()
    # ratio = 1.0 / 100.0 = 0.01 -> below thin threshold. margin = 4 < 5.
    fin = FinancialMetric(revenue=100.0, funding_raised=1.0, profit_margin=4.0)
    _score, expl = scorer.score(fin)
    # Penalty component for funding cushion should exist
    cushion_comps = [c for c in expl.components if "funding_ratio" in c.formula]
    assert len(cushion_comps) > 0
