"""Data loaders for SolStein.

EPIC-021: Refactored from monolithic 938-line file to modular structure.
This module now serves as the orchestration layer, delegating to specialized modules.
"""

from __future__ import annotations

# Main loader classes
from .competitor_loader import CompetitorDataLoader, loader

# Data converters
from .converters import (
    convert_to_domain_company,
    determine_tier,
    estimate_headquarters,
    extract_geographic_presence,
)

# Bond yield loader
from .financial_loaders.bond_yield import BondYieldData, BondYieldLoader

# S&P 500 membership loader
from .financial_loaders.sp500_membership import SP500MembershipData, SP500MembershipLoader

# Parsers
from .parsers import (
    convert_confidence,
    detect_currency_multiplier,
    parse_funding_amount,
    parse_numeric_value,
    parse_valuation,
)

__all__ = [
    # Main loaders
    "CompetitorDataLoader",
    "loader",
    # Bond yield
    "BondYieldData",
    "BondYieldLoader",
    # S&P 500
    "SP500MembershipData",
    "SP500MembershipLoader",
    # Converters
    "convert_to_domain_company",
    "determine_tier",
    "estimate_headquarters",
    "extract_geographic_presence",
    # Parsers
    "parse_funding_amount",
    "parse_valuation",
    "detect_currency_multiplier",
    "parse_numeric_value",
    "convert_confidence",
]
