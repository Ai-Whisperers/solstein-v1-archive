"""Signal extractors for pulling data from various agents.

Extractors know how to pull specific signals from agent results
and convert them into SignalExtraction objects with confidence scores.
"""

from typing import Any

from solstein.domain.models import SignalExtraction


class SignalExtractor:
    """Base class for signal extraction from agent data."""

    def extract(self, data: dict[str, Any]) -> list[SignalExtraction]:
        """Extract signals from agent data.

        Args:
            data: Dictionary of agent results

        Returns:
            List of extracted signals
        """
        raise NotImplementedError


class GitHubSignalExtractor(SignalExtractor):
    """Extract signals from GitHub agent results."""

    def extract(self, data: dict[str, Any]) -> list[SignalExtraction]:
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
                SignalExtraction(
                    signal_name="Open Source Contribution",
                    signal_value=float(min(total_stars / 100, 10.0)),
                    signal_confidence=0.8,
                    source_facts=["GitHub"],
                    calculation_method="extraction",
                    reasoning=f"{total_stars} total GitHub stars across {len(repos)} repos",
                )
            )

        commits_per_month = activity.get("commits_per_month", 0)
        if commits_per_month > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Product Deployment Frequency",
                    signal_value=float(min(commits_per_month / 10, 10.0)),
                    signal_confidence=0.85,
                    source_facts=["GitHub"],
                    calculation_method="extraction",
                    reasoning=f"{commits_per_month} commits per month",
                )
            )

        contributors = stats.get("total_contributors", 0)
        if contributors > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Engineering Team Size (GitHub)",
                    signal_value=float(min(contributors / 5, 10.0)),
                    signal_confidence=0.7,
                    source_facts=["GitHub"],
                    calculation_method="extraction",
                    reasoning=f"{contributors} active contributors",
                )
            )

        return signals


class FinancialSignalExtractor(SignalExtractor):
    """Extract signals from financial/funding data."""

    def extract(self, data: dict[str, Any]) -> list[SignalExtraction]:
        """Extract financial signals."""
        signals = []

        if not data:
            return signals

        funding = data.get("total_funding", 0)
        if funding > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Total Funding Raised",
                    signal_value=float(min(funding / 1_000_000, 10.0)),
                    signal_confidence=0.9,
                    source_facts=["Crunchbase/Pitchbook"],
                    calculation_method="extraction",
                    reasoning=f"${funding:,} total funding",
                )
            )

        latest_round = data.get("latest_round", {})
        if latest_round:
            signals.append(
                SignalExtraction(
                    signal_name="Latest Funding Round Size",
                    signal_value=float(min(latest_round.get("size", 0) / 1_000_000, 10.0)),
                    signal_confidence=0.85,
                    source_facts=["Crunchbase"],
                    calculation_method="extraction",
                    reasoning=(f"${latest_round.get('size', 0):,} at ${latest_round.get('valuation', 0):,} valuation"),
                )
            )

        runway_months = data.get("runway_months", 0)
        if runway_months > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Runway Months",
                    signal_value=float(min(runway_months / 12, 10.0)),
                    signal_confidence=0.6,
                    source_facts=["Financial Analysis"],
                    calculation_method="extraction",
                    reasoning=f"{runway_months} months of runway",
                )
            )

        return signals


class CompaniesHouseSignalExtractor(SignalExtractor):
    """Extract signals from Companies House data."""

    def extract(self, data: dict[str, Any]) -> list[SignalExtraction]:
        """Extract company operational signals."""
        signals = []

        if not data:
            return signals

        employees = data.get("number_of_employees", 0)
        if employees > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Total Headcount",
                    signal_value=float(min(employees / 50, 10.0)),
                    signal_confidence=0.85,
                    source_facts=["Companies House"],
                    calculation_method="extraction",
                    reasoning=f"{employees} employees",
                )
            )

        revenue = data.get("revenue", 0)
        if revenue > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Annual Revenue",
                    signal_value=float(min(revenue / 1_000_000, 10.0)),
                    signal_confidence=0.95,
                    source_facts=["Companies House"],
                    calculation_method="extraction",
                    reasoning=f"£{revenue:,} annual revenue",
                )
            )

        filings_recent = data.get("recent_filings", 0)
        if filings_recent > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Process Maturity Level",
                    signal_value=float(min(filings_recent / 5, 10.0)),
                    signal_confidence=0.7,
                    source_facts=["Companies House"],
                    calculation_method="extraction",
                    reasoning=f"{filings_recent} recent filings",
                )
            )

        return signals


class WebSearchSignalExtractor(SignalExtractor):
    """Extract signals from web search/news data."""

    def extract(self, data: dict[str, Any]) -> list[SignalExtraction]:
        """Extract market and strategic signals."""
        signals = []

        if not data:
            return signals

        mentions = data.get("press_mentions", 0)
        if mentions > 0:
            signals.append(
                SignalExtraction(
                    signal_name="Media Mention Frequency",
                    signal_value=float(min(mentions / 20, 10.0)),
                    signal_confidence=0.75,
                    source_facts=["Web Search"],
                    calculation_method="extraction",
                    reasoning=f"{mentions} press mentions",
                )
            )

        awards = data.get("industry_awards", [])
        if awards:
            signals.append(
                SignalExtraction(
                    signal_name="Industry Award Count",
                    signal_value=float(min(len(awards) / 2, 10.0)),
                    signal_confidence=0.8,
                    source_facts=["Web Search"],
                    calculation_method="extraction",
                    reasoning=f"{len(awards)} awards: {', '.join(awards[:3])}",
                )
            )

        product_reviews = data.get("product_reviews", [])
        if product_reviews:
            avg_rating = sum(r.get("rating", 5) for r in product_reviews) / len(product_reviews)
            signals.append(
                SignalExtraction(
                    signal_name="Product Review Average",
                    signal_value=avg_rating,
                    signal_confidence=0.8,
                    source_facts=["Review Sites"],
                    calculation_method="average",
                    reasoning=f"{avg_rating:.1f}/5.0 average rating from {len(product_reviews)} reviews",
                )
            )

        return signals


class AggregateSignalExtractor:
    """Orchestrates extraction from multiple sources."""

    def __init__(self):
        """Initialize with all extractors."""
        self.extractors: dict[str, SignalExtractor] = {
            "github": GitHubSignalExtractor(),
            "financial": FinancialSignalExtractor(),
            "companies_house": CompaniesHouseSignalExtractor(),
            "web_search": WebSearchSignalExtractor(),
        }

    def extract_all(self, agent_results: dict[str, dict[str, Any]]) -> list[SignalExtraction]:
        """Extract all signals from all agent results.

        Args:
            agent_results: Dictionary mapping agent names to their results

        Returns:
            List of all extracted signals
        """
        all_signals: list[SignalExtraction] = []

        for agent_name, results in agent_results.items():
            if agent_name in self.extractors:
                extractor = self.extractors[agent_name]
                signals = extractor.extract(results)
                all_signals.extend(signals)

        return all_signals

    def extract_by_agent(self, agent_name: str, results: dict[str, Any]) -> list[SignalExtraction]:
        """Extract signals from a single agent.

        Args:
            agent_name: Name of the agent
            results: Agent results dictionary

        Returns:
            List of extracted signals
        """
        if agent_name not in self.extractors:
            return []

        return self.extractors[agent_name].extract(results)
