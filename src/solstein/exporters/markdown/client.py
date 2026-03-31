"""Client report generator for competitive analysis.

Extracted from generator.py as part of EPIC-021 file splitting.
Generates comprehensive client reports with competitive analysis.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from solstein.analytics.constants import derive_threat_level
from solstein.domain.models import Company

from .company import CompanyReportGenerator


class ClientReportGenerator(CompanyReportGenerator):
    """Extended report generator for client-specific reports."""

    def generate_client_report(
        self,
        client_company: Company,
        competitors: list[Company],
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate complete client report with competitive analysis."""
        output_dir = output_dir or self.output_dir / self.formatter.sanitize_filename(client_company.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        # Generate individual company reports
        generated.update(self.generate_company_reports(client_company, output_dir))

        # Generate competitive analysis
        generated["competitive_analysis"] = self._generate_competitive_analysis(client_company, competitors, output_dir)

        # Generate market overview for this client's market
        from .market import MarketReportGenerator

        market_gen = MarketReportGenerator(output_dir)
        generated["market_overview"] = market_gen.generate_market_overview(competitors + [client_company], output_dir)

        logger.info(f"Generated client report for {client_company.name} in {output_dir}")
        return generated

    def _generate_competitive_analysis(self, client: Company, competitors: list[Company], output_dir: Path) -> Path:
        """Generate competitive analysis report."""

        # Sort competitors by score
        sorted_comp = sorted(competitors, key=lambda c: c.composite_score or 0, reverse=True)

        # Find direct competitors (similar tier/score)
        [c for c in sorted_comp if c.tier == client.tier and c.id != client.id][:5]

        # Find threats (higher score competitors)
        [c for c in sorted_comp if (c.composite_score or 0) > (client.composite_score or 0)][:5]

        def _fmt_float(value: float | None) -> str:
            if value is None:
                return "N/A"
            return f"{value:.1f}"

        self._avg([c.ai_score for c in competitors if c.ai_score is not None]) if competitors else None

    def _generate_competitive_analysis(
        self,
        client: Company,
        competitors: list[Company],
        output_dir: Path,
    ) -> Path:
        """Generate competitive analysis report using section generators.

        EPIC-020: Refactored from 222-line monolithic function to use
        ReportSectionGenerator for better maintainability.
        """
        from .report_sections import ReportSectionGenerator

        # Identify competitive threats
        threats = [c for c in competitors if (c.composite_score or 0) > (client.composite_score or 0)]
        direct = [c for c in competitors if c.tier == client.tier]

        # Calculate market averages
        ai_market_avg = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
        growth_market_avg = self._avg([c.growth_score for c in competitors if c.growth_score is not None])
        growth_top = max([c.growth_score or 0 for c in competitors], default=None)
        health_market_avg = self._avg([c.financial_health_score for c in competitors if c.financial_health_score is not None])
        health_top = max([c.financial_health_score or 0 for c in competitors], default=None)
        position_market_avg = self._avg([c.competitive_position_score for c in competitors if c.competitive_position_score is not None])
        position_top = max([c.competitive_position_score or 0 for c in competitors], default=None)
        composite_market_avg = self._avg([c.composite_score for c in competitors if c.composite_score is not None])
        composite_top = max([c.composite_score or 0 for c in competitors], default=None)

        # Check data authenticity
        is_authentic, warning = self._check_data_authenticity([client] + competitors)

        # Sort competitors by score
        sorted_comp = sorted(
            [c for c in competitors if c.composite_score is not None],
            key=lambda c: c.composite_score or 0,
            reverse=True,
        )

        # Generate report sections
        section_gen = ReportSectionGenerator(self.formatter)

        report_parts = [
            section_gen.generate_executive_summary(client, competitors, threats, ai_market_avg, warning),
            section_gen.generate_client_profile(
                client, competitors,
                self._rank_revenue, self._rank_growth, self._rank_score, self._rank_ai, self._rank_saas
            ),
            section_gen.generate_competitive_positioning(
                client, competitors, growth_market_avg, growth_top,
                health_market_avg, health_top, position_market_avg, position_top,
                composite_market_avg, composite_top
            ),
            section_gen.generate_direct_competitors(client, direct),
            section_gen.generate_competitor_details(client, direct),
            section_gen.generate_competitive_threats(client, threats),
            section_gen.generate_competitive_landscape(client, sorted_comp),
            section_gen.generate_strategic_recommendations(
                client, competitors, threats, self._generate_client_strengths, self._generate_client_weaknesses
            ),
            section_gen.generate_appendix(sorted_comp, derive_threat_level),
        ]

        report = "\n".join(report_parts)

        output_path = output_dir / "competitive-analysis.md"
        output_path.write_text(report)
        return output_path


    def _rank_revenue(self, client: Company, competitors: list[Company]) -> str:
        """Get revenue rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.financials.revenue],
            key=lambda c: c.financials.revenue or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_growth(self, client: Company, competitors: list[Company]) -> str:
        """Get growth rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.revenue_cagr_3yr],
            key=lambda c: c.revenue_cagr_3yr or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_score(self, client: Company, competitors: list[Company]) -> str:
        """Get score rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.composite_score],
            key=lambda c: c.composite_score or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_ai(self, client: Company, competitors: list[Company]) -> str:
        """Get AI score rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.ai_score is not None],
            key=lambda c: c.ai_score or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_saas(self, client: Company, competitors: list[Company]) -> str:
        """Get SaaS maturity rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.saas_maturity],
            key=lambda c: c.saas_maturity or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _generate_client_strengths(self, client: Company, competitors: list[Company]) -> str:
        """Generate client strengths."""
        client_score = client.composite_score or 0
        market_avg = self._avg([c.composite_score for c in competitors if c.composite_score])

        strengths = []
        if client_score > market_avg + 1:
            strengths.append(f"Superior composite score ({client_score:.1f} vs {market_avg:.1f} market avg)")

        if client.saas_maturity:
            avg_saas = self._avg([c.saas_maturity for c in competitors if c.saas_maturity])
            if client.saas_maturity > avg_saas + 1:
                strengths.append(f"Advanced SaaS maturity ({client.saas_maturity} vs {avg_saas:.1f} avg)")

        if client.ai_score:
            avg_ai = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
            if client.ai_score > avg_ai:
                strengths.append(f"Strong AI position ({client.ai_score}/10 vs {avg_ai:.1f} avg)")

        return "\n".join([f"- {s}" for s in strengths]) if strengths else "- No significant strengths identified"

    def _generate_client_weaknesses(self, client: Company, competitors: list[Company]) -> str:
        """Generate client weaknesses."""
        weaknesses = []
        classification = getattr(client, "classification", None)

        # AI gap analysis
        if client.ai_score is not None:
            avg_ai = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
            if client.ai_score < avg_ai - 1:
                weaknesses.append(f"AI capability gap ({client.ai_score}/10 vs {avg_ai:.1f} market avg)")
            elif client.ai_score < avg_ai - 0.5:
                weaknesses.append(f"Below-average AI maturity ({client.ai_score}/10)")
            elif client.ai_score < 5:
                weaknesses.append(
                    f"Limited AI adoption ({client.ai_score}/10) - opportunity for digital transformation"
                )

        # SaaS maturity gaps
        if client.saas_maturity:
            avg_saas = self._avg([c.saas_maturity for c in competitors if c.saas_maturity])
            if client.saas_maturity < avg_saas - 1:
                weaknesses.append(f"SaaS maturity gap ({client.saas_maturity} vs {avg_saas:.1f} avg)")
            elif client.saas_maturity < 5:
                weaknesses.append(f"Legacy technology stack (SaaS: {client.saas_maturity}/10)")

        # Financial/market position gaps
        client_score = client.composite_score or 0
        market_avg = self._avg([c.composite_score for c in competitors if c.composite_score])
        if client_score < market_avg - 1:
            weaknesses.append(f"Below-market composite score ({client_score:.1f} vs {market_avg:.1f} avg)")
        elif classification == "Lead":
            weaknesses.append(f"Legacy classification ({client_score:.1f}/10) - transformation opportunity")

        if not client.latest_valuation_eur:
            weaknesses.append("No disclosed valuation (competitors have clearer market positioning)")

        if not client.total_funding_raised_eur and any(c.total_funding_raised_eur for c in competitors):
            weaknesses.append("Bootstrapped/unfunded vs. funded competitors")

        # Growth concerns
        if client.revenue_cagr_3yr is not None and client.revenue_cagr_3yr < 5:
            weaknesses.append(f"Low growth trajectory ({client.revenue_cagr_3yr}% CAGR)")

        # For Phoenix/high-performing companies, show strategic considerations instead of weaknesses
        if classification == "Phoenix" and not weaknesses:
            weaknesses.append(f"**Strategic Position**: Phoenix-class company ({client_score:.1f}/10)")
            # Add market leadership risks
            threats = [c for c in competitors if (c.composite_score or 0) > (client.composite_score or 0)]
            if threats:
                weaknesses.append(f"Market leadership challenged by {len(threats)} higher-scoring competitor(s)")
            else:
                weaknesses.append("Market leader - maintain innovation edge to defend position")

            # Add scale-based considerations
            revenue = getattr(client.financials, "revenue", 0) or 0
            if revenue < 10:
                weaknesses.append(f"High-growth but small scale (€{revenue:.1f}M) - execution risk at scale")

        if weaknesses:
            return "\n".join([f"- {w}" for w in weaknesses])
        else:
            return f"- Market-competitive position across key metrics (score: {client_score:.1f}/10)"

    def _avg(self, values: list) -> float:
        """Calculate average."""
        values = [v for v in values if v is not None and v != float("inf")]
        return sum(values) / len(values) if values else 0
