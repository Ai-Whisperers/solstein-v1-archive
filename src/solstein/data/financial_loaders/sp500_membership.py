"""S&P 500 membership data loader.

Extracted from loaders.py as part of EPIC-021 file splitting.
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class SP500MembershipData:
    """Container for S&P 500 membership data."""

    def __init__(self, memberships: dict[str, dict[str, Any]] | None = None):
        self.memberships = memberships or {}

    def is_member(self, ticker: str, as_of: date) -> bool:
        """Check if ticker was in S&P 500 as of a specific date."""
        membership = self.memberships.get(ticker)

        if not membership:
            return False

        date_added = membership.get("date_added")
        date_removed = membership.get("date_removed")

        if date_added is None:
            return False

        if as_of < date_added:
            return False

        if date_removed is not None and as_of >= date_removed:
            return False

        return True


class SP500MembershipLoader:
    """Loader for S&P 500 membership history."""

    DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "snp_500_add_removal_dates.csv"

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH

    def load(self) -> SP500MembershipData:
        """Load S&P 500 membership data from CSV."""
        if not self.data_path.exists():
            logger.warning(f"S&P 500 membership data not found at {self.data_path}")
            return SP500MembershipData()

        df = pd.read_csv(self.data_path)

        memberships = {}

        for _, row in df.iterrows():
            ticker = row["Ticker"]

            date_added = None
            if pd.notna(row["Date_Added"]).item() and str(row["Date_Added"]) != "NA":
                date_added = pd.to_datetime(row["Date_Added"]).item().date()

            date_removed = None
            if pd.notna(row["Date_Removed"]).item() and str(row["Date_Removed"]) != "NA":
                date_removed = pd.to_datetime(row["Date_Removed"]).item().date()

            memberships[ticker] = {
                "date_added": date_added,
                "date_removed": date_removed,
            }

        logger.info(f"Loaded S&P 500 membership data for {len(memberships)} tickers")

        return SP500MembershipData(memberships=memberships)
