"""Strategic signal definitions.

Signals related to strategic positioning and business milestones.
"""

from ..base import Signal, SignalCategory

STRATEGIC_SIGNALS = [
    Signal(
        name="Series A Completion",
        category=SignalCategory.STRATEGIC,
        description="Successful Series A fundraise",
    ),
    Signal(
        name="Strategic Partnership Count",
        category=SignalCategory.STRATEGIC,
        description="Number of key partnerships",
    ),
    Signal(
        name="Acquisition of Competitors",
        category=SignalCategory.STRATEGIC,
        description="M&A activity to consolidate market",
    ),
    Signal(
        name="IPO Readiness",
        category=SignalCategory.STRATEGIC,
        description="Indicators of IPO preparation",
    ),
    Signal(
        name="Board Composition Quality",
        category=SignalCategory.STRATEGIC,
        description="Presence of industry veterans",
    ),
    Signal(
        name="Strategic Pivot Execution",
        category=SignalCategory.STRATEGIC,
        description="Successful repositioning of product",
    ),
    Signal(
        name="Investor Repeat Funding",
        category=SignalCategory.STRATEGIC,
        description="Previous investors participating in rounds",
    ),
    Signal(
        name="Strategic Investor Type",
        category=SignalCategory.STRATEGIC,
        description="Tier-1 VC, corporate venture, strategic",
    ),
    Signal(
        name="Customer Diversification",
        category=SignalCategory.STRATEGIC,
        description="Percentage from top 10 customers",
    ),
    Signal(
        name="Vertical Expansion Plans",
        category=SignalCategory.STRATEGIC,
        description="Moving into adjacent markets",
    ),
]
