"""X-API-Key tenant middleware for multi-tenancy support.

Each inbound request must carry an ``X-API-Key`` header whose SHA-256 hash
matches an *active* TenantRecord in the database.  On success the tenant
info is attached to ``request.state.tenant`` for downstream use.

Public endpoints (``/docs``, ``/openapi.json``, ``/healthz``, ``/metrics``)
bypass the key check so infrastructure tooling keeps working.

Usage::

    # In main.py
    from solstein.api.middleware.tenant import TenantMiddleware
    app.add_middleware(TenantMiddleware)
"""

from __future__ import annotations

import hashlib
from typing import Any, Awaitable, Callable

from fastapi import status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Endpoints that do not require a tenant API key
_PUBLIC_PATHS: frozenset[str] = frozenset(
    {
        "/docs",
        "/openapi.json",
        "/redoc",
        "/healthz",
        "/health",
        "/metrics",
        "/favicon.ico",
    }
)


class TenantMiddleware(BaseHTTPMiddleware):
    """Validate ``X-API-Key`` and attach tenant to ``request.state.tenant``.

    Multi-tenancy is enforced at the middleware layer so no route handler
    needs to repeat the lookup.  When ``REQUIRE_API_KEY`` is ``False`` in
    settings, the middleware logs a warning and skips enforcement (useful
    in local development where no tenants exist yet).
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Always allow public paths
        if request.url.path in _PUBLIC_PATHS or request.url.path.startswith("/docs"):
            return await call_next(request)

        # Allow disabling enforcement in dev via settings
        try:
            from solstein.config import get_settings

            settings = get_settings()
            require_api_key = getattr(
                settings.api,
                "require_api_key",
                getattr(settings, "require_api_key", True),
            )
            if not require_api_key:
                return await call_next(request)
        except Exception:  # pragma: no cover
            pass

        api_key = request.headers.get("X-API-Key", "").strip()
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "missing_api_key",
                    "detail": "X-API-Key header is required.",
                },
            )

        # Hash the key and look it up in DB
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        try:
            tenant = await _lookup_tenant(key_hash, request)
        except SQLAlchemyError as e:
            # Database errors should be visible and cause 500
            logger.exception(
                "Database error looking up tenant",
                api_key_prefix=api_key[:8],
                error_type=type(e).__name__,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_error",
                    "detail": "Failed to validate API key. Please try again.",
                },
            )
        except Exception as e:
            # Unexpected errors - log and return 500
            logger.exception(
                "Unexpected error looking up tenant",
                api_key_prefix=api_key[:8],
                error_type=type(e).__name__,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_error",
                    "detail": "Failed to validate API key. Please try again.",
                },
            )

        if tenant is None:
            logger.warning("Invalid or inactive API key used", key_prefix=api_key[:8])
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "invalid_api_key",
                    "detail": "API key not found or tenant is inactive.",
                },
            )

        # Store tenant info and ID in request state
        request.state.tenant = tenant
        request.state.tenant_id = tenant.get("id")
        logger.debug("Tenant authenticated", tenant_name=tenant.get("name"), path=request.url.path)
        return await call_next(request)


async def _lookup_tenant(key_hash: str, request: Request) -> dict[str, Any] | None:
    """Fetch tenant from DB by API key hash.

    Returns a plain dict with tenant info or ``None`` if not found / inactive.
    Uses the database session from ``request.state.db`` if available, otherwise
    falls back to a fresh session from the application's async engine.

    Raises:
        SQLAlchemyError: If database operation fails (caller should handle)
        Exception: For unexpected errors (caller should handle)
    """
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.database_models import TenantRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(TenantRecord).where(
                TenantRecord.api_key_hash == key_hash,
                TenantRecord.is_active.is_(True),
            )
        )
        tenant_record: TenantRecord | None = result.scalar_one_or_none()
        if tenant_record is None:
            return None
        return tenant_record.to_dict()
