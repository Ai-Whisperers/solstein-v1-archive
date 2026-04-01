"""Tests for STORY-127: Deduplicate profit_margin and employee fields.

Validates that:
- FinancialMetric is the canonical source of truth
- Company.profit_margin is a read-only computed property
- Company.employees is a read-only computed property
- Company.employee_count is a read-only computed property
- Constructor kwargs are routed to FinancialMetric
- Direct assignment to Company-level fields raises errors
- Write paths go through FinancialMetric exclusively
"""

import pytest

from solstein.domain.models import Company, FinancialMetric


class TestCanonicalSourceDesignation:
    """FinancialMetric is the single source of truth for financial metrics."""

    def test_profit_margin_reads_from_financials(self):
        """Company.profit_margin delegates to FinancialMetric."""
        fm = FinancialMetric(revenue=100.0, profit_margin=0.15)
        company = Company(id="TEST-001", name="Test Corp", financials=fm)
        assert company.profit_margin == 0.15
        assert company.profit_margin == company.financials.profit_margin

    def test_employees_reads_from_financials(self):
        """Company.employees delegates to FinancialMetric."""
        fm = FinancialMetric(employees=500, allow_empty_primary=True)
        company = Company(id="TEST-002", name="Test Corp 2", financials=fm)
        assert company.employees == 500
        assert company.employees == company.financials.employees

    def test_employee_count_reads_from_financials(self):
        """Company.employee_count delegates to FinancialMetric.employees."""
        fm = FinancialMetric(employees=300, allow_empty_primary=True)
        company = Company(id="TEST-003", name="Test Corp 3", financials=fm)
        assert company.employee_count == 300
        assert company.employee_count == company.financials.employees

    def test_employee_count_equals_employees(self):
        """Company.employee_count and Company.employees return same value."""
        fm = FinancialMetric(employees=200, allow_empty_primary=True)
        company = Company(id="TEST-004", name="Test Corp 4", financials=fm)
        assert company.employees == company.employee_count

    def test_no_financials_returns_none(self):
        """When financials is None, computed fields return None."""
        company = Company(id="TEST-005", name="Test Corp 5")
        assert company.profit_margin is None
        assert company.employees is None
        assert company.employee_count is None


class TestReadOnlyProperties:
    """Direct assignment to Company-level deprecated fields raises errors."""

    def test_profit_margin_is_read_only(self):
        """Assigning to Company.profit_margin raises AttributeError."""
        company = Company(id="TEST-010", name="Test Corp")
        with pytest.raises((AttributeError, ValueError)):
            company.profit_margin = 0.20  # type: ignore[misc]

    def test_employees_is_read_only(self):
        """Assigning to Company.employees raises AttributeError."""
        company = Company(id="TEST-011", name="Test Corp")
        with pytest.raises((AttributeError, ValueError)):
            company.employees = 200  # type: ignore[misc]

    def test_employee_count_is_read_only(self):
        """Assigning to Company.employee_count raises AttributeError."""
        company = Company(id="TEST-012", name="Test Corp")
        with pytest.raises((AttributeError, ValueError)):
            company.employee_count = 200  # type: ignore[misc]


class TestConstructorRouting:
    """Constructor kwargs for deprecated fields are routed to FinancialMetric."""

    def test_profit_margin_in_constructor(self):
        """profit_margin in constructor is routed to financials."""
        company = Company(id="TEST-020", name="Test Corp", profit_margin=0.25)
        assert company.financials.profit_margin == 0.25
        assert company.profit_margin == 0.25

    def test_employees_in_constructor(self):
        """employees in constructor is routed to financials."""
        company = Company(id="TEST-021", name="Test Corp", employees=150)
        assert company.financials.employees == 150
        assert company.employees == 150

    def test_employee_count_in_constructor(self):
        """employee_count in constructor is routed to financials.employees."""
        company = Company(id="TEST-022", name="Test Corp", employee_count=75)
        assert company.financials.employees == 75
        assert company.employee_count == 75

    def test_financials_takes_precedence_over_constructor_kwargs(self):
        """When both financials and top-level kwargs provided, financials wins."""
        fm = FinancialMetric(profit_margin=0.30, employees=500, allow_empty_primary=True)
        company = Company(
            id="TEST-023",
            name="Test Corp",
            financials=fm,
            profit_margin=0.10,  # Should not override financials
            employees=100,  # Should not override financials
        )
        assert company.profit_margin == 0.30
        assert company.employees == 500

    def test_constructor_creates_financials_when_missing(self):
        """When no financials provided, constructor kwargs create one."""
        company = Company(id="TEST-024", name="Test Corp", profit_margin=0.18, employees=80)
        assert company.financials is not None
        assert company.financials.profit_margin == 0.18
        assert company.financials.employees == 80

    def test_both_employees_and_employee_count_employees_wins(self):
        """When both employees and employee_count provided, employees is used first."""
        company = Company(id="TEST-025", name="Test Corp", employees=100, employee_count=200)
        # employees is processed first in the before-validator
        assert company.financials.employees == 100

    def test_model_dump_and_recreate(self):
        """Company.model_dump() output can recreate the same company."""
        original = Company(
            id="TEST-026",
            name="Test Corp",
            profit_margin=0.22,
            employees=350,
        )
        dump = original.model_dump()
        recreated = Company(**dump)
        assert recreated.profit_margin == original.profit_margin
        assert recreated.employees == original.employees
        assert recreated.employee_count == original.employee_count


