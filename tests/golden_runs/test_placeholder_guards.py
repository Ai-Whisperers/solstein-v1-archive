"""Tests for placeholder and empty-success detection guards.

STORY-269 / EPIC-070: Verify that graph nodes, router, and pipeline
adapters cannot silently succeed with empty/placeholder outputs.
"""

from __future__ import annotations

from typing import Any

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.research.graph.topology import _human_review_router

from .placeholder_guards import (
    check_analysis_output,
    check_conflict_resolution_output,
    check_export_output,
    check_raw_data_source_not_placeholder,
    check_router_empty_scores_bypass,
    check_scoring_output,
)

# ---------------------------------------------------------------------------
# Conflict Resolution Guards
# ---------------------------------------------------------------------------


class TestConflictResolutionGuards:
    """Verify conflict resolution placeholder detection."""

    def test_empty_resolved_facts_detected(self) -> None:
        """Empty resolved_facts dict must be flagged as placeholder."""
        output = {"resolved_facts": {}, "conflict_flags": []}
        report = check_conflict_resolution_output(output)
        assert not report.passed
        assert any(v.field_name == "resolved_facts" for v in report.violations)

    def test_populated_resolved_facts_passes(self) -> None:
        """Non-empty resolved_facts must pass."""
        output = {
            "resolved_facts": {"revenue": {"value": 1000, "source": "sec"}},
            "conflict_flags": [],
        }
        report = check_conflict_resolution_output(output)
        assert report.passed

    def test_empty_flags_with_real_facts_passes(self) -> None:
        """Empty conflict_flags with real resolved_facts is legitimate."""
        output = {
            "resolved_facts": {"employees": {"value": 500}},
            "conflict_flags": [],
        }
        report = check_conflict_resolution_output(output)
        assert report.passed

    def test_both_empty_is_placeholder_pattern(self) -> None:
        """Both empty flags and empty facts together is the known placeholder."""
        output = {"resolved_facts": {}, "conflict_flags": []}
        report = check_conflict_resolution_output(output)
        violations = [v.field_name for v in report.violations]
        assert "resolved_facts" in violations
        assert "conflict_flags" in violations


# ---------------------------------------------------------------------------
# Scoring Guards
# ---------------------------------------------------------------------------


class TestScoringGuards:
    """Verify scoring placeholder detection."""

    def test_empty_confidence_scores_detected(self) -> None:
        """Empty confidence_scores dict must be flagged."""
        output = {"confidence_scores": {}, "company_scores": {}}
        report = check_scoring_output(output)
        assert not report.passed
        assert any(v.field_name == "confidence_scores" for v in report.violations)

    def test_empty_company_scores_detected(self) -> None:
        """Empty company_scores dict must be flagged."""
        output = {"confidence_scores": {"corp-1": 0.8}, "company_scores": {}}
        report = check_scoring_output(output)
        assert any(v.field_name == "company_scores" for v in report.violations)

    def test_populated_scores_passes(self) -> None:
        """Real scores must pass."""
        output = {
            "confidence_scores": {"corp-1": 0.85},
            "company_scores": {"corp-1": {"tier": "Tier 1"}},
        }
        report = check_scoring_output(output)
        assert report.passed


# ---------------------------------------------------------------------------
# Analysis Guards
# ---------------------------------------------------------------------------


class TestAnalysisGuards:
    """Verify analysis placeholder detection."""

    def test_zero_ai_adoption_detected(self) -> None:
        """ai_adoption_index of 0.0 must be flagged."""
        output = {"market_analysis": {"ai_adoption_index": 0.0, "top_companies": []}}
        report = check_analysis_output(output)
        assert any("ai_adoption_index" in v.field_name for v in report.violations)

    def test_empty_top_companies_detected(self) -> None:
        """Empty top_companies list must be flagged."""
        output = {
            "market_analysis": {
                "ai_adoption_index": 0.75,
                "top_companies": [],
                "market_trends": ["trend-1"],
            }
        }
        report = check_analysis_output(output)
        assert any("top_companies" in v.field_name for v in report.violations)

    def test_real_analysis_passes(self) -> None:
        """Analysis with real data must pass."""
        output = {
            "market_analysis": {
                "ai_adoption_index": 0.72,
                "top_companies": [{"name": "Corp A", "score": 0.9}],
                "market_trends": [{"trend": "AI adoption"}],
            }
        }
        report = check_analysis_output(output)
        assert report.passed


