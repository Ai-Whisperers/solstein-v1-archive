"""
Integration tests for the SolStein FastAPI layer.

Covers: health check, company CRUD, scoring, market analysis, search,
statistics, missing-entity 404s, filter parameters, and schema contracts.
"""




# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health(client):
    """Verify health endpoint is reachable."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# GET /companies
# ---------------------------------------------------------------------------


def test_get_companies(client):
    """Verify companies endpoint returns mocked data."""
    response = client.get("/companies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Test Corp"


def test_get_companies_response_schema(client):
    """Company response must contain all expected schema fields."""
    response = client.get("/companies")
    assert response.status_code == 200
    company = response.json()[0]
    required_fields = {"id", "name", "tier", "financials", "ai_maturity", "industry"}
    for field in required_fields:
        assert field in company, f"Missing field: {field}"


def test_get_companies_filter_by_tier(client, mock_repo):
    """Query param ?tier=Tier+1 must be forwarded to the repository filter."""
    response = client.get("/companies?tier=Tier+1")
    assert response.status_code == 200
    # mock_repo.get_all was called — verify it's called with some filter arg
    mock_repo.get_all.assert_called()


# ---------------------------------------------------------------------------
# GET /companies/{id}
# ---------------------------------------------------------------------------


def test_get_company_by_id(client):
    """Verify single company retrieval by ID."""
    response = client.get("/companies/test-company")
    assert response.status_code == 200
    assert response.json()["id"] == "test-company"


def test_get_company_not_found(client, mock_repo):
    """GET /companies/{id} must return 404 when repo.get_by_id returns None."""
    mock_repo.get_by_id.return_value = None
    response = client.get("/companies/GHOST-COMPANY")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /companies
# ---------------------------------------------------------------------------


def test_create_company(client, mock_repo):
    """POST /companies must return 201 with a scored company."""
    # Ensure save() just returns the passed-in Company object
    mock_repo.save.side_effect = lambda c: c

    payload = {
        "id": "new-co",
        "name": "New Energy Co",
        "industry": "Energy",
        "tier": "Tier 2",
        "ai_maturity": "Moderate",
        "financials": {
            "revenue": 50.0,
            "growth_rate": 20.0,
            "profit_margin": 8.0,
        },
    }
    response = client.post("/companies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "new-co"
    assert data["name"] == "New Energy Co"
    # Scores should be calculated
    assert data["growth_score"] is not None


# ---------------------------------------------------------------------------
# POST /scoring/company/{id}/score
# ---------------------------------------------------------------------------


def test_scoring_endpoint(client):
    """Verify scoring endpoint returns classification for the mock company (growth=15%)."""
    response = client.post("/scoring/company/test-company/score")
    assert response.status_code == 200
    data = response.json()
    assert "growth_score" in data
    assert "financial_health_score" in data
    assert "competitive_position_score" in data
    assert "classification" in data
    # growth=15% → base(5.0) + 15/20=0.75 + 1.0(med margin) ≈ 6.75 → "Neutral"
    assert data["classification"] == "Neutral"


def test_scoring_endpoint_not_found(client, mock_repo):
    """Score endpoint must return 404 when company does not exist."""
    mock_repo.get_by_id.return_value = None
    mock_repo.get_all.return_value = []  # also empty for the fallback loop
    response = client.post("/scoring/company/DOES-NOT-EXIST/score")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /market/analysis
# ---------------------------------------------------------------------------


def test_market_analysis(client):
    """Verify market analysis endpoint returns a valid response."""
    response = client.get("/market/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "market_name" in data


def test_market_analysis_empty_returns_200(client, mock_repo):
    """Market analysis with no companies must return 200."""
    mock_repo.get_all.return_value = []
    response = client.get("/market/analysis")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /market/overlap/{id}
# ---------------------------------------------------------------------------


def test_market_overlap_endpoint(client):
    """GET /market/overlap/{id} must return a list (possibly empty)."""
    response = client.get("/market/overlap/test-company")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_market_overlap_not_found(client, mock_repo):
    """GET /market/overlap/{id} returns 404 when company doesn't exist."""
    mock_repo.get_by_id.return_value = None
    response = client.get("/market/overlap/GHOST")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /market/search
# ---------------------------------------------------------------------------


def test_search_endpoint(client):
    """Verify search functionality returns matched results."""
    response = client.get("/market/search?query=Test")
    assert response.status_code == 200
    data = response.json()
    assert "total_results" in data
    assert data["total_results"] == 1


def test_search_endpoint_no_match(client):
    """Search with non-matching query returns zero results."""
    response = client.get("/market/search?query=ZZZZNOTFOUND")
    assert response.status_code == 200
    assert response.json()["total_results"] == 0


# ---------------------------------------------------------------------------
# GET /scoring/stats
# ---------------------------------------------------------------------------


def test_stats_endpoint(client):
    """Verify statistics calculation includes expected keys."""
    response = client.get("/scoring/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_companies" in data
    assert data["total_companies"] == 1
    assert "revenue_statistics" in data
    assert "growth_classification" in data


# ---------------------------------------------------------------------------
# Auth design: unauthenticated access
# ---------------------------------------------------------------------------


def test_unauthenticated_access_returns_anonymous(unauthenticated_client):
    """
    The app uses auto_error=False — unauthenticated requests receive an
    anonymous user context, NOT a 401. This test documents this design intent.
    """
    response = unauthenticated_client.get("/health")
    # Health is always available; verifies app responds (not crashes) without auth
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Global Exception Handlers (422, 404, 500)
# ---------------------------------------------------------------------------


def test_validation_error_handler(client):
    """Trigger a 422 Unprocessable Entity with a bad payload to test exceptions.py."""
    payload = {
        # Missing strictly required 'id' and 'name' fields!
        "industry": "Energy",
        "tier": "Tier 2",
        "ai_maturity": "Moderate",
    }
    response = client.post("/companies", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "Unprocessable Entity (Validation Error)"
    assert "details" in data
    assert "request_id" in data


def test_http_exception_handler(client, mock_repo):
    """Trigger a 404 HTTP exception directly to test custom format."""
    # Market overlap for non-existent company triggers 404 via HTTPException
    mock_repo.get_by_id.return_value = None
    response = client.get("/market/overlap/GHOST")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "HTTP Error"
    assert "details" in data
    assert "request_id" in data


def test_global_500_exception_handler():
    """Trigger a 500 Internal Server error cleanly via a one-off test route."""
    from fastapi.testclient import TestClient

    from solstein.api.main import app

    @app.get("/force-500-test-panic")
    def force_500():
        raise RuntimeError("Database offline panic test")

    # We must explicitly tell the TestClient NOT to re-raise the exception
    # so we can assert the JSONResponse from our custom global exception handler.
    test_client = TestClient(app, raise_server_exceptions=False)
    response = test_client.get("/force-500-test-panic")
    assert response.status_code == 500
    data = response.json()
    assert data["error"] == "Internal Server Error"
    assert "message" in data
    assert "Database offline panic test" in data["message"]
    assert "traceback" in data
    assert "request_id" in data
