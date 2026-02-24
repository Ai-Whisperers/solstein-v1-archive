from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from solstein.core.repositories import CompanyFilter
from solstein.data.repositories import SupabaseRepository
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)


@pytest.fixture
def mock_supabase():
    with patch("solstein.core.supabase_client.get_supabase") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_company():
    return Company(
        id="test-id",
        name="Test Corp",
        industry="Software",
        description="Testing company",
        website="https://test.com",
        headquarters="New York",
        founded_year=2020,
        tier=CompanyTier.TIER_2,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.MODERATE,
        saas_maturity=7,
        tech_stack=["Python", "React"],
        financials=FinancialMetric(
            revenue=150.5,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=25.0,
            growth_confidence=ConfidenceLevel.ESTIMATED,
            profit_margin=12.5,
            valuation=1000.0,
            employees=500,
            funding_raised=50.0,
        ),
        geographic_presence=["NA"],
        key_customers=[],
        last_updated=datetime(2023, 1, 1, tzinfo=UTC),
        data_source="Test",
    )


def test_supabase_to_domain_mapping(mock_supabase):
    repo = SupabaseRepository()

    # Simulate flat Supabase columns for financial data
    db_record = {
        "id": "comp-1",
        "name": "Acme",
        "industry": "Tech",
        "description": "",
        "website": "",
        "headquarters": "",
        "founded_year": 2000,
        "tier": "Tier 1",
        "threat_level": "High",
        "ai_maturity": "Strong",
        "saas_maturity": 8,
        "tech_stack": [],
        "geographic_presence": [],
        "key_customers": [],
        "last_updated": "2023-01-01T00:00:00Z",
        "data_source": "manual",
        "revenue": 500.0,
        "growth_rate": 15.0,
        "profit_margin": 20.0,
        "valuation": 5000.0,
        "employees": 1000,
        "funding_raised": 200.0,
        # financials might be a dict or string if legacy JSONB exists
        "financials": {"revenue_confidence": "Confirmed"},
    }

    company = repo._to_domain(db_record)
    assert company.id == "comp-1"
    assert company.name == "Acme"

    # Verify financial mapping from flat to nested
    assert company.financials.revenue == 500.0
    assert company.financials.growth_rate == 15.0
    assert company.financials.revenue_confidence == ConfidenceLevel.CONFIRMED


def test_supabase_to_record_mapping(mock_supabase, sample_company):
    repo = SupabaseRepository()

    record = repo._to_record(sample_company)

    # Financial fields should be flattened for DB columns
    assert record["revenue"] == 150.5
    assert record["growth_rate"] == 25.0
    assert record["employees"] == 500

    # Check Enums are flattened to strings
    assert record["tier"] == "Tier 2"
    assert record["threat_level"] == "Medium"
    assert record["ai_maturity"] == "Moderate"

    # Check datetime
    assert isinstance(record["last_updated"], str)


def test_get_all_with_filters(mock_supabase):
    repo = SupabaseRepository()

    mock_query = MagicMock()
    mock_supabase.table().select.return_value = mock_query

    mock_query.eq.return_value = mock_query
    mock_query.ilike.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.gte.return_value = mock_query
    mock_query.lte.return_value = mock_query
    mock_query.range.return_value = mock_query

    mock_response = MagicMock()
    mock_response.data = [{"id": "1", "name": "Co1"}]
    mock_query.execute.return_value = mock_response

    filters = CompanyFilter(
        tier="Tier 1",
        industry="SaaS",
        classification="Competitor",
        min_revenue=100.0,
        min_growth_score=5.0,
        max_growth_score=9.0,
    )

    results = repo.get_all(limit=10, offset=5, filters=filters)

    assert len(results) == 1
    mock_query.eq.assert_any_call("tier", "Tier 1")
    mock_query.ilike.assert_called_with("industry", "%SaaS%")
    mock_query.filter.assert_called_with("financials->>revenue", "gte", "100.0")
    mock_query.range.assert_called_with(5, 14)


def test_get_by_id_found(mock_supabase):
    repo = SupabaseRepository()
    mock_response = MagicMock()
    mock_response.data = [{"id": "foo", "name": "Bar"}]
    mock_supabase.table().select().eq().execute.return_value = mock_response

    company = repo.get_by_id("foo")
    assert company is not None
    assert company.id == "foo"


def test_get_by_id_not_found(mock_supabase):
    repo = SupabaseRepository()
    mock_response = MagicMock()
    mock_response.data = []
    mock_supabase.table().select().eq().execute.return_value = mock_response

    company = repo.get_by_id("bar")
    assert company is None


def test_save(mock_supabase, sample_company):
    repo = SupabaseRepository()
    repo.save(sample_company)
    mock_supabase.table().upsert.assert_called_once()


def test_delete(mock_supabase):
    repo = SupabaseRepository()
    mock_response = MagicMock()
    mock_response.data = [{"id": "deleted"}]
    mock_supabase.table().delete().eq().execute.return_value = mock_response

    res = repo.delete("test")
    assert res is True


def test_search(mock_supabase):
    repo = SupabaseRepository()
    mock_response = MagicMock()
    mock_response.data = [{"id": "1", "name": "SearchRes"}]
    mock_supabase.table().select().ilike().execute.return_value = mock_response

    res = repo.search("Search")
    assert len(res) == 1
    assert res[0].name == "SearchRes"
