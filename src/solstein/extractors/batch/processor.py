"""Batch extraction and processing utilities.

EPIC-022: Extracted from MarkdownExtractor for modularity.
"""

from pathlib import Path
from typing import Any

from loguru import logger

from ...domain.models import Company, FinancialMetric


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

        Args:
            profiles: List of profiles for the same company

        Returns:
            Merged company profile
        """
        if not profiles:
            raise ValueError("Cannot merge empty profile list")

        if len(profiles) == 1:
            return profiles[0]

        # Start with the first profile
        base = profiles[0]

        # Merge financial metrics
        merged_metrics: dict[str, FinancialMetric] = {}
        for profile in profiles:
            for metric_name, metric in profile.financial_metrics.items():
                if metric_name not in merged_metrics:
                    merged_metrics[metric_name] = metric
                elif metric.confidence.value > merged_metrics[metric_name].confidence.value:
                    # Keep higher confidence metric
                    merged_metrics[metric_name] = metric

        # Merge data sources
        all_sources: set[str] = set()
        for profile in profiles:
            all_sources.update(profile.data_sources)

        # Create merged profile
        merged = Company(
            id=base.id,
            name=base.name,
            industry=base.industry or next((p.industry for p in profiles if p.industry), None),
            description=base.description or next((p.description for p in profiles if p.description), None),
            website=base.website or next((p.website for p in profiles if p.website), None),
            headquarters=base.headquarters or next((p.headquarters for p in profiles if p.headquarters), None),
            founded_year=base.founded_year or next((p.founded_year for p in profiles if p.founded_year), None),
            tier=base.tier,
            threat_level=base.threat_level,
            classification=base.classification,
            ai_maturity=base.ai_maturity,
            saas_maturity=base.saas_maturity,
            ai_score=base.ai_score,
            ai_signal_level=base.ai_signal_level,
            ai_key_capabilities=base.ai_key_capabilities or [],
            ai_in_production=base.ai_in_production,
            revenue_eur_m=base.revenue_eur_m,
            revenue_confidence=base.revenue_confidence,
            growth_rate_pct=base.growth_rate_pct,
            growth_confidence=base.growth_confidence,
            profit_margin_pct=base.profit_margin_pct,
            ebitda_margin_pct=base.ebitda_margin_pct,
            recurring_revenue_pct=base.recurring_revenue_pct,
            revenue_per_employee_eur_k=base.revenue_per_employee_eur_k,
            revenue_timeline=base.revenue_timeline or [],
            revenue_cagr_3yr=base.revenue_cagr_3yr,
            revenue_cagr_5yr=base.revenue_cagr_5yr,
            funding_rounds=base.funding_rounds or [],
            total_funding_raised_eur=base.total_funding_raised_eur,
            latest_valuation_eur=base.latest_valuation_eur,
            lead_investors=base.lead_investors or [],
            funding_war_chest=base.funding_war_chest,
            employee_count=base.employee_count,
            employee_cagr_3yr=base.employee_cagr_3yr,
            open_positions=base.open_positions,
            profitability_raw_metrics=base.profitability_raw_metrics or {},
            data_availability=base.data_availability or {},
            data_source=base.data_source,
            growth_score=base.growth_score,
            financial_health_score=base.financial_health_score,
            competitive_position_score=base.competitive_position_score,
            composite_score=base.composite_score,
            scoring_breakdown=base.scoring_breakdown or {},
            financial_metrics=merged_metrics,
            data_sources=list(all_sources),
            last_updated=base.last_updated,
            created_at=base.created_at,
        )

        return merged


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

        # Check required metrics
        for metric in self.REQUIRED_METRICS:
            if metric not in profile.financial_metrics:
                issues.append(f"Missing required metric: {metric}")

        # Check data sources
        if not profile.data_sources:
            issues.append("No data sources")

        # Check confidence levels
        low_confidence_metrics = [
            name
            for name, metric in profile.financial_metrics.items()
            if metric.confidence.value < 2  # Less than MEDIUM
        ]
        if low_confidence_metrics:
            issues.append(f"Low confidence metrics: {', '.join(low_confidence_metrics)}")

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

        # Process files
        profiles: list[Company] = []
        for file_path in files:
            try:
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
