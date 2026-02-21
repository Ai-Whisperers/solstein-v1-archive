import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from solstein.domain.models import CompanyTier, ThreatLevel, AIMaturity, ConfidenceLevel
from solstein.data.loaders import CompetitorDataLoader

def test_loader_missing_file():
    loader = CompetitorDataLoader(data_dir=Path("/non/existent/path"))
    with pytest.raises(FileNotFoundError):
        loader.load_companies()

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
    "competitors": [
        {
            "company_name": "Tech Corp",
            "folder": "tech-corp-uk",
            "description": "A UK startup",
            "revenue": {
                "timeline": [
                    {
                        "eur_millions": 50.5,
                        "yoy_growth_pct": 12.0,
                        "confidence": "Confirm"
                    }
                ]
            },
            "scorecard": {
                "composite_score": 7,
                "dimensions": {
                    "SaaS Maturity": {
                        "score": 6
                    }
                }
            }
        },
        {
            # Edge case: No revenue data, completely empty
        }
    ]
}))
def test_loader_success(mock_file, mock_exists):
    mock_exists.return_value = True
    
    loader = CompetitorDataLoader(data_dir=Path("/mocked/path"))
    companies = loader.load_companies()
    
    assert len(companies) == 2
    
    c1 = companies[0]
    assert c1.name == "Tech Corp"
    assert c1.id == "tech-corp-uk"
    assert c1.financials.revenue == 50.5
    assert c1.financials.growth_rate == 12.0
    assert c1.financials.revenue_confidence == ConfidenceLevel.CONFIRMED
    assert c1.tier == CompanyTier.TIER_3
    assert c1.ai_maturity == AIMaturity.MODERATE
    assert c1.threat_level == ThreatLevel.MEDIUM
    assert c1.headquarters == "United Kingdom"
    
    c2 = companies[1]
    assert c2.name == "Company 1" # Default fallback
    assert c2.financials.revenue is None
    assert c2.tier == CompanyTier.TIER_4
    assert c2.headquarters == "Europe"

@patch('pathlib.Path.exists')
@patch('builtins.open', new_callable=mock_open, read_data="INVALID JSON DATA")
def test_loader_invalid_json(mock_file, mock_exists):
    mock_exists.return_value = True
    
    loader = CompetitorDataLoader(data_dir=Path("/mocked/path"))
    companies = loader.load_companies()
    
    # Should safely swallow error and return empty list
    assert companies == []
