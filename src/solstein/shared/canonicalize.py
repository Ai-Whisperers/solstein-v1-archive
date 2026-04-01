"""Shared canonicalization and hashing utilities.

STORY-247: Moved from research.sources and research.hashing to this lower
shared boundary so both research and infrastructure layers can consume them
without infrastructure importing upward into research.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from uuid import UUID

from pydantic import BaseModel

# ---------- URL canonicalization ----------

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
    except Exception:
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


# ---------- JSON canonicalization / hashing ----------


def _qualified_type_name(value: object) -> str:
    cls = value if isinstance(value, type) else type(value)
    return f"{cls.__module__}.{cls.__qualname__}"


def _to_canonical_jsonable(value: object) -> object:
    if value is None or isinstance(value, (str, int, bool)):
        return value

    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return str(value)
        return value

    if isinstance(value, Decimal):
        return str(value.normalize())

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, (UUID, Path)):
        return str(value)

    if isinstance(value, bytes):
        return value.hex()

    if isinstance(value, Enum):
        return {
            "__type__": _qualified_type_name(value),
            "value": _to_canonical_jsonable(value.value),
        }

    if isinstance(value, BaseModel):
        return _to_canonical_jsonable(value.model_dump(mode="json"))

    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _to_canonical_jsonable(getattr(value, field.name)) for field in fields(value)}

    if isinstance(value, MappingProxyType):
        return _to_canonical_jsonable(dict(value))

    if isinstance(value, Mapping):
        items: list[tuple[str, object]] = []
        for k, v in value.items():
            items.append((str(k), _to_canonical_jsonable(v)))
        return dict(sorted(items, key=lambda item: item[0]))

    if isinstance(value, (list, tuple)):
        return [_to_canonical_jsonable(item) for item in value]

    if isinstance(value, (set, frozenset)):
        normalized = [_to_canonical_jsonable(item) for item in value]
        normalized.sort(
            key=lambda item: canonical_json_dumps(item),
        )
        return normalized

    if hasattr(value, "__dict__"):
        raw_dict = value.__dict__
        if isinstance(raw_dict, dict):
            return {
                "__type__": _qualified_type_name(value),
                "__dict__": _to_canonical_jsonable(raw_dict),
            }

    return {
        "__type__": _qualified_type_name(value),
        "__str__": str(value),
    }


def canonical_json_dumps(value: object) -> str:
    canonical = _to_canonical_jsonable(value)
    return json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_canonical_json(value: object) -> str:
    encoded = canonical_json_dumps(value).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
