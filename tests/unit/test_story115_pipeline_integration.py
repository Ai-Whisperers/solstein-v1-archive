"""Tests for STORY-115: Pipeline integration with storage backend.

Tests cover:
- _generate_file uses storage backend for upload
- Upload retry logic (3 attempts)
- Temp file cleanup after upload
- _build_filename for all formats
- _dispatch_exporter routing
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
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# _build_filename tests
# ---------------------------------------------------------------------------


class TestBuildFilename:
    """Tests for the filename builder."""

    def test_excel_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("excel", "all", "20260327_120000")
        assert result == "export_all_20260327_120000.xlsx"

    def test_csv_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("csv", "tech", "20260327_120000")
        assert result == "export_tech_20260327_120000.csv"

    def test_json_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("json", "all", "20260327_120000")
        assert result == "export_all_20260327_120000.json"

    def test_markdown_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("markdown", "all", "20260327_120000")
        assert result == "export_all_20260327_120000.md"

    def test_pdf_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("pdf", "all", "20260327_120000")
        assert result == "export_all_20260327_120000.pdf"

    def test_llm_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("llm", "all", "20260327_120000")
        assert result == "export_llm_all_20260327_120000.md"

    def test_llm_enhanced_format(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        result = _build_filename("llm_enhanced", "all", "20260327_120000")
        assert result == "export_llm_all_20260327_120000.md"

    def test_unsupported_format_raises(self) -> None:
        from solstein.worker.export_tasks import _build_filename

        with pytest.raises(ValueError, match="Unsupported"):
            _build_filename("invalid", "all", "20260327_120000")


# ---------------------------------------------------------------------------
# _generate_file integration tests (mocked exporters + storage)
# ---------------------------------------------------------------------------


class TestGenerateFileWithStorage:
    """Tests for _generate_file with storage backend integration."""

    def _patch_exporter_and_storage(
        self,
        storage_url: str = "https://storage.example.com/signed-url",
    ) -> tuple[mock.AsyncMock, mock.AsyncMock]:
        """Create mocks for exporter and storage backend."""
        mock_backend = mock.AsyncMock()
        mock_backend.upload.return_value = storage_url

        mock_dispatch = mock.AsyncMock()

        return mock_dispatch, mock_backend

    def test_upload_called_with_file_bytes(self, tmp_path: Path) -> None:
        from solstein.worker.export_tasks import _generate_file

        mock_dispatch, mock_backend = self._patch_exporter_and_storage()
        file_content = b"csv,data,here"

        # Make the dispatch actually write a file
        async def fake_dispatch(fmt: str, path: Path, filters: Any, cb: Any) -> None:
            path.write_bytes(file_content)

        mock_dispatch.side_effect = fake_dispatch

        with (
            mock.patch(
                "solstein.worker.export_tasks._dispatch_exporter",
                mock_dispatch,
            ),
            mock.patch(
                "solstein.worker.export_tasks.get_storage_backend",
                return_value=mock_backend,
                create=True,
            ),
            mock.patch(
                "solstein.exporters.storage.get_storage_backend",
                return_value=mock_backend,
            ),
        ):
            url = _run(
                _generate_file(
                    tenant_id="t1",
                    export_job_id="j1",
                    export_format="csv",
                    filters={},
                )
            )

        assert url == "https://storage.example.com/signed-url"
        mock_backend.upload.assert_called_once()
        call_kwargs = mock_backend.upload.call_args.kwargs
        assert call_kwargs["data"] == file_content
        assert call_kwargs["tenant_id"] == "t1"
        assert call_kwargs["job_id"] == "j1"

    def test_retries_upload_on_failure(self) -> None:
        from solstein.worker.export_tasks import _generate_file

        mock_dispatch = mock.AsyncMock()

        async def fake_dispatch(fmt: str, path: Path, filters: Any, cb: Any) -> None:
            path.write_bytes(b"data")

        mock_dispatch.side_effect = fake_dispatch

        mock_backend = mock.AsyncMock()
        # Fail twice, succeed on third
        mock_backend.upload.side_effect = [
            RuntimeError("fail 1"),
            RuntimeError("fail 2"),
            "https://ok.com/url",
        ]

        with (
            mock.patch(
                "solstein.worker.export_tasks._dispatch_exporter",
                mock_dispatch,
            ),
            mock.patch(
                "solstein.exporters.storage.get_storage_backend",
                return_value=mock_backend,
            ),
        ):
            url = _run(
                _generate_file(
                    tenant_id="t",
                    export_job_id="j",
                    export_format="json",
                    filters={},
                )
            )

        assert url == "https://ok.com/url"
        assert mock_backend.upload.call_count == 3

    def test_raises_after_3_failed_uploads(self) -> None:
        from solstein.worker.export_tasks import _generate_file

        mock_dispatch = mock.AsyncMock()

        async def fake_dispatch(fmt: str, path: Path, filters: Any, cb: Any) -> None:
            path.write_bytes(b"data")

        mock_dispatch.side_effect = fake_dispatch

        mock_backend = mock.AsyncMock()
        mock_backend.upload.side_effect = RuntimeError("storage down")

        with (
            mock.patch(
                "solstein.worker.export_tasks._dispatch_exporter",
                mock_dispatch,
            ),
            mock.patch(
                "solstein.exporters.storage.get_storage_backend",
                return_value=mock_backend,
            ),
        ):
            with pytest.raises(RuntimeError, match="3 attempts"):
                _run(
                    _generate_file(
                        tenant_id="t",
                        export_job_id="j",
                        export_format="csv",
                        filters={},
                    )
                )

        assert mock_backend.upload.call_count == 3

    def test_raises_when_exporter_produces_no_file(self) -> None:
        from solstein.worker.export_tasks import _generate_file

        # Dispatch that writes nothing
        mock_dispatch = mock.AsyncMock()

        with mock.patch(
            "solstein.worker.export_tasks._dispatch_exporter",
            mock_dispatch,
        ):
            with pytest.raises(RuntimeError, match="did not produce"):
                _run(
                    _generate_file(
                        tenant_id="t",
                        export_job_id="j",
                        export_format="csv",
                        filters={},
                    )
                )

    def test_temp_directory_cleaned_up(self) -> None:
        """Verify temp files are cleaned up after upload."""
        from solstein.worker.export_tasks import _generate_file

        captured_paths: list[Path] = []

        async def capturing_dispatch(
            fmt: str,
            path: Path,
            filters: Any,
            cb: Any,
        ) -> None:
            captured_paths.append(path)
            path.write_bytes(b"temp-data")

        mock_backend = mock.AsyncMock()
        mock_backend.upload.return_value = "https://ok.com/url"

        with (
            mock.patch(
                "solstein.worker.export_tasks._dispatch_exporter",
                capturing_dispatch,
            ),
            mock.patch(
                "solstein.exporters.storage.get_storage_backend",
                return_value=mock_backend,
            ),
        ):
            _run(
                _generate_file(
                    tenant_id="t",
                    export_job_id="j",
                    export_format="csv",
                    filters={},
                )
            )

        # Temp directory should be cleaned up
        assert len(captured_paths) == 1
        assert not captured_paths[0].exists()
        assert not captured_paths[0].parent.exists()
