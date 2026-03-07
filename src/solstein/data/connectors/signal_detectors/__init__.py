"""Signal detection strategies.

EPIC-022: Modularized signal detection operations.

Each signal type has its own detector with specific patterns and logic.
"""

from .base import Signal, SignalDetector
from .funding import FundingSignalDetector
from .key_hire import KeyHireSignalDetector
from .partnership import PartnershipSignalDetector

__all__ = [
    "Signal",
    "SignalDetector",
    "FundingSignalDetector",
    "PartnershipSignalDetector",
    "KeyHireSignalDetector",
]
