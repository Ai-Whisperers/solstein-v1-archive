"""
Supabase client integration.
Provides a singleton instance of the Supabase client for database operations.
"""

from loguru import logger
from supabase import Client, create_client

from solstein.config import get_settings


class SupabaseConnection:
    """Singleton wrapper for Supabase client."""

    _instance: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or initialize the Supabase client."""
        if cls._instance is None:
            settings = get_settings()
            if not settings.supabase.url or not settings.supabase.key:
                logger.error(
                    "Supabase URL or Key not configured. Database operations will fail."
                )  # noqa: E501
                raise ValueError("Missing Supabase configuration")

            logger.info("Initializing Supabase client connection.")
            cls._instance = create_client(settings.supabase.url, settings.supabase.key)
        return cls._instance


def get_supabase() -> Client:
    """Dependency injection helper for FastAPI and Repositories."""
    return SupabaseConnection.get_client()
