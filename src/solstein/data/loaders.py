"""
Data loaders for SolStein competitive intelligence platform.

Loads competitor data from various sources (JSON files, APIs, databases)
and converts them to standardized CompanyProfile models.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config import Settings
from .models import (
    AIMaturity,
    CompanyProfile,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)

logger = logging.getLogger(__name__)
settings = Settings()


class CompetitorDataLoader:
    """Load competitor data from JSON files and convert to models."""

    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path(settings.data.data_dir)
        self._cache = {}

    def load_companies(self, limit: int | None = None) -> list[CompanyProfile]:
        """Load all companies from data directory."""
        cache_key = f"companies_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        companies = []

        # Try to load from the main competitor data JSON
        json_path = self.data_dir / "competitor_data.json"
        if json_path.exists():
            companies.extend(self._load_from_json(json_path, limit))
        else:
            # Fallback: look for JSON files in the project
            project_json = Path(__file__).parent.parent.parent.parent / "SolStein" / "COMPETITION" / "competitor_data.json"
            if project_json.exists():
                companies.extend(self._load_from_json(project_json, limit))
            else:
                logger.warning(f"No competitor data found at {json_path} or {project_json}")
                # Create sample data for demo
                companies.extend(self._create_sample_data(limit or 10))

        if limit:
            companies = companies[:limit]

        self._cache[cache_key] = companies
        return companies

    def _load_from_json(self, json_path: Path, limit: int | None = None) -> list[CompanyProfile]:
        """Load companies from JSON file."""
        try:
            with open(json_path) as f:
                data = json.load(f)

            competitors = data.get("competitors", [])
            if limit:
                competitors = competitors[:limit]

            companies = []
            for i, comp in enumerate(competitors):
                try:
                    company = self._convert_to_company_profile(comp, i)
                    companies.append(company)
                except Exception as e:
                    logger.warning(f"Error converting competitor {i}: {e}")
                    continue

            logger.info(f"Loaded {len(companies)} companies from {json_path}")
            return companies

        except Exception as e:
            logger.error(f"Error loading JSON from {json_path}: {e}")
            return []

    def _convert_to_company_profile(self, raw_data: dict[str, Any], index: int) -> CompanyProfile:
        """Convert raw JSON data to CompanyProfile model."""
        # Extract basic info
        company_name = raw_data.get("company_name", f"Company {index}")
        folder = raw_data.get("folder", f"company-{index}")

        # Extract financial data
        revenue_data = raw_data.get("revenue", {})
        timeline = revenue_data.get("timeline", [])

        if timeline:
            latest = timeline[0]
            revenue = latest.get("eur_millions")
            growth = latest.get("yoy_growth_pct")
            revenue_confidence = self._convert_confidence(latest.get("confidence"))
        else:
            revenue = None
            growth = None
            revenue_confidence = ConfidenceLevel.UNKNOWN

        # Create financial metric
        financial = FinancialMetric(
            revenue=revenue,
            revenue_confidence=revenue_confidence,
            growth_rate=growth,
            growth_confidence=ConfidenceLevel.ESTIMATED if growth else ConfidenceLevel.UNKNOWN,
            employees=self._estimate_employees(revenue),
            employees_confidence=ConfidenceLevel.ESTIMATED
        )

        # Determine tier based on revenue
        tier = self._determine_tier(revenue)

        # Determine AI maturity from scorecard
        scorecard = raw_data.get("scorecard", {})
        dimensions = scorecard.get("dimensions", {})
        saas_score = dimensions.get("SaaS Maturity", {}).get("score", 5)

        # Convert to AI maturity
        if saas_score >= 8:
            ai_maturity = AIMaturity.STRONG
        elif saas_score >= 5:
            ai_maturity = AIMaturity.MODERATE
        else:
            ai_maturity = AIMaturity.LOW

        # Determine threat level from composite score
        composite_score = scorecard.get("composite_score", 5)
        if composite_score >= 8:
            threat_level = ThreatLevel.HIGH
        elif composite_score >= 6:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        # Create company profile
        company = CompanyProfile(
            id=folder.lower().replace(" ", "-").replace("/", "-"),
            name=company_name,
            industry="Energy Software",  # Default for this dataset
            description="Competitor in energy software market",
            website=None,  # Would extract from data in production
            headquarters=self._estimate_headquarters(folder),
            founded_year=self._estimate_founded_year(index),
            tier=tier,
            threat_level=threat_level,
            ai_maturity=ai_maturity,
            saas_maturity=int(saas_score),
            tech_stack=["Python", "React", "PostgreSQL"],  # Default
            financials=financial,
            geographic_presence=["Europe"],  # Default for this dataset
            key_customers=["Utilities", "Energy Traders"],  # Default
            parent_company=None,
            subsidiaries=[],
            acquisitions=[],
            last_updated=datetime.now(),
            data_source="SolStein Competitive Intelligence",
            notes=f"Loaded from competitor data. Data availability: {raw_data.get('data_availability', 'Unknown')}",
            growth_score=None,  # Will be calculated separately
            financial_health_score=None,
            competitive_position_score=None
        )

        return company

    def _convert_confidence(self, confidence_str: str | None) -> ConfidenceLevel:
        """Convert string confidence to ConfidenceLevel enum."""
        if not confidence_str:
            return ConfidenceLevel.UNKNOWN

        confidence_str = confidence_str.lower()
        if "confirm" in confidence_str:
            return ConfidenceLevel.CONFIRMED
        elif "estimate" in confidence_str:
            return ConfidenceLevel.ESTIMATED
        else:
            return ConfidenceLevel.UNKNOWN

    def _estimate_employees(self, revenue: float | None) -> int | None:
        """Estimate number of employees based on revenue."""
        if revenue is None:
            return None

        # Rough estimate: €200,000 revenue per employee for software companies
        employees = int(revenue * 1_000_000 / 200_000)
        return max(10, min(employees, 10000))  # Bound between 10 and 10,000

    def _determine_tier(self, revenue: float | None) -> CompanyTier:
        """Determine company tier based on revenue."""
        if revenue is None:
            return CompanyTier.TIER_4

        if revenue > 1000:  # > €1B
            return CompanyTier.TIER_1
        elif revenue > 100:  # > €100M
            return CompanyTier.TIER_2
        elif revenue > 10:  # > €10M
            return CompanyTier.TIER_3
        else:
            return CompanyTier.TIER_4

    def _estimate_headquarters(self, folder: str) -> str | None:
        """Estimate headquarters based on folder name."""
        folder_lower = folder.lower()

        if "uk" in folder_lower or "british" in folder_lower:
            return "United Kingdom"
        elif "german" in folder_lower or "deutsch" in folder_lower:
            return "Germany"
        elif "french" in folder_lower or "france" in folder_lower:
            return "France"
        elif "norway" in folder_lower or "norwegian" in folder_lower:
            return "Norway"
        elif "spain" in folder_lower or "spanish" in folder_lower:
            return "Spain"
        elif "poland" in folder_lower or "polish" in folder_lower:
            return "Poland"
        elif "swiss" in folder_lower or "switzerland" in folder_lower:
            return "Switzerland"
        else:
            return "Europe"

    def _estimate_founded_year(self, index: int) -> int | None:
        """Estimate founded year (for demo purposes)."""
        base_year = 2000
        return base_year + (index % 25)  # Between 2000 and 2025

    def _create_sample_data(self, count: int) -> list[CompanyProfile]:
        """Create sample data for demo purposes."""
        companies = []

        sample_names = [
            "Eneve (formerly Energy21)",
            "Volue ASA",
            "Octopus Energy Group",
            "CGI Inc.",
            "Hitachi Energy",
            "Sopra Steria",
            "Indra Sistemas",
            "Asseco Poland",
            "Engineering Ingegneria",
            "Hansen Technologies"
        ]

        for i in range(min(count, len(sample_names))):
            # Create sample financial data
            revenue = 1000.0 * (i + 1)  # €1M to €10M
            growth = 5.0 + (i * 2)  # 5% to 23%

            financial = FinancialMetric(
                revenue=revenue,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                growth_rate=growth,
                growth_confidence=ConfidenceLevel.ESTIMATED,
                employees=int(revenue * 5),  # Rough estimate
                employees_confidence=ConfidenceLevel.ESTIMATED
            )

            # Create company
            company = CompanyProfile(
                id=f"sample-{i}",
                name=sample_names[i],
                industry="Energy Software",
                description=f"Sample competitor {i+1} in energy software market",
                tier=self._determine_tier(revenue),
                threat_level=ThreatLevel.MEDIUM,
                ai_maturity=AIMaturity.MODERATE,
                saas_maturity=7,
                tech_stack=["Python", "React", "PostgreSQL", "Docker"],
                financials=financial,
                geographic_presence=["Europe"],
                key_customers=["Utilities", "Energy Traders"],
                last_updated=datetime.now(),
                data_source="Sample Data"
            )

            companies.append(company)

        logger.info(f"Created {len(companies)} sample companies")
        return companies

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
        logger.debug("Cleared data cache")


# Global instance for easy import
loader = CompetitorDataLoader()
