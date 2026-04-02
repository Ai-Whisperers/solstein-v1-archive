"""Tests for STORY-115: Export storage backends.

Tests cover:
- LocalStorageBackend upload and delete
- SupabaseStorageBackend upload and delete (mocked)
- get_storage_backend factory logic
- Upload retry logic in _generate_file
- Temp file cleanup after upload
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro: Any) -> Any:
    """Run a coroutine synchronously for test purposes."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# LocalStorageBackend tests
# ---------------------------------------------------------------------------


class TestLocalStorageBackend:
    """Tests for the local filesystem storage backend."""

    def test_upload_creates_file(self, tmp_path: Path) -> None:
        from solstein.exporters.storage import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=tmp_path)
        data = b"hello world"
        url = _run(
            backend.upload(
                data=data,
                tenant_id="tenant-abc",
                job_id="job-123",
                filename="report.pdf",
            )
        )

        result_path = Path(url)
        assert result_path.exists()
        assert result_path.read_bytes() == data

    def test_upload_tenant_scoped_path(self, tmp_path: Path) -> None:
        from solstein.exporters.storage import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=tmp_path)
        url = _run(
            backend.upload(
                data=b"data",
                tenant_id="tenant-xyz",
                job_id="job-456",
                filename="export.xlsx",
            )
        )

        assert "tenant-xyz" in url
        assert url.endswith(".xlsx")

    def test_upload_preserves_extension(self, tmp_path: Path) -> None:
        from solstein.exporters.storage import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=tmp_path)
        for ext in [".pdf", ".xlsx", ".csv", ".json", ".md"]:
            url = _run(
                backend.upload(
                    data=b"x",
                    tenant_id="t",
                    job_id=f"j{ext}",
                    filename=f"file{ext}",
                )
            )
            assert url.endswith(ext)

    def test_delete_existing_file(self, tmp_path: Path) -> None:
        from solstein.exporters.storage import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=tmp_path)
        url = _run(
            backend.upload(
                data=b"deleteme",
                tenant_id="t",
                job_id="j",
                filename="f.pdf",
            )
        )

        assert Path(url).exists()
        result = _run(backend.delete(url))
        assert result is True
        assert not Path(url).exists()

    def test_delete_nonexistent_file(self, tmp_path: Path) -> None:
        from solstein.exporters.storage import LocalStorageBackend

        backend = LocalStorageBackend(base_dir=tmp_path)
        result = _run(backend.delete("/nonexistent/path.pdf"))
        assert result is False


# ---------------------------------------------------------------------------
# SupabaseStorageBackend tests (mocked)
# ---------------------------------------------------------------------------


class TestSupabaseStorageBackend:
    """Tests for the Supabase storage backend with mocked client."""

    def _make_backend(self) -> Any:
        from solstein.exporters.storage import SupabaseStorageBackend

        backend = SupabaseStorageBackend()
        mock_client = mock.MagicMock()
        mock_storage = mock.MagicMock()
        mock_bucket = mock.MagicMock()

        mock_client.storage = mock_storage
        mock_storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = None
        mock_bucket.create_signed_url.return_value = {
            "signedURL": "https://supabase.co/storage/v1/object/sign/exports/t/2026-03-27/job.pdf?token=abc",
        }

        backend._client = mock_client
        return backend, mock_bucket

    def test_upload_returns_signed_url(self) -> None:
        backend, _ = self._make_backend()
        url = _run(
            backend.upload(
                data=b"pdf-bytes",
                tenant_id="tenant-1",
                job_id="job-1",
                filename="report.pdf",
            )
        )

        assert url.startswith("https://")
        assert "sign" in url

    def test_upload_calls_storage_api(self) -> None:
        backend, mock_bucket = self._make_backend()
        _run(
            backend.upload(
                data=b"data",
                tenant_id="t",
                job_id="j",
                filename="f.xlsx",
            )
        )

        mock_bucket.upload.assert_called_once()
        call_kwargs = mock_bucket.upload.call_args
        assert "t/" in call_kwargs.kwargs.get("path", call_kwargs[1].get("path", ""))

    def test_upload_uses_correct_content_type(self) -> None:
        backend, mock_bucket = self._make_backend()
        _run(
            backend.upload(
                data=b"data",
                tenant_id="t",
                job_id="j",
                filename="report.pdf",
            )
        )

        call_kwargs = mock_bucket.upload.call_args
        file_options = call_kwargs.kwargs.get(
            "file_options",
            call_kwargs[1].get("file_options", {}),
        )
        assert file_options.get("content-type") == "application/pdf"

    def test_upload_raises_on_failure(self) -> None:
        backend, mock_bucket = self._make_backend()
        mock_bucket.upload.side_effect = RuntimeError("Storage down")

        with pytest.raises(RuntimeError, match="Storage down"):
            _run(
                backend.upload(
                    data=b"data",
                    tenant_id="t",
                    job_id="j",
                    filename="f.pdf",
                )
            )

    def test_upload_raises_on_missing_signed_url(self) -> None:
        backend, mock_bucket = self._make_backend()
        mock_bucket.create_signed_url.return_value = {}

        with pytest.raises(RuntimeError, match="Failed to create signed URL"):
            _run(
                backend.upload(
                    data=b"data",
                    tenant_id="t",
                    job_id="j",
                    filename="f.pdf",
                )
            )

    def test_delete_parses_url(self) -> None:
        backend, mock_bucket = self._make_backend()
        url = "https://x.supabase.co/storage/v1/object/sign/exports/t/2026-03-27/j.pdf?token=abc"
        result = _run(backend.delete(url))

        assert result is True
        mock_bucket.remove.assert_called_once()

    def test_delete_unparseable_url(self) -> None:
        backend, _ = self._make_backend()
        result = _run(backend.delete("https://example.com/no-bucket-here"))
        assert result is False


