from __future__ import annotations

import re
from urllib.parse import urlparse


def normalize_source_key(source_type: str, source_name: str, source_namespace: str | None = None) -> str:
    namespace = (source_namespace or "solstein").strip().lower()
    type_slug = re.sub(r"[^a-z0-9]+", "-", source_type.lower()).strip("-") or "unknown"
    name_slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-") or "unknown"
    return f"{namespace}:{type_slug}:{name_slug}"


def canonical_source_uri(source_uri: str | None, fallback_url: str | None, source_key: str) -> str:
    candidate = (source_uri or fallback_url or "").strip()
    if candidate.startswith(("http://", "https://", "urn:")):
        return candidate
    if candidate:
        return f"urn:source:{source_key}:{candidate.lower()}"
    return f"urn:source:{source_key}"


def is_valid_source_uri(value: str) -> bool:
    if value.startswith("urn:"):
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
