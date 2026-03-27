"""Shared URL validation utility for SSRF prevention.

STORY-070: All agents must validate URLs before making HTTP requests.

REQ-1: All URLs must be validated before fetch.
REQ-2: Rejects private IPs, loopback, link-local, non-HTTP schemes.
REQ-3: DNS resolution checked against private ranges (DNS rebinding prevention).
REQ-4: Single shared utility — no per-agent duplication.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from loguru import logger


class SSRFError(ValueError):
    """Raised when a URL fails SSRF validation."""


# Private and reserved IP networks that must be blocked (REQ-2)
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),  # RFC 1918 private
    ipaddress.ip_network("172.16.0.0/12"),  # RFC 1918 private
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918 private
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local / AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),  # "This" network
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmarking
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]

_ALLOWED_SCHEMES = {"http", "https"}


def _is_blocked_ip(ip_str: str) -> bool:
    """Check if an IP address falls within a blocked network."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return any(addr in network for network in _BLOCKED_NETWORKS)


def validate_url(url: str) -> str:
    """Validate a URL for SSRF safety before making an HTTP request.

    Checks:
    1. Scheme must be http or https (REQ-2)
    2. Hostname must not be empty
    3. Hostname must not resolve to a private/reserved IP (REQ-2, REQ-3)

    Args:
        url: The URL to validate

    Returns:
        The validated URL (unchanged if valid)

    Raises:
        SSRFError: If the URL fails any validation check
    """
    if not url or not isinstance(url, str):
        raise SSRFError("URL must be a non-empty string")

    parsed = urlparse(url)

    # REQ-2: Scheme validation
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise SSRFError(f"URL scheme '{parsed.scheme}' not allowed. Only {_ALLOWED_SCHEMES} are permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL must include a hostname")

    # Check if hostname is itself an IP address
    try:
        addr = ipaddress.ip_address(hostname)
        if _is_blocked_ip(str(addr)):
            raise SSRFError(f"URL resolves to blocked IP range: {addr}")
        return url
    except ValueError:
        pass  # Not an IP literal — proceed to DNS resolution

    # REQ-3: DNS resolution check (DNS rebinding prevention)
    try:
        addrinfos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise SSRFError(f"DNS resolution failed for '{hostname}': {e}") from e

    for family, _type, _proto, _canonname, sockaddr in addrinfos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            logger.warning(f"SSRF blocked: '{hostname}' resolved to private IP {ip_str}")
            raise SSRFError(f"Hostname '{hostname}' resolves to a blocked IP range")

    return url
