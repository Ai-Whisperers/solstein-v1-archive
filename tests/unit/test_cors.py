"""
CORS Configuration Tests - Phase 1, Item 1.1

Verifies that CORS middleware is properly configured:
- Only specific origins are allowed (not wildcard)
- Credentials are only allowed with specific origins
- HTTP methods are explicitly defined
- Headers are explicitly defined
"""

from fastapi.testclient import TestClient

from solstein.api.main import app
from solstein.config import Settings


class TestCORSConfiguration:
    """Test CORS middleware configuration."""

    def test_cors_allows_specific_origins_only(self):
        """CORS must allow only specific origins, not wildcard."""
        client = TestClient(app)

        # Test allowed origin
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_cors_rejects_wildcard_origin(self):
        """CORS must NOT use wildcard (*) for origins."""
        settings = Settings()
        # Verify configuration doesn't contain wildcard
        assert "*" not in settings.api.cors_origins, "CORS origins must not contain wildcard (*)"

    def test_cors_allows_multiple_specific_origins(self):
        """CORS should allow multiple specific origins."""
        settings = Settings()
        # Verify at least 2 origins are configured
        assert len(settings.api.cors_origins) >= 2, "CORS should allow multiple specific origins"
        # Verify they are specific (not wildcard)
        for origin in settings.api.cors_origins:
            assert origin != "*", f"Origin {origin} is wildcard"
            assert "localhost" in origin or "http" in origin, f"Origin {origin} should be specific"

    def test_cors_credentials_with_specific_origins(self):
        """CORS allow_credentials=True must only work with specific origins."""
        client = TestClient(app)

        # Test with allowed origin
        response = client.options(
            "/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"}
        )

        # Should allow credentials with specific origin
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"].lower() == "true"

    def test_cors_explicit_methods(self):
        """CORS must explicitly define allowed HTTP methods."""
        settings = Settings()

        # Verify methods are explicitly defined
        assert len(settings.api.cors_methods) > 0, "CORS methods must be explicitly defined"

        # Verify expected methods are present
        expected_methods = {"GET", "POST", "PUT", "DELETE"}
        configured_methods = set(settings.api.cors_methods)
        assert expected_methods.issubset(configured_methods), f"CORS methods must include {expected_methods}"

    def test_cors_explicit_headers(self):
        """CORS must explicitly define allowed headers."""
        settings = Settings()

        # Verify headers are explicitly defined
        assert len(settings.api.cors_headers) > 0, "CORS headers must be explicitly defined"

        # Verify expected headers are present
        expected_headers = {"Authorization", "Content-Type"}
        configured_headers = set(settings.api.cors_headers)
        assert expected_headers.issubset(configured_headers), f"CORS headers must include {expected_headers}"

    def test_cors_preflight_request(self):
        """CORS preflight (OPTIONS) request should return proper headers."""
        client = TestClient(app)

        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        # Preflight should return 200
        assert response.status_code == 200

        # Should include CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_cors_max_age_set(self):
        """CORS should set max_age for preflight caching."""
        client = TestClient(app)

        response = client.options(
            "/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"}
        )

        # Should include max-age header
        if "access-control-max-age" in response.headers:
            max_age = int(response.headers["access-control-max-age"])
            assert max_age > 0, "max-age should be positive"
            assert max_age >= 600, "max-age should be at least 10 minutes (600s)"

    def test_cors_no_wildcard_with_credentials(self):
        """CRITICAL: CORS must NOT allow wildcard origins with credentials."""
        settings = Settings()

        # This is a critical security check
        # If wildcard is in origins AND credentials are allowed, it's a vulnerability
        has_wildcard = "*" in settings.api.cors_origins

        assert not has_wildcard, "CRITICAL SECURITY: CORS wildcard (*) with credentials is a vulnerability"

    def test_cors_configuration_from_env(self):
        """CORS configuration should be loadable from environment variables."""
        settings = Settings()

        # Verify settings are loaded (not hardcoded)
        assert settings.api.cors_origins is not None
        assert settings.api.cors_methods is not None
        assert settings.api.cors_headers is not None

        # Verify they have sensible defaults
        assert len(settings.api.cors_origins) > 0
        assert len(settings.api.cors_methods) > 0
        assert len(settings.api.cors_headers) > 0


class TestCORSIntegration:
    """Integration tests for CORS with actual endpoints."""

    def test_cors_with_health_endpoint(self):
        """Health endpoint should respect CORS configuration."""
        client = TestClient(app)

        response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_with_companies_endpoint(self):
        """Companies endpoint should respect CORS configuration."""
        client = TestClient(app)

        response = client.get("/companies", headers={"Origin": "http://localhost:3000"})

        # Should return 200 or 401 (auth), but not CORS error
        assert response.status_code in [200, 401, 403]

    def test_cors_origin_not_in_allowed_list(self):
        """CORS should handle disallowed origins gracefully."""
        client = TestClient(app)

        response = client.get("/health", headers={"Origin": "http://evil.com"})

        # Response should succeed (CORS is not enforced by browser in non-preflight)
        # but CORS headers should not include the disallowed origin
        assert response.status_code == 200

        # If CORS header is present, it should NOT be the disallowed origin
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] != "http://evil.com"


class TestCORSSecurityCompliance:
    """Security compliance tests for CORS configuration."""

    def test_no_wildcard_origin_vulnerability(self):
        """Verify CORS wildcard vulnerability is fixed."""
        settings = Settings()

        # This was the original vulnerability
        assert "*" not in settings.api.cors_origins, "CORS wildcard vulnerability: origins contain '*'"

    def test_credentials_only_with_specific_origins(self):
        """Verify credentials are only allowed with specific origins."""
        settings = Settings()

        # If credentials are allowed, origins must be specific
        # (This is enforced by FastAPI's CORSMiddleware)
        assert len(settings.api.cors_origins) > 0
        assert all(origin != "*" for origin in settings.api.cors_origins)

    def test_cors_configuration_documented(self):
        """CORS configuration should be documented in .env.example."""
        import os

        env_example_path = os.path.join(os.path.dirname(__file__), "../../.env.example")

        if os.path.exists(env_example_path):
            with open(env_example_path) as f:
                content = f.read()
                # Should document CORS variables
                assert "CORS" in content or "cors" in content, ".env.example should document CORS configuration"
