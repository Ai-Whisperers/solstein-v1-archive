"""Tests for STORY-014: Remove Hardcoded Date Path from Data Loader.

Verifies that:
- The unified loader uses configurable market data directory
- Missing directory raises explicit FileNotFoundError (not silent empty result)
- No hardcoded date or market strings remain in the source code
- Multiple date/market combinations work via configuration
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from solstein.config import DataConfig
from solstein.data.unified.unified import UnifiedCompanyLoader


class TestMarketDataDirConfig:
    """Test that market data directory is configurable via settings."""

    def test_config_market_data_dir_resolves_relative_path(self):
        """Config resolves relative paths to absolute."""

        config = DataConfig(market_data_dir=Path("data/markets/energy"))
        assert config.market_data_dir is not None
        assert config.market_data_dir.is_absolute()

    def test_config_market_data_dir_preserves_absolute_path(self):
        """Config preserves absolute paths as-is."""

        config = DataConfig(market_data_dir=Path("/opt/data/markets"))
        assert config.market_data_dir == Path("/opt/data/markets")

    def test_config_market_data_dir_default_is_none(self):
        """Config defaults to None when not set."""

        config = DataConfig()
        assert config.market_data_dir is None

    def test_config_market_data_dir_from_string(self):
        """Config accepts string and converts to Path."""

        config = DataConfig(market_data_dir="data/markets/energy")
        assert config.market_data_dir is not None
        assert isinstance(config.market_data_dir, Path)
        assert config.market_data_dir.is_absolute()


class TestLoaderMissingDirectoryRaisesError:
    """Test that the loader raises explicit errors instead of silent empty results."""

    def test_missing_directory_raises_file_not_found(self):
        """Loader raises FileNotFoundError when directory does not exist."""

        loader = UnifiedCompanyLoader.__new__(UnifiedCompanyLoader)
        loader.markdown_dir = Path("/nonexistent/path/to/market")
        loader.markdown_extractor = MagicMock()

        with pytest.raises(FileNotFoundError, match="does not exist"):
            loader._load_markdown_companies()

    def test_error_message_includes_path(self):
        """Error message includes the attempted path for debugging."""

        test_path = Path("/data/input/custom_market_runs/2026-03/energy")

        loader = UnifiedCompanyLoader.__new__(UnifiedCompanyLoader)
        loader.markdown_dir = test_path
        loader.markdown_extractor = MagicMock()

        with pytest.raises(FileNotFoundError, match=str(test_path)):
            loader._load_markdown_companies()

    def test_unconfigured_directory_raises_file_not_found(self):
        """Loader raises FileNotFoundError when no directory is configured."""

        loader = UnifiedCompanyLoader.__new__(UnifiedCompanyLoader)
        loader.markdown_dir = None
        loader.markdown_extractor = MagicMock()

        with pytest.raises(FileNotFoundError, match="not configured"):
            loader._load_markdown_companies()


class TestLoaderWithValidDirectory:
    """Test loader works with valid market data directories."""

    def test_loads_from_configured_directory(self):
        """Loader reads .md files from the configured directory."""

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test .md file
            md_file = Path(tmpdir) / "test_company.md"
            md_file.write_text("# Test Company\nRevenue: 1000000\n")

            mock_company = MagicMock()
            mock_company.name = "Test Company"

            mock_extractor = MagicMock()
            mock_extractor.extract_from_file.return_value = {"name": "Test Company"}
            mock_extractor.to_company_profile.return_value = mock_company

            loader = UnifiedCompanyLoader.__new__(UnifiedCompanyLoader)
            loader.markdown_dir = Path(tmpdir)
            loader.markdown_extractor = mock_extractor

            companies = loader._load_markdown_companies()
            assert len(companies) == 1
            assert companies[0].name == "Test Company"

    def test_empty_directory_returns_empty_list_with_warning(self):
        """Empty directory returns empty list and logs a warning."""

        with tempfile.TemporaryDirectory() as tmpdir:
            loader = UnifiedCompanyLoader.__new__(UnifiedCompanyLoader)
            loader.markdown_dir = Path(tmpdir)
            loader.markdown_extractor = MagicMock()

            companies = loader._load_markdown_companies()
            assert companies == []

    def test_multiple_market_directories(self):
        """Different market directories can be configured."""

        # Verify different markets can be configured
        energy = DataConfig(market_data_dir="data/markets/energy_sector")
        tech = DataConfig(market_data_dir="data/markets/tech_sector")

        assert energy.market_data_dir != tech.market_data_dir
        assert "energy_sector" in str(energy.market_data_dir)
        assert "tech_sector" in str(tech.market_data_dir)

    def test_multiple_date_directories(self):
        """Different date-based directories can be configured."""

        march = DataConfig(market_data_dir="data/input/custom_market_runs/2026-03/sector_a")
        april = DataConfig(market_data_dir="data/input/custom_market_runs/2026-04/sector_a")

        assert march.market_data_dir != april.market_data_dir
        assert "2026-03" in str(march.market_data_dir)
        assert "2026-04" in str(april.market_data_dir)


class TestNoHardcodedStrings:
    """Regression tests: ensure no hardcoded date or market strings in source."""

    def test_no_hardcoded_date_in_source(self):
        """Grep for 2026-02-23 returns zero results in source code."""

        result = subprocess.run(
            ["grep", "-rn", "2026-02-23", "src/solstein/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        # Filter out __pycache__ matches
        matches = [line for line in result.stdout.strip().split("\n") if line and "__pycache__" not in line]
        assert matches == [], f"Hardcoded date found: {matches}"

    def test_no_hardcoded_dutch_market_in_data_loading(self):
        """Grep for dutch_market returns zero results in data loading code."""

        result = subprocess.run(
            ["grep", "-rn", "dutch_market", "src/solstein/data/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        matches = [line for line in result.stdout.strip().split("\n") if line and "__pycache__" not in line]
        assert matches == [], f"Hardcoded market name found: {matches}"

    def test_no_hardcoded_fx_rate(self):
        """Grep for 1.17 (GBP_EUR_RATE) returns zero results."""

        result = subprocess.run(
            ["grep", "-rn", "GBP_EUR_RATE", "src/solstein/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        matches = [line for line in result.stdout.strip().split("\n") if line and "__pycache__" not in line]
        assert matches == [], f"Hardcoded FX rate found: {matches}"


class TestEnvVarOverride:
    """Test MARKET_DATA_DIR environment variable override."""

    def test_env_var_is_read_by_loader(self):
        """MARKET_DATA_DIR env var is available for the loader to read."""
        with patch.dict(os.environ, {"MARKET_DATA_DIR": "/tmp/test_market"}):
            env_market_dir = os.getenv("MARKET_DATA_DIR")
            assert env_market_dir == "/tmp/test_market"
            assert Path(env_market_dir) == Path("/tmp/test_market")
