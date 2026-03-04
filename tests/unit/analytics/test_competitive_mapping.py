"""Unit tests for Competitive Mapping (EPIC-042).

Run with: pytest tests/unit/analytics/test_competitive_mapping.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

import pytest

from solstein.analytics.competitive_mapping import (
    CompetitiveLandscape,
    CompetitiveMapper,
    CompetitiveRelation,
)
from solstein.domain.models import Company


class TestCompetitiveMapper:
    """Test suite for competitive landscape mapping."""

    @pytest.fixture
    def mapper(self) -> CompetitiveMapper:
        return CompetitiveMapper()

    @pytest.fixture
    def reference_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "Stripe"
        company.industry = "Fintech"
        company.composite_score = 6.0
        company.ai_score = 8.0
        company.financials = MagicMock()
        company.financials.revenue = 1000.0
        company.financials.growth_rate = 25.0
        return company

    @pytest.fixture
    def direct_competitor(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "Adyen"
        company.industry = "Fintech"
        company.composite_score = 8.5
        company.ai_score = 6.0
        company.financials = MagicMock()
        company.financials.revenue = 800.0
        company.financials.growth_rate = 15.0
        company.tier = MagicMock()
        company.tier.value = "Phoenix"
        return company

    @pytest.fixture
    def aspirational_peer(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "Visa"
        company.industry = "Fintech"
        company.composite_score = 9.8
        company.ai_score = 9.0
        company.financials = MagicMock()
        company.financials.revenue = 20000.0
        company.financials.growth_rate = 10.0
        company.tier = MagicMock()
        company.tier.value = "Phoenix"
        return company

    @pytest.fixture
    def distant_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "OilCorp"
        company.industry = "Oil & Gas"
        company.composite_score = 5.0
        company.ai_score = 3.0
        company.financials = MagicMock()
        company.financials.revenue = 5000.0
        company.financials.growth_rate = 5.0
        return company

    def test_map_returns_landscape(self, mapper: CompetitiveMapper, reference_company: MagicMock) -> None:
        landscape = mapper.map([reference_company], reference_company)
        assert isinstance(landscape, CompetitiveLandscape)
        assert landscape.reference == reference_company

    def test_direct_competitor_classification(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
        direct_competitor: MagicMock,
    ) -> None:
        landscape = mapper.map([direct_competitor], reference_company)
        assert len(landscape.direct_competitors) == 1
        assert landscape.direct_competitors[0].relation == CompetitiveRelation.DIRECT

    def test_aspirational_peer_classification(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
        aspirational_peer: MagicMock,
    ) -> None:
        landscape = mapper.map([aspirational_peer], reference_company)
        assert len(landscape.aspirational_peers) == 1
        assert landscape.aspirational_peers[0].relation == CompetitiveRelation.ASPIRATIONAL

    def test_distant_company_filtered(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
        distant_company: MagicMock,
    ) -> None:
        landscape = mapper.map([distant_company], reference_company)
        # Distant companies don't appear in any tier
        assert len(landscape.direct_competitors) == 0
        assert len(landscape.adjacent_players) == 0
        assert len(landscape.aspirational_peers) == 0

    def test_overlap_score_calculation(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
        direct_competitor: MagicMock,
    ) -> None:
        landscape = mapper.map([direct_competitor], reference_company)
        entry = landscape.direct_competitors[0]
        assert 0.0 <= entry.overlap_score <= 1.0
        assert entry.overlap_score > 0.5  # High overlap for direct competitor

    def test_positioning_gap_generation(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
        direct_competitor: MagicMock,
    ) -> None:
        landscape = mapper.map([direct_competitor], reference_company)
        assert isinstance(landscape.positioning_gap, str)
        assert "1 direct competitor" in landscape.positioning_gap

    def test_differentiation_factors(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
    ) -> None:
        reference_company.ai_score = 8.0
        landscape = mapper.map([], reference_company)
        assert len(landscape.differentiation_factors) > 0
        assert any("AI" in f for f in landscape.differentiation_factors)

    def test_top_n_limit(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
    ) -> None:
        # Create 15 direct competitors
        competitors = []
        for i in range(15):
            c = MagicMock(spec=Company)
            c.name = f"Competitor{i}"
            c.industry = "Fintech"
            c.composite_score = 8.0
            c.financials = MagicMock()
            c.financials.revenue = 500.0
            competitors.append(c)

        landscape = mapper.map(competitors, reference_company, top_n=5)
        assert len(landscape.direct_competitors) <= 5

    def test_self_exclusion(
        self,
        mapper: CompetitiveMapper,
        reference_company: MagicMock,
    ) -> None:
        # Reference company should not appear in results
        landscape = mapper.map([reference_company], reference_company)
        all_competitors = landscape.direct_competitors + landscape.adjacent_players + landscape.aspirational_peers
        assert len(all_competitors) == 0
