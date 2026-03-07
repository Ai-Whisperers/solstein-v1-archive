"""Financial signal definitions.

Signals related to company financial metrics.
"""

from ..base import Signal, SignalCategory

FINANCIAL_SIGNALS = [
    Signal(
        name="Total Funding Raised",
        category=SignalCategory.FINANCIAL,
        description="Cumulative capital raised from all sources",
    ),
    Signal(
        name="Latest Funding Round Size",
        category=SignalCategory.FINANCIAL,
        description="Size and valuation of most recent round",
    ),
    Signal(
        name="Funding Round Velocity",
        category=SignalCategory.FINANCIAL,
        description="Time between funding rounds (faster = better)",
    ),
    Signal(
        name="Monthly Burn Rate",
        category=SignalCategory.FINANCIAL,
        description="Monthly cash consumption",
    ),
    Signal(
        name="Runway Months",
        category=SignalCategory.FINANCIAL,
        description="Months of runway at current burn rate",
    ),
    Signal(
        name="Cash Efficiency Ratio",
        category=SignalCategory.FINANCIAL,
        description="Revenue per dollar of funding",
    ),
    Signal(
        name="Customer Acquisition Cost (CAC)",
        category=SignalCategory.FINANCIAL,
        description="Cost to acquire one customer",
    ),
    Signal(
        name="Customer Lifetime Value (LTV)",
        category=SignalCategory.FINANCIAL,
        description="Total expected revenue per customer",
    ),
    Signal(
        name="LTV-to-CAC Ratio",
        category=SignalCategory.FINANCIAL,
        description="Ratio of LTV to CAC (3:1 is healthy)",
    ),
    Signal(
        name="Gross Margin",
        category=SignalCategory.FINANCIAL,
        description="Percentage of revenue after COGS",
    ),
]
