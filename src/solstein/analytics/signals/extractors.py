"""Signal extractors for pulling data from various agents.

Extractors know how to pull specific signals from agent results
and convert them into Signal objects with confidence scores.
"""

from typing import Any

from .models import Signal, SignalCategory


class SignalExtractor:
    """Base class for signal extraction from agent data."""

    def extract(self, data: dict[str, Any]) -> list[Signal]:
        """Extract signals from agent data.

        Args:
            data: Dictionary of agent results

        Returns:
            List of extracted signals
        """
        raise NotImplementedError


class GitHubSignalExtractor(SignalExtractor):
    """Extract signals from GitHub agent results."""

    def extract(self, data: dict[str, Any]) -> list[Signal]:
        """Extract GitHub signals."""
        signals = []

        if not data:
            return signals

        repos = data.get("repositories", [])
        activity = data.get("activity", {})
        stats = data.get("stats", {})

        total_stars = sum(r.get("stars", 0) for r in repos)
        if total_stars > 0:
            signals.append(
                Signal(
                    name="Open Source Contribution",
                    category=SignalCategory.TECHNICAL,
                    description="GitHub stars, forks, contributions",
                    value=float(min(total_stars / 100, 10.0)),
                    text=f"{total_stars} total GitHub stars",
                    source="GitHub",
                    confidence=0.8,
                    evidence={"repo_count": len(repos), "total_stars": total_stars},
                )
            )

        commits_per_month = activity.get("commits_per_month", 0)
        if commits_per_month > 0:
            signals.append(
                Signal(
                    name="Product Deployment Frequency",
                    category=SignalCategory.GROWTH,
                    description="Releases per month (GitHub commits/PRs)",
                    value=float(min(commits_per_month / 10, 10.0)),
                    text=f"{commits_per_month} commits per month",
                    source="GitHub",
                    confidence=0.85,
                    evidence={"commits_per_month": commits_per_month},
                )
            )

        contributors = stats.get("total_contributors", 0)
        if contributors > 0:
            signals.append(
                Signal(
                    name="Engineering Team Size (GitHub)",
                    category=SignalCategory.HIRING,
                    description="Active contributors on GitHub",
                    value=float(min(contributors / 5, 10.0)),
                    text=f"{contributors} active contributors",
                    source="GitHub",
                    confidence=0.7,
                    evidence={"contributors": contributors},
                )
            )

        return signals


class FinancialSignalExtractor(SignalExtractor):
    """Extract signals from financial/funding data."""

    def extract(self, data: dict[str, Any]) -> list[Signal]:
        """Extract financial signals."""
        signals = []

        if not data:
            return signals

        funding = data.get("total_funding", 0)
        if funding > 0:
            signals.append(
                Signal(
                    name="Total Funding Raised",
                    category=SignalCategory.FINANCIAL,
                    description="Cumulative capital raised from all sources",
                    value=float(min(funding / 1000000, 10.0)),
                    text=f"${funding:,}",
                    source="Crunchbase/Pitchbook",
                    confidence=0.9,
                    evidence={"funding": funding},
                )
            )

        latest_round = data.get("latest_round", {})
        if latest_round:
            signals.append(
                Signal(
                    name="Latest Funding Round Size",
                    category=SignalCategory.FINANCIAL,
                    description="Size and valuation of most recent round",
                    value=float(min(latest_round.get("size", 0) / 1000000, 10.0)),
                    text=f"${latest_round.get('size', 0):,} at ${latest_round.get('valuation', 0):,} valuation",
                    source="Crunchbase",
                    confidence=0.85,
                    evidence=latest_round,
                )
            )

        runway_months = data.get("runway_months", 0)
        if runway_months > 0:
            signals.append(
                Signal(
                    name="Runway Months",
                    category=SignalCategory.FINANCIAL,
                    description="Months of runway at current burn rate",
                    value=float(min(runway_months / 12, 10.0)),
                    text=f"{runway_months} months of runway",
                    source="Financial Analysis",
                    confidence=0.6,
                    evidence={"runway_months": runway_months},
                )
            )

        return signals


