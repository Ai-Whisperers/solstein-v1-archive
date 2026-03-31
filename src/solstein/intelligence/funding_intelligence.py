"""Funding intelligence analyzer for Epic 2.

Analyzes funding rounds, calculates investor quality, estimates runway.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from .financial_models import (
    FundingRound,
    FundingVelocity,
)

# Tier 1 venture capital firms - prestigious lead investors
TIER_1_INVESTORS = {
    "sequoia",
    "andreessen horowitz",
    "a16z",
    "benchmark",
    "greylock",
    "kleiner perkins",
    "kp",
    "index ventures",
    "accel",
    "bessemer",
    "bessemer venture partners",
    "general catalyst",
    "gc",
    "insight partners",
    "lightspeed",
    "lightspeed venture partners",
    "founders fund",
    "thrive capital",
    "tiger global",
    "softbank vision",
    "softbank",
    "norwest",
    "ivp",
    "institutional venture partners",
}

# Tier 2 investors - established but less prestigious
TIER_2_INVESTORS = {
    "balderton",
    "atomico",
    "northzone",
    "creandum",
    "point nine",
    "pointnine",
    "e.ventures",
    "eventures",
    "target global",
    "sap.io",
    "salesforce ventures",
    "google ventures",
    "gv",
    "intel capital",
    " qualcomm ventures",
    "comcast ventures",
    "m12",
    "microsoft m12",
}

# Strategic/corporate investors
STRATEGIC_INVESTORS = {
    "shell ventures",
    "bp ventures",
    "equinor ventures",
    "total energy ventures",
    "engie",
    "enel",
    "siemens",
    "ge ventures",
    "schneider electric",
    "abb",
    "honeywell",
    "rockwell",
    "emerson",
}

# Energy sector specialists
ENERGY_INVESTORS = {
    "energy impact partners",
    "eip",
    "cleantech group",
    "activate capital",
    "constellation technology ventures",
    "national grid partners",
    "next47",
    "siemens energy",
}


@dataclass
class FundingAnalysis:
    """Result of funding intelligence analysis."""

    rounds: list[FundingRound]
    total_raised: float | None
    investor_quality_score: float
    funding_velocity: FundingVelocity
    runway_estimate_months: int | None
    last_funding_date: date | None
    narrative: str


class FundingIntelligenceAnalyzer:
    """Analyze funding intelligence from various data sources."""

    def __init__(self):
        self.tier_1 = TIER_1_INVESTORS
        self.tier_2 = TIER_2_INVESTORS
        self.strategic = STRATEGIC_INVESTORS
        self.energy = ENERGY_INVESTORS

    def analyze(
        self,
        funding_rounds: list[dict[str, Any]],
        total_funding: float | None = None,
        current_revenue: float | None = None,
        employee_count: int | None = None,
    ) -> FundingAnalysis:
        """Analyze funding data.

        Args:
            funding_rounds: Raw funding round data from sources
            total_funding: Total funding raised in millions EUR
            current_revenue: Current annual revenue in millions EUR
            employee_count: Current employee count

        Returns:
            FundingAnalysis with enriched funding intelligence
        """
        # Parse funding rounds
        parsed_rounds = self._parse_funding_rounds(funding_rounds)

        # Calculate total if not provided
        if total_funding is None and parsed_rounds:
            total_funding = sum(r.amount for r in parsed_rounds if r.amount is not None)

        # Calculate investor quality
        investor_quality = self._calculate_investor_quality(parsed_rounds)

        # Determine funding velocity
        velocity = self._determine_velocity(parsed_rounds)

        # Estimate runway
        last_funding = self._get_last_funding_date(parsed_rounds)
        runway = self._estimate_runway(parsed_rounds, current_revenue, employee_count, total_funding)

        # Generate narrative
        narrative = self._generate_narrative(parsed_rounds, total_funding, investor_quality, velocity, runway)

        return FundingAnalysis(
            rounds=parsed_rounds,
            total_raised=total_funding,
            investor_quality_score=investor_quality,
            funding_velocity=velocity,
            runway_estimate_months=runway,
            last_funding_date=last_funding,
            narrative=narrative,
        )

    def _parse_funding_rounds(self, raw_rounds: list[dict[str, Any]]) -> list[FundingRound]:
        """Parse raw funding round data into structured format."""
        parsed = []

        for raw in raw_rounds:
            if not isinstance(raw, dict):
                continue

            # Extract round name
            round_name = raw.get("round", raw.get("round_name", "Unknown"))
            if isinstance(round_name, str):
                round_name = round_name.strip()
            else:
                round_name = "Unknown"

            # Extract amount
            amount = self._parse_amount(raw.get("amount"))

            # Extract date
            round_date = self._parse_date(raw.get("date", raw.get("announced_on")))

            # Extract investors
            lead = raw.get("lead_investor", raw.get("lead"))
            co_investors = raw.get("co_investors", raw.get("investors", []))
            if isinstance(co_investors, str):
                co_investors = [i.strip() for i in co_investors.split(",")]
            elif not isinstance(co_investors, list):
                co_investors = []

            # Extract valuation
            valuation = self._parse_amount(raw.get("valuation"))

            parsed.append(
                FundingRound(
                    round_name=round_name,
                    amount=amount,
                    date=round_date,
                    lead_investor=lead,
                    co_investors=co_investors,
                    valuation=valuation,
                    source=raw.get("source", "unknown"),
                )
            )

        # Sort by date (most recent first)
        parsed.sort(key=lambda x: x.date or date.min, reverse=True)

        return parsed

    def _parse_amount(self, value: Any) -> float | None:
        """Parse amount from various formats (returns millions)."""
        if value is None:
            return None

        if isinstance(value, (int, float)):
            # Assume already in millions if < 1000, otherwise convert
            if value > 1000000:
                return value / 1_000_000
            return float(value)

        if isinstance(value, str):
            value = value.lower().replace(",", "").replace("$", "").replace("€", "")
            value = value.replace("gbp", "").replace("usd", "").replace("eur", "")
            value = value.strip()
            try:
                # Check for millions/billions indicators
                if "b" in value:
                    num = float(value.replace("b", "").strip())
                    return num * 1000  # Convert billions to millions
                elif "m" in value:
                    return float(value.replace("m", "").strip())
                else:
                    num = float(value)
                    # Guess unit based on magnitude
                    if num > 1000000:
                        return num / 1_000_000
                    elif num < 100:
                        return num  # Assume already in millions
                    else:
                        return num / 1_000_000
            except ValueError:
                return None

        return None

    def _parse_date(self, value: Any) -> date | None:
        """Parse date from various formats."""
        if value is None:
            return None

        if isinstance(value, date):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            # Try various formats
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue

        return None

    def _calculate_investor_quality(self, rounds: list[FundingRound]) -> float:
        """Calculate investor quality score (0-10)."""
        if not rounds:
            return 0.0

        all_investors = []
        for r in rounds:
            if r.lead_investor:
                all_investors.append(r.lead_investor.lower())
            for co in r.co_investors:
                if isinstance(co, str):
                    all_investors.append(co.lower())

        if not all_investors:
            return 5.0  # Neutral score

        # Score based on investor tiers
        score = 5.0  # Base score

        for investor in all_investors:
            investor_lower = investor.lower()

            # Check for tier matches
            if any(t1 in investor_lower for t1 in self.tier_1):
                score += 1.5
            elif any(t2 in investor_lower for t2 in self.tier_2):
                score += 1.0
            elif any(st in investor_lower for st in self.strategic):
                score += 0.8
            elif any(en in investor_lower for en in self.energy):
                score += 0.6

        # Normalize to 0-10 scale
        # More rounds with quality investors = higher score
        score = min(10.0, score + (len(rounds) * 0.5))

        return round(score, 1)

    def _determine_velocity(self, rounds: list[FundingRound]) -> FundingVelocity:
        """Determine funding velocity based on round frequency."""
        if len(rounds) < 2:
            return FundingVelocity.SPARSE

        # Get dates
        dates = [r.date for r in rounds if r.date]
        if len(dates) < 2:
            return FundingVelocity.SPARSE

        dates.sort()

        # Calculate average months between rounds
        total_days = (dates[-1] - dates[0]).days
        months_between = total_days / 30.0 / (len(dates) - 1)

        if months_between <= 12:
            return FundingVelocity.RAPID
        elif months_between <= 24:
            return FundingVelocity.STEADY
        else:
            return FundingVelocity.SPARSE

    def _get_last_funding_date(self, rounds: list[FundingRound]) -> date | None:
        """Get most recent funding date."""
        dates = [r.date for r in rounds if r.date]
        return max(dates) if dates else None

    def _estimate_runway(
        self,
        rounds: list[FundingRound],
        current_revenue: float | None,
        employee_count: int | None,
        total_funding: float | None,
    ) -> int | None:
        """Estimate runway in months."""
        if not total_funding or total_funding <= 0:
            return None

        # Estimate burn rate
        if current_revenue and current_revenue > 0:
            # If profitable or break-even, infinite runway
            # Simplified: assume break-even at revenue = 2x burn
            estimated_burn = current_revenue / 2
            if estimated_burn <= 0:
                estimated_burn = 0.5  # Minimum 500K/year
        elif employee_count and employee_count > 0:
            # Estimate based on employees (avg 150K EUR/employee/year for tech)
            estimated_burn = (employee_count * 150) / 1000  # Convert to millions
        else:
            # Default assumption
            estimated_burn = total_funding / 3  # Assume 3 years runway if no data

        # Get last funding amount
        last_round_amount = None
        for r in rounds:
            if r.amount and r.date:
                # Check if within last 18 months
                if r.date > (datetime.now().date() - timedelta(days=547)):
                    last_round_amount = r.amount
                    break

        if last_round_amount:
            runway_months = int((last_round_amount / estimated_burn) * 12)
        else:
            # Use total funding (less accurate)
            runway_months = int((total_funding / estimated_burn) * 12)

        return max(0, min(60, runway_months))  # Cap at 60 months

    def _generate_narrative(
        self,
        rounds: list[FundingRound],
        total_funding: float | None,
        investor_quality: float,
        velocity: FundingVelocity,
        runway: int | None,
    ) -> str:
        """Generate funding narrative."""
        parts = []

        # Total funding
        if total_funding:
            funding_desc = (
                "substantial"
                if total_funding >= 100
                else "significant"
                if total_funding >= 50
                else "moderate"
                if total_funding >= 10
                else "limited"
            )
            parts.append(
                f"Company has raised a {funding_desc} €{total_funding:.1f}M across {len(rounds)} funding round(s)."
            )
        else:
            parts.append(f"Company has completed {len(rounds)} funding round(s).")

        # Investor quality
        quality_desc = (
            "exceptional"
            if investor_quality >= 8
            else "strong"
            if investor_quality >= 6
            else "moderate"
            if investor_quality >= 4
            else "limited"
        )
        parts.append(f"Investor quality score of {investor_quality}/10 indicates {quality_desc} investor backing.")

        # Velocity
        velocity_desc = {
            FundingVelocity.RAPID: "rapid fundraising pace suggests high growth and investor interest",
            FundingVelocity.STEADY: "steady fundraising pattern indicates sustainable growth",
            FundingVelocity.SPARSE: "sparse funding history may indicate bootstrapping or limited capital needs",
        }
        parts.append(f"{velocity_desc[velocity]}.")

        # Runway
        if runway is not None:
            if runway >= 24:
                parts.append(f"Strong financial position with estimated {runway}+ months of runway.")
            elif runway >= 12:
                parts.append(f"Adequate runway of approximately {runway} months.")
            else:
                parts.append(f"Limited runway of ~{runway} months - potential funding need.")

        # Recent rounds
        if rounds and rounds[0].date:
            latest = rounds[0]
            months_ago = (datetime.now().date() - latest.date).days / 30
            if months_ago < 12:
                parts.append(
                    f"Most recent {latest.round_name} round (€{latest.amount or 'undisclosed'}M) "
                    f"closed {months_ago:.0f} months ago."
                )

        return " ".join(parts)
