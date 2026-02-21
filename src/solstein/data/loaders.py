import json
import logging
from datetime import UTC, datetime, date
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import get_settings
from ..domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)

logger = logging.getLogger(__name__)


class CompetitorDataLoader:
    """Load competitor data from JSON files and convert to domain entities."""

    def __init__(self, data_dir: Path | None = None):
        settings = get_settings()
        self.data_dir = data_dir or Path(settings.data.data_dir)
        self._cache: dict[str, list[Company]] = {}

    def load_companies(self, limit: int | None = None) -> list[Company]:
        """Load all companies from data directory."""
        cache_key = f"companies_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        companies = []

        # Try to load from the main competitor data JSON
        json_path = self.data_dir / "competitor_data.json"

        if not json_path.exists():
            error_msg = f"Critical error: Competitor data not found at {json_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        companies.extend(self._load_from_json(json_path, limit))

        if limit:
            companies = companies[:limit]

        self._cache[cache_key] = companies
        return companies

    def _load_from_json(
        self, json_path: Path, limit: int | None = None
    ) -> list[Company]:
        """Load companies from JSON file."""
        try:
            with open(json_path) as f:
                data = json.load(f)

            competitors = data.get("competitors", [])
            if limit:
                competitors = competitors[:limit]

            companies = []
            for i, comp in enumerate(competitors):
                try:
                    company = self._convert_to_domain_company(comp, i)
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"Error converting competitor {i}: {e}")
                    continue

            logger.info(f"Loaded {len(companies)} companies from {json_path}")
            return companies

        except Exception as e:
            logger.error(f"Error loading JSON from {json_path}: {e}")
            return []

    def _convert_to_domain_company(
        self, raw_data: dict[str, Any], index: int
    ) -> Company:
        """Convert raw JSON data to Company domain entity."""
        # Extract basic info
        company_name = raw_data.get("company_name", f"Company {index}")
        folder = raw_data.get("folder", f"company-{index}")

        # Extract financial data
        revenue_data = raw_data.get("revenue", {})
        timeline = revenue_data.get("timeline", [])

        if timeline:
            latest = timeline[0]
            revenue = latest.get("eur_millions")
            growth = latest.get("yoy_growth_pct")
            revenue_confidence = self._convert_confidence(latest.get("confidence"))
        else:
            revenue = None
            growth = None
            revenue_confidence = ConfidenceLevel.UNKNOWN

        # Create financial metric
        financial = FinancialMetric(
            revenue=revenue,
            revenue_confidence=revenue_confidence,
            growth_rate=growth,
            growth_confidence=ConfidenceLevel.ESTIMATED
            if growth
            else ConfidenceLevel.UNKNOWN,
            employees=None,  # No authentic data available
            employees_confidence=ConfidenceLevel.UNKNOWN,
        )

        # Determine tier based on revenue
        tier = self._determine_tier(revenue)

        # Determine AI maturity from scorecard
        scorecard = raw_data.get("scorecard", {})
        dimensions = scorecard.get("dimensions", {})
        saas_score = dimensions.get("SaaS Maturity", {}).get("score", 5)

        # Convert to AI maturity
        if saas_score >= 8:
            ai_maturity = AIMaturity.STRONG
        elif saas_score >= 5:
            ai_maturity = AIMaturity.MODERATE
        else:
            ai_maturity = AIMaturity.LOW

        # Determine threat level from composite score
        composite_score = scorecard.get("composite_score", 5)
        if composite_score >= 8:
            threat_level = ThreatLevel.HIGH
        elif composite_score >= 6:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        # Create company profile
        company = Company(
            id=folder.lower().replace(" ", "-").replace("/", "-"),
            name=company_name,
            industry="Energy Software",
            description=raw_data.get(
                "description", "Competitor in energy software market"
            ),  # noqa: E501
            website=None,
            headquarters=self._estimate_headquarters(folder),
            founded_year=None,  # No authentic data available
            tier=tier,
            threat_level=threat_level,
            ai_maturity=ai_maturity,
            saas_maturity=int(saas_score),
            tech_stack=[],  # No authentic data available
            financials=financial,
            geographic_presence=["Europe"],
            key_customers=[],
            last_updated=datetime.now(UTC),
            data_source="SolStein Competitive Intelligence",
        )

        return company

    def _convert_confidence(self, confidence_str: str | None) -> ConfidenceLevel:
        """Convert string confidence to ConfidenceLevel enum."""
        if not confidence_str:
            return ConfidenceLevel.UNKNOWN

        confidence_str = confidence_str.lower()
        if "confirm" in confidence_str:
            return ConfidenceLevel.CONFIRMED
        elif "estimate" in confidence_str:
            return ConfidenceLevel.ESTIMATED
        else:
            return ConfidenceLevel.UNKNOWN

    def _determine_tier(self, revenue: float | None) -> CompanyTier:
        """Determine company tier based on revenue."""
        if revenue is None:
            return CompanyTier.TIER_4

        if revenue > 1000:  # > €1B
            return CompanyTier.TIER_1
        elif revenue > 100:  # > €100M
            return CompanyTier.TIER_2
        elif revenue > 10:  # > €10M
            return CompanyTier.TIER_3
        else:
            return CompanyTier.TIER_4

    def _estimate_headquarters(self, folder: str) -> str | None:
        """Estimate headquarters based on folder name."""
        folder_lower = folder.lower()

        if "uk" in folder_lower or "british" in folder_lower:
            return "United Kingdom"
        elif "german" in folder_lower or "deutsch" in folder_lower:
            return "Germany"
        elif "french" in folder_lower or "france" in folder_lower:
            return "France"
        elif "norway" in folder_lower or "norwegian" in folder_lower:
            return "Norway"
        elif "spain" in folder_lower or "spanish" in folder_lower:
            return "Spain"
        elif "poland" in folder_lower or "polish" in folder_lower:
            return "Poland"
        elif "swiss" in folder_lower or "switzerland" in folder_lower:
            return "Switzerland"
        else:
            return "Europe"

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()
        logger.debug("Cleared data cache")


# Global instance for easy import
loader = CompetitorDataLoader()


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

    DEFAULT_DATA_PATH = (
        Path(__file__).parent.parent.parent.parent / "data" / "bond_yield.csv"
    )

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


class SP500MembershipData:
    """Container for S&P 500 membership data."""

    def __init__(self, memberships: dict[str, dict] | None = None):
        self.memberships = memberships or {}

    def is_member(self, ticker: str, as_of: date) -> bool:
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

    DEFAULT_DATA_PATH = (
        Path(__file__).parent.parent.parent.parent
        / "data"
        / "snp_500_add_removal_dates.csv"
    )

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
            if pd.notna(row["Date_Added"]) and row["Date_Added"] != "NA":
                date_added = pd.to_datetime(row["Date_Added"]).date()

            date_removed = None
            if pd.notna(row["Date_Removed"]) and row["Date_Removed"] != "NA":
                date_removed = pd.to_datetime(row["Date_Removed"]).date()

            memberships[ticker] = {
                "date_added": date_added,
                "date_removed": date_removed,
            }

        logger.info(f"Loaded S&P 500 membership data for {len(memberships)} tickers")

        return SP500MembershipData(memberships=memberships)
