"""Company data validation module.

Provides validation for company data to ensure data integrity
and catch impossible or inconsistent values.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"  # Must fix - data is invalid
    WARNING = "warning"  # Should fix - data is suspicious
    INFO = "info"  # Optional - data could be improved


@dataclass
class ValidationIssue:
    """A single validation issue."""
    field: str
    message: str
    severity: ValidationSeverity
    value: Any = None


@dataclass
class ValidationResult:
    """Result of validating a company."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def errors(self) -> List[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]


class CompanyValidator:
    """Validate company data for integrity and consistency."""
    
    # Validation rules with min/max values
    RULES = {
        "revenue": {"min": 0, "max": 1_000_000, "unit": "EUR millions"},  # €0 to €1B
        "employees": {"min": 1, "max": 500_000, "unit": "count"},
        "growth_rate": {"min": -100, "max": 1000, "unit": "percent"},  # -100% to 1000%
        "funding_raised": {"min": 0, "max": 100_000, "unit": "EUR millions"},  # €0 to €100B
        "valuation": {"min": 0, "max": 1_000_000, "unit": "EUR millions"},  # €0 to €1T
        "founded_year": {"min": 1800, "max": 2030, "unit": "year"},
        "profit_margin": {"min": -100, "max": 100, "unit": "percent"},
        "ebitda_margin": {"min": -100, "max": 100, "unit": "percent"},
    }
    
    @classmethod
    def validate(cls, company_data: Dict[str, Any]) -> ValidationResult:
        """Validate company data.
        
        Args:
            company_data: Raw company data dictionary
            
        Returns:
            ValidationResult with issues found
        """
        issues = []
        
        # Validate individual fields
        issues.extend(cls._validate_revenue(company_data))
        issues.extend(cls._validate_employees(company_data))
        issues.extend(cls._validate_growth(company_data))
        issues.extend(cls._validate_funding(company_data))
        issues.extend(cls._validate_valuation(company_data))
        issues.extend(cls._validate_founded_year(company_data))
        issues.extend(cls._validate_consistency(company_data))
        
        # Company is valid if no errors
        is_valid = len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0
        
        return ValidationResult(is_valid=is_valid, issues=issues)
    
    @classmethod
    def _validate_revenue(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate revenue field."""
        issues = []
        revenue_data = data.get("revenue", {})
        timeline = revenue_data.get("timeline", [])
        
        if not timeline:
            issues.append(ValidationIssue(
                field="revenue.timeline",
                message="Revenue timeline is missing",
                severity=ValidationSeverity.ERROR
            ))
            return issues
        
        latest = timeline[0]
        revenue = latest.get("eur_millions")
        
        if revenue is None:
            issues.append(ValidationIssue(
                field="revenue.eur_millions",
                message="Revenue value is missing",
                severity=ValidationSeverity.ERROR
            ))
        elif revenue < 0:
            issues.append(ValidationIssue(
                field="revenue.eur_millions",
                message=f"Revenue cannot be negative: {revenue}",
                severity=ValidationSeverity.ERROR,
                value=revenue
            ))
        elif revenue > cls.RULES["revenue"]["max"]:
            issues.append(ValidationIssue(
                field="revenue.eur_millions",
                message=f"Revenue seems unrealistically high: €{revenue}M",
                severity=ValidationSeverity.WARNING,
                value=revenue
            ))
        
        return issues
    
    @classmethod
    def _validate_employees(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate employees field."""
        issues = []
        employees = data.get("employees")
        
        if employees is None:
            issues.append(ValidationIssue(
                field="employees",
                message="Employee count is missing",
                severity=ValidationSeverity.WARNING
            ))
        elif employees < 0:
            issues.append(ValidationIssue(
                field="employees",
                message=f"Employee count cannot be negative: {employees}",
                severity=ValidationSeverity.ERROR,
                value=employees
            ))
        elif employees > cls.RULES["employees"]["max"]:
            issues.append(ValidationIssue(
                field="employees",
                message=f"Employee count seems unrealistically high: {employees}",
                severity=ValidationSeverity.WARNING,
                value=employees
            ))
        
        return issues
    
    @classmethod
    def _validate_growth(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate growth rate field."""
        issues = []
        revenue_data = data.get("revenue", {})
        timeline = revenue_data.get("timeline", [])
        
        if not timeline:
            return issues
        
        latest = timeline[0]
        growth = latest.get("yoy_growth_pct")
        
        if growth is None:
            issues.append(ValidationIssue(
                field="revenue.yoy_growth_pct",
                message="Growth rate is missing",
                severity=ValidationSeverity.WARNING
            ))
        elif growth < -100:
            issues.append(ValidationIssue(
                field="revenue.yoy_growth_pct",
                message=f"Growth rate cannot be less than -100%: {growth}%",
                severity=ValidationSeverity.ERROR,
                value=growth
            ))
        elif growth > 1000:
            issues.append(ValidationIssue(
                field="revenue.yoy_growth_pct",
                message=f"Growth rate seems unrealistically high: {growth}%",
                severity=ValidationSeverity.WARNING,
                value=growth
            ))
        
        return issues
    
    @classmethod
    def _validate_funding(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate funding field."""
        issues = []
        funding = data.get("funding_raised")
        
        if funding is not None and funding < 0:
            issues.append(ValidationIssue(
                field="funding_raised",
                message=f"Funding cannot be negative: {funding}",
                severity=ValidationSeverity.ERROR,
                value=funding
            ))
        
        return issues
    
    @classmethod
    def _validate_valuation(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate valuation field."""
        issues = []
        valuation = data.get("valuation")
        
        if valuation is not None and valuation < 0:
            issues.append(ValidationIssue(
                field="valuation",
                message=f"Valuation cannot be negative: {valuation}",
                severity=ValidationSeverity.ERROR,
                value=valuation
            ))
        
        return issues
    
    @classmethod
    def _validate_founded_year(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate founded year field."""
        issues = []
        founded_year = data.get("founded_year")
        
        if founded_year is not None:
            if founded_year < cls.RULES["founded_year"]["min"]:
                issues.append(ValidationIssue(
                    field="founded_year",
                    message=f"Founded year seems too old: {founded_year}",
                    severity=ValidationSeverity.WARNING,
                    value=founded_year
                ))
            elif founded_year > cls.RULES["founded_year"]["max"]:
                issues.append(ValidationIssue(
                    field="founded_year",
                    message=f"Founded year is in the future: {founded_year}",
                    severity=ValidationSeverity.ERROR,
                    value=founded_year
                ))
        
        return issues
    
    @classmethod
    def _validate_consistency(cls, data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate consistency between fields."""
        issues = []
        
        # Check funding > valuation (unusual)
        funding = data.get("funding_raised")
        valuation = data.get("valuation")
        
        if funding and valuation and funding > valuation:
            issues.append(ValidationIssue(
                field="funding_raised/valuation",
                message=f"Funding (€{funding}M) exceeds valuation (€{valuation}M) - unusual",
                severity=ValidationSeverity.WARNING,
                value={"funding": funding, "valuation": valuation}
            ))
        
        # Check revenue per employee (sanity check)
        revenue_data = data.get("revenue", {})
        timeline = revenue_data.get("timeline", [])
        employees = data.get("employees")
        
        if timeline and employees and employees > 0:
            revenue = timeline[0].get("eur_millions")
            if revenue:
                rev_per_emp = (revenue * 1_000_000) / employees
                if rev_per_emp < 10_000:  # Less than €10K per employee
                    issues.append(ValidationIssue(
                        field="revenue/employees",
                        message=f"Revenue per employee seems very low: €{rev_per_emp:,.0f}",
                        severity=ValidationSeverity.WARNING,
                        value={"revenue": revenue, "employees": employees, "rev_per_emp": rev_per_emp}
                    ))
                elif rev_per_emp > 10_000_000:  # More than €10M per employee
                    issues.append(ValidationIssue(
                        field="revenue/employees",
                        message=f"Revenue per employee seems very high: €{rev_per_emp:,.0f}",
                        severity=ValidationSeverity.WARNING,
                        value={"revenue": revenue, "employees": employees, "rev_per_emp": rev_per_emp}
                    ))
        
        return issues
