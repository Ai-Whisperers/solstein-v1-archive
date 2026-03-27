"""Authentication router for Solstein API.

STORY-067: Migrated to Supabase Auth. All credential verification, token
lifecycle management, and password hashing are now delegated to Supabase Auth
SDK. No custom password hashing or JWT signing logic exists in this codebase.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel, EmailStr
from supabase_auth.errors import AuthApiError

from ...core.supabase_client import get_supabase

router = APIRouter(tags=["Authentication"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Request model for login endpoint."""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {"example": {"email": "user@example.com", "password": "securepassword123"}}


class SignupRequest(BaseModel):
    """Request model for signup endpoint."""

    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {"example": {"email": "newuser@example.com", "password": "securepassword123"}}


class RefreshRequest(BaseModel):
    """Request model for token refresh endpoint."""

    refresh_token: str

    class Config:
        json_schema_extra = {"example": {"refresh_token": "your-refresh-token-here"}}


class AuthTokenResponse(BaseModel):
    """Response model for authentication endpoints."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict[str, Any] | None = None


class UserInfoResponse(BaseModel):
    """Response model for user info endpoint."""

    user_id: str
    email: str
    role: str = "user"


@router.post("/auth/login", response_model=AuthTokenResponse)
async def login(request: LoginRequest) -> AuthTokenResponse:
    """Authenticate user via Supabase Auth and return tokens.

    Delegates all credential verification to Supabase Auth SDK.
    No password hashing or comparison happens in this codebase.

    Args:
        request: Login credentials (email and password)

    Returns:
        AuthTokenResponse with access and refresh tokens

    Raises:
        HTTPException: 401 if authentication fails, 503 if Supabase unavailable
    """
    logger.info(f"Login attempt for user: {request.email}")

    try:
        client = get_supabase()
        response = client.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )
    except (ValueError, ImportError) as e:
        logger.error(f"Supabase configuration error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from e
    except AuthApiError as e:
        logger.warning(f"Login failed for {request.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    session = response.session
    if not session:
        logger.warning(f"Login returned no session for {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = None
    if response.user:
        user_data = {
            "id": response.user.id,
            "email": response.user.email,
            "role": response.user.role,
        }

    logger.info(f"Login successful for user: {request.email}")
    return AuthTokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
        user=user_data,
    )


@router.post("/auth/signup", response_model=AuthTokenResponse)
async def signup(request: SignupRequest) -> AuthTokenResponse:
    """Register a new user via Supabase Auth.

    Args:
        request: Signup credentials (email and password)

    Returns:
        AuthTokenResponse with access and refresh tokens

    Raises:
        HTTPException: 400 if signup fails, 503 if Supabase unavailable
    """
    logger.info(f"Signup attempt for: {request.email}")

    try:
        client = get_supabase()
        response = client.auth.sign_up(
            {"email": request.email, "password": request.password}
        )
    except (ValueError, ImportError) as e:
        logger.error(f"Supabase configuration error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from e
    except AuthApiError as e:
        error_msg = str(e.message).lower() if e.message else ""
        if "already registered" in error_msg or "duplicate" in error_msg:
            logger.warning(f"Signup failed — email already registered: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            ) from e
        logger.error(f"Supabase auth error during signup for {request.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed",
        ) from e

    session = response.session
    if not session:
        # Supabase may require email confirmation before issuing a session
        logger.info(f"Signup successful for {request.email} — email confirmation may be required")
        return AuthTokenResponse(
            access_token="",
            refresh_token="",
            token_type="bearer",
            expires_in=0,
            user={"id": response.user.id, "email": response.user.email} if response.user else None,
        )

    user_data = None
    if response.user:
        user_data = {
            "id": response.user.id,
            "email": response.user.email,
            "role": response.user.role,
        }

    logger.info(f"Signup successful for: {request.email}")
    return AuthTokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
        user=user_data,
    )


@router.post("/auth/refresh", response_model=AuthTokenResponse)
async def refresh_token(request: RefreshRequest) -> AuthTokenResponse:
    """Refresh an access token using a Supabase refresh token.

    Delegates token refresh entirely to Supabase Auth SDK.

    Args:
        request: Refresh token

    Returns:
        AuthTokenResponse with new access and refresh tokens

    Raises:
        HTTPException: 401 if refresh token is invalid or expired
    """
    logger.info("Token refresh requested")

    try:
        client = get_supabase()
        response = client.auth.refresh_session(request.refresh_token)
    except AuthApiError as e:
        logger.warning(f"Token refresh failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except (ValueError, ImportError) as e:
        logger.error(f"Supabase configuration error during refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from e

    session = response.session
    if not session:
        logger.warning("Token refresh returned no session")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Token refresh successful")
    return AuthTokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
    )


@router.post("/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    """Log out the current user by invalidating their session.

    Args:
        credentials: Current Bearer token

    Returns:
        Success message
    """
    try:
        client = get_supabase()
        client.auth.sign_out()
        logger.info("User logged out successfully")
    except AuthApiError as e:
        logger.warning(f"Logout encountered an error (session may already be invalid): {e.message}")
    except (ValueError, ImportError) as e:
        logger.warning(f"Supabase unavailable during logout: {e}")

    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserInfoResponse)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInfoResponse:
    """Get current user information from Supabase JWT.

    Validates the access token via Supabase Auth and returns user info.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        UserInfoResponse with user information

    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    try:
        client = get_supabase()
        user_response = client.auth.get_user(credentials.credentials)
    except AuthApiError as e:
        logger.warning(f"Token verification failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except (ValueError, ImportError) as e:
        logger.error(f"Supabase configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from e

    if not user_response or not user_response.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_response.user
    logger.info(f"User info requested for: {user.email}")
    return UserInfoResponse(
        user_id=user.id,
        email=user.email or "",
        role=user.role or "user",
    )
