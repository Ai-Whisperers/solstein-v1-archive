"""Golden contract run tests for Patents provider adapter.

STORY-267 / EPIC-070: Patents covers multi-backend search surface
(USPTO/Google/DDG), cascade fallback with variable confidence,
degradation semantics.
"""

from __future__ import annotations

import re
from typing import Any
from unittest.mock import patch

import pytest

from solstein.adapters.enrichment.patents import PatentEnrichment
from solstein.data.patent_client import PatentResult
from solstein.domain.models import RawDataSource

from .artifact_differ import ArtifactDiffer
from .conftest import ARTIFACTS_DIR, load_artifact


def _raw_data_source_to_dict(rds: RawDataSource) -> dict[str, Any]:
    """Convert a RawDataSource to a flat dict for contract comparison."""
    data = rds.model_dump(mode="json")
    if hasattr(rds.source_type, "name"):
        data["source_type"] = rds.source_type.name
    elif hasattr(rds.source_type, "value"):
        data["source_type"] = rds.source_type.value
    return data


def _make_patent_result(
    source: str = "uspto_peds",
    total: int = 42,
    recent: int = 5,
    ai: int = 3,
) -> PatentResult:
    """Create a PatentResult fixture."""
    return PatentResult(
        total_patents=total,
        recent_patents=[{"title": f"Patent {i}"} for i in range(recent)],
        ai_related_patents=ai,
        top_categories=["AI", "ML", "Cloud"],
        source=source,
    )


# ---------------------------------------------------------------------------
# Patents: Success Contract
# ---------------------------------------------------------------------------


class TestPatentsSuccessContract:
    """Verify Patents adapter output matches golden success contract."""

    @pytest.fixture()
    def contract(self) -> dict[str, Any]:
        return load_artifact("patents_success")

    @pytest.fixture()
    def adapter(self) -> PatentEnrichment:
        return PatentEnrichment()

    def test_success_output_shape_uspto(self, adapter: PatentEnrichment, contract: dict[str, Any]) -> None:
        """USPTO success path matches golden contract shape."""
        mock_result = _make_patent_result(source="uspto_peds")
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p01", company_name="Google LLC")

        actual = _raw_data_source_to_dict(result)
        differ = ArtifactDiffer(ARTIFACTS_DIR)
        report = differ.compare_success("patents", actual, contract)
        differ.store_actual("patents", "success_uspto", actual)

        assert report.passed, report.summary()
        assert report.checked_fields >= 8

    def test_success_output_shape_fallback(self, adapter: PatentEnrichment, contract: dict[str, Any]) -> None:
        """Fallback (Google Patents) success path matches golden contract."""
        mock_result = _make_patent_result(source="google_patents", total=10, ai=1)
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p02", company_name="Small Corp")

        actual = _raw_data_source_to_dict(result)
        differ = ArtifactDiffer(ARTIFACTS_DIR)
        report = differ.compare_success("patents", actual, contract)
        assert report.passed, report.summary()

    def test_raw_content_required_keys(self, adapter: PatentEnrichment) -> None:
        """raw_content must contain all contract-required keys."""
        mock_result = _make_patent_result()
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p03", company_name="Test Corp")

        content = result.raw_content
        assert isinstance(content, dict)
        required = ["total_patents", "recent_patents", "ai_related_patents", "top_categories", "source_backend"]
        for key in required:
            assert key in content, f"Missing required key: {key}"

    def test_metadata_required_keys(self, adapter: PatentEnrichment) -> None:
        """metadata must contain backend, total_patents, ai_related_patents."""
        mock_result = _make_patent_result()
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p04", company_name="Test Corp")

        assert "backend" in result.metadata
        assert "total_patents" in result.metadata
        assert "ai_related_patents" in result.metadata

    def test_url_is_none(self, adapter: PatentEnrichment) -> None:
        """Patents adapter must return url=None per contract."""
        mock_result = _make_patent_result()
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p05", company_name="Test Corp")

        assert result.url is None

    def test_patent_counts_are_non_negative(self, adapter: PatentEnrichment) -> None:
        """All patent counts in raw_content must be >= 0."""
        mock_result = _make_patent_result()
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p06", company_name="Test Corp")

        content = result.raw_content
        assert isinstance(content, dict)
        assert content["total_patents"] >= 0
        assert content["ai_related_patents"] >= 0

    def test_extraction_method_includes_backend(self, adapter: PatentEnrichment) -> None:
        """extraction_method must match patent_client_{backend}."""
        mock_result = _make_patent_result(source="duckduckgo")
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=mock_result,
        ):
            result = adapter.enrich(company_id="p07", company_name="Test Corp")

        assert result.extraction_method is not None
        assert re.match(r"patent_client_.+", result.extraction_method)
        assert "duckduckgo" in result.extraction_method


# ---------------------------------------------------------------------------
# Patents: Degraded / Failure Contract
# ---------------------------------------------------------------------------


class TestPatentsDegradedContract:
    """Verify Patents adapter degradation semantics."""

    @pytest.fixture()
    def adapter(self) -> PatentEnrichment:
        return PatentEnrichment()

    def test_confidence_drops_on_fallback(self, adapter: PatentEnrichment) -> None:
        """Confidence must drop from 0.7 (USPTO) to 0.4 on fallback."""
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=PatentResult(total_patents=10, source="uspto_peds", top_categories=["AI"]),
        ):
            uspto = adapter.enrich(company_id="t1", company_name="Corp")

        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=PatentResult(total_patents=5, source="google_patents", top_categories=["ML"]),
        ):
            google = adapter.enrich(company_id="t2", company_name="Corp")

        assert uspto.confidence == 0.7
        assert google.confidence == 0.4

    def test_backend_identity_preserved_in_metadata(self, adapter: PatentEnrichment) -> None:
        """metadata.backend must match raw_content.source_backend."""
        for backend in ["uspto_peds", "google_patents", "duckduckgo"]:
            result = PatentResult(total_patents=1, source=backend, top_categories=[])
            with patch(
                "solstein.data.patent_client.search_company_patents",
                return_value=result,
            ):
                output = adapter.enrich(company_id="t3", company_name="Corp")

            assert isinstance(output.raw_content, dict)
            assert output.metadata["backend"] == output.raw_content["source_backend"]

    def test_zero_patents_is_valid_result(self, adapter: PatentEnrichment) -> None:
        """Zero patents is a valid result, not an error."""
        with patch(
            "solstein.data.patent_client.search_company_patents",
            return_value=PatentResult(total_patents=0, source="none", top_categories=[]),
        ):
            output = adapter.enrich(company_id="t4", company_name="NoPatents LLC")

        assert isinstance(output, RawDataSource)
        assert isinstance(output.raw_content, dict)
        assert output.raw_content["total_patents"] == 0

    def test_all_backends_fail_propagates(self, adapter: PatentEnrichment) -> None:
        """If search_company_patents raises, the error must propagate."""
        with patch(
            "solstein.data.patent_client.search_company_patents",
            side_effect=ConnectionError("All backends unreachable"),
        ):
            with pytest.raises(ConnectionError, match="All backends unreachable"):
                adapter.enrich(company_id="t5", company_name="Offline Corp")
