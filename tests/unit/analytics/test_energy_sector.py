"""Unit tests for Energy Sector Analyzer (EPIC-039).

Run with: pytest tests/unit/analytics/test_energy_sector.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

import pytest

from solstein.analytics.energy_sector import (
    EnergySectorAnalyzer,
    EnergySubSector,
)
from solstein.domain.models import Company


class TestEnergySectorAnalyzer:
    """Test suite for energy sector classification."""

    @pytest.fixture
    def analyzer(self) -> EnergySectorAnalyzer:
        return EnergySectorAnalyzer()

    @pytest.fixture
    def renewable_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "SolarTech Inc"
        company.description = "Leading solar panel manufacturer"
        company.industry = "Renewable Energy"
        company.composite_score = 7.5
        company.total_funding_raised_eur = 100_000_000
        return company

    @pytest.fixture
    def oil_gas_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "PetroMax"
        company.description = "Upstream oil and gas exploration"
        company.industry = "Oil & Gas"
        company.composite_score = 6.0
        company.total_funding_raised_eur = 500_000_000
        return company

    def test_renewables_classification(self, analyzer: EnergySectorAnalyzer, renewable_company: MagicMock) -> None:
        result = analyzer.analyze(renewable_company)
        assert result.sub_sector == EnergySubSector.RENEWABLES

    def test_oil_gas_classification(self, analyzer: EnergySectorAnalyzer, oil_gas_company: MagicMock) -> None:
        result = analyzer.analyze(oil_gas_company)
        assert result.sub_sector == EnergySubSector.OIL_AND_GAS

    def test_transition_score_renewables(self, analyzer: EnergySectorAnalyzer, renewable_company: MagicMock) -> None:
        result = analyzer.analyze(renewable_company)
        # Renewables get 1.4x multiplier, should have high transition score
        assert result.transition_score >= 5.0

    def test_transition_score_oil_gas(self, analyzer: EnergySectorAnalyzer, oil_gas_company: MagicMock) -> None:
        result = analyzer.analyze(oil_gas_company)
        # Oil & Gas gets 0.7x multiplier
        assert result.transition_score < 5.0

    def test_composite_adjusted_renewables(self, analyzer: EnergySectorAnalyzer, renewable_company: MagicMock) -> None:
        result = analyzer.analyze(renewable_company)
        # 7.5 * 1.4 = 10.5, clamped to 10.0
        assert result.composite_adjusted == 10.0

    def test_composite_adjusted_oil_gas(self, analyzer: EnergySectorAnalyzer, oil_gas_company: MagicMock) -> None:
        result = analyzer.analyze(oil_gas_company)
        # 6.0 * 0.7 = 4.2
        assert result.composite_adjusted == 4.2

    def test_flags_for_oil_gas(self, analyzer: EnergySectorAnalyzer, oil_gas_company: MagicMock) -> None:
        result = analyzer.analyze(oil_gas_company)
        assert any("ESG" in flag for flag in result.flags)

    def test_flags_for_well_funded_renewables(
        self, analyzer: EnergySectorAnalyzer, renewable_company: MagicMock
    ) -> None:
        result = analyzer.analyze(renewable_company)
        assert any("Well-funded" in flag for flag in result.flags)

    def test_unknown_classification(self, analyzer: EnergySectorAnalyzer) -> None:
        company = MagicMock(spec=Company)
        company.name = "Generic Corp"
        company.description = "Software company"
        company.industry = "Technology"
        company.composite_score = 5.0
        company.total_funding_raised_eur = 0
        result = analyzer.analyze(company)
        assert result.sub_sector == EnergySubSector.UNKNOWN

    def test_cleantech_keywords(self, analyzer: EnergySectorAnalyzer) -> None:
        company = MagicMock(spec=Company)
        company.name = "CleanTech Solutions"
        company.description = "Carbon capture technology"
        company.industry = "Clean Energy"
        company.composite_score = 7.0
        company.total_funding_raised_eur = 50_000_000
        result = analyzer.analyze(company)
        assert result.sub_sector == EnergySubSector.CLEANTECH
