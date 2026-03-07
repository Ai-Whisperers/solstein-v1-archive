"""Metric parsers for markdown content extraction.

EPIC-022: Extracted from MarkdownExtractor for modularity.
"""

import re
from typing import Any

from .base import PatternBasedParser


class BasicMetricsParser(PatternBasedParser):
    """Parse basic company metrics from markdown."""

    def __init__(self) -> None:
        patterns = {
            "revenue": r"Revenue:\s*([€$]?\s*[\d.,]+[MKBT]?)",
            "growth_rate": r"Growth Rate:\s*([\d.,]+\s*%)",
            "employees": r"Employees:\s*([\d.,]+)",
            "profit_margin": r"Profit Margin:\s*([\d.,]+\s*%)",
            "funding": r"Funding Raised:\s*([€$]?\s*[\d.,]+[MKBT]?)",
            "valuation": r"Valuation:\s*([€$]?\s*[\d.,]+[MKBT]?)",
            "ai_maturity": r"AI Maturity:\s*(\w+(?:[\s\t]+\w+)*)",
            "threat_level": r"Threat Level:\s*(\w+)",
            "tier": r"Tier:\s*(\w+(?:[\s\t]+\w+)*)",
        }
        super().__init__(patterns)

    @property
    def name(self) -> str:
        return "basic_metrics"


class MetadataParser(PatternBasedParser):
    """Parse metadata sections from markdown."""

    def __init__(self) -> None:
        patterns = {
            "geographic_presence": r"Geographic Presence:\s*(.+)",
            "tech_stack": r"Tech Stack:\s*(.+)",
            "industry": r"Industry:\s*(.+)",
            "headquarters": r"Headquarters:\s*(.+)",
            "founded_year": r"Founded:\s*(\d{4})",
        }
        super().__init__(patterns)

    @property
    def name(self) -> str:
        return "metadata"

    def parse(self, content: str) -> dict[str, Any]:
        """Parse metadata with special handling for lists."""
        data = super().parse(content)

        # Convert comma-separated values to lists
        if "geographic_presence" in data:
            data["geographic_presence"] = [g.strip() for g in data["geographic_presence"].split(",")]

        if "tech_stack" in data:
            data["tech_stack"] = [t.strip() for t in data["tech_stack"].split(",")]

        return data


class DescriptionParser(PatternBasedParser):
    """Parse company description from markdown."""

    def __init__(self) -> None:
        super().__init__({})

    @property
    def name(self) -> str:
        return "description"

    def parse(self, content: str) -> dict[str, Any]:
        """Extract company name and description."""
        data: dict[str, Any] = {}

        # Extract company name from first heading
        name_match = re.search(r"#\s+(.+)", content)
        if name_match:
            data["name"] = name_match.group(1).strip()

        # Extract description (first paragraph after title)
        desc_match = re.search(r"#\s+[^\n]+\n\n(.+?)(?:\n\n|$)", content, re.DOTALL)
        if desc_match:
            data["description"] = desc_match.group(1).strip()

        return data


class SourceLinksParser(PatternBasedParser):
    """Parse source links from markdown."""

    def __init__(self) -> None:
        super().__init__({})

    @property
    def name(self) -> str:
        return "source_links"

    def parse(self, content: str) -> dict[str, Any]:
        """Extract source URLs from markdown."""
        url_pattern = re.compile(r"https?://[^\s\)\]>\"']+")
        seen: set[str] = set()
        urls: list[str] = []

        for match in url_pattern.findall(content):
            url = match.rstrip('."')
            if url not in seen:
                seen.add(url)
                urls.append(url)

        return {"source_links": urls}


class MetricSourcesParser(PatternBasedParser):
    """Parse metric-specific sources from markdown."""

    def __init__(self) -> None:
        super().__init__({})

    @property
    def name(self) -> str:
        return "metric_sources"

    def parse(self, content: str) -> dict[str, Any]:
        """Extract metric-specific source URLs."""
        data: dict[str, list[str]] = {}

        # Pattern: "Revenue Sources:" or "Growth Rate Sources:"
        sections = re.findall(r"([\w\s]+)\s+Sources:\s*\n?((?:\s*-\s*[^\n]+\n?)+)", content, re.IGNORECASE)

        for metric_name, source_list in sections:
            metric_key = metric_name.strip().lower().replace(" ", "_")
            sources = re.findall(r"-\s*([^\n]+)", source_list)
            data[metric_key] = [s.strip() for s in sources if s.strip()]

        return {"metric_sources": data}


class MetricJustificationsParser(PatternBasedParser):
    """Parse metric justifications from markdown."""

    def __init__(self) -> None:
        super().__init__({})

    @property
    def name(self) -> str:
        return "metric_justifications"

    def parse(self, content: str) -> dict[str, Any]:
        """Extract metric-specific justifications."""
        data: dict[str, str] = {}

        # Pattern: "Revenue Justification:" or "Growth Rate Justification:"
        sections = re.findall(
            r"([\w\s]+)\s+Justification:\s*\n?([^\n]+(?:\n(?![\w\s]+Justification:)[^\n]+)*)", content, re.IGNORECASE
        )

        for metric_name, justification in sections:
            metric_key = metric_name.strip().lower().replace(" ", "_")
            data[metric_key] = justification.strip()

        return {"metric_justifications": data}


class ConfidenceParser(PatternBasedParser):
    """Parse confidence levels from markdown."""

    def __init__(self) -> None:
        super().__init__({})

    @property
    def name(self) -> str:
        return "confidence"

    def parse(self, content: str) -> dict[str, Any]:
        """Extract confidence levels for metrics."""
        data: dict[str, str] = {}

        # Pattern: "Revenue Confidence: HIGH" or "Growth Rate Confidence: MEDIUM"
        matches = re.findall(r"([\w\s]+)\s+Confidence:\s*(HIGH|MEDIUM|LOW|UNVERIFIED)", content, re.IGNORECASE)

        for metric_name, confidence in matches:
            metric_key = metric_name.strip().lower().replace(" ", "_")
            data[metric_key] = confidence.upper()

        return {"confidence_levels": data}
