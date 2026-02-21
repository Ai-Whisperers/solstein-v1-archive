"""
API Dependencies.
"""

from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from ..config import get_settings
from ..core.repositories import CompanyRepository
from ..data.repositories import JsonFileRepository, SupabaseRepository

security = HTTPBearer(auto_error=False)


def get_repository() -> CompanyRepository:
    """Get repository instance. Falls back to JSON for local testing."""
    settings = get_settings()

    if not settings.supabase.url or "your-project" in settings.supabase.url:
        logger.warning("Supabase URL not configured. Falling back to local JSON repository.")  # noqa: E501
        return JsonFileRepository()

    try:
        return SupabaseRepository()
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}. Falling back to JSON.")
        return JsonFileRepository()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get current user from JWT token (simplified for demo)."""
    # For demo, authentication is optional
    if not credentials:
        return {"username": "anonymous", "role": "viewer"}

    # In production, validate JWT token here
    return {"username": "demo_user", "role": "admin"}
