"""
Task 2: Unified CompanyData Model with Conflict Resolution

Merges JSON and Markdown data sources with conflict resolution and data source tracking.
Priority: Markdown > JSON (when conflicts exist)
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

from ..domain.models import Company, FinancialMetric, ConfidenceLevel, AIMaturity, ThreatLevel, CompanyTier
from .loaders import CompetitorDataLoader
from ..extractors.markdown_extractor import MarkdownExtractor
from ..analytics.confidence_weighting import populate_signal_confidences

logger = logging.getLogger(__name__)


class UnifiedCompany(Company):
    """Extended Company model with data source tracking and merge conflict documentation."""

    data_source_per_field: Dict[str, str] = {}  # Track where each field came from
    merge_conflicts: List[str] = []  # Fields where JSON and Markdown differed
    merge_priority: str = "Markdown > JSON"  # Document priority rules
    merge_timestamp: Optional[datetime] = None


class UnifiedCompanyLoader:
    """Load and merge company data from JSON and Markdown sources."""

    def __init__(self):
        self.json_loader = CompetitorDataLoader()
        self.markdown_extractor = MarkdownExtractor()
        self.markdown_dir = (
            Path(__file__).parent.parent.parent.parent
            / "data"
            / "input"
            / "custom_market_runs"
            / "2026-02-23"
            / "dutch_market"
        )

    def load_unified_companies(self) -> List[UnifiedCompany]:
        """Load all companies with unified data from both sources."""

        # Load JSON companies
        json_companies = self.json_loader.load_companies()
        logger.info(f"Loaded {len(json_companies)} companies from JSON")

        # Load Markdown companies
        markdown_companies = self._load_markdown_companies()
        logger.info(f"Loaded {len(markdown_companies)} companies from Markdown")

        # Create mapping for quick lookup
        markdown_map = {c.id: c for c in markdown_companies}

        # Merge companies
        unified_companies = []
        for json_company in json_companies:
            markdown_company = markdown_map.get(json_company.id)

            if markdown_company:
                # Merge with conflict resolution
                unified = self._merge_companies(json_company, markdown_company)
            else:
                # Use JSON only
                unified = self._convert_to_unified(json_company, source="JSON")

            unified_companies.append(unified)

        # Add Markdown-only companies (if any)
        json_ids = {c.id for c in json_companies}
        for markdown_company in markdown_companies:
            if markdown_company.id not in json_ids:
                unified = self._convert_to_unified(markdown_company, source="Markdown")
                unified_companies.append(unified)

        logger.info(f"Created {len(unified_companies)} unified companies")
        
        # Populate signal confidences for scoring component weighting
        for company in unified_companies:
            populate_signal_confidences(company)
        
        return unified_companies
        return unified_companies

    def _load_markdown_companies(self) -> List[Company]:
        """Load companies from Markdown files in dutch_market directory."""

        companies = []

        if not self.markdown_dir.exists():
            logger.warning(f"Markdown directory not found: {self.markdown_dir}")
            return companies

        # Find all .md files
        for md_file in self.markdown_dir.glob("*.md"):
            try:
                extracted_data = self.markdown_extractor.extract_from_file(md_file)
                if extracted_data:
                    company = self.markdown_extractor.to_company_profile(extracted_data)
                    companies.append(company)
                    logger.debug(f"Loaded Markdown company: {company.name}")
            except Exception as e:
                logger.warning(f"Failed to load Markdown file {md_file}: {e}")

        return companies

    def _merge_companies(self, json_company: Company, markdown_company: Company) -> UnifiedCompany:
        """
        Merge JSON and Markdown companies with conflict resolution.
        Priority: Markdown > JSON
        """

        conflicts = []
        data_sources = {}

        # Start with JSON company as base
        merged = UnifiedCompany(**json_company.model_dump())

        # Merge financial metrics
        if json_company.financials and markdown_company.financials:
            merged_financials = self._merge_financials(
                json_company.financials, markdown_company.financials, conflicts, data_sources
            )
            merged.financials = merged_financials
        elif markdown_company.financials:
            merged.financials = markdown_company.financials
            data_sources["financials"] = "Markdown"

        # Merge other fields with Markdown priority
        if markdown_company.tier != json_company.tier:
            conflicts.append("tier")
            merged.tier = markdown_company.tier
            data_sources["tier"] = "Markdown"
        else:
            data_sources["tier"] = "JSON"

        if markdown_company.ai_maturity != json_company.ai_maturity:
            conflicts.append("ai_maturity")
            merged.ai_maturity = markdown_company.ai_maturity
            data_sources["ai_maturity"] = "Markdown"
            # Infer AI score from AI maturity when there's a conflict
            self._infer_ai_score_from_maturity(merged, markdown_company.ai_maturity)
        else:
            data_sources["ai_maturity"] = "JSON"
            # Also check if AI score is 0 but maturity is Strong/Very Strong - fix contradiction
            if merged.ai_score == 0 and merged.ai_maturity in ["Strong", "Very Strong"]:
                self._infer_ai_score_from_maturity(merged, merged.ai_maturity)

        if markdown_company.threat_level != json_company.threat_level:
            conflicts.append("threat_level")
            merged.threat_level = markdown_company.threat_level
            data_sources["threat_level"] = "Markdown"
        else:
            data_sources["threat_level"] = "JSON"

        if markdown_company.geographic_presence != json_company.geographic_presence:
            conflicts.append("geographic_presence")
            merged.geographic_presence = markdown_company.geographic_presence
            data_sources["geographic_presence"] = "Markdown"
        else:
            data_sources["geographic_presence"] = "JSON"

        # Set tracking fields
        merged.data_source_per_field = data_sources
        merged.merge_conflicts = conflicts
        merged.merge_timestamp = datetime.now(timezone.utc)

        if conflicts:
            logger.info(f"Merged {merged.name} with {len(conflicts)} conflicts: {conflicts}")

        return merged

    def _merge_financials(
        self,
        json_fin: FinancialMetric,
        markdown_fin: FinancialMetric,
        conflicts: List[str],
        data_sources: Dict[str, str],
    ) -> FinancialMetric:
        """Merge financial metrics with Markdown priority."""

        # Start with JSON
        merged = FinancialMetric(**json_fin.model_dump())

        # Apply Markdown values with priority
        if markdown_fin.revenue is not None and markdown_fin.revenue != json_fin.revenue:
            conflicts.append("revenue")
            merged.revenue = markdown_fin.revenue
            merged.revenue_confidence = markdown_fin.revenue_confidence
            data_sources["revenue"] = "Markdown"
        else:
            data_sources["revenue"] = "JSON"

        if markdown_fin.growth_rate is not None and markdown_fin.growth_rate != json_fin.growth_rate:
            conflicts.append("growth_rate")
            merged.growth_rate = markdown_fin.growth_rate
            merged.growth_confidence = markdown_fin.growth_confidence
            data_sources["growth_rate"] = "Markdown"
        else:
            data_sources["growth_rate"] = "JSON"

        if markdown_fin.employees is not None and markdown_fin.employees != json_fin.employees:
            conflicts.append("employees")
            merged.employees = markdown_fin.employees
            merged.employees_confidence = markdown_fin.employees_confidence
            data_sources["employees"] = "Markdown"
        else:
            data_sources["employees"] = "JSON"

        if markdown_fin.profit_margin is not None and markdown_fin.profit_margin != json_fin.profit_margin:
            conflicts.append("profit_margin")
            merged.profit_margin = markdown_fin.profit_margin
            merged.margin_confidence = markdown_fin.margin_confidence
            data_sources["profit_margin"] = "Markdown"
        else:
            data_sources["profit_margin"] = "JSON"

        if markdown_fin.funding_raised is not None and markdown_fin.funding_raised != json_fin.funding_raised:
            conflicts.append("funding_raised")
            merged.funding_raised = markdown_fin.funding_raised
            merged.funding_confidence = markdown_fin.funding_confidence
            data_sources["funding_raised"] = "Markdown"
        else:
            data_sources["funding_raised"] = "JSON"

        if markdown_fin.valuation is not None and markdown_fin.valuation != json_fin.valuation:
            conflicts.append("valuation")
            merged.valuation = markdown_fin.valuation
            merged.valuation_confidence = markdown_fin.valuation_confidence
            data_sources["valuation"] = "Markdown"
        else:
            data_sources["valuation"] = "JSON"

        return merged

    def _convert_to_unified(self, company: Company, source: str) -> UnifiedCompany:
        """Convert a Company to UnifiedCompany with source tracking."""

        unified = UnifiedCompany(**company.model_dump())

        # Track all fields as coming from single source
        unified.data_source_per_field = {
            "revenue": source,
            "growth_rate": source,
            "employees": source,
            "profit_margin": source,
            "funding_raised": source,
            "valuation": source,
            "tier": source,
            "ai_maturity": source,
            "threat_level": source,
            "geographic_presence": source,
        }
        unified.merge_conflicts = []
        unified.merge_timestamp = datetime.now(timezone.utc)

        return unified


    def _infer_ai_score_from_maturity(self, company: UnifiedCompany, ai_maturity: str) -> None:
        """Infer AI score from AI maturity level when there's a conflict.
        
        Maps AI maturity levels to scores using the CompetitivePositionConfig mapping.
        This fixes contradictions like 'Strong' maturity with 0/10 score.
        """
        from ..core.scoring_config import CompetitivePositionConfig
        
        config = CompetitivePositionConfig()
        ai_maturity_scores = config.ai_maturity_scores
        
        # Map AI maturity to score (0-10 scale)
        # CompetitivePositionConfig uses -1.0 to 2.5 scale, so we need to normalize to 0-10
        maturity_score = ai_maturity_scores.get(ai_maturity, 0.0)
        # Normalize: -1.0 to 2.5 range maps to 0-10 range
        # Formula: ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
        normalized_score = ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
        normalized_score = max(0, min(10, int(round(normalized_score))))  # Round to int and clamp to 0-10
        
        company.ai_score = normalized_score
        logger.info(f"Inferred AI score {normalized_score}/10 for {company.name} from AI maturity '{ai_maturity}'")


# Global instance
unified_loader = UnifiedCompanyLoader()
