"""JWT compatibility module.

Provides ``verify_token`` and ``create_token`` used by
``solstein.security.auth`` and ``solstein.tenant.context``.
Delegates to the canonical ``jwt_handler`` where possible but
returns raw dicts so callers can use ``.get()`` access patterns.
"""

from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from solstein.config import get_settings


def verify_token(token: str) -> dict:
    """Decode *token* and return the raw JWT payload dict."""
    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string")
    settings = get_settings()
    return pyjwt.decode(
        token,
        settings.security.secret_key,
        algorithms=[settings.security.algorithm],
    )


def create_token(*, data: dict, expires_delta: datetime | timedelta | None = None) -> str:
    """Encode *data* into a signed JWT string.

    ``expires_delta`` may be either an absolute ``datetime`` (the exp claim)
    or a ``timedelta`` added to *now*.  When *None* a 15-minute default is used.
    """
    settings = get_settings()
    to_encode = data.copy()
    if isinstance(expires_delta, datetime):
        to_encode["exp"] = expires_delta
    elif isinstance(expires_delta, timedelta):
        to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    else:
        to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.security.access_token_expire_minutes)
    return pyjwt.encode(
        to_encode,
        settings.security.secret_key,
        algorithm=settings.security.algorithm,
    )
