"""STORY-206: Company Model Field Validation Tests.

Validates that Company and FinancialMetric models enforce field constraints:
- Revenue must be non-negative
- Growth rate must be in reasonable range
- AI score must be 0-10
- Required fields cannot be None/empty
- Scoring readiness warnings are produced for missing data
"""

import pytest
from pydantic import ValidationError

from solstein.domain.models import Company, FinancialMetric

# -----------------------------------------------------------------------
# FinancialMetric validation
# -----------------------------------------------------------------------


class TestFinancialMetricValidation:
    """Tests for FinancialMetric field validators."""

    def test_valid_financial_metric(self):
        """Complete FinancialMetric with all fields passes validation."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=15.0,
            employees=100,
            profit_margin=12.5,
        )
        assert fm.revenue == 1000.0
        assert fm.growth_rate == 15.0
        assert fm.employees == 100

    def test_revenue_negative_raises(self):
        """Negative revenue raises ValidationError."""
        with pytest.raises(ValidationError, match="revenue must be >= 0"):
            FinancialMetric(revenue=-500.0, employees=10)

    def test_revenue_zero_allowed(self):
        """Revenue of 0 is technically valid (pre-revenue company)."""
        fm = FinancialMetric(revenue=0.0, employees=10)
        assert fm.revenue == 0.0

    def test_growth_rate_too_high_raises(self):
        """Growth rate > 1000% raises ValidationError."""
        with pytest.raises(ValidationError, match="growth_rate must be in"):
            FinancialMetric(growth_rate=1500.0, employees=10)

    def test_growth_rate_too_low_raises(self):
        """Growth rate < -100% raises ValidationError."""
        with pytest.raises(ValidationError, match="growth_rate must be in"):
            FinancialMetric(growth_rate=-150.0, employees=10)

    def test_growth_rate_negative_allowed(self):
        """Negative growth rate within range is valid (declining company)."""
        fm = FinancialMetric(growth_rate=-50.0, employees=10)
        assert fm.growth_rate == -50.0

    def test_growth_rate_hyper_growth_allowed(self):
        """Hyper-growth rates up to 1000% are valid."""
        fm = FinancialMetric(growth_rate=200.0, employees=10)
        assert fm.growth_rate == 200.0

    def test_employees_negative_raises(self):
        """Negative employee count raises ValidationError."""
        with pytest.raises(ValidationError, match="Employees cannot be negative"):
            FinancialMetric(employees=-5, revenue=100.0)

    def test_require_primary_metric(self):
        """At least revenue OR employees must be provided."""
        with pytest.raises(ValidationError, match="At least revenue OR employees"):
            FinancialMetric()

    def test_allow_empty_primary(self):
        """allow_empty_primary=True bypasses primary metric requirement."""
        fm = FinancialMetric(allow_empty_primary=True)
        assert fm.revenue is None
        assert fm.employees is None

    def test_revenue_none_with_employees_valid(self):
        """Revenue None is valid when employees is provided."""
        fm = FinancialMetric(revenue=None, employees=100)
        assert fm.revenue is None
        assert fm.employees == 100

    def test_employees_none_with_revenue_valid(self):
        """Employees None is valid when revenue is provided."""
        fm = FinancialMetric(revenue=1000.0, employees=None)
        assert fm.revenue == 1000.0
        assert fm.employees is None


# -----------------------------------------------------------------------
# Company model validation
# -----------------------------------------------------------------------


class TestCompanyValidation:
    """Tests for Company field validators."""

    def _make_company(self, **kwargs):
        """Helper to create a valid Company with overrides."""
        defaults = {
            "id": "COMP-TEST-001",
            "name": "Test Corp",
            "revenue": 1000.0,
            "growth_rate": 15.0,
            "financials": FinancialMetric(
                revenue=1000.0,
                growth_rate=15.0,
                employees=100,
                profit_margin=10.0,
            ),
        }
        defaults.update(kwargs)
        return Company(**defaults)

    def test_valid_company_passes(self):
        """Fully valid company passes all validation."""
        company = self._make_company()
        assert company.name == "Test Corp"
        assert company.revenue == 1000.0

    def test_name_required(self):
        """Company name cannot be omitted."""
        with pytest.raises(ValidationError):
            Company(id="COMP-TEST-001")

    def test_id_required(self):
        """Company ID cannot be empty."""
        with pytest.raises(ValidationError, match="Company ID cannot be empty"):
            Company(id="", name="Test")

    def test_id_too_short(self):
        """Company ID must be at least 3 characters."""
        with pytest.raises(ValidationError, match="at least 3 characters"):
            Company(id="AB", name="Test")

    def test_revenue_negative_raises(self):
        """Negative revenue at Company level raises ValidationError."""
        with pytest.raises(ValidationError, match="revenue must be >= 0"):
            self._make_company(revenue=-500.0)

    def test_growth_rate_extreme_raises(self):
        """Extremely high growth rate raises ValidationError."""
        with pytest.raises(ValidationError, match="growth_rate must be in"):
            self._make_company(growth_rate=1500.0)

    def test_ai_score_above_10_raises(self):
        """AI score > 10 raises ValidationError."""
        with pytest.raises(ValidationError, match="AI score must be between 0 and 10"):
            self._make_company(ai_score=11.0)

    def test_ai_score_below_0_raises(self):
        """AI score < 0 raises ValidationError."""
        with pytest.raises(ValidationError, match="AI score must be between 0 and 10"):
            self._make_company(ai_score=-1.0)

    def test_ai_score_valid(self):
        """Valid AI score is accepted."""
        company = self._make_company(ai_score=7.5)
        assert company.ai_score == 7.5

    def test_revenue_zero_allowed_on_company(self):
        """Revenue of 0 is valid at Company level."""
        company = self._make_company(revenue=0.0)
        assert company.revenue == 0.0

    def test_growth_rate_none_allowed(self):
        """Growth rate None is valid (missing data case)."""
        company = self._make_company(
            growth_rate=None,
            financials=FinancialMetric(
                revenue=1000.0,
                growth_rate=None,
                employees=100,
            ),
        )
        assert company.growth_rate is None

    def test_revenue_none_allowed(self):
        """Revenue None is valid (missing data case)."""
        company = self._make_company(
            revenue=None,
            financials=FinancialMetric(
                revenue=None,
                employees=100,
                growth_rate=15.0,
            ),
        )
        assert company.revenue is None


# -----------------------------------------------------------------------
# Scoring readiness validation
# -----------------------------------------------------------------------


class TestScoringReadiness:
    """Tests for validate_scoring_readiness method."""

    def _make_company(self, **kwargs):
        """Helper to create a Company with override support."""
        defaults = {
            "id": "COMP-TEST-001",
            "name": "Test Corp",
            "financials": FinancialMetric(
                revenue=1000.0,
                growth_rate=15.0,
                employees=100,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
            "signal_confidences": {"revenue": 0.85, "growth_rate": 0.72},
        }
        defaults.update(kwargs)
        return Company(**defaults)

    def test_complete_company_no_warnings(self):
        """Company with all data produces no warnings."""
        company = self._make_company()
        warnings = company.validate_scoring_readiness()
        assert len(warnings) == 0

    def test_missing_revenue_warns(self):
        """Company with None revenue produces warning."""
        company = self._make_company(
            financials=FinancialMetric(
                revenue=None,
                employees=100,
                growth_rate=15.0,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
        )
        warnings = company.validate_scoring_readiness()
        assert any("revenue is None" in w for w in warnings)

    def test_missing_employees_warns(self):
        """Company with None employees produces warning."""
        company = self._make_company(
            financials=FinancialMetric(
                revenue=1000.0,
                employees=None,
                growth_rate=15.0,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
        )
        warnings = company.validate_scoring_readiness()
        assert any("employees is None" in w for w in warnings)

    def test_missing_growth_rate_warns(self):
        """Company with None growth_rate produces warning."""
        company = self._make_company(
            financials=FinancialMetric(
                revenue=1000.0,
                employees=100,
                growth_rate=None,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
        )
        warnings = company.validate_scoring_readiness()
        assert any("growth_rate is None" in w for w in warnings)

    def test_missing_signal_confidences_warns(self):
        """Company with empty signal_confidences produces warning."""
        company = self._make_company(signal_confidences={})
        warnings = company.validate_scoring_readiness()
        assert any("signal_confidences is empty" in w for w in warnings)

    def test_zero_revenue_warns(self):
        """Company with revenue=0 produces suspicious data warning."""
        company = self._make_company(
            financials=FinancialMetric(
                revenue=0.0,
                employees=100,
                growth_rate=15.0,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
        )
        warnings = company.validate_scoring_readiness()
        assert any("revenue is 0" in w for w in warnings)

    def test_zero_employees_warns(self):
        """Company with employees=0 produces suspicious data warning."""
        company = self._make_company(
            financials=FinancialMetric(
                revenue=1000.0,
                employees=0,
                growth_rate=15.0,
                profit_margin=10.0,
                funding_raised=5000.0,
            ),
        )
        warnings = company.validate_scoring_readiness()
        assert any("employees is 0" in w for w in warnings)

    def test_all_missing_financials_warns(self):
        """Company with all financial fields None produces multiple warnings."""
        company = self._make_company(
            financials=FinancialMetric(allow_empty_primary=True),
            signal_confidences={},
        )
        warnings = company.validate_scoring_readiness()
        assert len(warnings) >= 4  # revenue, employees, growth_rate, profit_margin, funding, confidences

    def test_none_financials_defaults_and_warns(self):
        """Company with financials=None gets default FinancialMetric and warns about missing data."""
        company = Company(
            id="COMP-TEST-001",
            name="Test Corp",
            financials=None,
        )
        # sync_financial_fields model_validator creates a default FinancialMetric
        assert company.financials is not None
        warnings = company.validate_scoring_readiness()
        # Should warn about missing financial data fields
        assert len(warnings) >= 4
