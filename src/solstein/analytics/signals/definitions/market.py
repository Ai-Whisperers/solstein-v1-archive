"""Market signal definitions.

Signals related to market position and competitive landscape.
"""

from ..base import Signal, SignalCategory

MARKET_SIGNALS = [
    Signal(
        name="Total Addressable Market (TAM)",
        category=SignalCategory.MARKET,
        description="Size of market opportunity",
    ),
    Signal(
        name="Market Share Percentage",
        category=SignalCategory.MARKET,
        description="Percentage of TAM captured",
    ),
    Signal(
        name="Competitive Differentiation",
        category=SignalCategory.MARKET,
        description="Unique value propositions vs competitors",
    ),
    Signal(
        name="Competitor Analysis Score",
        category=SignalCategory.MARKET,
        description="Evaluation vs top 3 competitors",
    ),
    Signal(
        name="Industry Award Count",
        category=SignalCategory.MARKET,
        description="Gartner, Forrester, or industry awards",
    ),
    Signal(
        name="Media Mention Frequency",
        category=SignalCategory.MARKET,
        description="Press coverage in past 6 months",
    ),
    Signal(
        name="Industry Event Presence",
        category=SignalCategory.MARKET,
        description="Speaking slots at major conferences",
    ),
    Signal(
        name="Analyst Report Coverage",
        category=SignalCategory.MARKET,
        description="Gartner Magic Quadrant, Forrester Wave",
    ),
    Signal(
        name="Brand Recognition Score",
        category=SignalCategory.MARKET,
        description="Brand awareness in target market",
    ),
    Signal(
        name="Pricing Power",
        category=SignalCategory.MARKET,
        description="Ability to raise prices without churn",
    ),
]
