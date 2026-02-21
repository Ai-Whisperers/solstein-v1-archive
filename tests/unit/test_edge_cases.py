"""
Edge case tests to cover remaining uncovered branches after the Pydantic refactor.
These tests target specific code paths that require special setup to exercise.
"""
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from solstein.data.loaders import CompetitorDataLoader
from solstein.extractors.markdown_extractor import MarkdownExtractor
from solstein.exporters.excel_exporter import ExcelExporter
from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import FinancialMetric


# ---- Logging Intercept ----

def test_logger_intercept_frame_walk():
    """Trigger the InterceptHandler while-loop frame walk in setup_logging."""
    std_logger = logging.getLogger("test_frame_walk")
    std_logger.warning("Triggering intercept frame walk")


# ---- CLI entrypoint ----

def test_cli_main_import():
    """Ensure cli.main() can be imported and is callable."""
    from solstein.cli import main
    assert callable(main)


# ---- Data Loader Fallbacks ----

def test_determine_tier_very_low_revenue():
    """Revenue < 10 → TIER_4."""
    loader = CompetitorDataLoader()
    tier = loader._determine_tier(5.0)
    assert tier.value == "Tier 4"


def test_convert_confidence_fallback():
    """An unrecognised confidence string → UNKNOWN."""
    loader = CompetitorDataLoader()
    conf = loader._convert_confidence("some garbage")
    assert conf.value == "Unknown"


# ---- Markdown Extractor Fallbacks ----

def test_parse_threat_high_variant():
    """'EXTREMELY HIGH RISK' string → ThreatLevel.HIGH."""
    extractor = MarkdownExtractor()
    assert extractor._parse_threat_level("EXTREMELY HIGH RISK").value == "High"


def test_parse_threat_critical_variant():
    """'CRITICAL SYSTEM' string → ThreatLevel.CRITICAL."""
    extractor = MarkdownExtractor()
    assert extractor._parse_threat_level("CRITICAL SYSTEM").value == "Critical"


def test_parse_threat_low_variant():
    """'VERY LOW DANGER' string → ThreatLevel.LOW."""
    extractor = MarkdownExtractor()
    assert extractor._parse_threat_level("VERY LOW DANGER").value == "Low"


def test_get_confidence_bad_value():
    """Non-existent ConfidenceLevel string → UNKNOWN."""
    extractor = MarkdownExtractor()
    data = {"confidence": {"revenue": "Bogus"}}
    assert extractor._get_confidence(data, "revenue").value == "Unknown"


# ---- Excel Exporter Branches ----

def test_excel_exporter_none_active_sheet():
    """If wb.active is None, create_sheet should be called."""
    exporter = ExcelExporter()

    with patch("solstein.exporters.excel_exporter.Workbook") as mock_wb_class:
        mock_wb = MagicMock()
        mock_wb.active = None
        mock_wb_class.return_value = mock_wb

        exporter.create_dashboard([], Path("/tmp/test_output.xlsx"))
        mock_wb.create_sheet.assert_called_with("Competitive Dashboard")


def test_excel_auto_adjust_value_error():
    """ValueError inside cell value access should be caught and logged."""
    exporter = ExcelExporter()

    class BadCell:
        coordinate = "A1"
        column = 1

        @property
        def value(self):
            class Exploder(str):
                def __len__(self):
                    raise ValueError("boom")
            return Exploder("x")

    mock_ws = MagicMock()
    mock_ws.columns = [[BadCell()]]
    # Should not raise — the ValueError is caught internally
    exporter._auto_adjust_columns(mock_ws)


# ---- Scoring Cushion Penalty ----

def test_financial_score_cushion_thin_penalty():
    """funding/revenue < thin ratio and profit_margin < 5 → cushion thin penalty."""
    scorer = GrowthScorer()
    # ratio = 1.0 / 100.0 = 0.01 → below thin threshold. margin = 4 < 5.
    fin = FinancialMetric(revenue=100.0, funding_raised=1.0, profit_margin=4.0)
    score, expl = scorer._calculate_financial_health_score(fin)
    # Penalty component for funding cushion should exist
    cushion_comps = [c for c in expl.components if "funding_ratio" in c.formula]
    assert len(cushion_comps) > 0
