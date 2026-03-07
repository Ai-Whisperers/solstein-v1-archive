"""Tenant context and isolation utilities.

EPIC-030 Story 2: Strict data isolation between tenants.

Usage:
    from solstein.tenant.context import TenantContext, get_current_tenant

    async with TenantContext(tenant_id):
        # All operations are scoped to this tenant
        companies = await company_repo.get_all()
"""

import hashlib
import secrets
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Optional

from fastapi import Request, HTTPException, status
from loguru import logger

# Context variable for current tenant
current_tenant_var: ContextVar[Optional[str]] = ContextVar("current_tenant", default=None)


class TenantContext:
    """Context manager for tenant isolation.

    Usage:
        async with TenantContext(tenant_id):
            # Database queries automatically filtered by tenant
            companies = await get_companies()
    """

    def __init__(self, tenant_id: str):
        """Initialize tenant context.

        Args:
            tenant_id: Tenant identifier.
        """
        self.tenant_id = tenant_id
        self.token = None

    async def __aenter__(self):
        """Enter tenant context."""
        self.token = current_tenant_var.set(self.tenant_id)
        logger.debug(f"Entered tenant context: {self.tenant_id[:8]}...")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit tenant context."""
        current_tenant_var.reset(self.token)
        logger.debug(f"Exited tenant context: {self.tenant_id[:8]}...")


def get_current_tenant() -> Optional[str]:
    """Get current tenant ID from context.

    Returns:
        Current tenant ID or None.
    """
    return current_tenant_var.get()


def require_tenant() -> str:
    """Get current tenant ID, raising if not set.

    Returns:
        Current tenant ID.

    Raises:
        RuntimeError: If no tenant is set in context.
    """
    tenant_id = get_current_tenant()
    if not tenant_id:
        raise RuntimeError("No tenant context set")
    return tenant_id


class TenantIsolationMiddleware:
    """FastAPI middleware for tenant isolation.

    Extracts tenant from API key or JWT and sets context.
    """

    def __init__(self, app):
        """Initialize middleware.

        Args:
            app: ASGI application.
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process request with tenant context.

        Args:
            scope: ASGI scope.
            receive: ASGI receive.
            send: ASGI send.
        """
        if scope["type"] == "http":
            request = Request(scope, receive)
            tenant_id = await self._extract_tenant_id(request)

            if tenant_id:
                async with TenantContext(tenant_id):
                    await self.app(scope, receive, send)
            else:
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    async def _extract_tenant_id(self, request: Request) -> Optional[str]:
        """Extract tenant ID from request.

        Args:
            request: HTTP request.

        Returns:
            Tenant ID or None.
        """
        # Try API key header first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await self._validate_api_key(api_key)

        # Try JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return await self._validate_jwt(token)

        return None

    async def _validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return tenant ID.

        Args:
            api_key: API key to validate.

        Returns:
            Tenant ID if valid, None otherwise.
        """
        # Hash the API key for lookup
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # In production, query database
        # For now, return a mock tenant ID
        # This should query your tenant repository
        return None

    async def _validate_jwt(self, token: str) -> Optional[str]:
        """Validate JWT and extract tenant ID.

        Args:
            token: JWT token.

        Returns:
            Tenant ID if valid, None otherwise.
        """
        try:
            from solstein.security.jwt import verify_token

            payload = verify_token(token)
            return payload.get("tenant_id")
        except Exception:
            return None


class TenantAwareRepository:
    """Base repository with automatic tenant filtering.

    All queries automatically include tenant_id filter.
    """

    def __init__(self, session, tenant_id: Optional[str] = None):
        """Initialize repository.

        Args:
            session: Database session.
            tenant_id: Optional tenant ID override.
        """
        self.session = session
        self.tenant_id = tenant_id or get_current_tenant()

    def _require_tenant(self) -> str:
        """Require tenant ID for query.

        Returns:
            Tenant ID.

        Raises:
            RuntimeError: If no tenant ID available.
        """
        if not self.tenant_id:
            raise RuntimeError("No tenant ID available for query")
        return self.tenant_id

    def _apply_tenant_filter(self, query):
        """Apply tenant filter to query.

        Args:
            query: SQLAlchemy query.

        Returns:
            Filtered query.
        """
        tenant_id = self._require_tenant()
        # This assumes the model has a tenant_id column
        # Override in subclasses if needed
        return query.filter_by(tenant_id=tenant_id)


def generate_api_key() -> str:
    """Generate a secure API key.

    Returns:
        API key string.
    """
    prefix = "sk_live_"  # or sk_test_ for test keys
    key = secrets.token_urlsafe(32)
    return f"{prefix}{key}"


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage.

    Args:
        api_key: API key to hash.

    Returns:
        Hashed key.
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


class TenantValidator:
    """Validate tenant access and permissions."""

    @staticmethod
    def validate_resource_access(tenant_id: str, resource_tenant_id: str) -> bool:
        """Validate that tenant can access resource.

        Args:
            tenant_id: Requesting tenant ID.
            resource_tenant_id: Resource's tenant ID.

        Returns:
            True if access allowed.

        Raises:
            HTTPException: If access denied.
        """
        if tenant_id != resource_tenant_id:
            logger.warning(f"Cross-tenant access attempt: {tenant_id} -> {resource_tenant_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: resource belongs to different tenant"
            )
        return True

    @staticmethod
    def validate_admin_access(user_role: str) -> bool:
        """Validate admin access.

        Args:
            user_role: User's role.

        Returns:
            True if admin.

        Raises:
            HTTPException: If not admin.
        """
        if user_role not in ["admin", "platform_admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return True
