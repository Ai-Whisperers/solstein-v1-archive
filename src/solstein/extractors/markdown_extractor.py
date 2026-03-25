"""Markdown file extractor for SolStein.

EPIC-022: Refactored to use modular parsers and converters.

Extracts structured data from markdown files following SolStein's format.
Uses modular parsers for different content types and converters for data transformation.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from ..domain.models import (
    Company,
    CompanyTier,
)
from .batch import BatchExtractor
from .parsers import (
    BasicMetricsParser,
    ConfidenceParser,
    DataConverter,
    DescriptionParser,
    MetadataParser,
    MetricJustificationsParser,
    MetricSourcesParser,
    SourceLinksParser,
)


class MarkdownExtractor:
    """Extract structured data from markdown files using modular parsers.

    EPIC-022: Refactored to use Strategy Pattern for content parsing.
    Each parser handles a specific aspect of content extraction.
    """

    def __init__(self, use_llm: bool = False) -> None:
        """Initialize extractor with parsers.

        Args:
            use_llm: Whether to use LLM for financial extraction
        """
        # Initialize parsers (Strategy Pattern)
        self._parsers = [
            BasicMetricsParser(),
            MetadataParser(),
            DescriptionParser(),
            SourceLinksParser(),
            MetricSourcesParser(),
            MetricJustificationsParser(),
            ConfidenceParser(),
        ]

        # Initialize converter
        self._converter = DataConverter()

        self._llm_extractor: Any | None = None

        # Optional LLM extractor
        if use_llm:
            from .llm_financial_extractor import LLMFinancialExtractor

            self._llm_extractor = LLMFinancialExtractor()

    def extract_from_file(self, file_path: Path) -> dict[str, Any] | None:
        """Extract data from a single markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Extracted data dictionary or None if failed
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            return self._parse_content(content, str(file_path))
        except Exception as e:
            logger.error(f"Failed to extract from {file_path}: {e}")
            return None

    def _parse_content(self, content: str, source: str) -> dict[str, Any]:
        """Parse markdown content using all parsers.

        Args:
            content: Markdown content
            source: Source identifier

        Returns:
            Merged extracted data
        """
        data: dict[str, Any] = {"source": source}

        # Run all parsers and merge results
        for parser in self._parsers:
            try:
                parsed = parser.parse(content)
                data.update(parsed)
            except Exception as e:
                logger.warning(f"Parser {parser.name} failed: {e}")

        # Apply LLM extraction if enabled
        if self._llm_extractor:
            try:
                llm_data = self._llm_extractor.extract(content)
                data.update(llm_data)
            except Exception as e:
                logger.warning(f"LLM extraction failed: {e}")

        return data

    def to_company_profile(self, extracted_data: dict[str, Any]) -> Company:
        """Convert extracted data to Company domain model.

        Args:
            extracted_data: Data from extract_from_file

        Returns:
            Company domain model
        """
        # Parse basic fields
        name = extracted_data.get("name", "Unknown")
        industry = extracted_data.get("industry")
        description = extracted_data.get("description")

        # Parse financial metrics
        revenue = self._converter.parse_numeric(extracted_data.get("revenue"))
        growth_rate = self._converter.parse_percentage(extracted_data.get("growth_rate"))
        employees = self._converter.parse_numeric(extracted_data.get("employees"))
        profit_margin = self._converter.parse_percentage(extracted_data.get("profit_margin"))

        # Parse enums
        ai_maturity = self._converter.parse_ai_maturity(extracted_data.get("ai_maturity"))
        threat_level = self._converter.parse_threat_level(extracted_data.get("threat_level"))
        tier = self._converter.parse_tier(extracted_data.get("tier"))

        # Determine tier from revenue if not specified
        if tier == CompanyTier.TIER_3 and revenue:
            tier = self._converter.determine_tier_from_revenue(revenue)

        # Parse confidence levels
        confidence_levels = extracted_data.get("confidence_levels", {})
        revenue_confidence = self._converter.parse_confidence(confidence_levels.get("revenue"))
        growth_confidence = self._converter.parse_confidence(confidence_levels.get("growth_rate"))

        # Create company profile using actual Company field names
        return Company(
            id=name.lower().replace(" ", "_"),
            name=name,
            industry=industry,
            description=description,
            headquarters=extracted_data.get("headquarters"),
            founded_year=self._converter.parse_numeric(extracted_data.get("founded_year")),
            tier=tier,
            threat_level=threat_level,
            ai_maturity=ai_maturity,
            revenue=revenue,
            growth_rate=growth_rate,
            employees=int(employees) if employees else None,
            profit_margin=profit_margin,
            source_links=extracted_data.get("source_links", []),
            metric_sources=extracted_data.get("metric_sources", {}),
            metric_justifications=extracted_data.get("metric_justifications", {}),
        )


# Re-export BatchExtractor for convenience
__all__ = ["MarkdownExtractor", "BatchExtractor"]
