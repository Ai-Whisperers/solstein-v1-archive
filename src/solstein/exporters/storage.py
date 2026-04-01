"""Export file storage backends.

STORY-115: Abstracts export file storage so the pipeline writes to
Supabase Storage (signed URLs, tenant-scoped) instead of local disk.
Falls back to local storage when Supabase is unavailable.

Bucket layout: ``exports/{tenant_id}/{date}/{job_id}.{ext}``

Usage::

    from solstein.exporters.storage import get_storage_backend

    backend = get_storage_backend()
    url = await backend.upload(
        data=pdf_bytes,
        tenant_id="abc",
        job_id="xyz",
        filename="report.pdf",
    )
"""

from __future__ import annotations

import io
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

# Supabase signed URL expiry in seconds (7 days)
_SIGNED_URL_EXPIRY_SECONDS = 7 * 24 * 60 * 60

# Storage bucket name
EXPORTS_BUCKET = "exports"


class ExportStorageBackend(ABC):
    """Abstract base class for export file storage."""

    @abstractmethod
    async def upload(
        self,
        data: bytes,
        tenant_id: str,
        job_id: str,
        filename: str,
    ) -> str:
        """Upload export data and return a download URL.

        Args:
            data: File content as bytes.
            tenant_id: Tenant that owns this export.
            job_id: Export job UUID.
            filename: Original filename (e.g., ``export_all_20260327.pdf``).

        Returns:
            URL string (signed URL for Supabase, file path for local).
        """

    @abstractmethod
    async def delete(self, file_url: str) -> bool:
        """Delete a previously uploaded file. Returns True on success."""


class SupabaseStorageBackend(ExportStorageBackend):
    """Stores export files in Supabase Storage with signed URLs.

    Bucket layout: ``exports/{tenant_id}/{date}/{job_id}.{ext}``
    Signed URLs expire after 7 days (matching EXPORT_EXPIRY_DAYS).
    """

    def __init__(self) -> None:
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazy-load the Supabase client."""
        if self._client is None:
            from solstein.core.supabase_client import get_supabase

            self._client = get_supabase()
        return self._client

    async def upload(
        self,
        data: bytes,
        tenant_id: str,
        job_id: str,
        filename: str,
    ) -> str:
        """Upload to Supabase Storage and return a signed URL."""
        client = self._get_client()
        date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        ext = Path(filename).suffix
        object_path = f"{tenant_id}/{date_prefix}/{job_id}{ext}"

        logger.info(
            "[ExportStorage] Uploading to Supabase: bucket=%s path=%s size=%d",
            EXPORTS_BUCKET,
            object_path,
            len(data),
        )

        # Upload the file
        file_obj = io.BytesIO(data)
        content_type = _guess_content_type(ext)

        try:
            client.storage.from_(EXPORTS_BUCKET).upload(
                path=object_path,
                file=file_obj,
                file_options={"content-type": content_type},
            )
        except Exception as exc:
            logger.error(
                "[ExportStorage] Upload failed: %s", exc,
            )
            raise

        # Create signed URL
        try:
            result = client.storage.from_(EXPORTS_BUCKET).create_signed_url(
                path=object_path,
                expires_in=_SIGNED_URL_EXPIRY_SECONDS,
            )
            signed_url = result.get("signedURL") or result.get("signed_url", "")
            if not signed_url:
                logger.error("[ExportStorage] No signed URL in response: %s", result)
                raise RuntimeError("Failed to create signed URL")

            logger.info(
                "[ExportStorage] Upload complete: path=%s url_length=%d",
                object_path,
                len(signed_url),
            )
            return signed_url
        except Exception as exc:
            logger.error("[ExportStorage] Signed URL creation failed: %s", exc)
            raise

    async def delete(self, file_url: str) -> bool:
        """Delete a file from Supabase Storage by URL."""
        try:
            client = self._get_client()
            # Extract object path from URL — the path follows the bucket name
            # URL format: .../storage/v1/object/sign/exports/{tenant}/{date}/{job}.ext?...
            parts = file_url.split(f"/{EXPORTS_BUCKET}/")
            if len(parts) < 2:
                logger.warning("[ExportStorage] Cannot parse path from URL: %s", file_url[:80])
                return False
            object_path = parts[1].split("?")[0]
            client.storage.from_(EXPORTS_BUCKET).remove([object_path])
            return True
        except Exception as exc:
            logger.error("[ExportStorage] Delete failed: %s", exc)
            return False


class LocalStorageBackend(ExportStorageBackend):
    """Stores export files on the local filesystem.

    Used as fallback when Supabase is unavailable, or for development.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir

    def _get_base_dir(self) -> Path:
        """Get the export directory from config or default."""
        if self._base_dir is not None:
            return self._base_dir
        from solstein.config import get_settings

        return get_settings().data.export_dir

    async def upload(
        self,
        data: bytes,
        tenant_id: str,
        job_id: str,
        filename: str,
    ) -> str:
        """Write to local filesystem and return the file path."""
        base = self._get_base_dir()
        date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        ext = Path(filename).suffix
        output_dir = base / tenant_id / date_prefix
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{job_id}{ext}"

        output_path.write_bytes(data)

        logger.info(
            "[ExportStorage] Local write: path=%s size=%d",
            output_path,
            len(data),
        )
        return str(output_path.resolve())

    async def delete(self, file_url: str) -> bool:
        """Delete a local file."""
        try:
            path = Path(file_url)
            if path.exists():
                path.unlink()
                return True
            return False
        except (OSError, TypeError) as exc:
            logger.error("[ExportStorage] Local delete failed: %s", exc)
            return False


def get_storage_backend() -> ExportStorageBackend:
    """Factory: return Supabase backend if configured, else local.

    Checks whether Supabase credentials are available. If so,
    returns SupabaseStorageBackend. Otherwise, falls back to
    LocalStorageBackend with a warning.
    """
    try:
        from solstein.config import get_settings

        settings = get_settings()
        if settings.supabase.url and settings.supabase.key:
            return SupabaseStorageBackend()
    except Exception as exc:
        logger.warning("[ExportStorage] Supabase check failed: %s", exc)

    logger.warning(
        "[ExportStorage] Supabase not configured — using local storage. "
        "Exports will be lost on container restart.",
    )
    return LocalStorageBackend()


def _guess_content_type(ext: str) -> str:
    """Map file extension to MIME content type."""
    mapping = {
        ".pdf": "application/pdf",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".csv": "text/csv",
        ".json": "application/json",
        ".md": "text/markdown",
        ".txt": "text/plain",
    }
    return mapping.get(ext.lower(), "application/octet-stream")
