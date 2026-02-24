import hashlib
import json
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from uuid import UUID

from pydantic import BaseModel


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
        return {
            field.name: _to_canonical_jsonable(getattr(value, field.name))
            for field in fields(value)
        }

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
