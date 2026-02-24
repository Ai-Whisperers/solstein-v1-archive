"""
Supabase client integration.
Provides a singleton instance of the Supabase client for database operations.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

try:
    from supabase import Client, create_client
except ImportError:
    Client = None  # type: ignore[assignment, misc]
    create_client = None  # type: ignore[assignment]

from solstein.config import get_settings


class SupabaseConnection:
    """Singleton wrapper for Supabase client."""

    _instance: Any = None

    @classmethod
    def get_client(cls) -> Any:
        """Get or initialize the Supabase client."""
        if Client is None:
            raise ImportError("supabase package is not installed")
        if cls._instance is None:
            settings = get_settings()
            if not settings.supabase.url or not settings.supabase.key:
                logger.error("Supabase URL or Key not configured. Database operations will fail.")
                raise ValueError("Missing Supabase configuration")

            logger.info("Initializing Supabase client connection.")
            cls._instance = create_client(settings.supabase.url, settings.supabase.key)
        return cls._instance


def get_supabase() -> Any:
    """Dependency injection helper for FastAPI and Repositories."""
    return SupabaseConnection.get_client()
