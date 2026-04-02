"""Tests for CompetitorDataLoader — exercises real code paths.

STORY-044: Rewritten to test real loader behavior instead of relying on
autouse fixture that silently patched load_companies().
"""

import json

import pytest

from solstein.data.loaders import CompetitorDataLoader
from solstein.domain.models import AIMaturity, CompanyTier


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory with proper structure."""
    data_dir = tmp_path / "data" / "input"
    data_dir.mkdir(parents=True)
    return data_dir


def test_loader_missing_file(temp_data_dir):
    """Test that a missing competitor_data.json raises FileNotFoundError."""
    loader = CompetitorDataLoader(data_dir=temp_data_dir)
    with pytest.raises(FileNotFoundError, match="Competitor data not found"):
        loader.load_companies()


def test_loader_invalid_json(temp_data_dir):
    """Test that invalid JSON gracefully returns empty list."""
    json_path = temp_data_dir / "competitor_data.json"
    json_path.write_text("NOT VALID JSON {{{")

    loader = CompetitorDataLoader(data_dir=temp_data_dir)
    companies = loader.load_companies()
    assert len(companies) == 0


def test_loader_success(temp_data_dir):
    """Test that valid competitor JSON produces Company objects."""
    json_path = temp_data_dir / "competitor_data.json"
    comp_data = {
        "competitors": [
            {
                "company_name": "Tech Corp",
                "folder": "tech-corp",
                "description": "A tech startup",
                "revenue": {
                    "timeline": [
                        {
                            "eur_millions": 50.5,
                            "yoy_growth_pct": 12.0,
                            "confidence": "Confirmed",
                        }
                    ]
                },
                "scorecard": {
                    "composite_score": 7,
                    "dimensions": {"SaaS Maturity": {"score": 6}},
                },
            },
            {
                "company_name": "Energy Co",
                "folder": "energy-co",
                "revenue": {
                    "timeline": [
                        {
                            "eur_millions": 1500,
                            "yoy_growth_pct": 20,
                            "confidence": "Confirmed",
                        }
                    ]
                },
                "scorecard": {
                    "composite_score": 9,
                    "dimensions": {"SaaS Maturity": {"score": 9}},
                },
            },
        ]
    }
    json_path.write_text(json.dumps(comp_data))

    loader = CompetitorDataLoader(data_dir=temp_data_dir)
    companies = loader.load_companies()

    assert len(companies) == 2
    assert companies[0].name == "Tech Corp"
    assert companies[0].ai_maturity == AIMaturity.MODERATE
    assert companies[0].tier == CompanyTier.TIER_3
    assert companies[1].name == "Energy Co"
    assert companies[1].ai_maturity == AIMaturity.STRONG
    assert companies[1].tier == CompanyTier.TIER_1


def test_loader_caching(temp_data_dir):
    """Test that repeated calls use cache."""
    json_path = temp_data_dir / "competitor_data.json"
    json_path.write_text(
        json.dumps(
            {
                "competitors": [
                    {
                        "company_name": "Cached Co",
                        "folder": "cached",
                        "scorecard": {"composite_score": 5, "dimensions": {"SaaS Maturity": {"score": 5}}},
                    }
                ]
            }
        )
    )

    loader = CompetitorDataLoader(data_dir=temp_data_dir)
    first_call = loader.load_companies()
    assert len(first_call) == 1

    # Delete the file — cached result should still work
    json_path.unlink()
    second_call = loader.load_companies()
    assert len(second_call) == 1
    assert second_call[0].name == "Cached Co"


def test_loader_limit(temp_data_dir):
    """Test that limit parameter restricts results."""
    json_path = temp_data_dir / "competitor_data.json"
    json_path.write_text(
        json.dumps(
            {
                "competitors": [
                    {
                        "company_name": f"Co {i}",
                        "folder": f"co-{i}",
                        "scorecard": {"composite_score": 5, "dimensions": {"SaaS Maturity": {"score": 5}}},
                    }
                    for i in range(5)
                ]
            }
        )
    )

    loader = CompetitorDataLoader(data_dir=temp_data_dir)
    limited = loader.load_companies(limit=2)
    assert len(limited) == 2
