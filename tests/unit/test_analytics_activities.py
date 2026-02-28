"""Tests for analytics activities."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from tests.factories import make_company

from solstein.analytics.activities import (
    _get_repo,
    calculate_company_score,
    fetch_market_company_ids,
)


@pytest.mark.skip(reason="Requires database mocking - complex async setup")
@pytest.mark.asyncio
@patch("solstein.analytics.activities.get_settings")
async def test_get_repo_fallback(mock_get_settings):
    """Test repo fallback based on config."""
    mock_settings = MagicMock()
    mock_settings.supabase.url = None
    mock_get_settings.return_value = mock_settings

    repo = await _get_repo()
    # Repository could be any type (JsonFileRepository, SQLAlchemyRepository, etc.)
    assert repo is not None
    assert hasattr(repo, 'get_by_id')
    assert hasattr(repo, 'save')


@pytest.mark.asyncio
async def test_calculate_company_score():
    """Test calculate_company_score activity."""
    mock_repo = MagicMock()
    mock_company = make_company()
    mock_repo.get_by_id.return_value = mock_company

    # We must mock `repo.save` as synchronous because `asyncio.to_thread` wraps it
    mock_repo.save.return_value = mock_company

    async def mock_get_repo():
        return mock_repo

    with patch("solstein.analytics.activities._get_repo", side_effect=mock_get_repo):
        result = await calculate_company_score(mock_company.id)
        assert result["company_id"] == mock_company.id
        assert "classification" in result
        assert "growth_score" in result

        mock_repo.get_by_id.assert_called_once_with(mock_company.id)
        mock_repo.save.assert_called_once()


@pytest.mark.asyncio
@patch("solstein.analytics.activities._get_repo", new_callable=AsyncMock)
async def test_calculate_company_score_not_found(mock_get_repo):
    """Test calculate_company_score raises ValueError on missing company."""
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    mock_get_repo.return_value = mock_repo

    with pytest.raises(ValueError, match="not found"):
        await calculate_company_score("unknown-id")


@pytest.mark.asyncio
@patch("solstein.analytics.activities._get_repo", new_callable=AsyncMock)
async def test_fetch_market_company_ids(mock_get_repo):
    """Test fetch_market_company_ids activity."""
    mock_repo = MagicMock()
    mock_company1 = make_company()
    mock_company1.id = "c1"
    mock_repo.get_all.return_value = [mock_company1]
    mock_get_repo.return_value = mock_repo

    result = await fetch_market_company_ids({"industry": "Tech"})
    assert "c1" in result
