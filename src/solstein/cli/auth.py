"""CLI authentication — credential storage and token management.

STORY-118: Manages auth tokens stored in ~/.solstein/credentials.
Similar pattern to AWS CLI credential management.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CREDENTIALS_DIR = Path.home() / ".solstein"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"


def _ensure_credentials_dir() -> None:
    """Create credentials directory with restricted permissions."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CREDENTIALS_DIR, 0o700)


def store_credentials(
    access_token: str,
    refresh_token: str,
    *,
    api_url: str = "http://localhost:8000",
) -> None:
    """Store auth tokens to disk.

    Args:
        access_token: JWT access token from the API.
        refresh_token: Refresh token for renewing access.
        api_url: Base URL of the Solstein API.
    """
    _ensure_credentials_dir()
    payload: dict[str, Any] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "api_url": api_url,
    }
    CREDENTIALS_FILE.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    os.chmod(CREDENTIALS_FILE, 0o600)


def load_credentials() -> dict[str, str] | None:
    """Load stored credentials.

    Returns:
        Dict with access_token, refresh_token, api_url — or None if
        no credentials file exists.
    """
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        if "access_token" not in data:
            return None
        return data
    except (json.JSONDecodeError, OSError):
        return None


def clear_credentials() -> None:
    """Remove stored credentials."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def get_api_url() -> str:
    """Return the configured API URL (from credentials or env var).

    Priority:
        1. SOLSTEIN_API_URL environment variable
        2. Stored credentials file
        3. Default: http://localhost:8000
    """
    env_url = os.environ.get("SOLSTEIN_API_URL")
    if env_url:
        return env_url.rstrip("/")

    creds = load_credentials()
    if creds and "api_url" in creds:
        return creds["api_url"].rstrip("/")

    return "http://localhost:8000"


def get_access_token() -> str | None:
    """Return the stored access token, or None if not logged in."""
    creds = load_credentials()
    if creds:
        return creds.get("access_token")
    return None
