"""
Tests for JsonFileRepository.
"""

from unittest.mock import patch

import pytest

from solstein.core.repositories import CompanyFilter
from solstein.data.repositories import JsonFileRepository
from solstein.domain.models import Company, CompanyTier, FinancialMetric


@pytest.fixture
def mock_loader_companies():
    c1 = Company(
        id="co1",
        name="Alpha",
        tier=CompanyTier.TIER_1,
        industry="Tech",
        classification="Phoenix",
        financials=FinancialMetric(revenue=100.0),
    )
    c2 = Company(
        id="co2",
        name="Beta",
        tier=CompanyTier.TIER_2,
        industry="Finance",
        classification="Salt",
        financials=FinancialMetric(revenue=20.0),
    )
    return [c1, c2]


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_get_all_no_filters(MockLoader, mock_loader_companies, tmp_path):
    mock_instance = MockLoader.return_value
    mock_instance.load_companies.return_value = mock_loader_companies

    repo = JsonFileRepository(data_dir=tmp_path)

    results = repo.get_all()
    assert len(results) == 2


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_get_all_with_filters_and_limit(MockLoader, mock_loader_companies, tmp_path):
    mock_instance = MockLoader.return_value
    mock_instance.load_companies.return_value = mock_loader_companies

    repo = JsonFileRepository(data_dir=tmp_path)

    # Test filters that match c1
    filters = CompanyFilter(
        tier=CompanyTier.TIER_1,
        industry="Tech",
        classification="Phoenix",
        min_revenue=50.0,
    )
    results = repo.get_all(filters=filters)
    assert len(results) == 1
    assert results[0].id == "co1"

    # Test limit and offset
    filters2 = CompanyFilter(min_revenue=10.0)
    results2 = repo.get_all(filters=filters2, limit=1, offset=1)
    assert len(results2) == 1
    assert results2[0].id == "co2"


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_get_by_id(MockLoader, mock_loader_companies, tmp_path):
    mock_instance = MockLoader.return_value
    mock_instance.load_companies.return_value = mock_loader_companies

    repo = JsonFileRepository(data_dir=tmp_path)

    assert repo.get_by_id("co1").name == "Alpha"
    assert repo.get_by_id("co3") is None


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_save_delete(MockLoader, mock_loader_companies, tmp_path):
    repo = JsonFileRepository(data_dir=tmp_path)
    # They just simulate operations and return true/the object
    assert repo.save(mock_loader_companies[0]) == mock_loader_companies[0]
    assert repo.delete("co1") is True


@patch("solstein.data.repositories.CompetitorDataLoader")
def test_json_repo_search(MockLoader, mock_loader_companies, tmp_path):
    mock_instance = MockLoader.return_value
    mock_instance.load_companies.return_value = mock_loader_companies

    repo = JsonFileRepository(data_dir=tmp_path)

    results = repo.search("alph")
    assert len(results) == 1
    assert results[0].name == "Alpha"
