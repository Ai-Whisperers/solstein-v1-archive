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
from ..research.sources import canonicalize_url, is_probably_url
from .llm_financial_extractor import LLMFinancialExtractor

REQUIRED_PROVENANCE_METRICS = [
    "revenue",
    "growth_rate",
    "employees",
    "profit_margin",
    "funding",
    "valuation",
]


class MarkdownExtractor:
    """Extract structured data from markdown files."""

    def __init__(self, use_llm: bool = False) -> None:
        self.patterns = {
            "revenue": re.compile(r"Revenue:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "growth_rate": re.compile(r"Growth Rate:\s*([\d.,]+\s*%)"),
            "employees": re.compile(r"Employees:\s*([\d.,]+)"),
            "profit_margin": re.compile(r"Profit Margin:\s*([\d.,]+\s*%)"),
            "funding": re.compile(r"Funding Raised:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "valuation": re.compile(r"Valuation:\s*([€$]?\s*[\d.,]+[MKBT]?)"),
            "ai_maturity": re.compile(r"AI Maturity:\s*(\w+(?:[\s\t]+\w+)*)"),
            "threat_level": re.compile(r"Threat Level:\s*(\w+)"),
            "tier": re.compile(r"Tier:\s*(\w+(?:[\s\t]+\w+)*)"),
        }
        self.llm_extractor = LLMFinancialExtractor() if use_llm else None
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
            data["geographic_presence"] = [g.strip() for g in geo_match.group(1).split(",")]

        # Extract tech stack
        tech_match = re.search(r"Tech Stack:\s*(.+)", content)
        if tech_match:
            data["tech_stack"] = [t.strip() for t in tech_match.group(1).split(",")]

        # Extract confidence levels
        data["confidence"] = self._extract_confidence(content)
        data["source_links"] = self._extract_source_links(content)
        data["metric_sources"] = self._extract_metric_sources(content)
        data["metric_justifications"] = self._extract_metric_justifications(content)

        return data

    def _extract_source_links(self, content: str) -> list[str]:
        url_pattern = re.compile(r"https?://[^\s)\]>\"']+")
        seen: set[str] = set()
        urls: list[str] = []
        for match in url_pattern.findall(content):
            url = match.rstrip(".,")
            if url not in seen:
                seen.add(url)
                urls.append(url)
        return urls

    def _extract_metric_sources(self, content: str) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        lines = content.splitlines()
        in_section = False

        for line in lines:
            stripped = line.strip()
            if stripped.lower() in {
                "## metric sources",
                "### metric sources",
                "metric sources:",
            }:
                in_section = True
                continue

            if in_section and stripped.startswith("#"):
                break

            if in_section and stripped.startswith("-") and ":" in stripped:
                body = stripped.lstrip("- ")
                metric, raw_urls = body.split(":", 1)
                metric_key = metric.strip().lower()
                urls = [u.strip() for u in raw_urls.split(",") if u.strip().startswith("http")]
                if urls:
                    result[metric_key] = urls

        return result

    def _extract_metric_justifications(self, content: str) -> dict[str, str]:
        result: dict[str, str] = {}
        lines = content.splitlines()
        in_section = False

        for line in lines:
            stripped = line.strip()
            if stripped.lower() in {
                "## estimation notes",
                "### estimation notes",
                "estimation notes:",
            }:
                in_section = True
                continue

            if in_section and stripped.startswith("#"):
                break

            if in_section and stripped.startswith("-") and ":" in stripped:
                body = stripped.lstrip("- ")
                metric, note = body.split(":", 1)
                metric_key = metric.strip().lower()
                note_val = note.strip()
                if note_val:
                    result[metric_key] = note_val

        return result

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
        company_id = extracted_data.get("name", "unknown").lower().replace(" ", "-").replace(".", "").replace(",", "")

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
        metric_values = {
            "revenue": financials.revenue,
            "growth_rate": financials.growth_rate,
            "employees": financials.employees,
            "profit_margin": financials.profit_margin,
            "funding": financials.funding_raised,
            "valuation": financials.valuation,
        }
        metric_sources = extracted_data.get("metric_sources", {})
        metric_observations: dict[str, list[dict[str, Any]]] = {}
        for metric, value in metric_values.items():
            metric_observations[metric] = []
            sources = metric_sources.get(metric, [])
            if value is not None and isinstance(sources, list):
                for source in sources:
                    metric_observations[metric].append(
                        {
                            "source": source,
                            "value": value,
                        }
                    )

        profile = Company(
            id=company_id,
            name=extracted_data.get("name", "Unknown Company"),
            description=extracted_data.get("description"),
            financials=financials,
            ai_maturity=self._parse_ai_maturity(extracted_data.get("ai_maturity")),
            threat_level=self._parse_threat_level(extracted_data.get("threat_level")),
            tier=self._determine_tier_from_revenue(financials.revenue),
            geographic_presence=extracted_data.get("geographic_presence", []),
            tech_stack=extracted_data.get("tech_stack", []),
            data_source=extracted_data.get("source"),
            source_links=extracted_data.get("source_links", []),
            metric_sources=metric_sources,
            metric_justifications=extracted_data.get("metric_justifications", {}),
            metric_observations=metric_observations,
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

    def _determine_tier_from_revenue(self, revenue: float | None) -> CompanyTier:
        """Determine company tier based on revenue (in euros).

        Tier boundaries:
        - Tier 1: > €1B (1,000,000,000)
        - Tier 2: €100M - €1B (100,000,000 - 1,000,000,000)
        - Tier 3: €10M - €100M (10,000,000 - 100,000,000)
        - Tier 4: < €10M (< 10,000,000)
        """
        if revenue is None:
            return CompanyTier.TIER_3

        if revenue >= 1_000_000_000:  # >= €1B
            return CompanyTier.TIER_1
        elif revenue >= 100_000_000:  # >= €100M
            return CompanyTier.TIER_2
        elif revenue >= 10_000_000:  # >= €10M
            return CompanyTier.TIER_3
        else:
            return CompanyTier.TIER_4

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
    async def process_file(cls, file_path: Path, extractor: "MarkdownExtractor | None" = None) -> Company | None:
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

    def extract_directory(self, directory: Path, pattern: str = "*.md") -> list[Company]:
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

        profiles = self._group_and_merge_profiles(profiles)
        logger.info(f"Successfully extracted {len(profiles)} profiles (after merging duplicates)")
        return profiles

    def _group_and_merge_profiles(self, profiles: list[Company]) -> list[Company]:
        """Group profiles by company_name and merge duplicates into single records."""
        if not profiles:
            return profiles

        # Group profiles by company_name
        grouped: dict[str, list[Company]] = {}
        for profile in profiles:
            name = profile.name
            if name not in grouped:
                grouped[name] = []
            grouped[name].append(profile)

        # Merge duplicates
        merged = []
        for company_name, company_profiles in grouped.items():
            if len(company_profiles) == 1:
                merged.append(company_profiles[0])
            else:
                logger.debug(f"Merging {len(company_profiles)} profiles for {company_name}")
                merged_profile = self._merge_company_profiles(company_profiles)
                merged.append(merged_profile)

        return merged

    def _merge_company_profiles(self, profiles: list[Company]) -> Company:
        """Merge multiple Company profiles into a single record."""
        # Start with the first profile as base
        result = profiles[0]

        # Merge data from remaining profiles
        for other in profiles[1:]:
            # Merge numeric fields (prefer non-None)
            if result.employees is None and other.employees is not None:
                result.employees = other.employees
            if result.revenue is None and other.revenue is not None:
                result.revenue = other.revenue
            if result.growth_rate is None and other.growth_rate is not None:
                result.growth_rate = other.growth_rate
            if result.profit_margin is None and other.profit_margin is not None:
                result.profit_margin = other.profit_margin
            if result.funding is None and other.funding is not None:
                result.funding = other.funding
            if result.valuation is None and other.valuation is not None:
                result.valuation = other.valuation
            if result.ai_maturity is None and other.ai_maturity is not None:
                result.ai_maturity = other.ai_maturity
            if result.threat_level is None and other.threat_level is not None:
                result.threat_level = other.threat_level

            # Merge source links (combine and deduplicate)
            if other.source_links:
                result.source_links = list(set(result.source_links or []) | set(other.source_links))

            # Merge metric sources (combine per metric)
            if other.metric_sources:
                for metric, sources in other.metric_sources.items():
                    if metric not in result.metric_sources:
                        result.metric_sources[metric] = []
                    # Combine and deduplicate sources
                    existing = set(result.metric_sources[metric])
                    result.metric_sources[metric] = list(existing | set(sources))

            # Merge metric justifications (prefer non-empty)
            if other.metric_justifications:
                for metric, justification in other.metric_justifications.items():
                    if metric not in result.metric_justifications and justification:
                        result.metric_justifications[metric] = justification

            # Merge metric observations (combine all)
            if other.metric_observations:
                for metric, observations in other.metric_observations.items():
                    if metric not in result.metric_observations:
                        result.metric_observations[metric] = []
                    # Append new observations
                    if isinstance(observations, list):
                        result.metric_observations[metric].extend(observations)

        return result

    def save_to_json(self, profiles: list[Company], output_path: Path) -> None:
        """Save profiles to JSON file."""
        try:
            data = [profile.model_dump(mode="json") for profile in profiles]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            logger.info(f"Saved {len(profiles)} profiles to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save to JSON: {e}")
            raise

    def validate_profile_provenance(self, profile: Company) -> list[str]:
        violations: list[str] = []

        if not profile.source_links:
            violations.append("Missing source_links")

        canonical_sources = {
            canonicalize_url(link) for link in (profile.source_links or []) if isinstance(link, str) and link.strip()
        }

        for metric in REQUIRED_PROVENANCE_METRICS:
            sources = profile.metric_sources.get(metric, [])
            justification = profile.metric_justifications.get(metric, "").strip()

            if isinstance(sources, list):
                bad_urls = [s for s in sources if not isinstance(s, str) or not is_probably_url(s)]
                if bad_urls:
                    violations.append(f"Metric '{metric}' contains non-url metric_sources entries: {bad_urls[:3]}")

                missing_from_sources = [
                    s
                    for s in sources
                    if isinstance(s, str) and s.strip() and canonicalize_url(s) not in canonical_sources
                ]
                if missing_from_sources:
                    violations.append(
                        f"Metric '{metric}' has metric_sources not present in source_links: {missing_from_sources[:3]}"
                    )

            if not sources and not justification:
                violations.append(f"Metric '{metric}' has neither metric_sources nor metric_justification")

            observations = (profile.metric_observations or {}).get(metric, [])
            if isinstance(observations, list):
                expected = {canonicalize_url(s) for s in sources if isinstance(s, str) and s.strip()}
                for obs in observations:
                    if not isinstance(obs, dict):
                        violations.append(f"Metric '{metric}' has a non-dict metric_observation entry")
                        continue

                    if "source" not in obs or "value" not in obs:
                        violations.append(f"Metric '{metric}' observation missing 'source' or 'value'")
                        continue

                    src = obs.get("source")
                    if isinstance(src, str) and src.strip():
                        canon = canonicalize_url(src)
                        if canon not in canonical_sources:
                            violations.append(
                                f"Metric '{metric}' observation source not present in source_links: {src}"
                            )
                        if expected and canon not in expected:
                            violations.append(
                                f"Metric '{metric}' observation source not present in metric_sources: {src}"
                            )

        return violations

    def validate_profiles_provenance(self, profiles: list[Company]) -> dict[str, list[str]]:
        report: dict[str, list[str]] = {}
        for profile in profiles:
            violations = self.validate_profile_provenance(profile)
            if violations:
                report[profile.id] = violations
        return report
