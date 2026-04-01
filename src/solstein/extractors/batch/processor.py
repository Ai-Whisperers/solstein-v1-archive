"""Batch extraction and processing utilities.

EPIC-022: Extracted from MarkdownExtractor for modularity.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from ...domain.models import Company


class ProfileMerger:
    """Merge multiple company profiles into single profiles."""

    def group_and_merge(self, profiles: list[Company]) -> list[Company]:
        """Group profiles by company ID and merge duplicates.

        Args:
            profiles: List of company profiles

        Returns:
            List of merged company profiles
        """
        from collections import defaultdict

        # Group by normalized name
        groups: dict[str, list[Company]] = defaultdict(list)
        for profile in profiles:
            key = self._normalize_name(profile.name)
            groups[key].append(profile)

        # Merge each group
        merged: list[Company] = []
        for company_name, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged_profile = self._merge_company_profiles(group)
                merged.append(merged_profile)
                logger.info(f"Merged {len(group)} profiles for {company_name}")

        return merged

    def _normalize_name(self, name: str) -> str:
        """Normalize company name for grouping."""
        return name.lower().strip().replace(" ", "_")

    def _merge_company_profiles(self, profiles: list[Company]) -> Company:
        """Merge multiple profiles of the same company.

        Uses model_dump/model construction to merge, preferring non-None values
        from later profiles over earlier ones.

        Args:
            profiles: List of profiles for the same company

        Returns:
            Merged company profile
        """
        if not profiles:
            raise ValueError("Cannot merge empty profile list")

        if len(profiles) == 1:
            return profiles[0]

        # Start with the first profile's data
        merged_data = profiles[0].model_dump()

        # Merge: prefer non-None values from later profiles
        for profile in profiles[1:]:
            profile_data = profile.model_dump()
            for key, value in profile_data.items():
                if value is not None and merged_data.get(key) is None:
                    merged_data[key] = value

        # Merge source_links from all profiles
        all_sources: set[str] = set()
        for profile in profiles:
            if profile.source_links:
                all_sources.update(profile.source_links)
        merged_data["source_links"] = list(all_sources)

        # Merge metric_sources from all profiles
        all_metric_sources: dict[str, list[str]] = {}
        for profile in profiles:
            if profile.metric_sources:
                for key, sources in profile.metric_sources.items():
                    if key not in all_metric_sources:
                        all_metric_sources[key] = []
                    all_metric_sources[key].extend(sources)
        merged_data["metric_sources"] = all_metric_sources

        return Company(**merged_data)


class ProvenanceValidator:
    """Validate profile provenance and data quality."""

    REQUIRED_METRICS = [
        "revenue",
        "growth_rate",
        "employees",
        "profit_margin",
        "funding",
        "valuation",
    ]

    def validate(self, profile: Company) -> list[str]:
        """Validate a company profile's provenance.

        Args:
            profile: Company profile to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues: list[str] = []

        # Check required fields
        if not profile.name:
            issues.append("Missing company name")

        if not profile.industry:
            issues.append("Missing industry")

        # Check required metrics using actual Company fields
        metric_field_map = {
            "revenue": profile.revenue,
            "growth_rate": profile.growth_rate,
            "employees": profile.employees,
            "profit_margin": profile.profit_margin,
            "funding": profile.funding,
            "valuation": profile.valuation,
        }
        for metric_name, value in metric_field_map.items():
            if value is None:
                issues.append(f"Missing required metric: {metric_name}")

        # Check data sources
        if not profile.source_links:
            issues.append("No data sources")

        return issues

    def validate_batch(self, profiles: list[Company]) -> dict[str, list[str]]:
        """Validate multiple profiles.

        Args:
            profiles: List of company profiles

        Returns:
            Dictionary mapping company names to validation issues
        """
        results: dict[str, list[str]] = {}

        for profile in profiles:
            issues = self.validate(profile)
            if issues:
                results[profile.name] = issues

        return results


class BatchExtractor:
    """Extract and process multiple markdown files."""

    def __init__(self, extractor: Any | None = None):
        """Initialize batch extractor.

        Args:
            extractor: MarkdownExtractor instance
        """
        from ..markdown_extractor import MarkdownExtractor

        self._extractor = extractor or MarkdownExtractor()
        self._merger = ProfileMerger()
        self._validator = ProvenanceValidator()

    def extract_directory(
        self,
        directory: Path,
        pattern: str = "*.md",
    ) -> list[Company]:
        """Extract all markdown files in a directory.

        Args:
            directory: Directory to search
            pattern: File pattern to match

        Returns:
            List of extracted company profiles
        """
        import asyncio

        files = list(directory.glob(pattern))
        logger.info(f"Found {len(files)} files matching {pattern}")

        if not files:
            return []

        # Process files - handle both sync and async contexts
        profiles: list[Company] = []
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        for file_path in files:
            try:
                if loop and loop.is_running():
                    # Already in async context — run coroutine in a new thread
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        result = pool.submit(asyncio.run, self._process_file(file_path)).result()
                else:
                    result = asyncio.run(self._process_file(file_path))
                if result:
                    profiles.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

        # Merge duplicates
        merged = self._merger.group_and_merge(profiles)

        logger.info(f"Extracted {len(merged)} unique profiles from {len(files)} files")
        return merged

    async def _process_file(self, file_path: Path) -> Company | None:
        """Process a single file.

        Args:
            file_path: Path to markdown file

        Returns:
            Company profile or None if failed
        """
        from ...domain.models import Company

        extracted = self._extractor.extract_from_file(file_path)
        if not extracted:
            return None

        try:
            profile = self._extractor.to_company_profile(extracted)
            if isinstance(profile, Company):
                return profile
        except Exception as e:
            logger.error(f"Failed to convert {file_path} to profile: {e}")

        return None

    def save_to_json(self, profiles: list[Company], output_path: Path) -> None:
        """Save profiles to JSON file.

        Args:
            profiles: List of company profiles
            output_path: Output file path
        """
        import json

        data = [p.model_dump(mode="json") if hasattr(p, "model_dump") else p.to_dict() for p in profiles]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Saved {len(profiles)} profiles to {output_path}")

    def validate_profiles(self, profiles: list[Company]) -> dict[str, list[str]]:
        """Validate multiple profiles.

        Args:
            profiles: List of company profiles

        Returns:
            Dictionary of validation issues
        """
        return self._validator.validate_batch(profiles)

    def validate_profiles_provenance(self, profiles: list[Company]) -> dict[str, list[str]]:
        required_numeric_fields = ["revenue", "growth_rate", "employees", "profit_margin", "funding", "valuation"]
        violations: dict[str, list[str]] = {}

        for profile in profiles:
            issues: list[str] = []

            if not profile.source_links and not profile.metric_sources:
                issues.append("missing_source_links")

            for field_name in required_numeric_fields:
                field_value = getattr(profile, field_name, None)
                if field_value is None:
                    continue

                sources = profile.metric_sources.get(field_name, [])
                justification = profile.metric_justifications.get(field_name)
                if not sources and not justification:
                    issues.append(f"missing_provenance:{field_name}")

            if issues:
                violations[profile.id] = issues

        return violations
