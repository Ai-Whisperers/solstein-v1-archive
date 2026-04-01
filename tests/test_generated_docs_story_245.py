"""Tests for STORY-245: Expand Generated API Docs and Schema Registries.

Verifies that:
- Generator scripts produce valid output
- Package addressability blockers are resolved
- Generated docs are linked from reference docs
"""

import json
from pathlib import Path

import pytest

SRC = Path("src/solstein")
DOCS = Path("docs/reference")


class TestPackageAddressability:
    """Verify that previously non-importable packages now have __init__.py."""

    @pytest.mark.parametrize(
        "package",
        [
            "analytics",
            "data",
            "domain",
            "extractors",
            "intelligence",
            "analytics/market",
            "data/provenance",
            "data/financial_loaders",
        ],
    )
    def test_init_py_exists(self, package: str) -> None:
        """Each targeted package must have an __init__.py for import resolution."""
        init_path = SRC / package / "__init__.py"
        assert init_path.exists(), f"Missing __init__.py: {init_path}"


class TestSchemaOwnershipMap:
    """Verify schema ownership map generator output."""

    def test_md_exists(self) -> None:
        path = DOCS / "generated" / "SCHEMA_OWNERSHIP_MAP.md"
        assert path.exists(), "Schema ownership map markdown not generated"

    def test_json_exists(self) -> None:
        path = DOCS / "generated" / "SCHEMA_OWNERSHIP_MAP.json"
        assert path.exists(), "Schema ownership map JSON not generated"

    def test_json_valid(self) -> None:
        path = DOCS / "generated" / "SCHEMA_OWNERSHIP_MAP.json"
        data = json.loads(path.read_text())
        assert isinstance(data, list), "JSON root should be a list"
        assert len(data) > 0, "Should find at least one schema"

    def test_schemas_have_required_fields(self) -> None:
        path = DOCS / "generated" / "SCHEMA_OWNERSHIP_MAP.json"
        data = json.loads(path.read_text())
        required = {"class_name", "file", "line", "layer", "type"}
        for entry in data[:5]:  # spot check first 5
            assert required.issubset(entry.keys()), f"Missing fields in {entry}"

    def test_md_has_layer_sections(self) -> None:
        path = DOCS / "generated" / "SCHEMA_OWNERSHIP_MAP.md"
        content = path.read_text()
        assert "## " in content, "Should have layer sections"
        assert "Total schemas" in content, "Should report total count"


class TestPipelineBoundaryRegistry:
    """Verify pipeline boundary registry generator output."""

    def test_md_exists(self) -> None:
        path = DOCS / "generated" / "PIPELINE_BOUNDARY_REGISTRY.md"
        assert path.exists(), "Pipeline boundary registry markdown not generated"

    def test_json_exists(self) -> None:
        path = DOCS / "generated" / "PIPELINE_BOUNDARY_REGISTRY.json"
        assert path.exists(), "Pipeline boundary registry JSON not generated"

    def test_json_valid(self) -> None:
        path = DOCS / "generated" / "PIPELINE_BOUNDARY_REGISTRY.json"
        data = json.loads(path.read_text())
        assert isinstance(data, list), "JSON root should be a list"
        assert len(data) > 0, "Should find at least one cross-layer import"

    def test_boundaries_have_required_fields(self) -> None:
        path = DOCS / "generated" / "PIPELINE_BOUNDARY_REGISTRY.json"
        data = json.loads(path.read_text())
        required = {"source_file", "source_layer", "target_layer", "imported"}
        for entry in data[:5]:
            assert required.issubset(entry.keys()), f"Missing fields in {entry}"

    def test_md_has_matrix(self) -> None:
        path = DOCS / "generated" / "PIPELINE_BOUNDARY_REGISTRY.md"
        content = path.read_text()
        assert "Layer Dependency Matrix" in content
        assert "Boundary Hotspots" in content


class TestConnectorContractIndex:
    """Verify connector contract index generator output."""

    def test_md_exists(self) -> None:
        path = DOCS / "generated" / "CONNECTOR_CONTRACT_INDEX.md"
        assert path.exists(), "Connector contract index markdown not generated"

    def test_json_exists(self) -> None:
        path = DOCS / "generated" / "CONNECTOR_CONTRACT_INDEX.json"
        assert path.exists(), "Connector contract index JSON not generated"

    def test_json_valid(self) -> None:
        path = DOCS / "generated" / "CONNECTOR_CONTRACT_INDEX.json"
        data = json.loads(path.read_text())
        assert isinstance(data, list), "JSON root should be a list"
        assert len(data) > 0, "Should find at least one connector"

    def test_connectors_have_required_fields(self) -> None:
        path = DOCS / "generated" / "CONNECTOR_CONTRACT_INDEX.json"
        data = json.loads(path.read_text())
        required = {"class_name", "file", "methods", "method_count"}
        for entry in data[:5]:
            assert required.issubset(entry.keys()), f"Missing fields in {entry}"


class TestApiReferenceExpansion:
    """Verify the expanded PYTHON_API_REFERENCE.md."""

    def test_reference_links_registries(self) -> None:
        path = DOCS / "PYTHON_API_REFERENCE.md"
        content = path.read_text()
        assert "SCHEMA_OWNERSHIP_MAP.md" in content
        assert "PIPELINE_BOUNDARY_REGISTRY.md" in content
        assert "CONNECTOR_CONTRACT_INDEX.md" in content

    def test_reference_covers_domain_layer(self) -> None:
        path = DOCS / "PYTHON_API_REFERENCE.md"
        content = path.read_text()
        assert "solstein.domain" in content

    def test_reference_covers_analytics_layer(self) -> None:
        path = DOCS / "PYTHON_API_REFERENCE.md"
        content = path.read_text()
        assert "solstein.analytics" in content

    def test_reference_covers_data_layer(self) -> None:
        path = DOCS / "PYTHON_API_REFERENCE.md"
        content = path.read_text()
        assert "solstein.data" in content

    def test_reference_no_addressability_disclaimer(self) -> None:
        """The old disclaimer about missing packages should be gone."""
        path = DOCS / "PYTHON_API_REFERENCE.md"
        content = path.read_text()
        assert "still need package-structure cleanup" not in content
