"""Automated data remediation for EPIC-013.

Automatically fixes common data quality issues without manual intervention.
"""

from typing import Any, Callable
from dataclasses import dataclass
from loguru import logger

from solstein.domain.models import Company
from solstein.validation.company_validator import CompanyValidator, ValidationIssue


@dataclass
class RemediationRule:
    """Rule for automatically remediating data issues."""

    name: str
    check: Callable[[Company], bool]
    fix: Callable[[Company], Company]
    description: str


class DataRemediationEngine:
    """Automatically remediates data quality issues.

    Usage:
        engine = DataRemediationEngine()
        company = engine.remediate(company)
    """

    def __init__(self):
        self.rules = self._default_rules()

    def _default_rules(self) -> list[RemediationRule]:
        """Define default remediation rules."""
        return [
            RemediationRule(
                name="missing_company_name",
                check=lambda c: not c.name or c.name.strip() == "",
                fix=self._fix_missing_name,
                description="Generate company name from ID if missing",
            ),
            RemediationRule(
                name="negative_revenue",
                check=lambda c: c.financials and c.financials.revenue is not None and c.financials.revenue < 0,
                fix=self._fix_negative_revenue,
                description="Set negative revenue to None",
            ),
            RemediationRule(
                name="zero_employees",
                check=lambda c: c.financials and c.financials.employees == 0,
                fix=self._fix_zero_employees,
                description="Set zero employees to None (unknown)",
            ),
            RemediationRule(
                name="extreme_growth_rate",
                check=lambda c: (
                    c.financials and c.financials.growth_rate is not None and abs(c.financials.growth_rate) > 1000
                ),
                fix=self._fix_extreme_growth,
                description="Cap extreme growth rates at ±1000%",
            ),
            RemediationRule(
                name="future_founded_year",
                check=lambda c: c.founded_year is not None and c.founded_year > 2030,
                fix=self._fix_future_founded_year,
                description="Set future founded year to None",
            ),
            RemediationRule(
                name="missing_industry",
                check=lambda c: not c.industry or c.industry.strip() == "",
                fix=self._fix_missing_industry,
                description="Set default industry to 'Unknown'",
            ),
        ]

    def _fix_missing_name(self, company: Company) -> Company:
        """Generate company name from ID if missing."""
        if company.id:
            company.name = company.id.replace("-", " ").title()
        else:
            company.name = "Unknown Company"
        logger.info(f"Fixed missing name for {company.id}: {company.name}")
        return company

    def _fix_negative_revenue(self, company: Company) -> Company:
        """Set negative revenue to None."""
        logger.warning(f"Fixed negative revenue for {company.name}: {company.financials.revenue}")
        company.financials.revenue = None
        return company

    def _fix_zero_employees(self, company: Company) -> Company:
        """Set zero employees to None."""
        logger.info(f"Fixed zero employees for {company.name}")
        company.financials.employees = None
        return company

    def _fix_extreme_growth(self, company: Company) -> Company:
        """Cap extreme growth rates."""
        old_value = company.financials.growth_rate
        company.financials.growth_rate = max(-1000, min(1000, old_value))
        logger.warning(f"Fixed extreme growth for {company.name}: {old_value} -> {company.financials.growth_rate}")
        return company

    def _fix_future_founded_year(self, company: Company) -> Company:
        """Set future founded year to None."""
        logger.warning(f"Fixed future founded year for {company.name}: {company.founded_year}")
        company.founded_year = None
        return company

    def _fix_missing_industry(self, company: Company) -> Company:
        """Set default industry."""
        company.industry = "Unknown"
        logger.info(f"Fixed missing industry for {company.name}")
        return company

    def remediate(self, company: Company) -> tuple[Company, list[str]]:
        """Apply all remediation rules to a company.

        Returns:
            Tuple of (remediated_company, list_of_applied_fixes)
        """
        applied_fixes = []

        for rule in self.rules:
            try:
                if rule.check(company):
                    company = rule.fix(company)
                    applied_fixes.append(rule.name)
                    logger.info(f"Applied remediation '{rule.name}' to {company.name or company.id}")
            except Exception as e:
                logger.error(f"Failed to apply remediation '{rule.name}': {e}")

        return company, applied_fixes

    def remediate_batch(self, companies: list[Company]) -> tuple[list[Company], dict[str, int]]:
        """Remediate a batch of companies.

        Returns:
            Tuple of (remediated_companies, fix_statistics)
        """
        remediated = []
        stats: dict[str, int] = {}

        for company in companies:
            fixed_company, fixes = self.remediate(company)
            remediated.append(fixed_company)

            for fix in fixes:
                stats[fix] = stats.get(fix, 0) + 1

        logger.info(f"Batch remediation complete. Applied {sum(stats.values())} fixes to {len(companies)} companies.")
        return remediated, stats
