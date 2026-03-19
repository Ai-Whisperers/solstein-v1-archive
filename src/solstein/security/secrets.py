"""Secrets management with HashiCorp Vault integration.

EPIC-027 Story 2: Enterprise secrets management with automatic rotation.

Usage:
    from solstein.security.secrets import get_secret, SecretsManager

    # Get secret from Vault
    api_key = await get_secret("llm/openai/api_key")

    # Initialize manager
    secrets = SecretsManager()
    db_password = await secrets.get("database/password")
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from loguru import logger


class SecretBackend(Protocol):
    """Protocol for secret storage backends."""

    async def get(self, path: str) -> str | None:
        """Get secret at path."""
        ...

    async def put(self, path: str, value: str) -> bool:
        """Store secret at path."""
        ...

    async def delete(self, path: str) -> bool:
        """Delete secret at path."""
        ...


class EnvironmentBackend:
    """Fallback environment variable backend."""

    def __init__(self, prefix: str = "SOLSTEIN_"):
        """Initialize with prefix.

        Args:
            prefix: Environment variable prefix.
        """
        self.prefix = prefix

    def _env_name(self, path: str) -> str:
        """Convert path to env var name."""
        return f"{self.prefix}{path.upper().replace('/', '_')}"

    async def get(self, path: str) -> str | None:
        """Get from environment."""
        return os.getenv(self._env_name(path))

    async def put(self, path: str, value: str) -> bool:
        """Cannot write to env vars."""
        logger.warning(f"Cannot write secret {path} to environment")
        return False

    async def delete(self, path: str) -> bool:
        """Cannot delete env vars."""
        return False


class VaultBackend:
    """HashiCorp Vault backend."""

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        mount_point: str = "secret",
    ):
        """Initialize Vault client.

        Args:
            url: Vault URL.
            token: Vault token.
            mount_point: KV mount point.
        """
        self.url = url or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self._client = None

    def _get_client(self):
        """Get or create Vault client."""
        if self._client is None:
            try:
                import hvac

                self._client = hvac.Client(url=self.url, token=self.token)
            except ImportError:
                logger.error("hvac library not installed. Run: pip install hvac")
                raise
        return self._client

    async def get(self, path: str) -> str | None:
        """Get secret from Vault.

        Args:
            path: Secret path.

        Returns:
            Secret value or None.
        """
        try:
            client = self._get_client()
            response = client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point,
            )
            return response["data"]["data"].get("value")
        except Exception as e:
            logger.error(f"Failed to get secret {path}: {e}")
            return None

    async def put(self, path: str, value: str) -> bool:
        """Store secret in Vault.

        Args:
            path: Secret path.
            value: Secret value.

        Returns:
            True if successful.
        """
        try:
            client = self._get_client()
            client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={"value": value},
                mount_point=self.mount_point,
            )
            logger.info(f"Secret stored: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            return False

    async def delete(self, path: str) -> bool:
        """Delete secret from Vault.

        Args:
            path: Secret path.

        Returns:
            True if successful.
        """
        try:
            client = self._get_client()
            client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.mount_point,
            )
            logger.info(f"Secret deleted: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret {path}: {e}")
            return False


@dataclass
class SecretMetadata:
    """Metadata for a secret."""

    path: str
    created_at: datetime
    expires_at: datetime | None
    last_rotated: datetime
    rotation_interval_days: int
    tags: dict[str, str]


class SecretsManager:
    """Manage secrets with automatic rotation."""

    def __init__(self, backend: SecretBackend | None = None):
        """Initialize secrets manager.

        Args:
            backend: Secret storage backend.
        """
        # Try Vault, fall back to environment
        try:
            self.backend = backend or VaultBackend()
        except Exception:
            logger.warning("Vault not available, using environment backend")
            self.backend = EnvironmentBackend()

        self._cache: dict[str, tuple[str, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)

    async def get(self, path: str, use_cache: bool = True) -> str | None:
        """Get secret with caching.

        Args:
            path: Secret path.
            use_cache: Whether to use cache.

        Returns:
            Secret value or None.
        """
        # Check cache
        if use_cache and path in self._cache:
            value, cached_at = self._cache[path]
            if datetime.now(timezone.utc) - cached_at < self._cache_ttl:
                return value

        # Fetch from backend
        value = await self.backend.get(path)

        if value and use_cache:
            self._cache[path] = (value, datetime.now(timezone.utc))

        return value

    async def put(self, path: str, value: str) -> bool:
        """Store secret.

        Args:
            path: Secret path.
            value: Secret value.

        Returns:
            True if successful.
        """
        success = await self.backend.put(path, value)
        if success:
            # Update cache
            self._cache[path] = (value, datetime.now(timezone.utc))
        return success

    async def rotate(self, path: str, generator: callable) -> bool:
        """Rotate a secret.

        Args:
            path: Secret path.
            generator: Function to generate new secret.

        Returns:
            True if successful.
        """
        try:
            new_value = generator()
            success = await self.put(path, new_value)
            if success:
                logger.info(f"Secret rotated: {path}")
            return success
        except Exception as e:
            logger.error(f"Failed to rotate secret {path}: {e}")
            return False

    def clear_cache(self):
        """Clear secret cache."""
        self._cache.clear()


# Global secrets manager instance
_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    """Get global secrets manager instance.

    Returns:
        SecretsManager instance.
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


async def get_secret(path: str, default: str | None = None) -> str | None:
    """Get secret at path.

    Args:
        path: Secret path.
        default: Default value if not found.

    Returns:
        Secret value or default.
    """
    manager = get_secrets_manager()
    value = await manager.get(path)
    return value if value is not None else default


async def get_database_credentials() -> dict[str, str]:
    """Get database credentials.

    Returns:
        Dictionary with host, port, user, password, database.
    """
    return {
        "host": await get_secret("database/host", "localhost"),
        "port": await get_secret("database/port", "5432"),
        "user": await get_secret("database/user", "solstein"),
        "password": await get_secret("database/password", ""),
        "database": await get_secret("database/name", "solstein"),
    }


async def get_llm_api_key(provider: str) -> str | None:
    """Get LLM provider API key.

    Args:
        provider: Provider name (openai, anthropic, etc.).

    Returns:
        API key or None.
    """
    return await get_secret(f"llm/{provider}/api_key")


class SecretRotationScheduler:
    """Schedule automatic secret rotation."""

    ROTATION_INTERVALS = {
        "llm/openai/api_key": 30,  # Monthly
        "llm/anthropic/api_key": 30,
        "database/password": 90,  # Quarterly
        "jwt/secret": 90,
    }

    def __init__(self, manager: SecretsManager | None = None):
        """Initialize scheduler.

        Args:
            manager: Secrets manager.
        """
        self.manager = manager or get_secrets_manager()

    async def check_and_rotate(self):
        """Check all secrets and rotate if needed."""
        for path, interval_days in self.ROTATION_INTERVALS.items():
            # Check if rotation needed (simplified)
            # In production, track last rotation timestamp
            logger.debug(f"Checking rotation for {path} (every {interval_days} days)")

    async def rotate_llm_keys(self):
        """Rotate all LLM API keys."""
        providers = ["openai", "anthropic", "groq", "gemini"]
        for provider in providers:
            path = f"llm/{provider}/api_key"
            logger.info(f"Scheduling rotation for {provider}")
            # Actual rotation would call provider APIs
