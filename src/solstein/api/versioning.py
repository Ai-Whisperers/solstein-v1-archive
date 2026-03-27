"""API versioning configuration for EPIC-024 Story 3.

Supports /api/v1/, /api/v2/ URL patterns with deprecation headers.
"""

from __future__ import annotations

from enum import Enum

from fastapi import FastAPI
from loguru import logger


class APIVersion(str, Enum):
    """Supported API versions."""

    V1 = "v1"
    V2 = "v2"  # Future version


CURRENT_VERSION = APIVersion.V1
SUPPORTED_VERSIONS = [APIVersion.V1]
DEPRECATED_VERSIONS: list[APIVersion] = []


class VersionHeaderMiddleware:
    """Add API version headers to all responses."""

    def __init__(self, app: FastAPI, version: APIVersion = CURRENT_VERSION):
        self.app = app
        self.version = version

    async def __call__(self, scope, receive, send):
        """Add version headers."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Wrap send to add headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                # Add API version header
                headers.append((b"x-api-version", self.version.value.encode()))
                # Add deprecation warning if needed
                if self.version in DEPRECATED_VERSIONS:
                    headers.append((b"deprecation", b"true"))
                    headers.append((b"sunset", b"2026-12-31"))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


def setup_api_versioning(app: FastAPI) -> None:
    """Configure API versioning on FastAPI app."""
    # Add middleware for version headers
    app.add_middleware(VersionHeaderMiddleware, version=CURRENT_VERSION)

    # Add version info to OpenAPI
    app.openapi_schema = None  # Force regeneration

    logger.info(f"API versioning configured: {CURRENT_VERSION.value}")


# Version prefix for routers
def get_version_prefix(version: APIVersion = CURRENT_VERSION) -> str:
    """Get URL prefix for API version."""
    return f"/api/{version.value}"


__all__ = [
    "APIVersion",
    "CURRENT_VERSION",
    "SUPPORTED_VERSIONS",
    "DEPRECATED_VERSIONS",
    "VersionHeaderMiddleware",
    "setup_api_versioning",
    "get_version_prefix",
]
