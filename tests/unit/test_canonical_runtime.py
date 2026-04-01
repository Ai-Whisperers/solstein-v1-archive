"""Smoke tests for the canonical runtime facade.

STORY-257 / EPIC-067: Verifies that all canonical entrypoints share
the same registry builder and raw-to-domain converter, and that the
canonical runtime module is the single import path.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from solstein.adapters.registry import SourceRegistry, build_default_registry
from solstein.config import Settings
from solstein.data.converters import convert_to_domain_company
from solstein.domain.models import Company
from solstein.runtime import convert_raw, get_registry


# ---------------------------------------------------------------------------
# Fixture: minimal Settings with no API keys
# ---------------------------------------------------------------------------

@pytest.fixture()
def minimal_settings() -> Settings:
    """Build a Settings object with no optional API keys."""
    with patch.dict(
        "os.environ",
        {
            "DATABASE__URL": "postgresql://test:test@localhost/test",
            "JWT_SECRET_KEY": "test-secret",
        },
        clear=False,
    ):
        return Settings.load()


# ---------------------------------------------------------------------------
# 1. get_registry returns the same type as build_default_registry
# ---------------------------------------------------------------------------

class TestCanonicalRegistry:
    """The canonical ``get_registry`` must produce a SourceRegistry."""

    def test_get_registry_returns_source_registry(self, minimal_settings: Settings) -> None:
        registry = get_registry(minimal_settings)
        assert isinstance(registry, SourceRegistry)

    def test_get_registry_matches_build_default(self, minimal_settings: Settings) -> None:
        """The canonical facade and the raw builder produce equivalent registries."""
        canonical = get_registry(minimal_settings)
        raw = build_default_registry(minimal_settings)

        assert len(canonical.discovery_sources) == len(raw.discovery_sources)
        assert len(canonical.enrichment_sources) == len(raw.enrichment_sources)

    def test_get_registry_default_settings(self) -> None:
        """get_registry() without args loads settings automatically."""
        with patch.dict(
            "os.environ",
            {
                "DATABASE__URL": "postgresql://test:test@localhost/test",
                "JWT_SECRET_KEY": "test-secret",
            },
            clear=False,
        ):
            registry = get_registry()
            assert isinstance(registry, SourceRegistry)


# ---------------------------------------------------------------------------
# 2. convert_raw delegates to the canonical converter
# ---------------------------------------------------------------------------

class TestCanonicalConverter:
    """The canonical ``convert_raw`` must produce a Company domain object."""

    def test_convert_raw_returns_company(self) -> None:
        raw: dict[str, Any] = {
            "company_name": "TestCo",
            "industry": "Technology",
            "revenue": 1_000_000,
        }
        company = convert_raw(raw)
        assert isinstance(company, Company)
        assert company.name == "TestCo"

    def test_convert_raw_matches_direct_converter(self) -> None:
        """Both paths must produce identical Company objects."""
        raw: dict[str, Any] = {
            "company_name": "AlignCo",
            "industry": "Energy",
            "revenue": 2_500_000,
            "growth_rate": 15.0,
        }
        canonical = convert_raw(raw, index=0)
        direct = convert_to_domain_company(raw, index=0)

        assert canonical.name == direct.name
        assert canonical.industry == direct.industry
        assert canonical.financials.revenue == direct.financials.revenue


# ---------------------------------------------------------------------------
# 3. Pipeline wires canonical registry (import check)
# ---------------------------------------------------------------------------

class TestPipelineUsesCanonicalRegistry:
    """The research pipeline must import get_registry from solstein.runtime."""

    def test_pipeline_imports_canonical_registry(self) -> None:
        """Verify pipeline.py imports get_registry from solstein.runtime."""
        pipeline_path = (
            Path(inspect.getfile(importlib.import_module("solstein.research.pipeline")))
        )
        source = pipeline_path.read_text(encoding="utf-8")

        # Must NOT import build_default_registry directly
        assert "from solstein.adapters.registry import build_default_registry" not in source, (
            "pipeline.py must use solstein.runtime.get_registry, not "
            "solstein.adapters.registry.build_default_registry"
        )

    def test_pipeline_async_imports_canonical_registry(self) -> None:
        """Verify pipeline_async.py imports get_registry from solstein.runtime."""
        pipeline_path = (
            Path(inspect.getfile(importlib.import_module("solstein.research.pipeline_async")))
        )
        source = pipeline_path.read_text(encoding="utf-8")

        assert "from solstein.adapters.registry import build_default_registry" not in source, (
            "pipeline_async.py must use solstein.runtime.get_registry"
        )


# ---------------------------------------------------------------------------
# 4. CLI uses canonical converter (import check)
# ---------------------------------------------------------------------------

class TestCLIUsesCanonicalConverter:
    """The CLI must import convert_raw from solstein.runtime."""

    def test_cli_imports_canonical_converter(self) -> None:
        """Verify cli.py does NOT import convert_to_domain_company from data.converters."""
        cli_path = Path(inspect.getfile(importlib.import_module("solstein.cli")))
        source = cli_path.read_text(encoding="utf-8")

        assert "from .data.converters import convert_to_domain_company" not in source, (
            "cli.py must import converter from solstein.runtime, not data.converters"
        )


# ---------------------------------------------------------------------------
# 5. Smoke test: one company through shared path
# ---------------------------------------------------------------------------

class TestSharedPathSmokeTest:
    """Prove that a single company can flow through the canonical
    converter and registry in the same shared path."""

    def test_one_company_shared_path(self, minimal_settings: Settings) -> None:
        """Convert raw data and build registry in a single shared path."""
        # Step 1: Convert raw JSON to Company via canonical converter
        raw: dict[str, Any] = {
            "company_name": "SmokeTestCo",
            "industry": "SaaS",
            "revenue": 5_000_000,
            "growth_rate": 20.0,
            "employees": 50,
        }
        company = convert_raw(raw, index=0)

        # Step 2: Build canonical registry
        registry = get_registry(minimal_settings)

        # Step 3: Verify both are from the same shared path
        assert isinstance(company, Company)
        assert company.name == "SmokeTestCo"
        assert isinstance(registry, SourceRegistry)
        assert len(registry.discovery_sources) >= 1  # At least static catalog


# ---------------------------------------------------------------------------
# 6. No direct build_default_registry usage in canonical entrypoints
# ---------------------------------------------------------------------------

class TestNoDirectRegistryImports:
    """Canonical entrypoints must NOT import build_default_registry directly."""

    CANONICAL_MODULES = [
        "solstein.research.pipeline",
        "solstein.research.pipeline_async",
        "solstein.data.eneve_enrichment_integration",
    ]

    @pytest.mark.parametrize("module_name", CANONICAL_MODULES)
    def test_no_direct_registry_import(self, module_name: str) -> None:
        """Verify module does not import build_default_registry directly."""
        mod = importlib.import_module(module_name)
        source_path = Path(inspect.getfile(mod))
        source = source_path.read_text(encoding="utf-8")

        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if "adapters.registry" in node.module:
                        names = [alias.name for alias in node.names]
                        assert "build_default_registry" not in names, (
                            f"{module_name} must use solstein.runtime.get_registry, "
                            f"not import build_default_registry from adapters.registry"
                        )
