from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.analytics.activities import (
    _get_repo,
    calculate_company_score,
)
from solstein.analytics.simulation.market import SimulationEngine
from solstein.data.repositories import JsonFileRepository
from solstein.domain.models import Company, FinancialMetric
from solstein.domain.simulation import MarketCondition, MarketConditionType, Scenario


# --- Activities Tests ---
@pytest.mark.skip(reason="Async repository mocking requires complex setup")
@patch("solstein.analytics.activities.get_settings")
def test_get_repo_exception_fallback(mock_get_settings):
    mock_settings = MagicMock()
    # Provide a "valid" URL so it doesn't fallback immediately
    mock_settings.supabase.url = "https://valid-but-fails.supabase.co"
    mock_get_settings.return_value = mock_settings

    with patch(
        "solstein.analytics.activities.SupabaseRepository",
        side_effect=Exception("DB Error"),
    ):
        repo = _get_repo()
        assert isinstance(repo, JsonFileRepository)


@pytest.mark.asyncio
@patch("solstein.analytics.activities._get_repo")
async def test_calculate_company_score_not_found(mock_get_repo):
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None
    mock_get_repo.return_value = mock_repo

    with pytest.raises(ValueError, match="not found in database"):
        await calculate_company_score("missing_id")


# --- Simulation Tests ---
def test_simulation_engine_no_industry():
    engine = SimulationEngine()
    company = Company(
        id="c1",
        name="C1",
        description="desc",
        industry="",  # Missing industry / empty
        financials=FinancialMetric(valuation=100.0),
    )

    scenario = Scenario(
        id="s1",
        name="Test",
        description="desc",
        conditions=[
            MarketCondition(
                name="TestCondition",
                type=MarketConditionType.INTEREST_RATE,
                impact_factor=1.1,
                affected_industries=["Tech"],
            )
        ],
    )

    results = engine.run(scenario, [company])
    # Because industry is None, condition should be skipped
    assert results[0].simulated_valuation == 100.0  # Unchanged


# --- Workflows Tests ---
# We mock workflow from temporalio used inside workflows.py
from solstein.analytics.workflows import BatchScoreMarketWorkflow


@pytest.mark.asyncio
@patch("solstein.analytics.workflows.workflow")
async def test_batch_score_market_workflow(mock_workflow):
    # Setup the mock for workflow.execute_activity
    async def mock_execute_activity(activity_func, *args, **kwargs):
        # We check which activity is being called
        if activity_func.__name__ == "fetch_market_company_ids":
            return ["c1", "c2"]
        elif activity_func.__name__ == "calculate_company_score":
            cid = args[0]
            return {"company_id": cid, "classification": "Neutral", "growth_score": 5.0}
        return None

    mock_workflow.execute_activity = AsyncMock(side_effect=mock_execute_activity)

    # We also need to mock workflow.logger
    mock_workflow.logger = MagicMock()
    mock_workflow.RetryPolicy = MagicMock

    wf = BatchScoreMarketWorkflow()
    result = await wf.run({"tier": "Tier 1"})

    assert result["total_processed"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["company_id"] == "c1"
    assert result["results"][1]["company_id"] == "c2"
    assert result["status"] == "success"
