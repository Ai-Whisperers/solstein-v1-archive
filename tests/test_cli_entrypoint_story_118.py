"""Tests for STORY-118: Formalize CLI as Proper Package Entrypoint.

Verifies that:
- CLI package is importable and has main() entrypoint
- pyproject.toml registers solstein as a console script
- CLI commands use API client (no direct domain imports)
- Auth credential management works (store/load/clear)
- API client builds correct requests
- All CLI commands have --help
- --output json flag works
"""

import ast
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

import solstein.cli
from solstein.cli import cli, main
from solstein.cli.api_client import APIError, SolsteinAPIClient
from solstein.cli.auth import (
    clear_credentials,
    get_access_token,
    get_api_url,
    load_credentials,
    store_credentials,
)
from solstein.cli_legacy import cli as legacy_cli


class TestPackageEntrypoint:
    """Verify CLI is a proper package entrypoint."""

    def test_cli_package_importable(self) -> None:
        assert hasattr(solstein.cli, "main")
        assert hasattr(solstein.cli, "cli")

    def test_main_is_callable(self) -> None:
        assert callable(main)

    def test_pyproject_has_entrypoint(self) -> None:
        content = Path("pyproject.toml").read_text()
        assert 'solstein = "solstein.cli:main"' in content

    def test_cli_group_exists(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SolStein" in result.output

    def test_version_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0


class TestZeroDomainImports:
    """Verify the new CLI has zero direct domain-layer imports."""

    def test_cli_app_no_domain_imports(self) -> None:
        cli_app = Path("src/solstein/cli/app.py").read_text()
        tree = ast.parse(cli_app)
        forbidden = {
            "domain", "analytics", "infrastructure",
            "exporters", "extractors", "data",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("solstein."):
                    layer = node.module.split(".")[1]
                    assert layer not in forbidden, (
                        f"app.py imports from solstein.{layer} (forbidden)"
                    )

    def test_cli_init_no_domain_imports(self) -> None:
        init = Path("src/solstein/cli/__init__.py").read_text()
        tree = ast.parse(init)
        forbidden = {
            "domain", "analytics", "infrastructure",
            "exporters", "extractors", "data",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("solstein."):
                    layer = node.module.split(".")[1]
                    assert layer not in forbidden, (
                        f"__init__.py imports from solstein.{layer}"
                    )


class TestAuthCredentials:
    """Verify credential store/load/clear cycle."""

    def test_store_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = Path(tmpdir) / "credentials.json"
            with patch("solstein.cli.auth.CREDENTIALS_DIR", Path(tmpdir)):
                with patch("solstein.cli.auth.CREDENTIALS_FILE", creds_file):
                    store_credentials("tok123", "ref456", api_url="http://test:9000")
                    creds = load_credentials()
                    assert creds is not None
                    assert creds["access_token"] == "tok123"
                    assert creds["refresh_token"] == "ref456"
                    assert creds["api_url"] == "http://test:9000"

    def test_clear_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            creds_file = Path(tmpdir) / "credentials.json"
            creds_file.write_text('{"access_token": "x"}')
            with patch("solstein.cli.auth.CREDENTIALS_FILE", creds_file):
                clear_credentials()
                assert not creds_file.exists()

    def test_load_missing_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "nope.json"
            with patch("solstein.cli.auth.CREDENTIALS_FILE", missing):
                assert load_credentials() is None

    def test_get_access_token_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "nope.json"
            with patch("solstein.cli.auth.CREDENTIALS_FILE", missing):
                assert get_access_token() is None

    def test_get_api_url_from_env(self) -> None:
        with patch.dict(os.environ, {"SOLSTEIN_API_URL": "http://env:1234"}):
            assert get_api_url() == "http://env:1234"

    def test_get_api_url_default(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with tempfile.TemporaryDirectory() as tmpdir:
                missing = Path(tmpdir) / "nope.json"
                with patch("solstein.cli.auth.CREDENTIALS_FILE", missing):
                    url = get_api_url()
                    assert url == "http://localhost:8000"


class TestAPIClient:
    """Verify API client builds correct requests."""

    def test_client_sets_auth_header(self) -> None:
        client = SolsteinAPIClient(base_url="http://test", token="mytoken")
        headers = client._headers()
        assert headers["Authorization"] == "Bearer mytoken"

    def test_client_no_auth_without_token(self) -> None:
        with patch("solstein.cli.api_client.get_access_token", return_value=None):
            client = SolsteinAPIClient(base_url="http://test", token=None)
            # Force token to None since patching happens at init time
            client._token = None
            headers = client._headers()
            assert "Authorization" not in headers

    def test_api_error_raised_on_4xx(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {"detail": "Unauthorized"}
        mock_resp.text = "Unauthorized"
        client = SolsteinAPIClient(base_url="http://test", token="x")
        try:
            client._handle_response(mock_resp)
            raise AssertionError("Should have raised APIError")
        except APIError as exc:
            assert exc.status_code == 401
            assert "Unauthorized" in exc.detail


class TestCLICommands:
    """Verify CLI commands have --help and accept --output json."""

    def test_login_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["login", "--help"])
        assert result.exit_code == 0
        assert "email" in result.output.lower()

    def test_logout_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["logout", "--help"])
        assert result.exit_code == 0

    def test_whoami_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["whoami", "--help"])
        assert result.exit_code == 0

    def test_companies_list_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["companies", "list", "--help"])
        assert result.exit_code == 0
        assert "limit" in result.output.lower()

    def test_research_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["research", "--help"])
        assert result.exit_code == 0
        assert "company_name" in result.output.lower()

    def test_export_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0

    def test_status_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0

    def test_health_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["health", "--help"])
        assert result.exit_code == 0

    def test_whoami_not_logged_in(self) -> None:
        runner = CliRunner()
        with patch("solstein.cli.app.get_access_token", return_value=None):
            result = runner.invoke(cli, ["whoami"])
            assert result.exit_code == 0
            assert "Not logged in" in result.output

    def test_whoami_json_output(self) -> None:
        runner = CliRunner()
        with patch("solstein.cli.app.get_access_token", return_value=None):
            result = runner.invoke(cli, ["--output", "json", "whoami"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["authenticated"] is False

    def test_logout_clears_credentials(self) -> None:
        runner = CliRunner()
        with patch("solstein.cli.app.clear_credentials") as mock_clear:
            result = runner.invoke(cli, ["logout"])
            assert result.exit_code == 0
            mock_clear.assert_called_once()


class TestLegacyCLIPreserved:
    """Verify the legacy CLI still works for backward compatibility."""

    def test_legacy_cli_importable(self) -> None:
        assert legacy_cli is not None

    def test_legacy_entrypoint_in_pyproject(self) -> None:
        content = Path("pyproject.toml").read_text()
        assert 'solstein-legacy = "solstein.cli_legacy:main"' in content