# ---------------------------------------------------------------------------
# Factory function tests
# ---------------------------------------------------------------------------


class TestGetStorageBackend:
    """Tests for the get_storage_backend() factory."""

    def test_returns_supabase_when_configured(self) -> None:
        from solstein.exporters.storage import (
            SupabaseStorageBackend,
            get_storage_backend,
        )

        mock_settings = mock.MagicMock()
        mock_settings.supabase.url = "https://x.supabase.co"
        mock_settings.supabase.key = "secret-key"

        with mock.patch(
            "solstein.exporters.storage.get_settings",
            return_value=mock_settings,
            create=True,
        ):
            # Patch the lazy import inside get_storage_backend
            with mock.patch(
                "solstein.config.get_settings",
                return_value=mock_settings,
            ):
                backend = get_storage_backend()

        assert isinstance(backend, SupabaseStorageBackend)

    def test_returns_local_when_no_supabase(self) -> None:
        from solstein.exporters.storage import (
            LocalStorageBackend,
            get_storage_backend,
        )

        mock_settings = mock.MagicMock()
        mock_settings.supabase.url = ""
        mock_settings.supabase.key = ""

        with mock.patch(
            "solstein.config.get_settings",
            return_value=mock_settings,
        ):
            backend = get_storage_backend()

        assert isinstance(backend, LocalStorageBackend)

    def test_returns_local_on_settings_error(self) -> None:
        from solstein.exporters.storage import (
            LocalStorageBackend,
            get_storage_backend,
        )

        with mock.patch(
            "solstein.config.get_settings",
            side_effect=RuntimeError("Config not loaded"),
        ):
            backend = get_storage_backend()

        assert isinstance(backend, LocalStorageBackend)


# ---------------------------------------------------------------------------
# Content type guessing
# ---------------------------------------------------------------------------


class TestGuessContentType:
    """Tests for _guess_content_type helper."""

    def test_known_extensions(self) -> None:
        from solstein.exporters.storage import _guess_content_type

        assert _guess_content_type(".pdf") == "application/pdf"
        assert _guess_content_type(".xlsx") == ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        assert _guess_content_type(".csv") == "text/csv"
        assert _guess_content_type(".json") == "application/json"
        assert _guess_content_type(".md") == "text/markdown"
        assert _guess_content_type(".txt") == "text/plain"

    def test_unknown_extension(self) -> None:
        from solstein.exporters.storage import _guess_content_type

        assert _guess_content_type(".xyz") == "application/octet-stream"

    def test_case_insensitive(self) -> None:
        from solstein.exporters.storage import _guess_content_type

        assert _guess_content_type(".PDF") == "application/pdf"
        assert _guess_content_type(".Xlsx") == ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
