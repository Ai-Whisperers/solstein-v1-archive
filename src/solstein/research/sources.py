from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from loguru import logger

_DROP_QUERY_KEYS_PREFIX = ("utm_",)

_DROP_QUERY_KEYS_EXACT = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
    "spm",
}


def canonicalize_url(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return raw

    try:
        parsed = urlparse(raw)
    except Exception as e:
        logger.debug(f"Failed to parse URL: {e}", url=raw)
        return raw

    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()

    path = parsed.path or ""
    if path != "/":
        path = path.rstrip("/")
        if not path:
            path = "/"

    kept: list[tuple[str, str]] = []
    for k, v in parse_qsl(parsed.query, keep_blank_values=True):
        key = k.strip()
        if not key:
            continue
        low = key.lower()
        if low in _DROP_QUERY_KEYS_EXACT:
            continue
        if any(low.startswith(prefix) for prefix in _DROP_QUERY_KEYS_PREFIX):
            continue
        kept.append((key, v))

    kept.sort(key=lambda pair: (pair[0].lower(), pair[1]))
    query = urlencode(kept, doseq=True)

    rebuilt = urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            query,
            "",
        )
    )
    return rebuilt


def is_probably_url(value: str) -> bool:
    raw = (value or "").strip()
    if not raw:
        return False
    try:
        parsed = urlparse(raw)
    except Exception:
        return False
    if parsed.scheme not in {"http", "https"}:
        return False
    return bool(parsed.netloc)
