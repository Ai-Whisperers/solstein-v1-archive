from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from supabase_auth.errors import AuthApiError

from ..api.services.drill_down_service import DrillDownService
from ..core.supabase_client import get_supabase
from ..infrastructure.company_repository import CompanyRepository
from ..infrastructure.database import db_manager
from ..infrastructure.database_service import DatabaseService
from ..infrastructure.enrichment_repositories import EnrichmentAuditRepository, EnrichmentCacheRepository
from ..infrastructure.repositories import FactRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session."""
    async for session in db_manager.get_session():
        yield session


async def get_company_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CompanyRepository:
    """Get async CompanyRepository instance."""
    return CompanyRepository(session)


async def get_fact_repository(
    session: AsyncSession = Depends(get_db_session),
) -> FactRepository:
    """Get async FactRepository instance."""
    return FactRepository(session)


async def get_database_service(
    session: AsyncSession = Depends(get_db_session),
) -> DatabaseService:
    """Dependency to get a DatabaseService instance."""
    return DatabaseService(session)


def get_drill_down_service(
    session: AsyncSession = Depends(get_db_session),
    db_service: DatabaseService = Depends(get_database_service),
) -> DrillDownService:
    """Dependency to get a DrillDownService instance."""
    return DrillDownService(session=session, db_service=db_service)


async def get_enrichment_audit_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EnrichmentAuditRepository:
    """Dependency to get an EnrichmentAuditRepository instance."""
    return EnrichmentAuditRepository(session)


async def get_enrichment_cache_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EnrichmentCacheRepository:
    """Dependency to get an EnrichmentCacheRepository instance."""
    return EnrichmentCacheRepository(session)


security = HTTPBearer()


class UserPayload(BaseModel):
    """User payload extracted from Supabase JWT token.

    STORY-067: Replaces the old jwt_handler.UserPayload. Fields are now
    sourced from Supabase Auth's user object rather than a custom JWT.
    """

    user_id: str
    email: str
    role: str = "user"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserPayload:
    """Get current user by verifying token with Supabase Auth.

    STORY-067: Delegates token verification entirely to Supabase Auth SDK.
    No custom JWT decoding or signing logic exists in this codebase.

    Args:
        credentials: HTTP Authorization credentials with Bearer token

    Returns:
        UserPayload with user information

    Raises:
        HTTPException: 401 if token is missing, expired, or invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    return UserPayload(
        user_id=user.id,
        email=user.email or "",
        role=user.role or "user",
    )


async def get_current_tenant(request: Request) -> dict[str, Any]:
    tenant = getattr(request.state, "tenant", None)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant authentication required",
        )

    if not isinstance(tenant, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid tenant context",
        )

    return tenant


async def require_admin(user: UserPayload = Depends(get_current_user)) -> UserPayload:
    """Require admin role for access.

    Args:
        user: Current authenticated user

    Returns:
        UserPayload if user is admin

    Raises:
        HTTPException: 403 if user is not admin
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
