"""Funding and valuation parsing utilities.

Extracted from loaders.py as part of EPIC-021 file splitting.
Provides functions to parse funding amounts and valuations from text.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def parse_funding_amount(text: str | None) -> float | None:
    """Parse funding amount from text like '$1.0B', 'EUR 400M', '~£3.8B', etc."""
    if not text:
        return None

    text = text.upper()

    # Check for bootstrapped/no funding
    if any(
        x in text
        for x in [
            "BOOTSTRAPPED",
            "ZERO EXTERNAL",
            "€0 ",
            "EUR 0 (",
            "EUR 0.0",
            "NOT APPLICABLE",
            "N/A (",
            "NO EXTERNAL",
            "SELF-FUNDED",
            "UNFUNDED",
        ]
    ):
        return 0.0

    currency_mult = detect_currency_multiplier(text)
    if currency_mult is None:
        return None

    explicit_match = re.search(r"(EUR|USD|GBP|A\$|AUD|£|\$)\s*([\d.,]+)\s*(B|BN|BILLION|M|MLN|MILLION)", text)
    if explicit_match:
        amount = parse_numeric_value(explicit_match.group(2))
        if amount is not None:
            mag = explicit_match.group(3)
            magnitude = 1_000_000_000 if mag.startswith("B") else 1_000_000
            rate = detect_currency_multiplier(explicit_match.group(1))
            if rate is not None:
                return amount * magnitude * rate

    # Patterns: (regex, multiplier_key)
    patterns = [
        (r"~\$?\s*([\d.]+)\s*BILLION", "BILLION"),
        (r"~\$?\s*([\d.]+)\s*B\b", "BILLION"),
        (r"\$\s*([\d.]+)\s*B", "BILLION"),
        (r"EUR\s*([\d.]+)\s*BILLION", "BILLION"),
        (r"EUR\s*([\d.]+)\s*B\b", "BILLION"),
        (r"([\d.]+)\s*BILLION", "BILLION"),
        (r"~\$?\s*([\d.]+)\s*M\b", "MILLION"),
        (r"\$\s*([\d.]+)\s*M\b", "MILLION"),
        (r"EUR\s*([\d.]+)\s*M\b", "MILLION"),
        (r"GBP\s*([\d.]+)\s*M\b", "MILLION"),
        (r"NOK\s*([\d.]+)\s*B\b", "BILLION"),
        (r"DKK\s*([\d.]+)\s*B\b", "BILLION"),
        (r"DKK\s*([\d.]+)\s*M\b", "MILLION"),
        (r"AUD\s*([\d.]+)\s*M\b", "MILLION"),
    ]

    magnitude = {"BILLION": 1_000_000_000, "MILLION": 1_000_000}

    for pattern, mag_key in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                amount = parse_numeric_value(match.group(1))
                if amount is None:
                    continue
                return amount * magnitude[mag_key] * currency_mult
            except (ValueError, KeyError):
                continue
    return None


def parse_valuation(text: str | None) -> float | None:
    """Parse valuation from text like '$8.65B', 'EUR 1.5 billion', market cap."""
    if not text:
        return None

    text = text.upper()

    currency_mult = detect_currency_multiplier(text)
    if currency_mult is None:
        return None

    explicit_match = re.search(r"(EUR|USD|GBP|A\$|AUD|£|\$)\s*([\d.,]+)\s*(B|BN|BILLION|M|MLN|MILLION)", text)
    if explicit_match:
        amount = parse_numeric_value(explicit_match.group(2))
        if amount is not None:
            mag = explicit_match.group(3)
            magnitude = 1_000_000_000 if mag.startswith("B") else 1_000_000
            rate = detect_currency_multiplier(explicit_match.group(1))
            if rate is not None:
                return amount * magnitude * rate

    # Check for no valuation
    if any(
        x in text
        for x in [
            "UNDISCLOSED",
            "UNKNOWN",
            "NOT APPLICABLE",
            "NO EXTERNAL",
            "NONE",
        ]
    ):
        return None

    # Handle ranges like "EUR 30-60M" - use midpoint
    range_match = re.search(r"(EUR|\$|USD|GBP)\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*(M|B)", text)
    if range_match:
        try:
            curr = range_match.group(1)
            low = parse_numeric_value(range_match.group(2))
            high = parse_numeric_value(range_match.group(3))
            if low is None or high is None:
                return None
            mag = range_match.group(4)
            midpoint = (low + high) / 2
            mult = 1_000_000 if mag == "M" else 1_000_000_000
            rate = detect_currency_multiplier(curr) or currency_mult
            return midpoint * mult * rate
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse valuation range: {e}")

    # Extract market cap / enterprise value
    if "MARKET CAP" in text or "ENTERPRISE VALUE" in text:
        patterns_to_try = [
            r"(EUR|USD|\$|GBP|£|A\$|AUD)\s*([\d.]+)\s*(B|BN|BILLION)",
            r"(EUR|USD|\$|GBP|£|A\$|AUD)\s*([\d.]+)\s*(M|MLN|MILLION)",
        ]
        for pattern in patterns_to_try:
            match = re.search(pattern, text)
            if match:
                try:
                    curr = match.group(1)
                    amount = parse_numeric_value(match.group(2))
                    if amount is None:
                        continue
                    mag = match.group(3)
                    mult = 1_000_000 if mag.startswith("M") else 1_000_000_000
                    rate = detect_currency_multiplier(curr) or currency_mult
                    return amount * mult * rate
                except (ValueError, TypeError, AttributeError) as e:
                    logger.debug(f"Could not parse market cap: {e}")
                    continue

    patterns = [
        (r"~\$?\s*([\d.]+)\s*BILLION", "BILLION"),
        (r"~\$?\s*([\d.]+)\s*B\b", "BILLION"),
        (r"\$\s*([\d.]+)\s*B\b", "BILLION"),
        (r"EUR\s*([\d.]+)\s*BILLION", "BILLION"),
        (r"EUR\s*([\d.]+)\s*B\b", "BILLION"),
        (r"([\d.]+)\s*BILLION", "BILLION"),
        (r"~\$?\s*([\d.]+)\s*M\b", "MILLION"),
        (r"\$\s*([\d.]+)\s*M\b", "MILLION"),
        (r"EUR\s*([\d.]+)\s*M\b", "MILLION"),
        (r"GBP\s*([\d.]+)\s*M\b", "MILLION"),
        (r"£\s*([\d.]+)\s*M\b", "MILLION"),
    ]

    magnitude = {"BILLION": 1_000_000_000, "MILLION": 1_000_000}

    for pattern, mag_key in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                amount = parse_numeric_value(match.group(1))
                if amount is None:
                    continue
                return amount * magnitude[mag_key] * currency_mult
            except (ValueError, KeyError):
                continue
    return None


def detect_currency_multiplier(text: str) -> float | None:
    """Detect currency and return EUR conversion rate."""
    currency_mult = [
        ("A$", 0.60),
        ("AUD", 0.60),
        ("USD", 1.0),
        ("$", 1.0),
        ("EUR", 1.0),
        ("€", 1.0),
        ("GBP", 1.18),
        ("£", 1.18),
        ("NOK", 0.085),
        ("DKK", 0.134),
    ]
    for token, rate in currency_mult:
        if token in text:
            return rate
    return None


def parse_numeric_value(raw: str) -> float | None:
    """Parse numeric value from string, handling commas."""
    cleaned = raw.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None
