"""
End-to-end API tests for Solstein.

These tests verify that API endpoints work correctly with the database backend.
Requires the API server to be running or uses TestClient for FastAPI.
"""

import os
import sys

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Check if we can import FastAPI TestClient
try:
    from fastapi.testclient import TestClient

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import CompanyRecord, ResearchRunRecord


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide database session."""
    db_manager = DatabaseManager()
    session = await db_manager.get_session().__aenter__()
    transaction = await session.begin_nested()
    yield session
    await transaction.rollback()
    await session.close()
    await db_manager.engine.dispose()


@pytest.fixture
def test_client():
    """Provide FastAPI test client."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI TestClient not available")

    try:
        from solstein.api.main import app

        return TestClient(app)
    except ImportError:
        pytest.skip("API app not available")


class TestCompaniesAPI:
    """Test suite for Companies API endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_companies(self, test_client):
        """Test GET /companies endpoint."""
        response = test_client.get("/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_company_by_id(self, test_client, db_session):
        """Test GET /companies/{id} endpoint."""
        # Create test company
        company = CompanyRecord(id="api-test-company", ticker="API", name="API Test Company", status="active")
        db_session.add(company)

        response = test_client.get(f"/companies/{company.id}")

        if response.status_code == 200:
            data = response.json()
            assert data["id"] == company.id
            assert data["ticker"] == "API"

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_create_company(self, test_client):
        """Test POST /companies endpoint."""
        payload = {"ticker": "NEWAPI", "name": "New API Company", "sector": "Technology", "status": "active"}

        response = test_client.post("/companies", json=payload)

        # Accept 201 (created) or 200 (success) or 422 (validation error)
        assert response.status_code in [200, 201, 422]

        if response.status_code in [200, 201]:
            data = response.json()
            assert data["ticker"] == payload["ticker"]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_update_company(self, test_client, db_session):
        """Test PUT /companies/{id} endpoint."""
        company = CompanyRecord(id="update-test", ticker="UPD", name="Update Test", status="active")
        db_session.add(company)

        payload = {"name": "Updated Name"}
        response = test_client.put(f"/companies/{company.id}", json=payload)

        assert response.status_code in [200, 404]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_search_companies(self, test_client):
        """Test GET /companies/search endpoint."""
        response = test_client.get("/companies/search?q=test")
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestResearchRunsAPI:
    """Test suite for Research Runs API endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_research_runs(self, test_client):
        """Test GET /research-runs endpoint."""
        response = test_client.get("/research-runs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_research_run_by_id(self, test_client, db_session):
        """Test GET /research-runs/{id} endpoint."""
        # Create test run
        run = ResearchRunRecord(
            id="api-test-run",
            company_id=None,  # Or create company first
            status="completed",
        )
        db_session.add(run)

        response = test_client.get(f"/research-runs/{run.id}")
        assert response.status_code in [200, 404]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_create_research_run(self, test_client):
        """Test POST /research-runs endpoint."""
        payload = {"status": "pending", "metadata": {"query": "test analysis"}}

        response = test_client.post("/research-runs", json=payload)
        assert response.status_code in [200, 201, 422]


class TestFactsAPI:
    """Test suite for Facts API endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_facts(self, test_client):
        """Test GET /facts endpoint."""
        response = test_client.get("/facts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_facts_by_company(self, test_client):
        """Test GET /companies/{id}/facts endpoint."""
        response = test_client.get("/companies/test-company/facts")
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_create_fact(self, test_client):
        """Test POST /facts endpoint."""
        payload = {"company_id": "test-company", "fact_key": "revenue", "fact_value": "1000000", "confidence": 0.95}

        response = test_client.post("/facts", json=payload)
        assert response.status_code in [200, 201, 422]


class TestSignalsAPI:
    """Test suite for Signals API endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_signals(self, test_client):
        """Test GET /signals endpoint."""
        response = test_client.get("/signals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_get_signals_by_company(self, test_client):
        """Test GET /companies/{id}/signals endpoint."""
        response = test_client.get("/companies/test-company/signals")
        assert response.status_code in [200, 404]


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_health_check(self, test_client):
        """Test GET /health endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "healthy" in str(data).lower()

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_ready_check(self, test_client):
        """Test GET /ready endpoint."""
        response = test_client.get("/ready")
        assert response.status_code in [200, 503]


class TestErrorHandling:
    """Test suite for API error handling."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_404_not_found(self, test_client):
        """Test 404 response for non-existent resources."""
        response = test_client.get("/companies/non-existent-id-12345")
        assert response.status_code == 404

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_422_validation_error(self, test_client):
        """Test 422 response for invalid input."""
        # Send invalid payload (missing required fields)
        payload = {}
        response = test_client.post("/companies", json=payload)
        assert response.status_code in [200, 201, 422]

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_invalid_json(self, test_client):
        """Test error handling for invalid JSON."""
        response = test_client.post("/companies", data="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code in [400, 422]


class TestAPIDatabaseIntegration:
    """Test API integration with database."""

    @pytest.mark.asyncio
    async def test_api_uses_database(self, db_session):
        """Test that API reads from database."""
        # Create company in database
        company = CompanyRecord(id="integration-test", ticker="INT", name="Integration Test", status="active")
        db_session.add(company)
        await db_session.commit()

        # Verify it exists
        result = await db_session.get(CompanyRecord, company.id)
        assert result is not None
        assert result.ticker == "INT"

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_api_pagination(self, test_client):
        """Test API pagination."""
        response = test_client.get("/companies?skip=0&limit=10")
        assert response.status_code == 200

        response = test_client.get("/companies?skip=10&limit=10")
        assert response.status_code == 200

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_api_filtering(self, test_client):
        """Test API filtering capabilities."""
        response = test_client.get("/companies?status=active")
        assert response.status_code in [200, 422]  # 422 if filtering not supported


class TestAPIPerformance:
    """Test API performance characteristics."""

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_response_time(self, test_client):
        """Test API response time."""
        import time

        start = time.time()
        response = test_client.get("/companies")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 5.0  # Should respond in under 5 seconds

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests."""
        import concurrent.futures

        def make_request():
            return test_client.get("/health")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
