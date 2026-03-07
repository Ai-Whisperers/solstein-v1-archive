"""Signal definitions by category.

This package contains signal definitions organized by category:
- growth: Growth metrics and user acquisition
- financial: Funding, revenue, and financial health
- technical: Technology stack and infrastructure
- hiring: Team growth and talent acquisition
- product: Product development and user satisfaction
- market: Market position and competitive landscape
- operational: Operational excellence and compliance
- strategic: Strategic positioning and milestones
"""

from .financial import FINANCIAL_SIGNALS
from .growth import GROWTH_SIGNALS
from .hiring import HIRING_SIGNALS
from .market import MARKET_SIGNALS
from .operational import OPERATIONAL_SIGNALS
from .product import PRODUCT_SIGNALS
from .strategic import STRATEGIC_SIGNALS
from .technical import TECHNICAL_SIGNALS

__all__ = [
    "FINANCIAL_SIGNALS",
    "GROWTH_SIGNALS",
    "HIRING_SIGNALS",
    "MARKET_SIGNALS",
    "OPERATIONAL_SIGNALS",
    "PRODUCT_SIGNALS",
    "STRATEGIC_SIGNALS",
    "TECHNICAL_SIGNALS",
]
