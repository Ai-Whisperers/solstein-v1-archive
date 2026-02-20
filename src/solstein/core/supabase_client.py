"""
Supabase client integration.
Provides a singleton instance of the Supabase client for database operations.
"""

from typing import Optional
from loguru import logger
from supabase import create_client, Client

from solstein.config import get_settings


class SupabaseConnection:
    """Singleton wrapper for Supabase client."""
    
    _instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or initialize the Supabase client."""
        if cls._instance is None:
            settings = get_settings()
            if not settings.supabase.url or not settings.supabase.key:
                logger.error("Supabase URL or Key not configured. Database operations will fail.")
                raise ValueError("Missing Supabase configuration")

            logger.info("Initializing Supabase client connection.")
            cls._instance = create_client(
                settings.supabase.url,
                settings.supabase.key
            )
        return cls._instance


def get_supabase() -> Client:
    """Dependency injection helper for FastAPI and Repositories."""
    return SupabaseConnection.get_client()