class CompaniesHouseSignalExtractor(SignalExtractor):
    """Extract signals from Companies House data."""

    def extract(self, data: dict[str, Any]) -> list[Signal]:
        """Extract company operational signals."""
        signals = []

        if not data:
            return signals

        employees = data.get("number_of_employees", 0)
        if employees > 0:
            signals.append(
                Signal(
                    name="Total Headcount Growth",
                    category=SignalCategory.HIRING,
                    description="Total employees hired per month",
                    value=float(min(employees / 50, 10.0)),
                    text=f"{employees} employees",
                    source="Companies House",
                    confidence=0.85,
                    evidence={"employees": employees},
                )
            )

        revenue = data.get("revenue", 0)
        if revenue > 0:
            signals.append(
                Signal(
                    name="Annual Revenue",
                    category=SignalCategory.GROWTH,
                    description="Official registered annual revenue",
                    value=float(min(revenue / 1000000, 10.0)),
                    text=f"£{revenue:,}",
                    source="Companies House",
                    confidence=0.95,
                    evidence={"revenue": revenue},
                )
            )

        filings_recent = data.get("recent_filings", 0)
        if filings_recent > 0:
            signals.append(
                Signal(
                    name="Process Maturity Level",
                    category=SignalCategory.OPERATIONAL,
                    description="Degree of documented processes",
                    value=float(min(filings_recent / 5, 10.0)),
                    text=f"{filings_recent} recent filings",
                    source="Companies House",
                    confidence=0.7,
                    evidence={"recent_filings": filings_recent},
                )
            )

        return signals


class WebSearchSignalExtractor(SignalExtractor):
    """Extract signals from web search/news data."""

    def extract(self, data: dict[str, Any]) -> list[Signal]:
        """Extract market and strategic signals."""
        signals = []

        if not data:
            return signals

        mentions = data.get("press_mentions", 0)
        if mentions > 0:
            signals.append(
                Signal(
                    name="Media Mention Frequency",
                    category=SignalCategory.MARKET,
                    description="Press coverage in past 6 months",
                    value=float(min(mentions / 20, 10.0)),
                    text=f"{mentions} press mentions",
                    source="Web Search",
                    confidence=0.75,
                    evidence={"mentions": mentions},
                )
            )

        awards = data.get("industry_awards", [])
        if awards:
            signals.append(
                Signal(
                    name="Industry Award Count",
                    category=SignalCategory.MARKET,
                    description="Gartner, Forrester, or industry awards",
                    value=float(min(len(awards) / 2, 10.0)),
                    text=f"{len(awards)} awards: {', '.join(awards[:3])}",
                    source="Web Search",
                    confidence=0.8,
                    evidence={"awards": awards},
                )
            )

        product_reviews = data.get("product_reviews", [])
        if product_reviews:
            avg_rating = sum(r.get("rating", 5) for r in product_reviews) / len(
                product_reviews
            )
            signals.append(
                Signal(
                    name="Product Review Average",
                    category=SignalCategory.PRODUCT,
                    description="Average rating from review sites",
                    value=avg_rating,
                    text=f"{avg_rating:.1f}/5.0 average rating",
                    source="Review Sites",
                    confidence=0.8,
                    evidence={"review_count": len(product_reviews)},
                )
            )

        return signals


class AggregateSignalExtractor:
    """Orchestrates extraction from multiple sources."""

    def __init__(self):
        """Initialize with all extractors."""
        self.extractors = {
            "github": GitHubSignalExtractor(),
            "financial": FinancialSignalExtractor(),
            "companies_house": CompaniesHouseSignalExtractor(),
            "web_search": WebSearchSignalExtractor(),
        }

    def extract_all(self, agent_results: dict[str, dict[str, Any]]) -> list[Signal]:
        """Extract all signals from all agent results.

        Args:
            agent_results: Dictionary mapping agent names to their results

        Returns:
            List of all extracted signals
        """
        all_signals = []

        for agent_name, results in agent_results.items():
            if agent_name in self.extractors:
                extractor = self.extractors[agent_name]
                signals = extractor.extract(results)
                all_signals.extend(signals)

        return all_signals

    def extract_by_agent(
        self, agent_name: str, results: dict[str, Any]
    ) -> list[Signal]:
        """Extract signals from a single agent.

        Args:
            agent_name: Name of the agent
            results: Agent results dictionary

        Returns:
            List of extracted signals
        """
        if agent_name not in self.extractors:
            return []

        extractor = self.extractors[agent_name]
        return extractor.extract(results)
