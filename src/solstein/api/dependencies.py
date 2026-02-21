from collections.abc import AsyncGenerator
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..core.repositories import CompanyRepository
from ..data.repositories import JsonFileRepository, SupabaseRepository
from ..infrastructure.database import db_manager
from ..infrastructure.database_service import DatabaseService

security = HTTPBearer(auto_error=False)


def get_repository() -> CompanyRepository:
    """Get repository instance. Falls back to JSON for local testing."""
    settings = get_settings()

    if not settings.supabase.url or "your-project" in settings.supabase.url:
        logger.warning(
            "Supabase URL not configured. Falling back to local JSON repository."
        )  # noqa: E501
        return JsonFileRepository()

    try:
        return SupabaseRepository()
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}. Falling back to JSON.")
        return JsonFileRepository()


from ..api.services.drill_down_service import DrillDownService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get a database session."""
    async for session in db_manager.get_session():
        yield session


def get_database_service(
    session: AsyncSession = Depends(get_db_session),
) -> DatabaseService:
    """Dependency to get a DatabaseService instance."""
    return DatabaseService(session)


def get_drill_down_service(
    db_service: DatabaseService = Depends(get_database_service),
) -> DrillDownService:
    """Dependency to get a DrillDownService instance."""
    return DrillDownService(db_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get current user from JWT token (simplified for demo)."""
    # For demo, authentication is optional
    if not credentials:
        return {"username": "anonymous", "role": "viewer"}

    # In production, validate JWT token here
    return {"username": "demo_user", "role": "admin"}
