"""Shared fixtures for market analysis pipeline tests."""

import sys
from pathlib import Path

import pytest

# Ensure the parent package is importable without installation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_competitor():
    """A fully-populated competitor dict matching the JSON schema."""
    return {
        "company_name": "Acme Energy",
        "folder": "acme-energy",
        "data_availability": "High",
        "tier": "Tier 1",
        "scorecard": {
            "dimensions": {
                "Revenue Growth": {"score": 7.5, "evidence": "Strong 25% CAGR"},
                "Funding Momentum": {"score": 8.0, "evidence": "Series C closed"},
                "Employee Growth": {"score": 6.0, "evidence": "15% headcount growth"},
                "Geographic Expansion": {"score": 5.0, "evidence": "Expanded to 3 countries"},
                "M&A Activity": {"score": 4.0, "evidence": "One acquisition"},
                "SaaS Maturity": {"score": 7.0, "evidence": "80% cloud revenue"},
            },
            "composite_score": 6.3,
            "classification": "Riser",
        },
        "revenue": {
            "timeline": [
                {"year": "2024", "eur_millions": 150.0, "yoy_growth_pct": 25.0, "confidence": "High"},
                {"year": "2023", "eur_millions": 120.0, "yoy_growth_pct": 20.0, "confidence": "High"},
                {"year": "2022", "eur_millions": 100.0, "yoy_growth_pct": 18.0, "confidence": "Medium"},
            ],
            "cagr_3yr_pct": 22.5,
            "cagr_5yr_pct": 18.0,
            "latest_revenue_eur_m": 150.0,
        },
        "profitability": {
            "recurring_revenue_pct": 75.0,
            "raw_metrics": {"EBITDA Margin (2024)": "12%", "Revenue per Employee (2024)": "EUR 118K"},
            "ebitda_margin_pct": 12.0,
            "revenue_per_employee_eur_k": 118.0,
        },
        "funding": {
            "rounds": [
                {"date": "2023-06", "round": "Series C", "amount": "EUR 50M", "valuation": "EUR 300M", "lead_investors": "Tiger Global"},
            ],
            "total_raised_text": "EUR 80M",
            "latest_valuation_text": "EUR 300M",
            "lead_investors": ["Tiger Global", "Sequoia"],
            "war_chest_signals": "Aggressive hiring in AI team",
        },
        "employees": {
            "timeline": [
                {"year": "2024", "headcount": 350.0},
                {"year": "2023", "headcount": 300.0},
                {"year": "2022", "headcount": 260.0},
            ],
            "employee_cagr_pct": 16.0,
            "latest_headcount": 350.0,
            "open_positions": 45.0,
        },
        "geographic": {
            "international_revenue_pct": 40.0,
            "countries_count": 8,
        },
        "saas": {
            "deployment_model": "SaaS",
            "cloud_revenue_pct": 80.0,
        },
    }


@pytest.fixture
def eneve_competitor():
    """Eneve-specific competitor with known values."""
    return {
        "company_name": "Eneve (formerly Energy21)",
        "folder": "eneve-energy21",
        "data_availability": "High",
        "tier": "Self",
        "scorecard": {
            "dimensions": {
                "Revenue Growth": {"score": 3.0, "evidence": "Moderate growth"},
                "Funding Momentum": {"score": 2.0, "evidence": "Bootstrapped"},
                "Employee Growth": {"score": 3.5, "evidence": "Stable"},
                "Geographic Expansion": {"score": 2.0, "evidence": "Netherlands only"},
                "M&A Activity": {"score": 1.0, "evidence": "None"},
                "SaaS Maturity": {"score": 4.0, "evidence": "Transitioning"},
            },
            "composite_score": 2.6,
            "classification": "Dinosaur",
        },
        "revenue": {
            "timeline": [
                {"year": "2024", "eur_millions": 25.0, "yoy_growth_pct": 8.0, "confidence": "High"},
                {"year": "2023", "eur_millions": 23.0, "yoy_growth_pct": 5.0, "confidence": "High"},
            ],
            "cagr_3yr_pct": 6.5,
            "cagr_5yr_pct": 5.0,
            "latest_revenue_eur_m": 25.0,
        },
        "profitability": {
            "recurring_revenue_pct": 60.0,
            "raw_metrics": {},
            "ebitda_margin_pct": 8.0,
            "revenue_per_employee_eur_k": 95.0,
        },
        "funding": {
            "rounds": [],
            "total_raised_text": None,
            "latest_valuation_text": None,
            "lead_investors": [],
            "war_chest_signals": None,
        },
        "employees": {
            "timeline": [{"year": "2024", "headcount": 120.0}],
            "employee_cagr_pct": 4.0,
            "latest_headcount": 120.0,
            "open_positions": 10.0,
        },
        "geographic": {
            "international_revenue_pct": 5.0,
            "countries_count": 1,
        },
        "saas": {
            "deployment_model": "Hybrid",
            "cloud_revenue_pct": 35.0,
        },
    }


@pytest.fixture
def competitors_list(sample_competitor, eneve_competitor):
    """List of competitors for multi-record tests."""
    return [sample_competitor, eneve_competitor]


@pytest.fixture
def empty_competitor():
    """Minimal dict with empty/missing nested keys for edge-case testing."""
    return {
        "company_name": "Ghost Corp",
        "folder": "ghost-corp",
        "data_availability": None,
        "tier": None,
        "scorecard": {},
        "revenue": {},
        "profitability": {},
        "funding": {},
        "employees": {},
        "geographic": {},
        "saas": {},
    }
