"""Canonical runtime package.

STORY-257 / EPIC-067: Single source of truth for the canonical pipeline
runtime components.  Every CLI command, API endpoint, and script that
participates in the **canonical legacy pipeline** MUST import its
registry builder and raw-to-domain converter from this package.

Canonical components
--------------------
- ``get_registry``  -- build the canonical ``SourceRegistry``
- ``convert_raw``   -- the canonical raw-dict-to-``Company`` converter
- ``run_pipeline``  -- canonical ``run_market_intelligence`` entry-point

Non-canonical paths (report export, graph runtime, standalone AI research)
are documented in ``docs/architecture/runtime-entrypoints.md`` and do NOT
import from here.
"""

from solstein.runtime.canonical import convert_raw, get_registry, run_pipeline

__all__ = [
    "convert_raw",
    "get_registry",
    "run_pipeline",
]