# ---------------------------------------------------------------------------
# Export Guards
# ---------------------------------------------------------------------------


class TestExportGuards:
    """Verify export placeholder detection."""

    def test_empty_export_path_detected(self) -> None:
        """Empty export_path must be flagged."""
        output = {"export_path": "", "export_status": "pending"}
        report = check_export_output(output)
        assert any(v.field_name == "export_path" for v in report.violations)

    def test_pending_status_detected(self) -> None:
        """export_status='pending' must be flagged."""
        output = {"export_path": "", "export_status": "pending"}
        report = check_export_output(output)
        assert any(v.field_name == "export_status" for v in report.violations)

    def test_completed_export_passes(self) -> None:
        """Real export with path and status must pass."""
        output = {
            "export_path": "/data/exports/run_20260331.xlsx",
            "export_status": "completed",
        }
        report = check_export_output(output)
        assert report.passed


# ---------------------------------------------------------------------------
# Router Bypass Guard
# ---------------------------------------------------------------------------


class TestRouterBypassGuard:
    """Verify the router correctly handles empty confidence scores."""

    def test_empty_scores_bypass_detected(self) -> None:
        """Empty scores + no review flag must be flagged as bypass."""
        report = check_router_empty_scores_bypass(
            confidence_scores={},
            human_review_required=False,
        )
        assert not report.passed

    def test_empty_scores_with_review_flag_passes(self) -> None:
        """Empty scores but review flag already set is acceptable."""
        report = check_router_empty_scores_bypass(
            confidence_scores={},
            human_review_required=True,
        )
        assert report.passed

    def test_real_scores_passes(self) -> None:
        """Real scores must pass regardless of review flag."""
        report = check_router_empty_scores_bypass(
            confidence_scores={"corp-1": 0.9},
            human_review_required=False,
        )
        assert report.passed

    def test_topology_router_fixed(self) -> None:
        """The actual _human_review_router must route to review on empty scores.

        This tests the STORY-269 fix to topology.py line 234.
        """
        state: dict[str, Any] = {
            "human_review_required": False,
            "confidence_scores": {},
            "config": {"human_review_confidence_threshold": 0.5},
        }
        result = _human_review_router(state)
        assert result == "human_review_gate", (
            f"Router returned '{result}' instead of 'human_review_gate' — "
            "empty confidence_scores must trigger review"
        )

    def test_topology_router_passes_high_scores(self) -> None:
        """Router must route to analysis when all scores are above threshold."""
        state: dict[str, Any] = {
            "human_review_required": False,
            "confidence_scores": {"corp-1": 0.9, "corp-2": 0.85},
            "config": {"human_review_confidence_threshold": 0.5},
        }
        result = _human_review_router(state)
        assert result == "analysis"

    def test_topology_router_review_on_low_score(self) -> None:
        """Router must route to review when any score is below threshold."""
        state: dict[str, Any] = {
            "human_review_required": False,
            "confidence_scores": {"corp-1": 0.9, "corp-2": 0.3},
            "config": {"human_review_confidence_threshold": 0.5},
        }
        result = _human_review_router(state)
        assert result == "human_review_gate"


# ---------------------------------------------------------------------------
# Enrichment Pipeline Guards
# ---------------------------------------------------------------------------


