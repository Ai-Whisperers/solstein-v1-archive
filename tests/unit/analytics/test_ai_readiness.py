"""Unit tests for AI Readiness Scorer (EPIC-038).

Run with: pytest tests/unit/analytics/test_ai_readiness.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

import pytest

from solstein.analytics.ai_readiness import AIReadinessResult, AIReadinessScorer
from solstein.domain.models import AIMaturity, Company


class TestAIReadinessScorer:
    """Test suite for AIReadinessScorer."""

    @pytest.fixture
    def scorer(self) -> AIReadinessScorer:
        return AIReadinessScorer()

    @pytest.fixture
    def mock_company(self) -> MagicMock:
        """Create a mock company with configurable attributes."""
        company = MagicMock(spec=Company)
        company.name = "TestCorp"
        company.ai_score = 8.0
        company.ai_maturity = AIMaturity.STRONG
        company.ai_in_production = True
        company.saas_maturity = 7.0
        company.employees = 500
        company.financials = MagicMock()
        company.financials.growth_rate = 25.0
        company.total_funding_raised_eur = 50_000_000
        company.tier = MagicMock()
        company.tier.value = "Phoenix"
        return company

    def test_score_returns_result(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        result = scorer.score(mock_company)
        assert isinstance(result, AIReadinessResult)
        assert 0 <= result.score <= 10
        assert result.tier in ["Leader", "Adopter", "Laggard"]
        assert "deployment_maturity" in result.breakdown
        assert "data_infrastructure" in result.breakdown
        assert "strategic_alignment" in result.breakdown

    def test_leader_tier(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        # High AI score, in production, well-funded
        mock_company.ai_score = 9.0
        mock_company.total_funding_raised_eur = 200_000_000
        result = scorer.score(mock_company)
        assert result.tier == "Leader"
        assert result.score >= 7.5

    def test_laggard_tier(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        # Low AI maturity, no funding
        mock_company.ai_maturity = AIMaturity.NONE
        mock_company.ai_score = 1.0
        mock_company.ai_in_production = False
        mock_company.total_funding_raised_eur = 0
        mock_company.tier.value = "Lead"
        result = scorer.score(mock_company)
        assert result.tier == "Laggard"
        assert result.score < 4.5

    def test_deployment_maturity_bonus(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        mock_company.ai_in_production = True
        result_prod = scorer.score(mock_company)

        mock_company.ai_in_production = False
        result_no_prod = scorer.score(mock_company)

        assert result_prod.breakdown["deployment_maturity"] > result_no_prod.breakdown["deployment_maturity"]

    def test_insights_not_empty(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        result = scorer.score(mock_company)
        assert len(result.insights) > 0
        assert all(isinstance(i, str) for i in result.insights)

    def test_score_bounds(self, scorer: AIReadinessScorer, mock_company: MagicMock) -> None:
        result = scorer.score(mock_company)
        assert 0.0 <= result.score <= 10.0
