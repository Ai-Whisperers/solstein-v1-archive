from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["run_market_intelligence"]


def __getattr__(name: str) -> Any:
    if name == "run_market_intelligence":
        pipeline = import_module(".pipeline", __name__)
        attr = getattr(pipeline, name)
        globals()[name] = attr
        return attr

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
