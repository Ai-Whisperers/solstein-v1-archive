import json

import pytest

from solstein.data.loaders import CompetitorDataLoader
from solstein.domain.models import AIMaturity, CompanyTier, ConfidenceLevel, ThreatLevel


@pytest.fixture
def temp_data_dir(tmp_path):
    # Setup dummy data
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


def test_loader_missing_file(temp_data_dir):
    loader = CompetitorDataLoader(temp_data_dir)
    with pytest.raises(FileNotFoundError):
        loader.load_companies()


def test_loader_success_and_cache(temp_data_dir):
    json_path = temp_data_dir / "competitor_data.json"
    comp_data = {
        "competitors": [
            {
                "company_name": "Tech Corp",
                "folder": "company-1",
                "revenue": {
                    "timeline": [
                        {
                            "eur_millions": 1500,  # Tier 1
                            "yoy_growth_pct": 20,
                            "confidence": "Confirmed",
                        }
                    ]
                },
                "scorecard": {
                    "dimensions": {
                        "SaaS Maturity": {"score": 9}  # STRONG
                    },
                    "composite_score": 9,  # HIGH
                },
            },
            {
                "folder": "uk-company",
                "revenue": {
                    "timeline": [
                        {
                            "eur_millions": 50,  # Tier 3
                            "confidence": "Estimate",
                        }
                    ]
                },
                "scorecard": {
                    "dimensions": {
                        "SaaS Maturity": {"score": 6}  # MODERATE
                    },
                    "composite_score": 7,  # MEDIUM
                },
            },
            {
                "folder": "german-company",
                "revenue": {},  # Tier 4, Missing revenue
                "scorecard": {
                    "dimensions": {
                        "SaaS Maturity": {"score": 2}  # LOW
                    },
                    "composite_score": 2,  # LOW
                },
            },
            {
                "folder": "french-company",
                "revenue": {"timeline": [{"eur_millions": 200}]},  # Tier 2
            },
            {"folder": "norwegian-company"},
            {"folder": "spanish-company"},
            {"folder": "polish-company"},
            {"folder": "swiss-company"},
        ]
    }
    json_path.write_text(json.dumps(comp_data))
    loader = CompetitorDataLoader(temp_data_dir)

    # Test load
    comps = loader.load_companies()
    assert len(comps) == 8

    c1 = comps[0]
    assert c1.tier == CompanyTier.TIER_1
    assert c1.ai_maturity == AIMaturity.STRONG
    assert c1.threat_level == ThreatLevel.HIGH
    assert c1.financials.revenue_confidence == ConfidenceLevel.CONFIRMED
    assert c1.financials.growth_confidence == ConfidenceLevel.ESTIMATED

    c2 = comps[1]
    assert c2.tier == CompanyTier.TIER_3
    assert c2.ai_maturity == AIMaturity.MODERATE
    assert c2.threat_level == ThreatLevel.MEDIUM
    assert c2.financials.revenue_confidence == ConfidenceLevel.ESTIMATED
    assert c2.headquarters == "United Kingdom"

    c3 = comps[2]
    assert c3.tier == CompanyTier.TIER_4
    assert c3.headquarters == "Germany"

    c4 = comps[3]
    assert c4.tier == CompanyTier.TIER_2
    assert c4.headquarters == "France"

    assert comps[4].headquarters == "Norway"
    assert comps[5].headquarters == "Spain"
    assert comps[6].headquarters == "Poland"
    assert comps[7].headquarters == "Switzerland"

    # Test limit
    loader.clear_cache()
    assert len(loader._cache) == 0
    lim_comps = loader.load_companies(limit=2)
    assert len(lim_comps) == 2

    # Test caching
    json_path.unlink()  # Delete file
    lim_comps_2 = loader.load_companies(limit=2)  # Should read from cache, no crash
    assert len(lim_comps_2) == 2


def test_loader_bad_json(temp_data_dir):
    json_path = temp_data_dir / "competitor_data.json"
    json_path.write_text("invalid json")

    loader = CompetitorDataLoader(temp_data_dir)
    comps = loader.load_companies()
    assert len(comps) == 0


def test_loader_bad_competitor(temp_data_dir, caplog):
    json_path = temp_data_dir / "competitor_data.json"
    json_path.write_text(json.dumps({"competitors": ["not a dict"]}))

    loader = CompetitorDataLoader(temp_data_dir)
    comps = loader.load_companies()
    assert len(comps) == 0
    assert "Error converting competitor" in caplog.text
