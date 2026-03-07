"""Signal definitions for analytics.

EPIC-022: SignalDefinitions has been refactored to use modular category definitions.
The signal lists are now defined in the definitions/ package and imported here.

This maintains backward compatibility while reducing the class size from 454 lines
to approximately 50 lines.
"""

from .base import Signal, SignalCategory
from .definitions import (
    FINANCIAL_SIGNALS,
    GROWTH_SIGNALS,
    HIRING_SIGNALS,
    MARKET_SIGNALS,
    OPERATIONAL_SIGNALS,
    PRODUCT_SIGNALS,
    STRATEGIC_SIGNALS,
    TECHNICAL_SIGNALS,
)


class SignalDefinitions:
    """Registry of all business signal definitions.

    This class provides access to signal definitions organized by category.
    Signal lists are imported from the definitions/ package modules.
    """

    # Import signal lists from category modules
    GROWTH_SIGNALS = GROWTH_SIGNALS
    FINANCIAL_SIGNALS = FINANCIAL_SIGNALS
    TECHNICAL_SIGNALS = TECHNICAL_SIGNALS
    HIRING_SIGNALS = HIRING_SIGNALS
    PRODUCT_SIGNALS = PRODUCT_SIGNALS
    MARKET_SIGNALS = MARKET_SIGNALS
    OPERATIONAL_SIGNALS = OPERATIONAL_SIGNALS
    STRATEGIC_SIGNALS = STRATEGIC_SIGNALS

    # Combined list of all signals
    ALL_SIGNALS = (
        GROWTH_SIGNALS
        + FINANCIAL_SIGNALS
        + TECHNICAL_SIGNALS
        + HIRING_SIGNALS
        + PRODUCT_SIGNALS
        + MARKET_SIGNALS
        + OPERATIONAL_SIGNALS
        + STRATEGIC_SIGNALS
    )

    @classmethod
    def get_signals_by_category(cls, category: SignalCategory) -> list[Signal]:
        """Get all signals in a category."""
        return [s for s in cls.ALL_SIGNALS if s.category == category]

    @classmethod
    def get_signal_count(cls) -> int:
        """Get total number of defined signals."""
        return len(cls.ALL_SIGNALS)

    @classmethod
    def get_category_distribution(cls) -> dict[str, int]:
        """Get count of signals per category."""
        distribution = {}
        for category in SignalCategory:
            distribution[category.value] = len(cls.get_signals_by_category(category))
        return distribution