class TestRawDataSourceGuards:
    """Verify RawDataSource placeholder detection."""

    def test_empty_dict_content_detected(self) -> None:
        """Empty dict raw_content must be flagged."""
        source = RawDataSource(
            source_type=DataSourceType.NEWS,
            source_name="test",
            raw_content={},
            confidence=0.5,
        )
        report = check_raw_data_source_not_placeholder(source, "TestAdapter")
        assert not report.passed
        assert any(v.field_name == "raw_content" for v in report.violations)

    def test_empty_string_content_detected(self) -> None:
        """Empty/whitespace string raw_content must be flagged."""
        source = RawDataSource(
            source_type=DataSourceType.NEWS,
            source_name="test",
            raw_content="   ",
            confidence=0.5,
        )
        report = check_raw_data_source_not_placeholder(source, "TestAdapter")
        assert not report.passed

    def test_zero_confidence_warned(self) -> None:
        """Zero confidence must produce a warning."""
        source = RawDataSource(
            source_type=DataSourceType.PATENTS,
            source_name="test",
            raw_content={"data": "real"},
            confidence=0.0,
        )
        report = check_raw_data_source_not_placeholder(source, "TestAdapter")
        assert any(
            v.field_name == "confidence" and v.severity == "warning"
            for v in report.violations
        )

    def test_missing_extraction_method_warned(self) -> None:
        """Missing extraction_method must produce a warning."""
        source = RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="test",
            raw_content={"ticker": "AAPL"},
            confidence=0.8,
            extraction_method=None,
        )
        report = check_raw_data_source_not_placeholder(source, "TestAdapter")
        assert any(
            v.field_name == "extraction_method" and v.severity == "warning"
            for v in report.violations
        )

    def test_real_source_passes(self) -> None:
        """A properly filled RawDataSource must pass all guards."""
        source = RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="YahooFinance",
            raw_content={"ticker": "AAPL", "market_cap": 3e12},
            url="https://finance.yahoo.com/quote/AAPL/",
            confidence=0.8,
            relevance_score=0.9,
            extraction_method="yfinance_api",
        )
        report = check_raw_data_source_not_placeholder(source, "YahooFinance")
        assert report.passed


# ---------------------------------------------------------------------------
# Integration: Known Placeholder Patterns from STORY-271 Ledger
# ---------------------------------------------------------------------------


class TestKnownPlaceholderPatterns:
    """Verify all placeholder patterns documented in STORY-271 ledger are caught."""

    def test_conflict_resolution_placeholder(self) -> None:
        """The exact placeholder from topology.py _conflict_resolution_node."""
        output = {
            "conflict_flags": [],
            "resolved_facts": {},
            "completed_nodes": ["conflict_resolution"],
        }
        report = check_conflict_resolution_output(output)
        assert not report.passed, "Known placeholder pattern must be detected"

    def test_scoring_placeholder(self) -> None:
        """The exact placeholder from topology.py _scoring_node."""
        output = {
            "confidence_scores": {},
            "company_scores": {},
            "human_review_required": False,
            "completed_nodes": ["scoring"],
        }
        report = check_scoring_output(output)
        assert not report.passed, "Known placeholder pattern must be detected"

    def test_analysis_placeholder(self) -> None:
        """The exact placeholder from topology.py _analysis_node."""
        output = {
            "market_analysis": {
                "top_companies": [],
                "market_trends": [],
                "competitive_landscape": {},
                "ai_adoption_index": 0.0,
                "sector_breakdown": {},
                "data_quality_summary": {},
            },
            "completed_nodes": ["analysis"],
        }
        report = check_analysis_output(output)
        assert not report.passed, "Known placeholder pattern must be detected"

    def test_export_placeholder(self) -> None:
        """The exact placeholder from topology.py _export_node."""
        output = {
            "export_path": "",
            "export_status": "pending",
            "export_errors": [],
            "completed_nodes": ["export"],
        }
        report = check_export_output(output)
        assert not report.passed, "Known placeholder pattern must be detected"
