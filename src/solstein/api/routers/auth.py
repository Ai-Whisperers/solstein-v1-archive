"""Authentication router for Solstein API.

Phase 1, Item 1.2: JWT Authentication Endpoints
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel

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

    For demo purposes, accepts any email/password combination
    and returns a valid JWT token. In production, this would
    validate against a user database.

    Args:
        request: Login credentials (email and password)

    Returns:
        TokenResponse with access token and expiration info

    Raises:
        HTTPException: 401 if authentication fails
    """
    try:
        # Demo: Accept any credentials
        # In production, validate against user database
        logger.info(f"Login attempt for user: {request.email}")

        # Create token data
        token_data = {"user_id": f"user_{request.email.split('@')[0]}", "email": request.email, "role": "user"}

        # Generate access token
        access_token = jwt_handler.create_access_token(token_data)

        logger.info(f"Login successful for user: {request.email}")

        return TokenResponse(
            access_token=access_token, token_type="bearer", expires_in=jwt_handler.token_expire_minutes * 60
        )

    except Exception as e:
        logger.error(f"Login failed for user {request.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
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
