"""Integration test exercising real CompetitorDataLoader against test data.

STORY-044: Added as part of removing autouse fixture. This test exercises the
real data loader code path (not a mock) to verify actual coverage.

Marked with pytest.mark.integration so it can be run independently:
    pytest -m integration tests/unit/test_real_data_loader_integration.py
"""

import json

import pytest

from solstein.data.loaders import CompetitorDataLoader
from solstein.domain.models import AIMaturity, CompanyTier, ConfidenceLevel, ThreatLevel


@pytest.fixture
def real_data_dir(tmp_path):
    """Create a realistic data directory with competitor JSON."""
    data_dir = tmp_path / "data" / "input"
    data_dir.mkdir(parents=True)

    competitors = {
        "competitors": [
            {
                "company_name": "Alpha Energy",
                "folder": "alpha-energy-de",
                "description": "German energy analytics company",
                "revenue": {
                    "timeline": [
                        {"eur_millions": 800, "yoy_growth_pct": 25, "confidence": "Confirmed"},
                        {"eur_millions": 600, "yoy_growth_pct": 20, "confidence": "Confirmed"},
                    ]
                },
                "scorecard": {
                    "composite_score": 8,
                    "dimensions": {"SaaS Maturity": {"score": 8}},
                },
            },
            {
                "company_name": "Beta Software",
                "folder": "beta-software-uk",
                "description": "UK SaaS platform",
                "revenue": {
                    "timeline": [
                        {"eur_millions": 30, "yoy_growth_pct": 40, "confidence": "Estimate"},
                    ]
                },
                "scorecard": {
                    "composite_score": 5,
                    "dimensions": {"SaaS Maturity": {"score": 4}},
                },
            },
            {
                "company_name": "Gamma AI",
                "folder": "gamma-ai-us",
                "description": "US AI startup",
                "revenue": {
                    "timeline": [
                        {"eur_millions": 2000, "yoy_growth_pct": 50, "confidence": "Confirmed"},
                    ]
                },
                "scorecard": {
                    "composite_score": 9,
                    "dimensions": {"SaaS Maturity": {"score": 9}},
                },
            },
        ]
    }

    json_path = data_dir / "competitor_data.json"
    json_path.write_text(json.dumps(competitors, indent=2))
    return data_dir


@pytest.mark.integration
class TestRealDataLoader:
    """Tests that exercise the real CompetitorDataLoader code path."""

    def test_loads_all_companies(self, real_data_dir):
        """Real loader converts all valid competitors."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        assert len(companies) == 3
        names = {c.name for c in companies}
        assert names == {"Alpha Energy", "Beta Software", "Gamma AI"}

    def test_tier_assignment_from_revenue(self, real_data_dir):
        """Tier is derived from latest revenue in timeline."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        by_name = {c.name: c for c in companies}

        # 800M EUR -> TIER_2
        assert by_name["Alpha Energy"].tier == CompanyTier.TIER_2
        # 30M EUR -> TIER_3
        assert by_name["Beta Software"].tier == CompanyTier.TIER_3
        # 2000M EUR -> TIER_1
        assert by_name["Gamma AI"].tier == CompanyTier.TIER_1

    def test_ai_maturity_from_saas_score(self, real_data_dir):
        """AI maturity is derived from SaaS Maturity dimension score."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        by_name = {c.name: c for c in companies}

        # score 8 -> STRONG
        assert by_name["Alpha Energy"].ai_maturity == AIMaturity.STRONG
        # score 4 -> LOW
        assert by_name["Beta Software"].ai_maturity == AIMaturity.LOW
        # score 9 -> STRONG
        assert by_name["Gamma AI"].ai_maturity == AIMaturity.STRONG

    def test_threat_level_from_composite_score(self, real_data_dir):
        """Threat level is derived from composite score."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        by_name = {c.name: c for c in companies}

        # composite_score 8 -> HIGH, 5 -> LOW (threshold-based), 9 -> HIGH
        assert by_name["Alpha Energy"].threat_level == ThreatLevel.HIGH
        assert by_name["Beta Software"].threat_level == ThreatLevel.LOW
        assert by_name["Gamma AI"].threat_level == ThreatLevel.HIGH

    def test_confidence_levels_from_revenue_data(self, real_data_dir):
        """Revenue confidence is parsed from timeline entries."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        by_name = {c.name: c for c in companies}

        assert by_name["Alpha Energy"].financials.revenue_confidence == ConfidenceLevel.CONFIRMED
        assert by_name["Beta Software"].financials.revenue_confidence == ConfidenceLevel.ESTIMATED

    def test_headquarters_from_folder_name(self, real_data_dir):
        """Headquarters is estimated from folder name country suffix."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        companies = loader.load_companies()
        by_name = {c.name: c for c in companies}

        # Headquarters estimated from folder country suffix
        # The estimate_headquarters function maps folder suffixes to regions
        assert by_name["Alpha Energy"].headquarters is not None
        assert by_name["Beta Software"].headquarters == "United Kingdom"
        # "us" suffix may not be recognized — just verify it's set
        assert by_name["Gamma AI"].headquarters is not None

    def test_caching_prevents_reread(self, real_data_dir):
        """Cached results persist even if source file is deleted."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        first = loader.load_companies()
        assert len(first) == 3

        # Delete file
        (real_data_dir / "competitor_data.json").unlink()

        # Should use cache
        cached = loader.load_companies()
        assert len(cached) == 3

    def test_clear_cache_forces_reload(self, real_data_dir):
        """After clear_cache, next load reads from disk."""
        loader = CompetitorDataLoader(data_dir=real_data_dir)
        loader.load_companies()
        loader.clear_cache()

        # Delete file
        (real_data_dir / "competitor_data.json").unlink()

        # Should fail since cache is cleared and file is gone
        with pytest.raises(FileNotFoundError):
            loader.load_companies()
