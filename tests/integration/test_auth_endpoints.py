"""Integration tests for Authentication Endpoints - Phase 1, Item 1.2

Verifies /auth/login, /auth/refresh, and /auth/me endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from solstein.api.main import app


class TestAuthEndpoints:
    """Test authentication endpoints."""

    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)

    def test_login_success(self, client):
        """POST /auth/login should return valid token for valid credentials."""
        response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] > 0
        assert len(data["access_token"]) > 0

    def test_login_missing_email(self, client):
        """POST /auth/login should return 422 for missing email."""
        response = client.post("/auth/login", json={"password": "password123"})

        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """POST /auth/login should return 422 for missing password."""
        response = client.post("/auth/login", json={"email": "test@example.com"})

        assert response.status_code == 422

    def test_login_invalid_email_format(self, client):
        """POST /auth/login should return 422 for invalid email format."""
        response = client.post("/auth/login", json={"email": "not-an-email", "password": "password123"})

        assert response.status_code == 422

    def test_refresh_token_success(self, client):
        """POST /auth/refresh should return new token for valid token."""
        # First, login to get a token
        login_response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]

        # Refresh the token
        response = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] != token  # Should be different token

    def test_refresh_token_missing_header(self, client):
        """POST /auth/refresh should return 403 for missing Authorization header."""
        response = client.post("/auth/refresh")

        assert response.status_code == 403

    def test_refresh_token_invalid_token(self, client):
        """POST /auth/refresh should return 401 for invalid token."""
        response = client.post("/auth/refresh", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401

    def test_get_me_success(self, client):
        """GET /auth/me should return user info for valid token."""
        # First, login to get a token
        login_response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]

        # Get user info
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert data["email"] == "test@example.com"
        assert "role" in data

    def test_get_me_missing_header(self, client):
        """GET /auth/me should return 403 for missing Authorization header."""
        response = client.get("/auth/me")

        assert response.status_code == 403

    def test_get_me_invalid_token(self, client):
        """GET /auth/me should return 401 for invalid token."""
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})

        assert response.status_code == 401

    def test_protected_endpoint_requires_auth(self, client):
        """Protected endpoints should require authentication."""
        # Try to access a protected endpoint without auth
        response = client.get("/companies")

        # Should be 401 (unauthorized) or 403 (forbidden)
        assert response.status_code in [401, 403]

    def test_protected_endpoint_with_valid_token(self, client):
        """Protected endpoints should work with valid token."""
        # First, login to get a token
        login_response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
        token = login_response.json()["access_token"]

        # Access protected endpoint with token
        response = client.get("/companies", headers={"Authorization": f"Bearer {token}"})

        # Should succeed (200) or return empty list, not auth error
        assert response.status_code in [200, 404]  # 404 if no companies
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    def test_token_in_response_headers(self, client):
        """Login response should not contain token in headers (security)."""
        response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})

        # Token should only be in body, not headers
        assert "access_token" not in response.headers
        assert "authorization" not in [h.lower() for h in response.headers.keys()]

    def test_login_response_content_type(self, client):
        """Login should return JSON content type."""
        response = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})

        assert "application/json" in response.headers.get("content-type", "")
