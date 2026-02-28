"""Unit tests for JWT Authentication Handler - Phase 1, Item 1.2

Verifies JWT token creation, verification, and refresh functionality.
"""

from datetime import datetime, timedelta

import jwt
import pytest

from solstein.security.jwt_handler import jwt_handler, UserPayload


class TestJWTHandler:
    """Test JWT handler functionality."""

    def test_create_access_token_success(self):
        """Should create a valid JWT token with user data."""
        token_data = {"user_id": "test_user_123", "email": "test@example.com", "role": "user"}

        token = jwt_handler.create_access_token(token_data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Verify it can be decoded
        decoded = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])
        assert decoded["user_id"] == "test_user_123"
        assert decoded["email"] == "test@example.com"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    def test_create_access_token_with_custom_expiry(self):
        """Should create token with custom expiration time."""
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        custom_delta = timedelta(hours=2)

        token = jwt_handler.create_access_token(token_data, expires_delta=custom_delta)

        decoded = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])

        # Verify expiration is approximately 2 hours from now
        exp_timestamp = decoded["exp"]
        now_timestamp = datetime.utcnow().timestamp()
        # exp should be roughly 2 hours (7200 seconds) in the future
        time_diff = exp_timestamp - now_timestamp
        assert 7100 < time_diff < 7300, f"Expected ~7200s, got {time_diff}s"

        """Should create token with custom expiration time."""
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        custom_delta = timedelta(hours=2)

    def test_create_access_token_with_custom_expiry(self):
        """Should create token with custom expiration time."""
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        custom_delta = timedelta(hours=2)

        token = jwt_handler.create_access_token(token_data, expires_delta=custom_delta)

        decoded = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])

        # Verify expiration is approximately 2 hours from now
        exp_timestamp = decoded["exp"]
        now_timestamp = datetime.utcnow().timestamp()
        # exp should be roughly 2 hours (7200 seconds) in the future
        time_diff = exp_timestamp - now_timestamp
        assert 7100 < time_diff < 7300, f"Expected ~7200s, got {time_diff}s"
    def test_create_access_token_empty_data_raises_error(self):
        """Should raise error when creating token with empty data."""
        with pytest.raises(ValueError, match="Token data cannot be empty"):
            jwt_handler.create_access_token({})

    def test_create_access_token_missing_user_id_raises_error(self):
        """Should raise error when user_id is missing."""
        token_data = {"email": "test@example.com"}  # Missing user_id

        with pytest.raises(ValueError, match="user_id"):
            jwt_handler.create_access_token(token_data)

    def test_verify_token_success(self):
        """Should successfully verify and decode valid token."""
        # Create a token
        token_data = {"user_id": "test_user_123", "email": "test@example.com", "role": "admin"}
        token = jwt_handler.create_access_token(token_data)

        # Verify the token
        user_payload = jwt_handler.verify_token(token)

        assert user_payload.user_id == "test_user_123"
        assert user_payload.email == "test@example.com"
        assert user_payload.role == "admin"
        assert user_payload.exp is not None

    def test_verify_token_expired_raises_error(self):
        """Should raise error for expired token."""
        # Create a token that expired in the past
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_token = jwt.encode(
            {**token_data, "exp": past_time}, jwt_handler.secret_key, algorithm=jwt_handler.algorithm
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_handler.verify_token(expired_token)

    def test_verify_token_invalid_signature_raises_error(self):
        """Should raise error for token with invalid signature."""
        # Create a token with wrong secret
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        invalid_token = jwt.encode(token_data, "wrong_secret_key", algorithm=jwt_handler.algorithm)

        with pytest.raises(jwt.InvalidTokenError):
            jwt_handler.verify_token(invalid_token)

    def test_verify_token_malformed_raises_error(self):
        """Should raise error for malformed token."""
        with pytest.raises(jwt.InvalidTokenError):
            jwt_handler.verify_token("not.a.valid.token")

    def test_verify_token_empty_string_raises_error(self):
        """Should raise error for empty token string."""
        with pytest.raises(ValueError):
            jwt_handler.verify_token("")

    def test_verify_token_none_raises_error(self):
        """Should raise error for None token."""
        with pytest.raises(ValueError):
            jwt_handler.verify_token(None)

    def test_refresh_token_success(self):
        """Should create new token with fresh expiration."""
        # Create initial token with short expiry
        token_data = {"user_id": "test_user", "email": "test@example.com", "role": "user"}
        original_token = jwt_handler.create_access_token(token_data, expires_delta=timedelta(minutes=5))
        original_exp = jwt.decode(original_token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])["exp"]

        # Small delay to ensure different expiration
        import time

        time.sleep(0.1)

        # Refresh the token
        new_token = jwt_handler.refresh_token(original_token)
        new_exp = jwt.decode(new_token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])["exp"]

        # New token should have later expiration
        assert new_exp > original_exp

        # New token should still contain the same user data
        new_payload = jwt_handler.verify_token(new_token)
        assert new_payload.user_id == "test_user"
        assert new_payload.email == "test@example.com"

    def test_refresh_token_expired_raises_error(self):
        """Should raise error when refreshing expired token."""
        token_data = {"user_id": "test_user", "email": "test@example.com"}
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_token = jwt.encode(
            {**token_data, "exp": past_time}, jwt_handler.secret_key, algorithm=jwt_handler.algorithm
        )

        with pytest.raises(jwt.ExpiredSignatureError):
            jwt_handler.refresh_token(expired_token)

    def test_token_contains_required_claims(self):
        """Token should contain all required claims."""
        token_data = {"user_id": "test_user", "email": "test@example.com", "role": "admin"}
        token = jwt_handler.create_access_token(token_data)

        decoded = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])

        assert "user_id" in decoded
        assert "email" in decoded
        assert "role" in decoded
        assert "exp" in decoded

    def test_default_token_expiry_is_30_minutes(self):
        """Default token expiration should be 30 minutes."""
        token_data = {"user_id": "test_user", "email": "test@example.com"}

        before_create = datetime.utcnow()
        token = jwt_handler.create_access_token(token_data)
        after_create = datetime.utcnow()

        decoded = jwt.decode(token, jwt_handler.secret_key, algorithms=[jwt_handler.algorithm])
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)

        # Should be approximately 30 minutes after creation
        expected_min = before_create + timedelta(minutes=30)
        expected_max = after_create + timedelta(minutes=30)

        assert expected_min <= exp_datetime <= expected_max + timedelta(seconds=5)

class TestUserPayload:
    """Test UserPayload model."""

    def test_user_payload_creation(self):
        """Should create UserPayload with all fields."""
        payload = UserPayload(user_id="user123", email="user@example.com", role="admin")

        assert payload.user_id == "user123"
        assert payload.email == "user@example.com"
        assert payload.role == "admin"

    def test_user_payload_default_role(self):
        """UserPayload should have default role of 'user'."""
        payload = UserPayload(user_id="user123", email="user@example.com")

        assert payload.role == "user"

    def test_user_payload_optional_exp(self):
        """UserPayload exp field should be optional."""
        payload = UserPayload(user_id="user123", email="user@example.com", role="user")

        assert payload.exp is None
