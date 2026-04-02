"""Tests for STORY-070: SSRF Prevention in Web and Website Agents.

Verifies that:
- Private IP ranges are rejected (REQ-2)
- Loopback addresses are rejected (REQ-2)
- Link-local / AWS metadata IPs are rejected (REQ-2)
- Non-HTTP schemes are rejected (REQ-2)
- Valid external URLs pass validation
- DNS rebinding to private IPs is detected (REQ-3)
- Shared URL validator is used by agents (REQ-4)
"""

from __future__ import annotations

import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from solstein.core.url_validator import SSRFError, validate_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "solstein"
WEBSITE_AGENT_PATH = SRC_DIR / "agents" / "website_agent.py"
URL_VALIDATOR_PATH = SRC_DIR / "core" / "url_validator.py"


class TestBlockedIPRanges:
    """REQ-2: Reject private, loopback, link-local, and metadata IPs."""

    def test_rejects_localhost(self):
        """http://localhost must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://localhost/")

    def test_rejects_127_0_0_1(self):
        """http://127.0.0.1 must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://127.0.0.1/")

    def test_rejects_aws_metadata(self):
        """http://169.254.169.254 (AWS metadata) must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://169.254.169.254/latest/meta-data/")

    def test_rejects_private_10_range(self):
        """http://10.0.0.1 must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://10.0.0.1/")

    def test_rejects_private_172_range(self):
        """http://172.16.0.1 must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://172.16.0.1/")

    def test_rejects_private_192_168_range(self):
        """http://192.168.1.1 must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://192.168.1.1/")

    def test_rejects_ipv6_loopback(self):
        """http://[::1] must be rejected."""
        with pytest.raises(SSRFError):
            validate_url("http://[::1]/")


class TestSchemeValidation:
    """REQ-2: Only HTTP and HTTPS schemes allowed."""

    def test_rejects_ftp_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("ftp://example.com/file.txt")

    def test_rejects_file_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("file:///etc/passwd")

    def test_rejects_gopher_scheme(self):
        with pytest.raises(SSRFError, match="scheme"):
            validate_url("gopher://evil.com/")

    def test_rejects_empty_url(self):
        with pytest.raises(SSRFError):
            validate_url("")

    def test_rejects_none_url(self):
        with pytest.raises(SSRFError):
            validate_url(None)  # type: ignore[arg-type]


class TestValidURLs:
    """Valid external URLs must pass validation."""

    def test_accepts_https_example_com(self):
        result = validate_url("https://example.com")
        assert result == "https://example.com"

    def test_accepts_http_example_com(self):
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_accepts_https_with_path(self):
        result = validate_url("https://example.com/path/to/page")
        assert result == "https://example.com/path/to/page"


class TestDNSRebinding:
    """REQ-3: DNS resolution to private IP must be blocked."""

    def test_blocks_hostname_resolving_to_private_ip(self):
        """Hostname that resolves to 10.x.x.x must be blocked."""
        fake_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 0)),
        ]
        with (
            patch("solstein.core.url_validator.socket.getaddrinfo", return_value=fake_addrinfo),
            pytest.raises(SSRFError, match="blocked"),
        ):
            validate_url("http://evil-rebind.example.com/")

    def test_blocks_hostname_resolving_to_loopback(self):
        """Hostname that resolves to 127.0.0.1 must be blocked."""
        fake_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0)),
        ]
        with (
            patch("solstein.core.url_validator.socket.getaddrinfo", return_value=fake_addrinfo),
            pytest.raises(SSRFError, match="blocked"),
        ):
            validate_url("http://localhost-rebind.example.com/")

    def test_blocks_hostname_resolving_to_metadata(self):
        """Hostname that resolves to 169.254.169.254 must be blocked."""
        fake_addrinfo = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 0)),
        ]
        with (
            patch("solstein.core.url_validator.socket.getaddrinfo", return_value=fake_addrinfo),
            pytest.raises(SSRFError, match="blocked"),
        ):
            validate_url("http://metadata-rebind.example.com/")


class TestSharedUtilityUsage:
    """REQ-4: Agents must use the shared URL validation utility."""

    def test_url_validator_module_exists(self):
        """url_validator.py must exist in core/."""
        assert URL_VALIDATOR_PATH.exists(), "core/url_validator.py not found"

    def test_website_agent_imports_validator(self):
        """website_agent.py must import from url_validator."""
        content = WEBSITE_AGENT_PATH.read_text()
        assert "validate_url" in content, "website_agent.py does not use validate_url"

    def test_website_agent_calls_validate_url(self):
        """website_agent.py must call validate_url before any HTTP fetch.

        STORY-135 migrated from requests to httpx.AsyncClient — check for
        httpx usage rather than requests.get.
        """
        content = WEBSITE_AGENT_PATH.read_text()
        validate_pos = content.find("validate_url")
        # Accept either requests.get (legacy) or httpx (STORY-135 migration)
        fetch_pos = content.find("httpx")
        if fetch_pos == -1:
            fetch_pos = content.find("requests.get")
        assert validate_pos != -1, "website_agent.py does not use validate_url"
        assert fetch_pos != -1, "website_agent.py does not use httpx or requests.get"
        assert validate_pos < fetch_pos, "validate_url must be called before HTTP fetch in website_agent.py"

    def test_website_agent_catches_ssrf_error(self):
        """website_agent.py must catch SSRFError specifically."""
        content = WEBSITE_AGENT_PATH.read_text()
        assert "SSRFError" in content, "website_agent.py does not catch SSRFError"
