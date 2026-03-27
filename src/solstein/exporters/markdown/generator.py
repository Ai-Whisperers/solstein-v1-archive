"""Markdown report generator for SolStein intelligence reports.

Generates professional reports from Company data - corporate history,
deep analysis, financial growth, and competitive dashboards.

This module serves as the orchestration layer for report generation,
delegating to specialized generators in the markdown package.

EPIC-021: Refactored from monolithic 1,402-line file to modular structure.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from solstein.domain.models import Company
from solstein.exceptions import SyntheticDataBlockingError

# Import decomposed modules for delegation
from .base import BaseReportGenerator, ReportFormatter, ScoreInterpreter
from .client import ClientReportGenerator
from .company import CompanyReportGenerator
from .helpers import (
    calculate_3yr_growth,
    classify_trajectory,
    format_funding_detail,
    format_funding_rounds,
    generate_strategic_assessment,
    generate_strengths,
    generate_weaknesses,
    interpret_employee_growth,
    interpret_funding,
    interpret_geographic,
    interpret_ma,
    interpret_saas,
    score_employee_growth,
    score_funding,
    score_geographic,
    score_ma,
)
from .llm_enhanced import LLMEnhancedReportGenerator
from .market import MarketReportGenerator


class ReportGenerator(BaseReportGenerator):
    """Generate markdown intelligence reports from Company data.

    This is the main orchestration class that delegates to specialized
    generators for different report types.
    """

    def __init__(self, output_dir: Path | None = None, use_llm: bool = True):
        super().__init__(output_dir)
        self.use_llm = use_llm
        self._llm_enhancer = None
        if use_llm:
            try:
                from ..llm import LLMReportEnhancer

                self._llm_enhancer = LLMReportEnhancer()
            except Exception as e:
                logger.warning(f"LLM enhancer not available: {e}")

    def _check_data_authenticity(self, companies: list[Company]) -> tuple[bool, str]:
        """Check if company data is authentic (not synthetic).

        Raises:
            SyntheticDataBlockingError: If any synthetic data is detected

        Returns:
            Tuple of (is_authentic, warning_message)
        """
        synthetic_count = 0
        total = len(companies)
        synthetic_company_names = []

        for company in companies:
            # Check for synthetic indicators
            data_source = getattr(company, "data_source_type", None)
            if data_source == "synthetic":
                synthetic_count += 1
                synthetic_company_names.append(company.name or "Unknown")
                continue

            # Check company name patterns - only match at start of name (case insensitive)
            name = (getattr(company, "name", "") or "").lower()
            # Only flag if name starts with these patterns (exact prefix match)
            synthetic_patterns = ["test-company", "test_company", "synthetic", "fake"]
            if any(name.startswith(pattern) for pattern in synthetic_patterns):
                synthetic_count += 1
                synthetic_company_names.append(company.name or "Unknown")
                continue

        if synthetic_count == 0:
            return True, ""

        # Raise exception instead of just warning
        synthetic_pct = (synthetic_count / total * 100) if total > 0 else 0
        synthetic_names_str = ", ".join(synthetic_company_names[:5])  # Show first 5
        if len(synthetic_company_names) > 5:
            synthetic_names_str += f" and {len(synthetic_company_names) - 5} more"

        raise SyntheticDataBlockingError(
            f"Found {synthetic_count} out of {total} companies ({synthetic_pct:.1f}%) with synthetic data. "
            f"Synthetic companies: {synthetic_names_str}"
        )

    def generate_all_reports(self, companies: list[Company], output_subdir: str | None = None) -> dict[str, Path]:
        """Generate all report types for all companies."""
        if output_subdir:
            report_dir = self.output_dir / output_subdir
        else:
            report_dir = self.output_dir
        report_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        for company in companies:
            company_reports = self.generate_company_reports(company, report_dir)
            generated[company.name] = company_reports

        # Generate market overview if multiple companies
        if len(companies) > 1:
            overview_path = self.generate_market_overview(companies, report_dir)
            generated["market_overview"] = overview_path

        logger.info(f"Generated {len(generated)} report sets in {report_dir}")
        return generated

    def generate_company_reports(self, company: Company, output_dir: Path | None = None) -> dict[str, Path]:
        """Generate all report types for a single company.

        Delegates to CompanyReportGenerator for maintainability.
        """
        output_dir = output_dir or self.output_dir

        # Create company-specific directory (avoid double nesting)
        sanitized_name = self.formatter.sanitize_filename(company.name)
        if output_dir.name == sanitized_name:
            # Already in company directory, don't nest further
            company_dir = output_dir
        else:
            company_dir = output_dir / sanitized_name
            company_dir.mkdir(parents=True, exist_ok=True)

        # Delegate to specialized generator
        company_gen = CompanyReportGenerator(output_dir)
        generated = {
            "corporate_history": company_gen.generate_corporate_history(company, company_dir),
            "deep_analysis": company_gen.generate_deep_analysis(company, company_dir),
            "financial_growth": company_gen.generate_financial_growth(company, company_dir),
        }

        return generated

    def generate_corporate_history(self, company: Company, output_dir: Path) -> Path:
        """Generate corporate history report."""
        company_gen = CompanyReportGenerator(self.output_dir)
        return company_gen.generate_corporate_history(company, output_dir)

    def generate_deep_analysis(self, company: Company, output_dir: Path) -> Path:
        """Generate deep analysis report."""
        company_gen = CompanyReportGenerator(self.output_dir)
        return company_gen.generate_deep_analysis(company, output_dir)

    def generate_financial_growth(self, company: Company, output_dir: Path) -> Path:
        """Generate financial growth report."""
        company_gen = CompanyReportGenerator(self.output_dir)
        return company_gen.generate_financial_growth(company, output_dir)

    def generate_market_overview(self, companies: list[Company], output_dir: Path) -> Path:
        """Generate market overview report with all companies.

        Delegates to MarketReportGenerator for maintainability.
        """
        # Delegate to specialized generator
        market_gen = MarketReportGenerator(output_dir)
        return market_gen.generate_market_overview(companies, output_dir)


def generate_enhanced_report(
    company_name: str,
    use_llm: bool = True,
    output_dir: str | None = None,
) -> dict[str, Path]:
    """Convenience function to generate report for a company.

    Args:
        company_name: Name of company to analyze
        use_llm: Whether to use LLM enhancements
        output_dir: Output directory path

    Returns:
        Dict of generated report files
    """
    from ..analytics.scoring import GrowthScorer
    from ..data.loaders import CompetitorDataLoader

    loader = CompetitorDataLoader()
    companies = loader.load_companies()

    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(c) for c in companies]

    target = None
    for c in scored:
        if company_name.lower() in c.name.lower():
            target = c
            break

    if not target:
        raise ValueError(f"Company not found: {company_name}")

    competitors = [c for c in scored if c.id != target.id]

    if use_llm:
        generator = LLMEnhancedReportGenerator(output_dir=Path(output_dir) if output_dir else None)
        return asyncio.run(generator.generate_llm_enhanced_report(target, competitors))
    else:
        generator = ClientReportGenerator(output_dir=Path(output_dir) if output_dir else None, use_llm=False)
        return generator.generate_client_report(target, competitors)


# Backward compatibility exports
__all__ = [
    "ReportGenerator",
    "ClientReportGenerator",
    "LLMEnhancedReportGenerator",
    "CompanyReportGenerator",
    "MarketReportGenerator",
    "BaseReportGenerator",
    "ReportFormatter",
    "ScoreInterpreter",
    "generate_enhanced_report",
    # Helper functions for backward compatibility
    "classify_trajectory",
    "calculate_3yr_growth",
    "generate_strengths",
    "generate_weaknesses",
    "generate_strategic_assessment",
    "format_funding_rounds",
    "format_funding_detail",
    "score_funding",
    "score_employee_growth",
    "score_geographic",
    "score_ma",
    "interpret_funding",
    "interpret_employee_growth",
    "interpret_geographic",
    "interpret_ma",
    "interpret_saas",
]
