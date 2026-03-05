from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SourceTier(StrEnum):
    FREE = "free"
    PAID = "paid"


@dataclass(frozen=True)
class SourcePolicy:
    source_name: str
    tier: SourceTier
    authority: float
    required_identifiers: set[str] = field(default_factory=set)
    field_coverage: set[str] = field(default_factory=set)


def default_source_policy_catalog() -> dict[str, SourcePolicy]:
    return {
        "SEC_EDGAR": SourcePolicy(
            source_name="SEC_EDGAR",
            tier=SourceTier.FREE,
            authority=0.95,
            required_identifiers={"ticker"},
            field_coverage={"revenue", "growth_rate", "profit_margin", "employees"},
        ),
        "COMPANIES_HOUSE": SourcePolicy(
            source_name="COMPANIES_HOUSE",
            tier=SourceTier.FREE,
            authority=0.92,
            required_identifiers={"company_number"},
            field_coverage={"revenue", "employees", "profit_margin"},
        ),
        "NEWS_SIGNALS": SourcePolicy(
            source_name="NEWS_SIGNALS",
            tier=SourceTier.FREE,
            authority=0.7,
            required_identifiers=set(),
            field_coverage={"growth_rate", "valuation", "funding"},
        ),
    }
