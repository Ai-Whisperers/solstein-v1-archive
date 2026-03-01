"""Authentication router for Solstein API.

Phase 1, Item 1.2: JWT Authentication Endpoints
"""

import hashlib
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel

from ...config import get_settings
from ...security.jwt_handler import jwt_handler, TokenResponse, UserPayload
from ..dependencies import get_current_user

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    
    email: str
    password: str
    
    class Config:
        json_schema_extra = {"example": {"email": "user@example.com", "password": "securepassword123"}}


class RefreshRequest(BaseModel):
    """Request model for token refresh endpoint."""

    refresh_token: str

    class Config:
        json_schema_extra = {"example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}}


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """Authenticate user and return access token.

    Validates credentials against ADMIN_EMAIL and ADMIN_PASSWORD_HASH
    environment variables. Password must be SHA-256 hex digest.

    Args:
        request: Login credentials (email and password)

    Returns:
        TokenResponse with access token and expiration info

    Raises:
        HTTPException: 401 if authentication fails or not configured
    """
    settings = get_settings()
    admin_email: Optional[str] = settings.security.admin_email
    admin_password_hash: Optional[str] = settings.security.admin_password_hash

    logger.info(f"Login attempt for user: {request.email}")

    # Ensure admin credentials are configured
    if not admin_email or not admin_password_hash:
        logger.error("Login rejected: ADMIN_EMAIL or ADMIN_PASSWORD_HASH not configured")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD_HASH env vars.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate email
    if request.email != admin_email:
        logger.warning(f"Login failed — unknown email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate password (compare SHA-256 hash)
    provided_hash = hashlib.sha256(request.password.encode()).hexdigest()
    if provided_hash != admin_password_hash:
        logger.warning(f"Login failed — wrong password for: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Build token payload
        token_data = {"user_id": f"user_{request.email.split('@')[0]}", "email": request.email, "role": "admin"}
        access_token = jwt_handler.create_access_token(token_data)
        logger.info(f"Login successful for user: {request.email}")
        return TokenResponse(
            access_token=access_token, token_type="bearer", expires_in=jwt_handler.token_expire_minutes * 60
        )
    except Exception as e:
        logger.error(f"Token creation failed for {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation failed",
        )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenResponse:
    """Refresh an expiring access token.

    Takes a valid (but potentially expiring) token and returns
    a new token with a fresh expiration time.

    Args:
        credentials: Current Bearer token

    Returns:
        TokenResponse with new access token

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        logger.info("Token refresh requested")

        # Refresh the token
        new_token = jwt_handler.refresh_token(credentials.credentials)

        logger.info("Token refresh successful")

        return TokenResponse(
            access_token=new_token, token_type="bearer", expires_in=jwt_handler.token_expire_minutes * 60
        )

    except Exception as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/auth/me", response_model=UserPayload)
async def get_me(current_user: UserPayload = Depends(get_current_user)) -> UserPayload:
    """Get current user information.

    Returns information about the currently authenticated user
    based on the provided JWT token.

    Args:
        current_user: User payload from JWT token (injected by dependency)

    Returns:
        UserPayload with user information

    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    logger.info(f"User info requested for: {current_user.email}")
    return current_user
