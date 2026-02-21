"""
Additional integration tests for Solstein FastAPI routers (scoring batch, simulation).
"""

from unittest.mock import AsyncMock, patch

from tests.factories import make_company


# ---------------------------------------------------------------------------
# GET /scoring/batch
# ---------------------------------------------------------------------------
@patch("solstein.api.routers.scoring.TemporalClient.connect")
def test_batch_scoring_endpoint_temporal_success(mock_connect, client):
    """Test batch scoring endpoint using Temporal."""
    mock_client = AsyncMock()
    mock_connect.return_value = mock_client
    mock_handle = AsyncMock()
    mock_handle.id = "workflow-123"
    mock_client.start_workflow.return_value = mock_handle

    response = client.get("/scoring/batch?industry=Energy")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Batch scoring workflow started via Temporal"
    assert data["workflow_id"] == "workflow-123"
    assert data["status"] == "running"
    assert data["filters"]["industry"] == "Energy"


@patch(
    "solstein.api.routers.scoring.TemporalClient.connect",
    side_effect=Exception("Connection failed"),
)
@patch("solstein.analytics.activities.fetch_market_company_ids", new_callable=AsyncMock)
@patch("solstein.analytics.activities.calculate_company_score", new_callable=AsyncMock)
def test_batch_scoring_endpoint_fallback(mock_calc, mock_fetch, mock_connect, client):
    """Test batch scoring synchronous fallback when Temporal is unavailable."""
    mock_fetch.return_value = ["c1"]
    mock_calc.return_value = {"company_id": "c1", "status": "scored"}

    response = client.get("/scoring/batch?industry=Finance")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Batch scoring completed synchronously (Local Fallback)"
    assert data["status"] == "completed"
    assert data["processed_count"] == 1
    assert data["filters"]["industry"] == "Finance"


# ---------------------------------------------------------------------------
# POST /simulation/run
# ---------------------------------------------------------------------------
def test_run_simulation_endpoint(client, mock_repo):
    """Test standard market simulation through the API."""
    mock_company = make_company()
    mock_repo.get_all.return_value = [mock_company]

    payload = {
        "id": "scenario-1",
        "name": "Tech Crash",
        "description": "A tech crash",
        "conditions": [
            {
                "type": "interest_rate",
                "name": "Tech Crash",
                "impact_factor": -0.2,
                "description": "Tech stocks drop 20%",
                "affected_industries": ["Energy"],
            }
        ],
    }

    response = client.post("/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company_id"] == mock_company.id


def test_run_simulation_endpoint_no_companies(client, mock_repo):
    """Test simulation when no companies match the filter."""
    mock_repo.get_all.return_value = []

    payload = {
        "id": "scenario-2",
        "name": "Empty Market",
        "description": "No companies",
        "conditions": [],
    }

    response = client.post("/simulation/run", json=payload)
    assert response.status_code == 404
    assert response.json()["error"] == "HTTP Error"
    assert "No companies found" in response.json()["details"]
