from datetime import datetime
from enum import Enum
from unittest.mock import MagicMock, patch

import pytest

from solstein.core.repositories import CompanyFilter
from solstein.data.repositories import JsonFileRepository, SupabaseRepository
from solstein.domain.models import Company, CompanyTier, FinancialMetric


@pytest.fixture
def sample_companies():
    return [
        Company(
            id="1",
            name="Alpha",
            industry="Tech",
            financials=FinancialMetric(revenue=500.0),
            tier=CompanyTier.TIER_2,
            classification="Phoenix",
        ),
        Company(
            id="2",
            name="Beta",
            industry="Energy",
            financials=FinancialMetric(revenue=10.0),
            tier=CompanyTier.TIER_3,
            classification="Salt",
        ),
        Company(
            id="3",
            name="Gamma",
            industry="Tech Energy",
            financials=FinancialMetric(revenue=None),
            tier=CompanyTier.TIER_4,
            classification="Lead",
        ),
    ]


# --- JsonFileRepository tests ---
@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_get_all(mock_loader_cls, sample_companies):
    mock_loader = MagicMock()
    mock_loader.load_companies.return_value = sample_companies
    mock_loader_cls.return_value = mock_loader

    repo = JsonFileRepository()

    # No filters, just limit/offset
    res = repo.get_all(limit=2, offset=0)
    assert len(res) == 2

    # Filters
    filters = CompanyFilter(
        tier=CompanyTier.TIER_3,
        industry="Energy",
        min_revenue=5.0,
        classification="Salt",
    )
    res = repo.get_all(filters=filters)
    assert len(res) == 1
    assert res[0].id == "2"

    # Filter with no match
    filters2 = CompanyFilter(min_revenue=1000.0)
    assert len(repo.get_all(filters=filters2)) == 0


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_methods(mock_loader_cls, sample_companies):
    mock_loader = MagicMock()
    mock_loader.load_companies.return_value = sample_companies
    mock_loader_cls.return_value = mock_loader
    repo = JsonFileRepository()

    # get_by_id
    assert repo.get_by_id("1").name == "Alpha"
    assert repo.get_by_id("99") is None

    # save
    c = sample_companies[0]
    assert repo.save(c) == c

    # delete
    assert repo.delete("1") is True

    # search
    assert len(repo.search("alpha")) == 1
    assert len(repo.search("unknown")) == 0
    assert repo._to_domain(c) == c


# --- SupabaseRepository tests ---
@patch("solstein.core.supabase_client.get_supabase")
def test_supabase_repo_get_all(mock_get_sb):
    mock_client = MagicMock()
    mock_get_sb.return_value = mock_client

    mock_query = MagicMock()
    mock_client.table().select.return_value = mock_query

    # Setup chain
    for method in ["eq", "ilike", "filter", "gte", "lte", "range"]:
        setattr(mock_query, method, MagicMock(return_value=mock_query))

    mock_query.execute.return_value.data = [
        {"id": "1", "name": "SB_Company", "revenue": 100.0, "financials": {}}
    ]

    repo = SupabaseRepository()

    filters = CompanyFilter(
        tier=CompanyTier.TIER_1,
        industry="Tech",
        classification="Phoenix",
        min_revenue=50.0,
        min_growth_score=1.0,
        max_growth_score=10.0,
    )
    res = repo.get_all(limit=10, offset=0, filters=filters)

    assert len(res) == 1
    assert res[0].name == "SB_Company"
    mock_query.eq.assert_called()
    mock_query.ilike.assert_called()
    mock_query.filter.assert_called()
    mock_query.gte.assert_called()
    mock_query.lte.assert_called()
    mock_query.range.assert_called_with(0, 9)


@patch("solstein.core.supabase_client.get_supabase")
def test_supabase_repo_methods(mock_get_sb):
    mock_client = MagicMock()
    mock_get_sb.return_value = mock_client
    repo = SupabaseRepository()

    # get_by_id
    mock_query = mock_client.table().select().eq()
    mock_query.execute.return_value.data = [{"id": "1", "name": "Test"}]
    assert repo.get_by_id("1").name == "Test"

    mock_query.execute.return_value.data = []
    assert repo.get_by_id("2") is None

    # save
    c = Company(
        id="1", name="Test", last_updated=datetime.now(), tier=CompanyTier.TIER_1
    )
    mock_client.table().upsert().execute = MagicMock()
    repo.save(c)
    mock_client.table().upsert.assert_called()

    # delete
    mock_client.table().delete().eq().execute.return_value.data = [{"id": "1"}]
    assert repo.delete("1") is True

    # search
    mock_client.table().select().ilike().execute.return_value.data = [
        {"id": "1", "name": "Test"}
    ]
    assert len(repo.search("Test")) == 1


@patch("solstein.core.supabase_client.get_supabase")
def test_supabase_repo_conversions(mock_get_sb):
    repo = SupabaseRepository()

    # _to_domain
    record = {
        "id": "1",
        "name": "Test",
        "revenue": 100.0,
        "growth_rate": 5.0,
        "financials": '{"some_old_field": 1}',  # Test string JSON failsafe
    }
    company = repo._to_domain(record)
    assert company.financials.revenue == 100.0

    # _to_record
    class DummyEnum(Enum):
        VAL = "val"

    company.classification = "Phoenix"  # String
    # Also test the internal json_safe using a dict with datetime and enum
    company.scoring_breakdown = {
        "test": datetime(2023, 1, 1),
        "enum": DummyEnum.VAL,
        "list_nested": [{"dt": datetime(2023, 1, 1)}],
    }

    rec = repo._to_record(company)
    assert rec["revenue"] == 100.0
    assert "2023" in rec["scoring_breakdown"]["test"]
    assert rec["scoring_breakdown"]["enum"] == "val"
    assert "2023" in rec["scoring_breakdown"]["list_nested"][0]["dt"]
