"""Tests for STORY-147: PE Due Diligence Integration Module.

Validates the DD engine, red flag detection, competitive positioning,
checklist generation, and investment memo assembly.
"""

from __future__ import annotations

import pytest

from solstein.application.due_diligence import (
    ChecklistStatus,
    DDReport,
    DueDiligenceEngine,
    InvestmentMemo,
    RedFlagSeverity,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "dd-test-001",
        "name": "TargetCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def engine() -> DueDiligenceEngine:
    return DueDiligenceEngine()


# ---------------------------------------------------------------------------
# TestDDReportStructure
# ---------------------------------------------------------------------------

class TestDDReportStructure:
    """Verify the DD report contains all required components."""

    def test_run_returns_dd_report(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert isinstance(result, DDReport)

    def test_report_has_red_flags(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert isinstance(result.red_flags, list)

    def test_report_has_checklist(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert isinstance(result.checklist, list)
        assert len(result.checklist) > 0

    def test_report_has_investment_memo(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert isinstance(result.investment_memo, InvestmentMemo)

    def test_report_has_data_sources(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert isinstance(result.data_sources_used, list)

    def test_report_has_quality_assessment(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert result.assessment_quality in ("limited", "standard", "comprehensive")


# ---------------------------------------------------------------------------
# TestRedFlagDetection
# ---------------------------------------------------------------------------

class TestRedFlagDetection:
    """Verify red flags are detected correctly."""

    def test_legacy_tech_critical_flag(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(tech_stack=["cobol", "mainframe", "fortran"])
        result = engine.run(target=company)
        critical = [f for f in result.red_flags if f.severity == RedFlagSeverity.CRITICAL]
        assert len(critical) > 0
        assert any("legacy" in f.title.lower() for f in critical)

    def test_low_saas_maturity_flag(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(saas_maturity=1)
        result = engine.run(target=company)
        data_flags = [f for f in result.red_flags if f.category == "data"]
        assert len(data_flags) > 0

    def test_no_ai_maturity_flag(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(ai_maturity="None")
        result = engine.run(target=company)
        ai_flags = [f for f in result.red_flags if f.category == "ai_readiness"]
        assert len(ai_flags) > 0

    def test_negative_growth_flag(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(growth_rate=-5.0)
        result = engine.run(target=company)
        fin_flags = [f for f in result.red_flags if f.category == "financial"]
        assert len(fin_flags) > 0

    def test_all_flags_have_recommendations(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(
            tech_stack=["cobol", "mainframe"],
            saas_maturity=1,
            ai_maturity="None",
            growth_rate=-10.0,
        )
        result = engine.run(target=company)
        for flag in result.red_flags:
            assert flag.recommendation, f"Flag '{flag.title}' missing recommendation"

    def test_healthy_company_fewer_flags(self, engine: DueDiligenceEngine) -> None:
        healthy = _make_company(
            tech_stack=["python", "kubernetes", "aws"],
            saas_maturity=8,
            ai_maturity="Strong",
            ai_score=7.5,
            growth_rate=25.0,
        )
        risky = _make_company(
            tech_stack=["cobol", "mainframe"],
            saas_maturity=1,
            ai_maturity="None",
            growth_rate=-5.0,
        )
        healthy_report = engine.run(target=healthy)
        risky_report = engine.run(target=risky)
        assert len(healthy_report.red_flags) < len(risky_report.red_flags)


# ---------------------------------------------------------------------------
# TestCompetitivePositioning
# ---------------------------------------------------------------------------

class TestCompetitivePositioning:
    """Verify competitive positioning against peers."""

    def test_no_peers_returns_none(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company(ai_score=7.0))
        assert result.competitive_position is None

    def test_with_peers_returns_position(self, engine: DueDiligenceEngine) -> None:
        target = _make_company(id="target-001", name="Target", ai_score=8.0)
        peers = [
            _make_company(id="peer-001", name="Peer A", ai_score=6.0),
            _make_company(id="peer-002", name="Peer B", ai_score=5.0),
        ]
        result = engine.run(target=target, peers=peers)
        assert result.competitive_position is not None
        assert result.competitive_position.target_rank == 1
        assert result.competitive_position.positioning == "leader"

    def test_laggard_positioning(self, engine: DueDiligenceEngine) -> None:
        target = _make_company(id="target-002", name="Target", ai_score=2.0)
        peers = [
            _make_company(id="peer-003", name="Peer A", ai_score=8.0),
            _make_company(id="peer-004", name="Peer B", ai_score=7.0),
            _make_company(id="peer-005", name="Peer C", ai_score=9.0),
            _make_company(id="peer-006", name="Peer D", ai_score=6.0),
        ]
        result = engine.run(target=target, peers=peers)
        pos = result.competitive_position
        assert pos is not None
        assert pos.target_rank == 5
        assert pos.positioning == "laggard"

    def test_peer_scores_in_position(self, engine: DueDiligenceEngine) -> None:
        target = _make_company(id="target-003", name="Target", ai_score=7.0)
        peers = [_make_company(id="peer-007", name="Peer A", ai_score=5.0)]
        result = engine.run(target=target, peers=peers)
        pos = result.competitive_position
        assert pos is not None
        assert len(pos.peer_scores) == 1
        assert pos.peer_scores[0][0] == "Peer A"


# ---------------------------------------------------------------------------
# TestChecklist
# ---------------------------------------------------------------------------

class TestChecklist:
    """Verify DD checklist generation and auto-assessment."""

    def test_checklist_has_standard_items(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        standard = [c for c in result.checklist if c.category == "standard"]
        assert len(standard) >= 10

    def test_checklist_has_ai_items(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        ai_items = [c for c in result.checklist if c.category == "ai_specific"]
        assert len(ai_items) >= 10

    def test_auto_assessment_with_data(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(
            ai_score=7.5,
            ai_maturity="Strong",
            tech_stack=["python", "kubernetes"],
            saas_maturity=8,
        )
        result = engine.run(target=company)
        auto = [c for c in result.checklist if c.auto_assessed]
        assert len(auto) > 0

    def test_auto_assessed_items_have_notes(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(ai_maturity="Strong", ai_score=7.0)
        result = engine.run(target=company)
        auto = [c for c in result.checklist if c.auto_assessed]
        for item in auto:
            assert item.notes, f"Auto-assessed item '{item.item}' missing notes"
            assert item.status == ChecklistStatus.COMPLETE


# ---------------------------------------------------------------------------
# TestInvestmentMemo
# ---------------------------------------------------------------------------

class TestInvestmentMemo:
    """Verify investment memo generation."""

    def test_memo_has_executive_summary(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        assert result.investment_memo is not None
        assert result.investment_memo.executive_summary
        assert "TargetCorp" in result.investment_memo.executive_summary

    def test_memo_has_recommendation(self, engine: DueDiligenceEngine) -> None:
        result = engine.run(target=_make_company())
        memo = result.investment_memo
        assert memo is not None
        assert memo.recommendation

    def test_critical_flags_in_memo(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(tech_stack=["cobol", "mainframe", "legacy"])
        result = engine.run(target=company)
        memo = result.investment_memo
        assert memo is not None
        assert memo.red_flag_count > 0
        assert len(memo.critical_flags) > 0

    def test_proceed_with_caution_on_critical(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(tech_stack=["cobol", "mainframe", "legacy"])
        result = engine.run(target=company)
        memo = result.investment_memo
        assert memo is not None
        assert "CAUTION" in memo.recommendation

    def test_proceed_on_healthy_company(self, engine: DueDiligenceEngine) -> None:
        company = _make_company(
            tech_stack=["python", "kubernetes", "aws"],
            saas_maturity=8,
            ai_maturity="Strong",
            ai_score=7.5,
            growth_rate=25.0,
        )
        result = engine.run(target=company)
        memo = result.investment_memo
        assert memo is not None
        assert "PROCEED" in memo.recommendation

    def test_memo_has_competitive_summary_with_peers(self, engine: DueDiligenceEngine) -> None:
        target = _make_company(id="memo-001", name="Target", ai_score=7.0)
        peers = [_make_company(id="memo-002", name="Peer", ai_score=5.0)]
        result = engine.run(target=target, peers=peers)
        memo = result.investment_memo
        assert memo is not None
        assert "leader" in memo.competitive_summary or "peer" in memo.competitive_summary.lower()
