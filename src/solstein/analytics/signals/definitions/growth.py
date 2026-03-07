"""Growth signal definitions.

Signals related to company growth metrics.
"""

from ..models import Signal, SignalCategory

GROWTH_SIGNALS = [
    Signal(
        name="Year-over-Year Revenue Growth Rate",
        category=SignalCategory.GROWTH,
        description="Percentage growth in annual revenue",
    ),
    Signal(
        name="Quarterly Revenue Trend",
        category=SignalCategory.GROWTH,
        description="Trend in quarterly revenue (ascending/stable/declining)",
    ),
    Signal(
        name="Monthly Recurring Revenue (MRR)",
        category=SignalCategory.GROWTH,
        description="Predictable monthly revenue from subscriptions",
    ),
    Signal(
        name="Annual Recurring Revenue (ARR)",
        category=SignalCategory.GROWTH,
        description="Annualized predictable revenue",
    ),
    Signal(
        name="Active User Growth",
        category=SignalCategory.GROWTH,
        description="Month-over-month user acquisition rate",
    ),
    Signal(
        name="Daily Active Users (DAU)",
        category=SignalCategory.GROWTH,
        description="Number of users engaging daily",
    ),
    Signal(
        name="Monthly Active Users (MAU)",
        category=SignalCategory.GROWTH,
        description="Number of users engaging monthly",
    ),
    Signal(
        name="User Churn Rate",
        category=SignalCategory.GROWTH,
        description="Percentage of users lost per period",
    ),
    Signal(
        name="Net Revenue Retention",
        category=SignalCategory.GROWTH,
        description="Revenue from existing customers including expansions",
    ),
    Signal(
        name="Customer Lifetime Value (LTV)",
        category=SignalCategory.GROWTH,
        description="Predicted total revenue per customer",
    ),
    Signal(
        name="Customer Acquisition Cost (CAC)",
        category=SignalCategory.GROWTH,
        description="Cost to acquire a new customer",
    ),
    Signal(
        name="LTV/CAC Ratio",
        category=SignalCategory.GROWTH,
        description="Efficiency of customer acquisition",
    ),
    Signal(
        name="Sales Cycle Length",
        category=SignalCategory.GROWTH,
        description="Average time from lead to close",
    ),
    Signal(
        name="Pipeline Velocity",
        category=SignalCategory.GROWTH,
        description="Speed of deals moving through pipeline",
    ),
    Signal(
        name="Market Expansion Rate",
        category=SignalCategory.GROWTH,
        description="Growth into new geographies or segments",
    ),
]
