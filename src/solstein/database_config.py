"""Database URL configuration utilities for multi-environment support.

Provides functions to load, validate, and convert database URLs for different
environments (test, dev, prod) with support for both sync and async SQLAlchemy.
"""

import os
from typing import Optional


class DatabaseURLError(Exception):
    """Raised when database URL is invalid or missing."""

    pass


def validate_database_url(url: str) -> bool:
    """Validate that a database URL is properly formatted.

    Args:
        url: Database URL to validate (postgresql:// or postgresql+asyncpg://)

    Returns:
        True if URL is valid, False otherwise

    Raises:
        DatabaseURLError: If URL is empty or None
    """
    if not url:
        raise DatabaseURLError("Database URL cannot be empty or None")

    # Check for required PostgreSQL URL format
    if not (url.startswith("postgresql://") or url.startswith("postgresql+asyncpg://")):
        return False

    # Check for required components: host, port, database
    if "@" not in url or ":" not in url:
        return False

    return True


def get_database_url(env_var: str = "DATABASE_URL") -> str:
    """Load database URL from environment variable.

    Args:
        env_var: Environment variable name to load (default: DATABASE_URL)

    Returns:
        Database URL string

    Raises:
        DatabaseURLError: If environment variable is not set or URL is invalid
    """
    url = os.getenv(env_var)

    if not url:
        raise DatabaseURLError(
            f"Environment variable '{env_var}' is not set. Set it before running: export {env_var}='postgresql://...'"
        )

    if not validate_database_url(url):
        raise DatabaseURLError(
            f"Invalid database URL format in {env_var}. Expected: postgresql://user:password@host:port/database"
        )

    return url


def get_test_database_url() -> str:
    """Get database URL for test environment.

    Loads from DATABASE_URL_TEST environment variable, falls back to DATABASE_URL.

    Returns:
        Test database URL string

    Raises:
        DatabaseURLError: If no valid test database URL is configured
    """
    # Try test-specific URL first
    test_url = os.getenv("DATABASE_URL_TEST")
    if test_url:
        if validate_database_url(test_url):
            return test_url
        raise DatabaseURLError(
            f"Invalid DATABASE_URL_TEST format. Expected: postgresql://user:password@host:port/database"
        )

    # Fall back to main DATABASE_URL
    return get_database_url("DATABASE_URL")


def get_dev_database_url() -> str:
    """Get database URL for development environment.

    Loads from DATABASE_URL_DEV environment variable, falls back to DATABASE_URL.

    Returns:
        Development database URL string

    Raises:
        DatabaseURLError: If no valid dev database URL is configured
    """
    # Try dev-specific URL first
    dev_url = os.getenv("DATABASE_URL_DEV")
    if dev_url:
        if validate_database_url(dev_url):
            return dev_url
        raise DatabaseURLError(
            f"Invalid DATABASE_URL_DEV format. Expected: postgresql://user:password@host:port/database"
        )

    # Fall back to main DATABASE_URL
    return get_database_url("DATABASE_URL")


def get_prod_database_url() -> str:
    """Get database URL for production environment.

    Loads from DATABASE_URL_PROD environment variable, falls back to DATABASE_URL.

    Returns:
        Production database URL string

    Raises:
        DatabaseURLError: If no valid prod database URL is configured
    """
    # Try prod-specific URL first
    prod_url = os.getenv("DATABASE_URL_PROD")
    if prod_url:
        if validate_database_url(prod_url):
            return prod_url
        raise DatabaseURLError(
            f"Invalid DATABASE_URL_PROD format. Expected: postgresql://user:password@host:port/database"
        )

    # Fall back to main DATABASE_URL
    return get_database_url("DATABASE_URL")


def convert_to_async_url(sync_url: str) -> str:
    """Convert a synchronous PostgreSQL URL to async (asyncpg) format.

    Args:
        sync_url: Synchronous PostgreSQL URL (postgresql://...)

    Returns:
        Async PostgreSQL URL (postgresql+asyncpg://...)

    Raises:
        DatabaseURLError: If URL is not a valid PostgreSQL URL
    """
    if not validate_database_url(sync_url):
        raise DatabaseURLError(f"Invalid database URL format. Expected: postgresql://user:password@host:port/database")

    # Replace postgresql:// with postgresql+asyncpg://
    if sync_url.startswith("postgresql://"):
        return sync_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Already async, return as-is
    return sync_url


__all__ = [
    "DatabaseURLError",
    "validate_database_url",
    "get_database_url",
    "get_test_database_url",
    "get_dev_database_url",
    "get_prod_database_url",
    "convert_to_async_url",
]
