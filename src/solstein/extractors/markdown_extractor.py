"""
Markdown file extractor for SolStein.

Extracts structured data from markdown files following SolStein's format.
Replaces the monolithic extract_competitor_data.py script.
"""

import json
import re
from pathlib import Path
from typing import Any

from loguru import logger

from ..domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)


class MarkdownExtractor:
    """Extract structured data from markdown files."""

    def __init__(self) -> None:
        self.patterns = {
            "revenue": re.compile(r"Revenue:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "growth_rate": re.compile(r"Growth Rate:\s*([\d.,]+\s*%)"),
            "employees": re.compile(r"Employees:\s*([\d.,]+)"),
            "profit_margin": re.compile(r"Profit Margin:\s*([\d.,]+\s*%)"),
            "funding": re.compile(r"Funding Raised:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "valuation": re.compile(r"Valuation:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "ai_maturity": re.compile(r"AI Maturity:\s*(\w+(?:[ \t]+\w+)*)"),
            "threat_level": re.compile(r"Threat Level:\s*(\w+)"),
            "tier": re.compile(r"Tier:\s*(\w+(?:[ \t]+\w+)*)"),
        }

    def extract_from_file(self, file_path: Path) -> dict[str, Any] | None:
        """Extract data from a single markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return self._parse_content(content, str(file_path))
        except Exception as e:
            logger.error(f"Failed to extract from {file_path}: {e}")
            return None

    def _parse_content(self, content: str, source: str) -> dict[str, Any]:
        """Parse markdown content and extract structured data."""
        data: dict[str, Any] = {"source": source}

        # Extract basic metrics
        for key, pattern in self.patterns.items():
            match = pattern.search(content)
            if match:
                data[key] = match.group(1).strip()

        # Extract company name from filename or content
        name_match = re.search(r"#\s+(.+)", content)
        if name_match:
            data["name"] = name_match.group(1).strip()

        # Extract description (first paragraph after title)
        desc_match = re.search(r"#\s+[^\n]+\n\n(.+?)(?:\n\n|$)", content, re.DOTALL)
        if desc_match:
            data["description"] = desc_match.group(1).strip()

        # Extract geographic presence
        geo_match = re.search(r"Geographic Presence:\s*(.+)", content)
        if geo_match:
            data["geographic_presence"] = [
                g.strip() for g in geo_match.group(1).split(",")
            ]

        # Extract tech stack
        tech_match = re.search(r"Tech Stack:\s*(.+)", content)
        if tech_match:
            data["tech_stack"] = [t.strip() for t in tech_match.group(1).split(",")]

        # Extract confidence levels
        data["confidence"] = self._extract_confidence(content)

        return data

    def _extract_confidence(self, content: str) -> dict[str, str]:
        """Extract confidence levels from content."""
        confidence = {}

        # Look for confidence annotations
        conf_pattern = re.compile(r"\(([Cc]onfirmed|[Ee]stimated|[Uu]nknown)\)")
        lines = content.split("\n")

        for line in lines:
            if "(" in line and ")" in line:
                matches = conf_pattern.findall(line)
                if matches:
                    # Get the metric name from the line
                    metric = line.split(":")[0].strip().lower()
                    confidence[metric] = matches[0].capitalize()

        return confidence

    def to_company_profile(self, extracted_data: dict[str, Any]) -> Company:
        """Convert extracted data to Company model."""
        # Generate ID from name
        company_id = (
            extracted_data.get("name", "unknown")
            .lower()
            .replace(" ", "-")
            .replace(".", "")
            .replace(",", "")
        )

        # Create financial metrics
        employees_val = self._parse_numeric(extracted_data.get("employees"))
        employees = int(employees_val) if employees_val is not None else None

        financials = FinancialMetric(
            revenue=self._parse_numeric(extracted_data.get("revenue")),
            revenue_confidence=self._get_confidence(extracted_data, "revenue"),
            growth_rate=self._parse_percentage(extracted_data.get("growth_rate")),
            growth_confidence=self._get_confidence(extracted_data, "growth_rate"),
            employees=employees,
            employees_confidence=self._get_confidence(extracted_data, "employees"),
            profit_margin=self._parse_percentage(extracted_data.get("profit_margin")),
            margin_confidence=self._get_confidence(extracted_data, "profit_margin"),
            funding_raised=self._parse_numeric(extracted_data.get("funding")),
            funding_confidence=self._get_confidence(extracted_data, "funding"),
            valuation=self._parse_numeric(extracted_data.get("valuation")),
            valuation_confidence=self._get_confidence(extracted_data, "valuation"),
        )

        # Create company profile
        profile = Company(
            id=company_id,
            name=extracted_data.get("name", "Unknown Company"),
            description=extracted_data.get("description"),
            financials=financials,
            ai_maturity=self._parse_ai_maturity(extracted_data.get("ai_maturity")),
            threat_level=self._parse_threat_level(extracted_data.get("threat_level")),
            tier=self._parse_tier(extracted_data.get("tier")),
            geographic_presence=extracted_data.get("geographic_presence", []),
            tech_stack=extracted_data.get("tech_stack", []),
            data_source=extracted_data.get("source"),
        )

        return profile

    def _parse_numeric(self, value: str | None) -> float | None:
        """Parse numeric values with suffixes (K, M, B, T)."""
        if not value:
            return None

        try:
            # Remove currency symbols and whitespace
            value = value.strip().replace("€", "").replace("$", "").replace(",", "")

            # Handle suffixes
            if value.endswith("T"):
                return float(value[:-1]) * 1_000_000_000_000
            elif value.endswith("B"):
                return float(value[:-1]) * 1_000_000_000
            elif value.endswith("M"):
                return float(value[:-1]) * 1_000_000
            elif value.endswith("K"):
                return float(value[:-1]) * 1_000
            else:
                return float(value)
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse numeric value: {value}")
            return None

    def _parse_percentage(self, value: str | None) -> float | None:
        """Parse percentage values."""
        if not value:
            return None

        try:
            value = value.strip().replace("%", "").replace(",", "")
            return float(value)
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse percentage: {value}")
            return None

    def _parse_ai_maturity(self, value: str | None) -> AIMaturity:
        """Parse AI maturity level."""
        if not value:
            return AIMaturity.NONE

        value = value.strip().lower()
        if "very strong" in value:
            return AIMaturity.VERY_STRONG
        elif "strong" in value:
            return AIMaturity.STRONG
        elif "moderate" in value:
            return AIMaturity.MODERATE
        elif "low" in value:
            return AIMaturity.LOW
        else:
            return AIMaturity.NONE

    def _parse_threat_level(self, value: str | None) -> ThreatLevel:
        """Parse threat level."""
        if not value:
            return ThreatLevel.MEDIUM

        value = value.strip().upper()
        try:
            return ThreatLevel(value.capitalize())
        except ValueError:
            # Try to map common variations
            if "HIGH" in value:
                return ThreatLevel.HIGH
            elif "CRITICAL" in value:
                return ThreatLevel.CRITICAL
            elif "LOW" in value:
                return ThreatLevel.LOW
            return ThreatLevel.MEDIUM

    def _parse_tier(self, value: str | None) -> CompanyTier:
        """Parse company tier."""
        if not value:
            return CompanyTier.TIER_3

        value = value.strip()
        if "Tier 1" in value:
            return CompanyTier.TIER_1
        elif "Tier 2" in value:
            return CompanyTier.TIER_2
        elif "Tier 3" in value:
            return CompanyTier.TIER_3
        elif "Tier 4" in value:
            return CompanyTier.TIER_4
        return CompanyTier.TIER_3

    def _get_confidence(self, data: dict[str, Any], metric: str) -> ConfidenceLevel:
        """Get confidence level for a metric."""
        confidence_data = data.get("confidence", {})
        val = confidence_data.get(metric, "Unknown")
        try:
            return ConfidenceLevel(val.capitalize())
        except ValueError:
            return ConfidenceLevel.UNKNOWN


class BatchExtractor:
    """Batch extraction from multiple files."""

    def __init__(self, extractor: MarkdownExtractor | None = None):
        self.extractor = extractor or MarkdownExtractor()

    @classmethod
    async def process_file(
        cls, file_path: Path, extractor: "MarkdownExtractor | None" = None
    ) -> Company | None:
        """Process a single file asynchronously."""
        if extractor is None:
            extractor = MarkdownExtractor()

        extracted = extractor.extract_from_file(file_path)
        if extracted:
            try:
                return extractor.to_company_profile(extracted)
            except Exception as e:
                logger.error(f"Failed to create profile from {file_path}: {e}")
        return None

    def extract_directory(
        self, directory: Path, pattern: str = "*.md"
    ) -> list[Company]:
        """Extract data from all markdown files in a directory."""
        profiles: list[Company] = []

        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return profiles

        md_files = list(directory.rglob(pattern))
        logger.info(f"Found {len(md_files)} markdown files in {directory}")

        for md_file in md_files:
            logger.debug(f"Processing {md_file}")
            extracted = self.extractor.extract_from_file(md_file)
            if extracted:
                try:
                    profile = self.extractor.to_company_profile(extracted)
                    profiles.append(profile)
                except Exception as e:
                    logger.error(f"Failed to create profile from {md_file}: {e}")

        logger.info(f"Successfully extracted {len(profiles)} profiles")
        return profiles

    def save_to_json(self, profiles: list[Company], output_path: Path) -> None:
        """Save profiles to JSON file."""
        try:
            data = [profile.model_dump(mode="json") for profile in profiles]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(data, indent=2, default=str), encoding="utf-8"
            )
            logger.info(f"Saved {len(profiles)} profiles to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save to JSON: {e}")
            raise
