"""Data access audit middleware.

STORY-086: Enforce universal audit trail across all data access endpoints.

Every authenticated request to a data-returning endpoint generates an
append-only audit record containing tenant_id, user_id, endpoint,
resource_id (if applicable), timestamp, and response status.

Security note: This middleware is designed so that audit logging failures
never fail the original request (REQ-5). If the audit write fails, the
failure is logged separately and the request proceeds normally.

Endpoints excluded from auditing:
- Health/readiness probes
- Metrics/docs endpoints
- Authentication endpoints (no user identity yet)
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Paths excluded from audit logging (no meaningful user identity)
_EXCLUDED_PREFIXES: tuple[str, ...] = (
    "/health",
    "/healthz",
    "/ready",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/favicon.ico",
    "/auth",
    "/admin/profiling",
)

# Pattern to extract resource IDs from common URL shapes
# e.g. /api/v1/companies/abc-123 -> abc-123
_RESOURCE_ID_PATTERN = re.compile(
    r"/(?:companies|research|jobs|enrichment|scoring)/([a-zA-Z0-9_-]+)(?:/|$)"
)


def _extract_resource_id(path: str) -> str | None:
    """Extract resource ID from request path if present."""
    match = _RESOURCE_ID_PATTERN.search(path)
    return match.group(1) if match else None


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP, respecting X-Forwarded-For behind proxies."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _is_excluded(path: str) -> bool:
    """Check if path should be excluded from auditing."""
    return any(path.startswith(prefix) for prefix in _EXCLUDED_PREFIXES)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that writes data access audit records.

    Fires after the response is generated so that the status code is
    available. Audit writes happen in-band but failures are swallowed
    to satisfy REQ-5 (audit failure must not fail the request).
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process request and write audit record for authenticated requests."""
        path = request.url.path

        # Skip excluded paths
        if _is_excluded(path):
            return await call_next(request)

        # Process the request first
        response = await call_next(request)

        # Only audit authenticated requests (tenant or user present)
        tenant_id = getattr(request.state, "tenant_id", None)
        user_id = _extract_user_id(request)

        if tenant_id is None and user_id is None:
            # Unauthenticated request — nothing to audit
            return response

        # Write audit record (fire-and-forget style, never fail the request)
        try:
            entry = AuditEntry(
                tenant_id=str(tenant_id) if tenant_id else None,
                user_id=str(user_id) if user_id else None,
                method=request.method,
                endpoint=path,
                resource_id=_extract_resource_id(path),
                status_code=response.status_code,
                client_ip=_get_client_ip(request),
                user_agent=request.headers.get("User-Agent"),
            )
            await _write_audit_record(entry)
        except (ConnectionError, OSError, RuntimeError, ValueError) as exc:
            # REQ-5: Audit failure must not fail the original request
            logger.error(
                "Audit trail write failed",
                error=str(exc),
                endpoint=path,
                tenant_id=str(tenant_id) if tenant_id else None,
            )

        return response


def _extract_user_id(request: Request) -> str | None:
    """Extract user ID from request state (set by auth middleware)."""
    user = getattr(request.state, "user", None)
    if user is None:
        return None
    # Support dict-style and object-style user representations
    if isinstance(user, dict):
        return user.get("id") or user.get("sub")
    return getattr(user, "id", None) or getattr(user, "sub", None)


@dataclass(frozen=True)
class AuditEntry:
    """Parameter object for audit record data."""

    tenant_id: str | None
    user_id: str | None
    method: str
    endpoint: str
    resource_id: str | None
    status_code: int
    client_ip: str | None = None
    user_agent: str | None = None


async def _write_audit_record(entry: AuditEntry) -> None:
    """Write an audit record to the database.

    Uses a short-lived session to avoid holding connections. Failures
    are raised to the caller (the middleware catches them).
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.audit import DataAccessAuditRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        record = DataAccessAuditRecord(
            tenant_id=entry.tenant_id,
            user_id=entry.user_id,
            method=entry.method,
            endpoint=entry.endpoint,
            resource_id=entry.resource_id,
            timestamp=datetime.now(timezone.utc),
            status_code=entry.status_code,
            client_ip=entry.client_ip,
            user_agent=entry.user_agent,
        )
        session.add(record)
        await session.commit()
