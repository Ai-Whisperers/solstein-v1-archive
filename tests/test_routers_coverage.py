"""
Additional integration tests for Solstein FastAPI routers (scoring batch, simulation).
"""

from tests.factories import make_company


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
    data = response.json()
    assert data["code"] == "NOT_FOUND"
    assert "No companies found" in data["message"]
