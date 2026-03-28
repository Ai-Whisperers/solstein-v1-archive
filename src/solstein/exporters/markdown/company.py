"""Company-specific report generators (EPIC-008).

EPIC-022: Refactored to use Strategy Pattern for report generation.

Uses modular report strategies for different report types:
- Corporate history
- Deep analysis
- Financial growth
"""

from __future__ import annotations

from pathlib import Path

from solstein.domain.models import Company

from .base import BaseReportGenerator
from .report_strategies import (
    CorporateHistoryStrategy,
    DeepAnalysisStrategy,
    FinancialGrowthStrategy,
)


class CompanyReportGenerator(BaseReportGenerator):
    """Generate reports for individual companies using Strategy Pattern.

    EPIC-022: Refactored to delegate to specialized report strategies.
    Each report type has its own strategy for modularity and testability.
    """

    def __init__(self, output_dir: Path | None = None):
        """Initialize generator with report strategies.

        Args:
            output_dir: Output directory for reports
        """
        super().__init__(output_dir)

        # Initialize report strategies
        self._strategies = {
            "corporate_history": CorporateHistoryStrategy(self.formatter, self.interpreter),
            "deep_analysis": DeepAnalysisStrategy(self.formatter, self.interpreter),
            "financial_growth": FinancialGrowthStrategy(self.formatter, self.interpreter),
        }

    def generate_corporate_history(self, company: Company, output_dir: Path) -> Path:
        """Generate corporate history report.

        Args:
            company: Company to generate report for
            output_dir: Output directory

        Returns:
            Path to generated report
        """
        strategy = self._strategies["corporate_history"]
        report = strategy.generate(company)
        output_path = strategy.get_output_path(company, output_dir)
        return self._write_report(report, output_path)

    def generate_deep_analysis(self, company: Company, output_dir: Path) -> Path:
        """Generate deep analytical report.

        Args:
            company: Company to generate report for
            output_dir: Output directory

        Returns:
            Path to generated report
        """
        strategy = self._strategies["deep_analysis"]
        report = strategy.generate(company)
        output_path = strategy.get_output_path(company, output_dir)
        return self._write_report(report, output_path)

    def generate_financial_growth(self, company: Company, output_dir: Path) -> Path:
        """Generate financial growth trajectory report.

        Args:
            company: Company to generate report for
            output_dir: Output directory

        Returns:
            Path to generated report
        """
        strategy = self._strategies["financial_growth"]
        report = strategy.generate(company)
        output_path = strategy.get_output_path(company, output_dir)
        return self._write_report(report, output_path)

    def generate_company_reports(self, company: Company, output_dir: Path | None = None) -> dict[str, Path]:
        """Generate all report types for a single company.

        STORY-181: Creates a company-named subdirectory and writes all
        reports there. Returns dict keyed by report type.

        Args:
            company: Company to generate reports for
            output_dir: Base output directory (company subdir created inside)

        Returns:
            Dict mapping report type name to output path
        """
        output_dir = output_dir or self.output_dir

        # Create company-specific directory (avoid double nesting)
        sanitized_name = self.formatter.sanitize_filename(company.name)
        if output_dir.name == sanitized_name:
            company_dir = output_dir
        else:
            company_dir = output_dir / sanitized_name
            company_dir.mkdir(parents=True, exist_ok=True)

        return {
            "corporate_history": self.generate_corporate_history(company, company_dir),
            "deep_analysis": self.generate_deep_analysis(company, company_dir),
            "financial_growth": self.generate_financial_growth(company, company_dir),
        }

    def generate_all_reports(self, company: Company, output_dir: Path | None = None) -> list[Path]:
        """Generate all report types for a company.

        Args:
            company: Company to generate reports for
            output_dir: Output directory (uses self.output_dir if None)

        Returns:
            List of paths to generated reports
        """
        reports = self.generate_company_reports(company, output_dir)
        return list(reports.values())
