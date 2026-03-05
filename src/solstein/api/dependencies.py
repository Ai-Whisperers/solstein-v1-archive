from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..infrastructure.company_repository import CompanyRepository
from ..infrastructure.repositories import FactRepository
from ..infrastructure.database import db_manager
from ..infrastructure.database_service import DatabaseService
from ..infrastructure.enrichment_repositories import EnrichmentAuditRepository, EnrichmentCacheRepository
from ..api.services.drill_down_service import DrillDownService
from ..security.jwt_handler import jwt_handler, UserPayload


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> UserPayload:
    """Get current user from JWT token.

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
        return jwt_handler.verify_token(credentials.credentials)
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
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
