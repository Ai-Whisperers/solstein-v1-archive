"""Identifier lookup strategies.

EPIC-022: Modularized identifier lookup operations.

Each lookup provider has its own strategy for finding company identifiers.
"""

from .base import LookupStrategy
from .duckduckgo import DuckDuckGoStrategy
from .openfigi import OpenFIGIStrategy
from .opencorporates import OpenCorporatesStrategy

__all__ = [
    "LookupStrategy",
    "OpenCorporatesStrategy",
    "OpenFIGIStrategy",
    "DuckDuckGoStrategy",
]
