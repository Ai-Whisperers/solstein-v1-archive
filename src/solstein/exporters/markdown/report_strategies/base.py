"""Base class for report generation strategies.

EPIC-022: Extracted from CompanyReportGenerator for modularity.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from solstein.domain.models import Company


class ReportStrategy(ABC):
    """Base class for report generation strategies.

    Each report type (corporate history, deep analysis, financial growth)
    implements its own strategy for generating the report.
    """

    def __init__(self, formatter: Any, interpreter: Any):
        """Initialize strategy with formatter and interpreter.

        Args:
            formatter: ReportFormatter instance
            interpreter: ScoreInterpreter instance
        """
        self.formatter = formatter
        self.interpreter = interpreter

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this report strategy."""
        pass

    @property
    @abstractmethod
    def filename_suffix(self) -> str:
        """Return the filename suffix for this report type."""
        pass

    @abstractmethod
    def generate(self, company: Company) -> str:
        """Generate the report content.

        Args:
            company: Company to generate report for

        Returns:
            Report content as markdown string
        """
        pass

    def get_output_path(self, company: Company, output_dir: Path) -> Path:
        """Get the output file path for this report.

        STORY-181: Use clean filenames (e.g., 'deep-analysis.md') since files
        are already placed in a company-named directory. No company name prefix.

        Args:
            company: Company being reported on
            output_dir: Output directory

        Returns:
            Path object for output file
        """
        filename = f"{self.filename_suffix.replace('_', '-')}.md"
        return output_dir / filename
