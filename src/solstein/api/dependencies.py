"""
API Dependencies.
"""

from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import get_settings
from ..core.repositories import CompanyRepository
from ..data.repositories import SupabaseRepository

security = HTTPBearer(auto_error=False)


def get_repository() -> CompanyRepository:
    """Get repository instance."""
    return SupabaseRepository()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict[str, Any]:
    """Get current user from JWT token (simplified for demo)."""
    # For demo, authentication is optional
    if not credentials:
        return {"username": "anonymous", "role": "viewer"}

    # In production, validate JWT token here
    return {"username": "demo_user", "role": "admin"}
