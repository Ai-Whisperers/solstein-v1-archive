"""Bond yield data loader.

Extracted from loaders.py as part of EPIC-021 file splitting.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class BondYieldData:
    """Container for bond yield time series data."""

    def __init__(self, yields: pd.DataFrame | None = None):
        self.yields = pd.DataFrame() if yields is None else yields

    def get_yield(self, as_of: datetime | date) -> float | None:
        """Get bond yield for a specific date."""
        if isinstance(as_of, date):
            as_of = datetime.combine(as_of, datetime.min.time())

        if as_of not in self.yields.index:
            return None

        yield_value = self.yields.loc[as_of, "DGS10"]

        if pd.isna(yield_value):
            return None

        return float(yield_value)

    def get_latest_yield(self) -> float | None:
        """Get the most recent bond yield."""
        if self.yields.empty:
            return None

        latest = self.yields["DGS10"].dropna()

        if latest.empty:
            return None

        return float(latest.iloc[-1])


class BondYieldLoader:
    """Loader for 10-year US Treasury bond yields."""

    DEFAULT_DATA_PATH = Path(__file__).parent.parent.parent.parent / "data" / "bond_yield.csv"

    def __init__(self, data_path: Path | None = None):
        self.data_path = data_path or self.DEFAULT_DATA_PATH

    def load(self) -> BondYieldData:
        """Load bond yield data from CSV."""
        if not self.data_path.exists():
            logger.warning(f"Bond yield data not found at {self.data_path}")
            return BondYieldData()

        df = pd.read_csv(self.data_path, parse_dates=["observation_date"])
        df.set_index("observation_date", inplace=True)
        df.sort_index(inplace=True)

        return BondYieldData(yields=df)
