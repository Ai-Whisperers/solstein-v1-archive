"""JWT Authentication Handler for Solstein API.

Phase 1, Item 1.2: JWT Authentication Implementation
"""

from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel

from solstein.config import get_settings


class UserPayload(BaseModel):
    """User payload extracted from JWT token."""

    user_id: str
    email: str
    role: str = "user"
    exp: datetime | None = None


class TokenResponse(BaseModel):
    """Response model for token endpoints."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class JWTHandler:
    """Handle JWT token creation, verification, and refresh.

    This class provides methods for:
    - Creating access tokens
    - Verifying and decoding tokens
    - Refreshing expiring tokens

    Uses HS256 algorithm with secret key from configuration.
    """

    def __init__(self):
        """Initialize JWT handler with settings."""
        settings = get_settings()
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.token_expire_minutes = settings.security.access_token_expire_minutes

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a new JWT access token.

        Args:
            data: Dictionary containing user data (user_id, email, role)
            expires_delta: Optional custom expiration time. Defaults to 30 minutes.

        Returns:
            Encoded JWT token string

        Raises:
            ValueError: If data is empty or missing required fields
        """
        if not data:
            raise ValueError("Token data cannot be empty")

        if "user_id" not in data:
            raise ValueError("Token data must contain 'user_id'")

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.token_expire_minutes)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        return encoded_jwt

    def verify_token(self, token: str) -> UserPayload:
        """Verify and decode a JWT token.

        Args:
            token: JWT token string to verify

        Returns:
            UserPayload with decoded user information

        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
            ValueError: If token format is invalid
        """
        if not token or not isinstance(token, str):
            raise ValueError("Token must be a non-empty string")

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            return UserPayload(
                user_id=payload.get("user_id"),
                email=payload.get("email", ""),
                role=payload.get("role", "user"),
                exp=datetime.fromtimestamp(payload.get("exp")) if payload.get("exp") else None,
            )
        except jwt.ExpiredSignatureError as err:
            raise jwt.ExpiredSignatureError("Token has expired") from err
        except jwt.InvalidSignatureError as err:
            raise jwt.InvalidTokenError("Invalid token signature") from err
        except jwt.DecodeError as err:
            raise jwt.InvalidTokenError("Could not decode token") from err

    def refresh_token(self, token: str) -> str:
        """Refresh an expiring token with a new expiration time.

        Args:
            token: Current valid JWT token

        Returns:
            New JWT token with refreshed expiration

        Raises:
            jwt.ExpiredSignatureError: If token has already expired
            jwt.InvalidTokenError: If token is invalid
        """
        # Verify current token (will raise if expired or invalid)
        payload = self.verify_token(token)

        # Create new token data (remove exp, it will be re-added)
        token_data = {"user_id": payload.user_id, "email": payload.email, "role": payload.role}

        # Create new token with fresh expiration
        return self.create_access_token(token_data)


# Singleton instance for convenience
jwt_handler = JWTHandler()
