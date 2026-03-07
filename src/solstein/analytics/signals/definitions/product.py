"""Product signal definitions.

Signals related to product development and user satisfaction.
"""

from ..base import Signal, SignalCategory

PRODUCT_SIGNALS = [
    Signal(
        name="Feature Release Velocity",
        category=SignalCategory.PRODUCT,
        description="Major features released per quarter",
    ),
    Signal(
        name="Product Roadmap Visibility",
        category=SignalCategory.PRODUCT,
        description="Public roadmap availability",
    ),
    Signal(
        name="User Satisfaction (NPS)",
        category=SignalCategory.PRODUCT,
        description="Net Promoter Score from users",
    ),
    Signal(
        name="App Store Rating",
        category=SignalCategory.PRODUCT,
        description="iOS/Android app ratings (4.0+)",
    ),
    Signal(
        name="Feature Adoption Rate",
        category=SignalCategory.PRODUCT,
        description="Percentage of users using key features",
    ),
    Signal(
        name="Integration Ecosystem",
        category=SignalCategory.PRODUCT,
        description="Third-party integrations (Zapier, API partners)",
    ),
    Signal(
        name="Product-Market Fit Signals",
        category=SignalCategory.PRODUCT,
        description="Signs of PMF (usage metrics, retention)",
    ),
    Signal(
        name="Beta/Early Access Program",
        category=SignalCategory.PRODUCT,
        description="Active beta tester community",
    ),
    Signal(
        name="User Documentation Quality",
        category=SignalCategory.PRODUCT,
        description="Comprehensive help center/docs",
    ),
    Signal(
        name="Community Forum Activity",
        category=SignalCategory.PRODUCT,
        description="Active user community discussions",
    ),
]