class TestWritePathConsolidation:
    """All write paths go through FinancialMetric exclusively."""

    def test_update_profit_margin_via_financials(self):
        """Updating FinancialMetric.profit_margin is reflected in Company."""
        company = Company(id="TEST-030", name="Test Corp", profit_margin=0.10)
        company.financials.profit_margin = 0.25
        assert company.profit_margin == 0.25

    def test_update_employees_via_financials(self):
        """Updating FinancialMetric.employees is reflected in Company."""
        company = Company(id="TEST-031", name="Test Corp", employees=100)
        company.financials.employees = 200
        assert company.employees == 200
        assert company.employee_count == 200


class TestModelDumpSerialization:
    """Computed fields appear in model_dump output."""

    def test_profit_margin_in_model_dump(self):
        """profit_margin appears in model_dump."""
        company = Company(id="TEST-040", name="Test Corp", profit_margin=0.15)
        dump = company.model_dump()
        assert "profit_margin" in dump
        assert dump["profit_margin"] == 0.15

    def test_employees_in_model_dump(self):
        """employees appears in model_dump."""
        company = Company(id="TEST-041", name="Test Corp", employees=250)
        dump = company.model_dump()
        assert "employees" in dump
        assert dump["employees"] == 250

    def test_employee_count_in_model_dump(self):
        """employee_count appears in model_dump."""
        company = Company(id="TEST-042", name="Test Corp", employees=250)
        dump = company.model_dump()
        assert "employee_count" in dump
        assert dump["employee_count"] == 250

    def test_null_computed_fields_in_model_dump(self):
        """Null computed fields still appear in model_dump."""
        company = Company(id="TEST-043", name="Test Corp")
        dump = company.model_dump()
        assert "profit_margin" in dump
        assert dump["profit_margin"] is None
        assert "employees" in dump
        assert dump["employees"] is None


class TestBackwardCompatibility:
    """Existing read patterns continue to work."""

    def test_getattr_profit_margin(self):
        """getattr(company, 'profit_margin') works."""
        company = Company(id="TEST-050", name="Test Corp", profit_margin=0.12)
        assert company.profit_margin == 0.12

    def test_getattr_employees(self):
        """getattr(company, 'employees') works."""
        company = Company(id="TEST-051", name="Test Corp", employees=100)
        assert company.employees == 100

    def test_getattr_employee_count(self):
        """getattr(company, 'employee_count') works."""
        company = Company(id="TEST-052", name="Test Corp", employees=100)
        assert company.employee_count == 100

    def test_safe_get_pattern(self):
        """Common safe_get pattern still works: getattr(obj, field, default)."""
        company = Company(id="TEST-053", name="Test Corp")
        assert getattr(company, "profit_margin", 0.0) is None  # Returns None, not default
        assert getattr(company, "employees", 0) is None  # Returns None, not default

    def test_dict_access_via_model_dump(self):
        """company.model_dump()['profit_margin'] still works."""
        company = Company(id="TEST-054", name="Test Corp", profit_margin=0.15, employees=100)
        d = company.model_dump()
        assert d["profit_margin"] == 0.15
        assert d["employees"] == 100
        assert d["employee_count"] == 100


class TestFinancialMetricValidation:
    """FinancialMetric validates profit_margin and employees at the canonical source."""

    def test_negative_employees_rejected(self):
        """Negative employees in FinancialMetric is rejected."""
        with pytest.raises(ValueError, match="cannot be negative"):
            FinancialMetric(employees=-5, allow_empty_primary=True)

    def test_profit_margin_on_financial_metric(self):
        """profit_margin is validated on FinancialMetric."""
        fm = FinancialMetric(profit_margin=0.5, allow_empty_primary=True)
        assert fm.profit_margin == 0.5

    def test_financial_metric_is_documented_as_canonical(self):
        """FinancialMetric docstring indicates it's the canonical source."""
        assert "financial metrics" in FinancialMetric.__doc__.lower()
